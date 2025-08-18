"""
Simplified Backend Server for Document Analysis RAG
"""

import os
import sys
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from typing import List, Dict, Any
import json
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to import config, fallback to defaults if not available
try:
    from backend.config import settings
except ImportError:
    # Fallback configuration
    class Settings:
        app_name = "Document Analysis RAG Backend"
        version = "1.0.0"
        debug = True
        host = "0.0.0.0"
        port = 8000
        openai_api_key = None
        embedding_model = "all-MiniLM-L6-v2"
        vector_db_type = "chroma"
        chroma_persist_directory = "./chroma_db"
    
    settings = Settings()

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    debug=settings.debug
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Document Analysis RAG Backend",
        "version": settings.version,
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "backend": "running",
            "database": "available"
        }
    }

@app.get("/api/status")
async def api_status():
    """API status endpoint"""
    return {
        "status": "operational",
        "version": settings.version,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    """Simple document upload endpoint"""
    try:
        # Basic file validation
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Return success response
        return {
            "message": "Document uploaded successfully",
            "filename": file.filename,
            "size": file.size,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/documents")
async def list_documents():
    """List uploaded documents"""
    return {
        "documents": [],
        "total": 0,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/query")
async def query_documents(query: Dict[str, str]):
    """Simple query endpoint"""
    try:
        user_query = query.get("query", "")
        if not user_query:
            raise HTTPException(status_code=400, detail="No query provided")
        
        # Return a simple response
        return {
            "query": user_query,
            "response": "This is a simplified backend. AI features are not available in this version.",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print(f"Starting {settings.app_name} v{settings.version}")
    print(f"Server will run on http://{settings.host}:{settings.port}")
    print("Note: This is a simplified backend without AI/ML features")
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    ) 