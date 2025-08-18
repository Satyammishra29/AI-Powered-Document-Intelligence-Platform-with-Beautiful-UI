"""
Configuration settings for the Visual Document Analysis RAG System Backend
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application settings loaded from environment variables"""
    
    # Application Configuration
    app_name: str = "Document Analysis RAG Backend"
    version: str = "1.0.0"
    
    # OpenAI Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4")
    openai_temperature: float = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    openai_max_tokens: int = int(os.getenv("OPENAI_MAX_TOKENS", "1000"))
    
    # Vector Database Configuration
    vector_db_type: str = os.getenv("VECTOR_DB_TYPE", "chroma")
    chroma_persist_directory: str = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")
    
    # Pinecone Configuration
    pinecone_api_key: Optional[str] = os.getenv("PINECONE_API_KEY")
    pinecone_environment: Optional[str] = os.getenv("PINECONE_ENVIRONMENT")
    pinecone_index_name: str = os.getenv("PINECONE_INDEX_NAME", "visual-doc-rag")
    
    # Embedding Configuration
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "1000"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    
    # OCR Configuration
    ocr_engine: str = os.getenv("OCR_ENGINE", "paddleocr")
    ocr_language: str = os.getenv("OCR_LANGUAGE", "en")
    
    # Document Processing Configuration
    max_file_size: int = int(os.getenv("MAX_FILE_SIZE", "52428800"))
    temp_directory: str = os.getenv("TEMP_DIRECTORY", "./temp")
    
    # Table Extraction Configuration
    table_extraction_method: str = os.getenv("TABLE_EXTRACTION_METHOD", "pdfplumber")
    min_table_confidence: float = float(os.getenv("MIN_TABLE_CONFIDENCE", "0.8"))
    
    # Chart Analysis Configuration
    chart_detection_enabled: bool = os.getenv("CHART_DETECTION_ENABLED", "true").lower() == "true"
    chart_analysis_method: str = os.getenv("CHART_ANALYSIS_METHOD", "opencv")
    
    # RAG Configuration
    retrieval_top_k: int = int(os.getenv("RETRIEVAL_TOP_K", "5"))
    similarity_threshold: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.7"))
    max_context_length: int = int(os.getenv("MAX_CONTEXT_LENGTH", "4000"))
    
    # Server Configuration
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Logging Configuration
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: Optional[str] = os.getenv("LOG_FILE")
    
    # Security Configuration
    cors_origins: list = os.getenv("CORS_ORIGINS", "['*']")
    api_key_header: str = os.getenv("API_KEY_HEADER", "X-API-Key")

# Create global settings instance
settings = Settings()
