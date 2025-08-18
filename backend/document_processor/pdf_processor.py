"""
PDF processor for extracting text, images, and metadata from PDF documents
"""

import asyncio
import os
from typing import Dict, List, Any, Optional
import fitz  # PyMuPDF
import pdfplumber
from PIL import Image
import io
import base64

class PDFProcessor:
    """
    Processes PDF documents to extract text, images, and metadata
    """
    
    def __init__(self):
        self.supported_formats = ['.pdf']
    
    async def process(self, file_path: str) -> Dict[str, Any]:
        """
        Process a PDF file and extract all relevant information
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dictionary containing extracted text, images, and metadata
        """
        try:
            # Extract text using PyMuPDF (faster for large PDFs)
            text_content = await self._extract_text_fitz(file_path)
            
            # Extract images
            images = await self._extract_images(file_path)
            
            # Get metadata
            metadata = await self._extract_metadata(file_path)
            
            # Get page count
            total_pages = await self._get_page_count(file_path)
            
            return {
                "text": text_content,
                "images": images,
                "metadata": metadata,
                "total_pages": total_pages,
                "processing_method": "PyMuPDF + pdfplumber"
            }
            
        except Exception as e:
            raise Exception(f"Error processing PDF {file_path}: {str(e)}")
    
    async def _extract_text_fitz(self, file_path: str) -> str:
        """Extract text using PyMuPDF (faster)"""
        try:
            text_content = ""
            
            # Open PDF with PyMuPDF
            with fitz.open(file_path) as doc:
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    
                    # Extract text from page
                    page_text = page.get_text()
                    
                    # Add page separator
                    if page_text.strip():
                        text_content += f"\n--- Page {page_num + 1} ---\n"
                        text_content += page_text.strip()
                        text_content += "\n"
            
            return text_content.strip()
            
        except Exception as e:
            raise Exception(f"Error extracting text with PyMuPDF: {str(e)}")
    
    async def _extract_text_pdfplumber(self, file_path: str) -> str:
        """Extract text using pdfplumber (better for complex layouts)"""
        try:
            text_content = ""
            
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    # Extract text from page
                    page_text = page.extract_text()
                    
                    if page_text and page_text.strip():
                        text_content += f"\n--- Page {page_num + 1} ---\n"
                        text_content += page_text.strip()
                        text_content += "\n"
            
            return text_content.strip()
            
        except Exception as e:
            raise Exception(f"Error extracting text with pdfplumber: {str(e)}")
    
    async def _extract_images(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract images from PDF pages"""
        try:
            images = []
            
            with fitz.open(file_path) as doc:
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    
                    # Get image list for this page
                    image_list = page.get_images()
                    
                    for img_index, img in enumerate(image_list):
                        try:
                            # Get image data
                            xref = img[0]
                            pix = fitz.Pixmap(doc, xref)
                            
                            if pix.n - pix.alpha < 4:  # GRAY or RGB
                                # Convert to PIL Image
                                img_data = pix.tobytes("png")
                                pil_image = Image.open(io.BytesIO(img_data))
                                
                                # Convert to base64 for storage
                                img_buffer = io.BytesIO()
                                pil_image.save(img_buffer, format='PNG')
                                img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
                                
                                images.append({
                                    "page": page_num + 1,
                                    "index": img_index,
                                    "width": pil_image.width,
                                    "height": pil_image.height,
                                    "format": "PNG",
                                    "data": img_base64,
                                    "size_bytes": len(img_data)
                                })
                            
                            pix = None  # Free memory
                            
                        except Exception as e:
                            print(f"Warning: Could not extract image {img_index} from page {page_num + 1}: {e}")
                            continue
            
            return images
            
        except Exception as e:
            raise Exception(f"Error extracting images: {str(e)}")
    
    async def _extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract PDF metadata"""
        try:
            metadata = {}
            
            with fitz.open(file_path) as doc:
                # Get basic metadata
                metadata.update(doc.metadata)
                
                # Get additional information
                metadata["page_count"] = len(doc)
                metadata["file_size"] = os.path.getsize(file_path)
                
                # Get first page dimensions
                if len(doc) > 0:
                    first_page = doc.load_page(0)
                    rect = first_page.rect
                    metadata["page_dimensions"] = {
                        "width": rect.width,
                        "height": rect.height
                    }
            
            return metadata
            
        except Exception as e:
            raise Exception(f"Error extracting metadata: {str(e)}")
    
    async def _get_page_count(self, file_path: str) -> int:
        """Get the total number of pages in the PDF"""
        try:
            with fitz.open(file_path) as doc:
                return len(doc)
        except Exception as e:
            raise Exception(f"Error getting page count: {str(e)}")
    
    async def extract_text_from_page(self, file_path: str, page_num: int) -> str:
        """Extract text from a specific page"""
        try:
            with fitz.open(file_path) as doc:
                if page_num >= len(doc):
                    raise ValueError(f"Page {page_num} does not exist. PDF has {len(doc)} pages.")
                
                page = doc.load_page(page_num)
                return page.get_text().strip()
                
        except Exception as e:
            raise Exception(f"Error extracting text from page {page_num}: {str(e)}")
    
    async def extract_images_from_page(self, file_path: str, page_num: int) -> List[Dict[str, Any]]:
        """Extract images from a specific page"""
        try:
            images = []
            
            with fitz.open(file_path) as doc:
                if page_num >= len(doc):
                    raise ValueError(f"Page {page_num} does not exist. PDF has {len(doc)} pages.")
                
                page = doc.load_page(page_num)
                image_list = page.get_images()
                
                for img_index, img in enumerate(image_list):
                    try:
                        xref = img[0]
                        pix = fitz.Pixmap(doc, xref)
                        
                        if pix.n - pix.alpha < 4:
                            img_data = pix.tobytes("png")
                            pil_image = Image.open(io.BytesIO(img_data))
                            
                            img_buffer = io.BytesIO()
                            pil_image.save(img_buffer, format='PNG')
                            img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
                            
                            images.append({
                                "page": page_num + 1,
                                "index": img_index,
                                "width": pil_image.width,
                                "height": pil_image.height,
                                "format": "PNG",
                                "data": img_base64,
                                "size_bytes": len(img_data)
                            })
                        
                        pix = None
                        
                    except Exception as e:
                        print(f"Warning: Could not extract image {img_index} from page {page_num + 1}: {e}")
                        continue
            
            return images
            
        except Exception as e:
            raise Exception(f"Error extracting images from page {page_num}: {str(e)}")
    
    async def get_page_preview(self, file_path: str, page_num: int, scale: float = 1.0) -> str:
        """Get a preview image of a specific page as base64"""
        try:
            with fitz.open(file_path) as doc:
                if page_num >= len(doc):
                    raise ValueError(f"Page {page_num} does not exist. PDF has {len(doc)} pages.")
                
                page = doc.load_page(page_num)
                
                # Create transformation matrix for scaling
                mat = fitz.Matrix(scale, scale)
                
                # Render page to pixmap
                pix = page.get_pixmap(matrix=mat)
                
                # Convert to PIL Image
                img_data = pix.tobytes("png")
                pil_image = Image.open(io.BytesIO(img_data))
                
                # Convert to base64
                img_buffer = io.BytesIO()
                pil_image.save(img_buffer, format='PNG')
                img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
                
                return img_base64
                
        except Exception as e:
            raise Exception(f"Error generating page preview: {str(e)}") 