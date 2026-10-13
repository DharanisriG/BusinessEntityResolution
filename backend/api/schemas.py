"""
Pydantic Schemas for Business Entity Resolution API.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class HealthResponse(BaseModel):
    status: str = "healthy"
    model_loaded: bool
    version: str = "1.0.0"

class SourceUploadInfo(BaseModel):
    filename: str
    source_name: str
    record_count: int
    columns_detected: List[str]
    sample_records: List[Dict[str, Any]]
    warnings: List[str] = []

class UploadResponse(BaseModel):
    status: str
    message: str
    sources_summary: List[SourceUploadInfo]
    total_records: int

class MatchRequest(BaseModel):
    threshold: Optional[float] = Field(default=60.0, ge=0.0, le=100.0)
    use_blocking: Optional[bool] = True
    dataset_type: Optional[str] = "train" # "train", "test", or "uploaded"

class SimilarityBreakdown(BaseModel):
    business_name_similarity: float
    address_similarity: float
    city_similarity: float
    phone_similarity: float
    email_similarity: float
    website_similarity: float
    country_match: bool
    exact_phone_match: bool
    exact_email_match: bool
    exact_website_match: bool

class PairwiseMatchResult(BaseModel):
    record_id_1: str
    record_id_2: str
    source_1: str
    source_2: str
    business_name_1: str
    business_name_2: str
    confidence_score: float
    tier: str
    status: str
    is_match: bool
    similarity_breakdown: SimilarityBreakdown
    evidence_summary: List[str]

class CanonicalEntityRecord(BaseModel):
    entity_id: str
    canonical_name: str
    address: str
    city: str
    state: str
    country: str
    phone: str
    email: str
    website: str
    records_count: int
    duplicate_count: int
    sources: List[str]
    confidence: float
    records: List[Dict[str, Any]]

class DashboardStatistics(BaseModel):
    total_records: int
    unique_entities: int
    potential_matches: int
    high_confidence_matches: int
    duplicate_records: int
    records_per_source: Dict[str, int]
    confidence_distribution: Dict[str, int]
    match_status_breakdown: Dict[str, int]

class EvaluationMetrics(BaseModel):
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    true_positives: int
    true_negatives: int
    false_positives: int
    false_negatives: int
    total_pairs: int

class ConfusionMatrixData(BaseModel):
    matrix: List[List[int]]
    labels: List[str]

class EvaluationResponse(BaseModel):
    dataset_evaluated: str
    threshold_used: float
    metrics: EvaluationMetrics
    confusion_matrix: ConfusionMatrixData
    threshold_analysis: List[Dict[str, Any]]
    tradeoff_explanation: str

class BusinessRecordInput(BaseModel):
    source_record_id: Optional[str] = "REC_01"
    business_name: str
    address: Optional[str] = ""
    city: Optional[str] = ""
    state: Optional[str] = ""
    country: Optional[str] = ""
    phone: Optional[str] = ""
    email: Optional[str] = ""
    website: Optional[str] = ""
    source: Optional[str] = "Manual Input"

class CompareRecordsRequest(BaseModel):
    record1: BusinessRecordInput
    record2: BusinessRecordInput
    threshold: Optional[float] = 60.0

class ReviewActionRequest(BaseModel):
    record_id_1: str
    record_id_2: str
    action: str # "confirm" or "reject"

