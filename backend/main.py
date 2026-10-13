"""
FastAPI Main Application for Business Entity Resolution.
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from backend.api.routes import router as api_router

app = FastAPI(
    title="Business Entity Resolution API",
    description="Enterprise-grade Business Entity Resolution & Record Linkage System",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static directory
STATIC_DIR = PROJECT_ROOT / "backend" / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Include API routes under prefix /api and directly
app.include_router(api_router, prefix="/api")
app.include_router(api_router)

@app.get("/", response_class=FileResponse)
def serve_ui():
    """Serves the interactive Business Entity Resolution Web UI."""
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {
        "system": "Business Entity Resolution API",
        "status": "online",
        "docs_url": "/docs"
    }

@app.get("/app", response_class=FileResponse)
def serve_app():
    """Direct route to Web UI."""
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"status": "online"}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal Server Error: {str(exc)}"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)

