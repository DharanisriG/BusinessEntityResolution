"""
FastAPI Route Handlers for Business Entity Resolution.
"""

import io
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query, Response
from fastapi.responses import JSONResponse
import pandas as pd

from backend.config import TRAIN_DIR, TEST_DIR, DEFAULT_MATCH_THRESHOLD, MODEL_PATH
from backend.preprocessing.normalization import normalize_record
from backend.utils.data_loader import load_table_file, load_and_normalize_dataset
from backend.matching.blocking import get_candidate_pairs
from backend.ml.predict import predict_pair_match, get_ml_model
from backend.matching.clustering import cluster_and_canonicalize_entities
from backend.evaluation.evaluate import evaluate_resolution_pipeline
from backend.api.schemas import (
    HealthResponse, UploadResponse, SourceUploadInfo, MatchRequest,
    PairwiseMatchResult, CanonicalEntityRecord, DashboardStatistics, EvaluationResponse,
    CompareRecordsRequest, ReviewActionRequest
)

router = APIRouter()

# In-memory application state
APP_STATE = {
    "current_records": [],          # List of normalized records
    "current_sources": {},          # Dict of source name -> DataFrame
    "matched_pairs": [],            # List of scored candidate pairs
    "canonical_entities": [],       # List of resolved canonical entities
    "last_threshold": DEFAULT_MATCH_THRESHOLD,
    "dataset_source": "train"       # "train", "test", "uploaded"
}

def run_entity_resolution_pipeline(records: List[Dict[str, Any]], threshold: float = DEFAULT_MATCH_THRESHOLD, use_blocking: bool = True):
    """
    Executes end-to-end entity resolution on given records and updates APP_STATE.
    """
    if not records:
        APP_STATE["matched_pairs"] = []
        APP_STATE["canonical_entities"] = []
        return

    # 1. Candidate pair generation via blocking
    candidate_pairs = get_candidate_pairs(records, use_blocking=use_blocking)
    
    # 2. Pairwise scoring with ML model + explainability
    scored_pairs = []
    for r1, r2 in candidate_pairs:
        res = predict_pair_match(r1, r2, custom_threshold=threshold)
        scored_pairs.append(res)
        
    # Sort pairs by confidence descending
    scored_pairs.sort(key=lambda p: p["confidence_score"], reverse=True)
    
    # 3. Entity clustering and canonical synthesis
    entities = cluster_and_canonicalize_entities(records, scored_pairs)
    
    # 4. Save into state
    APP_STATE["current_records"] = records
    APP_STATE["matched_pairs"] = scored_pairs
    APP_STATE["canonical_entities"] = entities
    APP_STATE["last_threshold"] = threshold

def initialize_default_dataset():
    """Initializes the backend with training dataset on startup."""
    try:
        records, sources = load_and_normalize_dataset(TRAIN_DIR, prefix="train")
        APP_STATE["current_records"] = records
        APP_STATE["current_sources"] = sources
        APP_STATE["dataset_source"] = "train"
        run_entity_resolution_pipeline(records, threshold=DEFAULT_MATCH_THRESHOLD, use_blocking=True)
        print(f"Initialized with {len(records)} records, resolved {len(APP_STATE['canonical_entities'])} entities.")
    except Exception as e:
        print(f"Warning during default initialization: {e}")

# Initial run on import/startup
initialize_default_dataset()

@router.get("/health", response_model=HealthResponse)
def health_check():
    """Returns the system health and ML model status."""
    model = get_ml_model()
    return HealthResponse(
        status="healthy",
        model_loaded=bool(model is not None),
        version="1.0.0"
    )

@router.post("/upload", response_model=UploadResponse)
async def upload_dataset_files(
    source1: Optional[UploadFile] = File(None),
    source2: Optional[UploadFile] = File(None),
    source3: Optional[UploadFile] = File(None)
):
    """
    Uploads up to 3 dataset source files (TSV or CSV), parses and standardizes them.
    """
    files_map = {"Source 1": source1, "Source 2": source2, "Source 3": source3}
    uploaded_summaries = []
    all_normalized = []
    sources_df = {}
    
    files_provided = False
    for default_name, f in files_map.items():
        if f is not None and f.filename:
            files_provided = True
            try:
                content = await f.read()
                if len(content) == 0:
                    raise HTTPException(status_code=400, detail=f"Uploaded file '{f.filename}' is empty.")
                    
                # Parse file buffer
                buffer = io.BytesIO(content)
                df, warnings = load_table_file(buffer, default_source_name=default_name)
                
                # Check minimum required records
                if len(df) == 0:
                    raise HTTPException(status_code=400, detail=f"No data rows found in '{f.filename}'.")
                    
                sources_df[default_name] = df
                sample = df.head(3).to_dict(orient="records")
                
                uploaded_summaries.append(SourceUploadInfo(
                    filename=f.filename,
                    source_name=default_name,
                    record_count=len(df),
                    columns_detected=list(df.columns),
                    sample_records=sample,
                    warnings=warnings
                ))
                
                for _, row in df.iterrows():
                    rec_dict = row.to_dict()
                    rec_dict["source"] = default_name
                    norm_rec = normalize_record(rec_dict)
                    norm_rec["source"] = default_name
                    all_normalized.append(norm_rec)
                    
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Failed to process '{f.filename}': {str(e)}")

    if not files_provided:
        raise HTTPException(status_code=400, detail="Please upload at least one valid TSV/CSV file.")
        
    APP_STATE["current_records"] = all_normalized
    APP_STATE["current_sources"] = sources_df
    APP_STATE["dataset_source"] = "uploaded"
    
    # Run resolution automatically on uploaded data
    run_entity_resolution_pipeline(all_normalized, threshold=DEFAULT_MATCH_THRESHOLD, use_blocking=True)
    
    return UploadResponse(
        status="success",
        message=f"Successfully loaded and resolved {len(all_normalized)} records across {len(uploaded_summaries)} sources.",
        sources_summary=uploaded_summaries,
        total_records=len(all_normalized)
    )

@router.post("/match")
def trigger_matching(req: MatchRequest):
    """
    Triggers or re-runs entity resolution with a custom confidence threshold,
    blocking choice, or dataset selection ('train', 'test', 'uploaded').
    """
    threshold = req.threshold if req.threshold is not None else DEFAULT_MATCH_THRESHOLD
    use_blocking = req.use_blocking if req.use_blocking is not None else True
    
    if req.dataset_type == "train":
        records, sources = load_and_normalize_dataset(TRAIN_DIR, prefix="train")
        APP_STATE["current_records"] = records
        APP_STATE["current_sources"] = sources
        APP_STATE["dataset_source"] = "train"
    elif req.dataset_type == "test":
        records, sources = load_and_normalize_dataset(TEST_DIR, prefix="test")
        APP_STATE["current_records"] = records
        APP_STATE["current_sources"] = sources
        APP_STATE["dataset_source"] = "test"
    else:
        # Use existing records
        records = APP_STATE["current_records"]
        
    if not records:
        raise HTTPException(status_code=400, detail="No records available to match. Please upload data first.")
        
    run_entity_resolution_pipeline(records, threshold=threshold, use_blocking=use_blocking)
    
    return {
        "status": "success",
        "message": f"Entity resolution completed for {len(records)} records.",
        "dataset_source": APP_STATE["dataset_source"],
        "threshold_used": threshold,
        "unique_entities_found": len(APP_STATE["canonical_entities"]),
        "total_candidate_pairs": len(APP_STATE["matched_pairs"]),
        "matched_pairs_count": sum(1 for p in APP_STATE["matched_pairs"] if p.get("is_match"))
    }

@router.get("/entities")
def get_entities(
    search: Optional[str] = Query(None, description="Search canonical name or ID"),
    source: Optional[str] = Query(None, description="Filter by source (e.g. Source1)"),
    has_duplicates: Optional[bool] = Query(None, description="Filter entities with duplicate records"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=200)
):
    """
    Returns list of resolved canonical entities with filtering and pagination.
    """
    entities = APP_STATE.get("canonical_entities", [])
    
    # Filter by search
    if search:
        s_lower = search.strip().lower()
        entities = [
            e for e in entities 
            if s_lower in e["canonical_name"].lower() 
            or s_lower in e["entity_id"].lower()
            or s_lower in e.get("city", "").lower()
            or s_lower in e.get("email", "").lower()
        ]
        
    # Filter by source
    if source:
        src_clean = source.strip().lower()
        entities = [
            e for e in entities 
            if any(src_clean in str(s).lower() for s in e.get("sources", []))
        ]
        
    # Filter by duplicate presence
    if has_duplicates is not None:
        if has_duplicates:
            entities = [e for e in entities if e["duplicate_count"] > 0]
        else:
            entities = [e for e in entities if e["duplicate_count"] == 0]
            
    total = len(entities)
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    paginated = entities[start_idx:end_idx]
    
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": max(1, (total + limit - 1) // limit),
        "entities": paginated
    }

@router.get("/entities/{entity_id}", response_model=CanonicalEntityRecord)
def get_entity_details(entity_id: str):
    """
    Returns detailed information for a single canonical entity, including all matched source records.
    """
    for e in APP_STATE.get("canonical_entities", []):
        if e["entity_id"].lower() == entity_id.lower():
            return e
            
    raise HTTPException(status_code=404, detail=f"Entity '{entity_id}' not found.")

@router.get("/results")
def get_pairwise_results(
    search: Optional[str] = Query(None, description="Search business name or record ID"),
    tier: Optional[str] = Query(None, description="Filter by tier (e.g. 'Very High Confidence')"),
    status: Optional[str] = Query(None, description="Filter by status (e.g. 'Match')"),
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=200)
):
    """
    Returns pairwise match comparisons with explainability scores and pagination.
    """
    pairs = APP_STATE.get("matched_pairs", [])
    
    if search:
        s_lower = search.strip().lower()
        pairs = [
            p for p in pairs
            if s_lower in p["business_name_1"].lower()
            or s_lower in p["business_name_2"].lower()
            or s_lower in p["record_id_1"].lower()
            or s_lower in p["record_id_2"].lower()
        ]
        
    if tier:
        pairs = [p for p in pairs if tier.lower() in p.get("tier", "").lower()]
        
    if status:
        pairs = [p for p in pairs if status.lower() in p.get("status", "").lower()]
        
    total = len(pairs)
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    paginated = pairs[start_idx:end_idx]
    
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": max(1, (total + limit - 1) // limit),
        "results": paginated
    }

@router.get("/statistics", response_model=DashboardStatistics)
def get_statistics():
    """
    Computes and returns aggregate system statistics for the dashboard.
    """
    records = APP_STATE.get("current_records", [])
    entities = APP_STATE.get("canonical_entities", [])
    pairs = APP_STATE.get("matched_pairs", [])
    
    total_records = len(records)
    unique_entities = len(entities)
    
    # Counts per source
    records_per_source = {}
    for r in records:
        src = r.get("source", "Source1")
        records_per_source[src] = records_per_source.get(src, 0) + 1
        
    # High confidence & potential matches
    potential_matches = sum(1 for p in pairs if p.get("status") in ["Match", "Potential Match"])
    high_confidence = sum(1 for p in pairs if p.get("confidence_score", 0) >= 75.0)
    
    # Duplicate records count: sum of extra records beyond 1 in each cluster
    duplicate_records = sum(e.get("duplicate_count", 0) for e in entities)
    
    # Confidence distribution
    confidence_dist = {
        "Very High (90-100%)": sum(1 for p in pairs if p.get("confidence_score", 0) >= 90.0),
        "High (75-89%)": sum(1 for p in pairs if 75.0 <= p.get("confidence_score", 0) < 90.0),
        "Possible (60-74%)": sum(1 for p in pairs if 60.0 <= p.get("confidence_score", 0) < 75.0),
        "Low (40-59%)": sum(1 for p in pairs if 40.0 <= p.get("confidence_score", 0) < 60.0),
        "Unlikely (0-39%)": sum(1 for p in pairs if p.get("confidence_score", 0) < 40.0)
    }
    
    status_breakdown = {
        "Resolved Matches": sum(1 for p in pairs if p.get("status") == "Match"),
        "Potential Matches": sum(1 for p in pairs if p.get("status") == "Potential Match"),
        "Requires Review": sum(1 for p in pairs if p.get("status") == "Review Required"),
        "Non-Matches": sum(1 for p in pairs if p.get("status") == "Non-Match")
    }
    
    return DashboardStatistics(
        total_records=total_records,
        unique_entities=unique_entities,
        potential_matches=potential_matches,
        high_confidence_matches=high_confidence,
        duplicate_records=duplicate_records,
        records_per_source=records_per_source,
        confidence_distribution=confidence_dist,
        match_status_breakdown=status_breakdown
    )

@router.get("/evaluation", response_model=EvaluationResponse)
def get_evaluation_metrics(
    dataset: str = Query("test", description="'test' or 'train'"),
    threshold: float = Query(60.0, ge=0.0, le=100.0)
):
    """
    Evaluates resolution accuracy against the synthetic ground-truth dataset.
    """
    prefix = "test" if dataset.lower() == "test" else "train"
    target_dir = TEST_DIR if prefix == "test" else TRAIN_DIR
    
    results = evaluate_resolution_pipeline(dataset_dir=target_dir, prefix=prefix, threshold=threshold)
    return results

@router.post("/compare")
def compare_arbitrary_records(req: CompareRecordsRequest):
    """
    Real-time sandbox comparator: Compares two user-provided business records on the fly,
    runs full normalization, calculates pairwise similarity metrics, and returns ML match classification with evidence.
    """
    r1_raw = req.record1.model_dump()
    r2_raw = req.record2.model_dump()
    
    norm1 = normalize_record(r1_raw)
    norm2 = normalize_record(r2_raw)
    
    threshold = req.threshold if req.threshold is not None else DEFAULT_MATCH_THRESHOLD
    match_result = predict_pair_match(norm1, norm2, custom_threshold=threshold)
    
    return {
        "status": "success",
        "result": match_result,
        "record1_normalized": norm1,
        "record2_normalized": norm2
    }

@router.get("/export/entities")
def export_canonical_entities(
    format: str = Query("csv", description="'csv' or 'json'"),
    has_duplicates: Optional[bool] = Query(None, description="Filter entities with duplicate records")
):
    """
    Exports the resolved canonical master entities into CSV or JSON format.
    """
    entities = APP_STATE.get("canonical_entities", [])
    if has_duplicates is not None:
        if has_duplicates:
            entities = [e for e in entities if e.get("duplicate_count", 0) > 0]
        else:
            entities = [e for e in entities if e.get("duplicate_count", 0) == 0]

    if format.lower() == "json":
        return JSONResponse(
            content=entities,
            headers={"Content-Disposition": "attachment; filename=canonical_entities.json"}
        )

    # Flatten entities for CSV export
    flat_rows = []
    for e in entities:
        flat_rows.append({
            "entity_id": e.get("entity_id", ""),
            "canonical_name": e.get("canonical_name", ""),
            "address": e.get("address", ""),
            "city": e.get("city", ""),
            "state": e.get("state", ""),
            "country": e.get("country", ""),
            "phone": e.get("phone", ""),
            "email": e.get("email", ""),
            "website": e.get("website", ""),
            "records_count": e.get("records_count", 1),
            "duplicate_count": e.get("duplicate_count", 0),
            "confidence_score": e.get("confidence", 100.0),
            "sources": ", ".join(e.get("sources", []))
        })

    entity_columns = [
        "entity_id", "canonical_name", "address", "city", "state", "country",
        "phone", "email", "website", "records_count", "duplicate_count",
        "confidence_score", "sources"
    ]
    df = pd.DataFrame(flat_rows, columns=entity_columns) if not flat_rows else pd.DataFrame(flat_rows)
    csv_str = df.to_csv(index=False)
    return Response(
        content=csv_str,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=canonical_entities.csv"}
    )

@router.get("/export/results")
def export_pairwise_results(
    format: str = Query("csv", description="'csv' or 'json'"),
    status: Optional[str] = Query(None, description="Filter by status ('Match', 'Potential Match', etc.)")
):
    """
    Exports pairwise match results and explainability scores into CSV or JSON format.
    """
    pairs = APP_STATE.get("matched_pairs", [])
    if status:
        pairs = [p for p in pairs if status.lower() in p.get("status", "").lower()]

    if format.lower() == "json":
        return JSONResponse(
            content=pairs,
            headers={"Content-Disposition": "attachment; filename=matched_pairs.json"}
        )

    # Flatten pairs for CSV
    flat_rows = []
    for p in pairs:
        sim = p.get("similarity_breakdown", {})
        flat_rows.append({
            "record_id_1": p.get("record_id_1", ""),
            "source_1": p.get("source_1", ""),
            "business_name_1": p.get("business_name_1", ""),
            "record_id_2": p.get("record_id_2", ""),
            "source_2": p.get("source_2", ""),
            "business_name_2": p.get("business_name_2", ""),
            "confidence_score": p.get("confidence_score", 0.0),
            "tier": p.get("tier", ""),
            "status": p.get("status", ""),
            "is_match": p.get("is_match", False),
            "name_similarity": sim.get("business_name_similarity", 0.0),
            "address_similarity": sim.get("address_similarity", 0.0),
            "city_similarity": sim.get("city_similarity", 0.0),
            "phone_similarity": sim.get("phone_similarity", 0.0),
            "email_similarity": sim.get("email_similarity", 0.0),
            "website_similarity": sim.get("website_similarity", 0.0),
            "evidence": "; ".join(p.get("evidence_summary", []))
        })

    pair_columns = [
        "record_id_1", "source_1", "business_name_1",
        "record_id_2", "source_2", "business_name_2",
        "confidence_score", "tier", "status", "is_match",
        "name_similarity", "address_similarity", "city_similarity",
        "phone_similarity", "email_similarity", "website_similarity",
        "evidence"
    ]
    df = pd.DataFrame(flat_rows, columns=pair_columns) if not flat_rows else pd.DataFrame(flat_rows)
    csv_str = df.to_csv(index=False)
    return Response(
        content=csv_str,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=matched_pairs.csv"}
    )

@router.post("/review")
def review_pairwise_match(req: ReviewActionRequest):
    """
    Manual override endpoint: Allows human reviewer to manually confirm or reject a candidate pair,
    updating the clustered canonical master entities immediately.
    """
    pairs = APP_STATE.get("matched_pairs", [])
    found = False
    
    r1 = req.record_id_1.strip()
    r2 = req.record_id_2.strip()
    
    for p in pairs:
        if (p["record_id_1"] == r1 and p["record_id_2"] == r2) or (p["record_id_1"] == r2 and p["record_id_2"] == r1):
            found = True
            if req.action == "confirm":
                p["is_match"] = True
                p["status"] = "Match"
                p["tier"] = "Manually Confirmed"
                p["confidence_score"] = max(p.get("confidence_score", 0.0), 99.0)
            elif req.action == "reject":
                p["is_match"] = False
                p["status"] = "Non-Match"
                p["tier"] = "Manually Rejected"
                p["confidence_score"] = min(p.get("confidence_score", 0.0), 10.0)
            break
            
    if not found:
        # If pair wasn't in candidate pairs, we can add it if both records exist in current records
        rec_by_id = {r["source_record_id"]: r for r in APP_STATE.get("current_records", [])}
        if r1 in rec_by_id and r2 in rec_by_id:
            pred = predict_pair_match(rec_by_id[r1], rec_by_id[r2])
            if req.action == "confirm":
                pred["is_match"] = True
                pred["status"] = "Match"
                pred["tier"] = "Manually Confirmed"
                pred["confidence_score"] = 99.0
            else:
                pred["is_match"] = False
                pred["status"] = "Non-Match"
                pred["tier"] = "Manually Rejected"
                pred["confidence_score"] = 10.0
            pairs.append(pred)
        else:
            raise HTTPException(status_code=404, detail=f"Pair ({r1}, {r2}) not found in active records.")
            
    # Re-run clustering with updated pair verdicts
    records = APP_STATE.get("current_records", [])
    entities = cluster_and_canonicalize_entities(records, pairs)
    APP_STATE["canonical_entities"] = entities
    
    return {
        "status": "success",
        "action": req.action,
        "pair": f"{r1} <-> {r2}",
        "unique_entities": len(entities),
        "duplicate_records": sum(e.get("duplicate_count", 0) for e in entities)
    }

