"""
Main document processor for handling different file types and coordinating extraction
"""

import asyncio
import os
import uuid
from typing import Dict, List, Any, Optional
from fastapi import UploadFile
import aiofiles
from datetime import datetime

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.document_processor.pdf_processor import PDFProcessor
from backend.document_processor.image_processor import ImageProcessor
from backend.document_processor.table_extractor import TableExtractor
from backend.document_processor.chart_analyzer import ChartAnalyzer
from backend.document_processor.text_chunker import TextChunker
from backend.config import settings

class DocumentProcessor:
    """
    Main document processor that coordinates the extraction of text, tables, and charts
    from various document formats
    """
    
    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.image_processor = ImageProcessor()
        self.table_extractor = TableExtractor()
        self.chart_analyzer = ChartAnalyzer()
        self.text_chunker = TextChunker()
        
        # Supported file extensions and their processors
        self.processors = {
            '.pdf': self._process_pdf,
            '.png': self._process_image,
            '.jpg': self._process_image,
            '.jpeg': self._process_image,
            '.tiff': self._process_image,
            '.bmp': self._process_image
        }
    
    async def process_document(self, file: UploadFile) -> Dict[str, Any]:
        """
        Process an uploaded document and extract all relevant information
        
        Args:
            file: Uploaded file from FastAPI
            
        Returns:
            Dictionary containing extracted content and metadata
        """
        try:
            # Generate unique document ID
            document_id = str(uuid.uuid4())
            
            # Save file temporarily
            temp_path = await self._save_temp_file(file, document_id)
            
            # Get file extension
            file_extension = os.path.splitext(file.filename)[1].lower()
            
            # Validate file type
            if file_extension not in self.processors:
                raise ValueError(f"Unsupported file type: {file_extension}")
            
            # Process the document based on its type
            processor_func = self.processors[file_extension]
            extracted_content = await processor_func(temp_path, document_id)
            
            # Add metadata
            extracted_content.update({
                "document_id": document_id,
                "filename": file.filename,
                "file_size": file.size,
                "file_type": file_extension,
                "uploaded_at": datetime.utcnow().isoformat(),
                "processing_status": "completed"
            })
            
            # Clean up temporary file
            await self._cleanup_temp_file(temp_path)
            
            return extracted_content
            
        except Exception as e:
            # Clean up on error
            if 'temp_path' in locals():
                await self._cleanup_temp_file(temp_path)
            raise e
    
    async def _process_pdf(self, file_path: str, document_id: str) -> Dict[str, Any]:
        """Process PDF documents"""
        try:
            # Extract text, tables, and charts from PDF
            pdf_content = await self.pdf_processor.process(file_path)
            
            # Extract tables
            tables = await self.table_extractor.extract_from_pdf(file_path)
            
            # Detect and analyze charts
            charts = await self.chart_analyzer.detect_charts(file_path)
            
            # Chunk text for vector storage
            text_chunks = await self.text_chunker.chunk_text(
                pdf_content["text"], 
                document_id
            )
            
            return {
                "text_chunks": text_chunks,
                "tables": tables,
                "charts": charts,
                "images": pdf_content.get("images", []),
                "metadata": pdf_content.get("metadata", {}),
                "total_pages": pdf_content.get("total_pages", 0)
            }
            
        except Exception as e:
            raise Exception(f"Error processing PDF: {str(e)}")
    
    async def _process_image(self, file_path: str, document_id: str) -> Dict[str, Any]:
        """Process image documents"""
        try:
            # Extract text using OCR
            ocr_content = await self.image_processor.process(file_path)
            
            # Detect tables in image
            tables = await self.table_extractor.extract_from_image(file_path)
            
            # Detect charts in image
            charts = await self.chart_analyzer.detect_charts(file_path)
            
            # Chunk OCR text for vector storage
            text_chunks = await self.text_chunker.chunk_text(
                ocr_content["text"], 
                document_id
            )
            
            return {
                "text_chunks": text_chunks,
                "tables": tables,
                "charts": charts,
                "images": [{"path": file_path, "type": "source_image"}],
                "ocr_confidence": ocr_content.get("confidence", 0.0),
                "metadata": {
                    "image_dimensions": ocr_content.get("dimensions"),
                    "ocr_engine": settings.ocr_engine
                }
            }
            
        except Exception as e:
            raise Exception(f"Error processing image: {str(e)}")
    
    async def _save_temp_file(self, file: UploadFile, document_id: str) -> str:
        """Save uploaded file to temporary location"""
        try:
            # Create temp directory if it doesn't exist
            os.makedirs(settings.temp_directory, exist_ok=True)
            
            # Generate temp file path
            file_extension = os.path.splitext(file.filename)[1]
            temp_filename = f"{document_id}{file_extension}"
            temp_path = os.path.join(settings.temp_directory, temp_filename)
            
            # Save file
            async with aiofiles.open(temp_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            return temp_path
            
        except Exception as e:
            raise Exception(f"Error saving temporary file: {str(e)}")
    
    async def _cleanup_temp_file(self, temp_path: str):
        """Clean up temporary file"""
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except Exception as e:
            print(f"Warning: Could not clean up temp file {temp_path}: {e}")
    
    async def get_processing_status(self, document_id: str) -> Dict[str, Any]:
        """Get the processing status of a document"""
        # This could be implemented with a database to track processing status
        return {
            "document_id": document_id,
            "status": "completed",  # For now, assume completed
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def reprocess_document(self, document_id: str) -> Dict[str, Any]:
        """Reprocess a document (useful for failed extractions)"""
        # This would require storing the original file and reprocessing
        # For now, return an error
        raise NotImplementedError("Document reprocessing not yet implemented") 