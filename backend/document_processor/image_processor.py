"""
Image processor for OCR and image analysis
"""

import asyncio
import os
from typing import Dict, List, Any, Optional, Tuple
from PIL import Image
import cv2
import numpy as np
import io
import base64

try:
    from paddleocr import PaddleOCR
    PADDLEOCR_AVAILABLE = True
except ImportError:
    PADDLEOCR_AVAILABLE = False
    print("Warning: PaddleOCR not available. Install with: pip install paddlepaddle paddleocr")

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    print("Warning: EasyOCR not available. Install with: pip install easyocr")

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    print("Warning: Tesseract not available. Install with: pip install pytesseract")

from backend.config import settings

class ImageProcessor:
    """
    Processes images for OCR and image analysis
    """
    
    def __init__(self):
        self.ocr_engine = settings.ocr_engine
        self.language = settings.ocr_language
        
        # Initialize OCR engines
        self._initialize_ocr_engines()
    
    def _initialize_ocr_engines(self):
        """Initialize available OCR engines"""
        self.ocr_engines = {}
        
        # Initialize PaddleOCR
        if PADDLEOCR_AVAILABLE:
            try:
                # Some PaddleOCR versions do not support 'show_log'. Omit it for compatibility.
                self.ocr_engines['paddleocr'] = PaddleOCR(
                    use_angle_cls=True,
                    lang=self.language
                )
                print("✅ PaddleOCR initialized successfully")
            except Exception as e:
                print(f"❌ Error initializing PaddleOCR: {e}")
        
        # Initialize EasyOCR
        if EASYOCR_AVAILABLE:
            try:
                self.ocr_engines['easyocr'] = easyocr.Reader([self.language])
                print("✅ EasyOCR initialized successfully")
            except Exception as e:
                print(f"❌ Error initializing EasyOCR: {e}")
        
        # Tesseract doesn't need initialization
        if TESSERACT_AVAILABLE:
            self.ocr_engines['tesseract'] = 'available'
            print("✅ Tesseract available")
        
        if not self.ocr_engines:
            raise RuntimeError("No OCR engines available. Please install at least one OCR library.")
    
    async def process(self, file_path: str) -> Dict[str, Any]:
        """
        Process an image file and extract text using OCR
        
        Args:
            file_path: Path to the image file
            
        Returns:
            Dictionary containing extracted text and metadata
        """
        try:
            # Load and preprocess image
            image = await self._load_image(file_path)
            preprocessed_image = await self._preprocess_image(image)
            
            # Extract text using OCR
            ocr_result = await self._extract_text(preprocessed_image)
            
            # Get image dimensions
            dimensions = image.size
            
            return {
                "text": ocr_result["text"],
                "confidence": ocr_result["confidence"],
                "dimensions": dimensions,
                "ocr_engine": self.ocr_engine,
                "processing_method": "OCR + Image Preprocessing"
            }
            
        except Exception as e:
            raise Exception(f"Error processing image {file_path}: {str(e)}")
    
    async def _load_image(self, file_path: str) -> Image.Image:
        """Load image from file path"""
        try:
            image = Image.open(file_path)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            return image
            
        except Exception as e:
            raise Exception(f"Error loading image: {str(e)}")
    
    async def _preprocess_image(self, image: Image.Image) -> np.ndarray:
        """Preprocess image for better OCR results"""
        try:
            # Convert PIL image to OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Convert to grayscale
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Apply noise reduction
            denoised = cv2.fastNlMeansDenoising(gray)
            
            # Apply adaptive thresholding for better text extraction
            thresh = cv2.adaptiveThreshold(
                denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            # Apply morphological operations to clean up the image
            kernel = np.ones((1, 1), np.uint8)
            cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
            return cleaned
            
        except Exception as e:
            raise Exception(f"Error preprocessing image: {str(e)}")
    
    async def _extract_text(self, image: np.ndarray) -> Dict[str, Any]:
        """Extract text using the specified OCR engine"""
        try:
            if self.ocr_engine == 'paddleocr' and 'paddleocr' in self.ocr_engines:
                return await self._extract_text_paddleocr(image)
            elif self.ocr_engine == 'easyocr' and 'easyocr' in self.ocr_engines:
                return await self._extract_text_easyocr(image)
            elif self.ocr_engine == 'tesseract' and 'tesseract' in self.ocr_engines:
                return await self._extract_text_tesseract(image)
            else:
                # Fallback to available engine
                for engine_name in self.ocr_engines:
                    if engine_name == 'paddleocr':
                        return await self._extract_text_paddleocr(image)
                    elif engine_name == 'easyocr':
                        return await self._extract_text_easyocr(image)
                    elif engine_name == 'tesseract':
                        return await self._extract_text_tesseract(image)
                
                raise RuntimeError("No OCR engines available")
                
        except Exception as e:
            raise Exception(f"Error extracting text: {str(e)}")
    
    async def _extract_text_paddleocr(self, image: np.ndarray) -> Dict[str, Any]:
        """Extract text using PaddleOCR"""
        try:
            # Convert numpy array back to PIL Image for PaddleOCR
            pil_image = Image.fromarray(image)
            
            # Run OCR
            result = self.ocr_engines['paddleocr'].ocr(np.array(pil_image), cls=True)
            
            # Extract text and confidence scores
            text_parts = []
            confidences = []
            
            if result and result[0]:
                for line in result[0]:
                    if line and len(line) >= 2:
                        text = line[1][0]  # Extract text
                        confidence = line[1][1]  # Extract confidence
                        
                        if text.strip():
                            text_parts.append(text.strip())
                            confidences.append(confidence)
            
            # Combine all text
            full_text = '\n'.join(text_parts)
            avg_confidence = np.mean(confidences) if confidences else 0.0
            
            return {
                "text": full_text,
                "confidence": float(avg_confidence),
                "text_parts": text_parts,
                "confidences": confidences
            }
            
        except Exception as e:
            raise Exception(f"Error with PaddleOCR: {str(e)}")
    
    async def _extract_text_easyocr(self, image: np.ndarray) -> Dict[str, Any]:
        """Extract text using EasyOCR"""
        try:
            # Run OCR
            result = self.ocr_engines['easyocr'].readtext(image)
            
            # Extract text and confidence scores
            text_parts = []
            confidences = []
            
            for detection in result:
                text = detection[1]
                confidence = detection[2]
                
                if text.strip():
                    text_parts.append(text.strip())
                    confidences.append(confidence)
            
            # Combine all text
            full_text = '\n'.join(text_parts)
            avg_confidence = np.mean(confidences) if confidences else 0.0
            
            return {
                "text": full_text,
                "confidence": float(avg_confidence),
                "text_parts": text_parts,
                "confidences": confidences
            }
            
        except Exception as e:
            raise Exception(f"Error with EasyOCR: {str(e)}")
    
    async def _extract_text_tesseract(self, image: np.ndarray) -> Dict[str, Any]:
        """Extract text using Tesseract"""
        try:
            # Run OCR
            text = pytesseract.image_to_string(image, lang=self.language)
            
            # Get confidence scores (if available)
            try:
                data = pytesseract.image_to_data(image, lang=self.language, output_type=pytesseract.Output.DICT)
                confidences = [float(conf) for conf in data['conf'] if float(conf) > 0]
                avg_confidence = np.mean(confidences) if confidences else 0.0
            except:
                avg_confidence = 0.0
            
            return {
                "text": text.strip(),
                "confidence": float(avg_confidence),
                "text_parts": [text.strip()],
                "confidences": [avg_confidence]
            }
            
        except Exception as e:
            raise Exception(f"Error with Tesseract: {str(e)}")
    
    async def detect_text_regions(self, image_path: str) -> List[Dict[str, Any]]:
        """Detect regions containing text in an image"""
        try:
            # Load image
            image = await self._load_image(image_path)
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Convert to grayscale
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Apply MSER (Maximally Stable Extremal Regions) for text detection
            mser = cv2.MSER_create()
            regions, _ = mser.detectRegions(gray)
            
            # Filter regions by size and aspect ratio
            text_regions = []
            for region in regions:
                # Get bounding box
                x, y, w, h = cv2.boundingRect(region)
                
                # Filter by size and aspect ratio
                if w > 20 and h > 10 and w < image.width * 0.8 and h < image.height * 0.8:
                    aspect_ratio = w / h
                    if 0.1 < aspect_ratio < 10:  # Reasonable text aspect ratio
                        text_regions.append({
                            "x": x,
                            "y": y,
                            "width": w,
                            "height": h,
                            "area": w * h
                        })
            
            return text_regions
            
        except Exception as e:
            raise Exception(f"Error detecting text regions: {str(e)}")
    
    async def enhance_image_for_ocr(self, image_path: str) -> str:
        """Enhance image for better OCR results and return as base64"""
        try:
            # Load image
            image = await self._load_image(image_path)
            
            # Apply various enhancement techniques
            enhanced = await self._apply_enhancements(image)
            
            # Convert to base64
            img_buffer = io.BytesIO()
            enhanced.save(img_buffer, format='PNG')
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
            
            return img_base64
            
        except Exception as e:
            raise Exception(f"Error enhancing image: {str(e)}")
    
    async def _apply_enhancements(self, image: Image.Image) -> Image.Image:
        """Apply various image enhancement techniques"""
        try:
            # Convert to numpy array
            img_array = np.array(image)
            
            # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
            lab = cv2.cvtColor(img_array, cv2.COLOR_RGB2LAB)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            lab[:, :, 0] = clahe.apply(lab[:, :, 0])
            enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
            
            # Convert back to PIL Image
            return Image.fromarray(enhanced)
            
        except Exception as e:
            raise Exception(f"Error applying enhancements: {str(e)}")
    
    async def get_image_info(self, image_path: str) -> Dict[str, Any]:
        """Get comprehensive information about an image"""
        try:
            image = await self._load_image(image_path)
            
            # Get basic information
            info = {
                "format": image.format,
                "mode": image.mode,
                "size": image.size,
                "width": image.width,
                "height": image.height,
                "file_size": os.path.getsize(image_path)
            }
            
            # Get histogram information
            if image.mode == 'RGB':
                r, g, b = image.split()
                info["histogram"] = {
                    "red": r.histogram(),
                    "green": g.histogram(),
                    "blue": b.histogram()
                }
            
            return info
            
        except Exception as e:
            raise Exception(f"Error getting image info: {str(e)}") 