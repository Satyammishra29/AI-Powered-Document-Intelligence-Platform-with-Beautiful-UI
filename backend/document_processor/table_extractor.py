"""
Table extractor for detecting and extracting tables from documents and images
"""

import asyncio
import os
from typing import Dict, List, Any, Optional, Tuple
import cv2
import numpy as np
from PIL import Image
import pandas as pd
import json

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    print("Warning: pdfplumber not available. Install with: pip install pdfplumber")

try:
    import camelot
    CAMELOT_AVAILABLE = True
except ImportError:
    CAMELOT_AVAILABLE = False
    print("Warning: camelot not available. Install with: pip install camelot-py")

from backend.config import settings

class TableExtractor:
    """
    Detects and extracts tables from PDFs and images
    """
    
    def __init__(self):
        self.extraction_method = settings.table_extraction_method
        self.min_confidence = settings.min_table_confidence
        
        # Initialize extraction methods
        self._initialize_extractors()
    
    def _initialize_extractors(self):
        """Initialize available table extraction methods"""
        self.extractors = {}
        
        if PDFPLUMBER_AVAILABLE:
            self.extractors['pdfplumber'] = 'available'
            print("✅ pdfplumber available for table extraction")
        
        if CAMELOT_AVAILABLE:
            self.extractors['camelot'] = 'available'
            print("✅ camelot available for table extraction")
        
        # OpenCV-based extraction is always available
        self.extractors['opencv'] = 'available'
        print("✅ OpenCV available for table extraction")
        
        if not self.extractors:
            raise RuntimeError("No table extraction methods available")
    
    async def extract_from_pdf(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Extract tables from PDF document
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            List of extracted tables with metadata
        """
        try:
            tables = []
            
            # Try different extraction methods
            if 'pdfplumber' in self.extractors:
                pdfplumber_tables = await self._extract_with_pdfplumber(file_path)
                tables.extend(pdfplumber_tables)
            
            if 'camelot' in self.extractors:
                camelot_tables = await self._extract_with_camelot(file_path)
                tables.extend(camelot_tables)
            
            # Remove duplicates and sort by confidence
            unique_tables = await self._deduplicate_tables(tables)
            unique_tables.sort(key=lambda x: x.get('confidence', 0), reverse=True)
            
            return unique_tables
            
        except Exception as e:
            raise Exception(f"Error extracting tables from PDF: {str(e)}")
    
    async def extract_from_image(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Extract tables from image using computer vision
        
        Args:
            file_path: Path to the image file
            
        Returns:
            List of extracted tables with metadata
        """
        try:
            # Load image
            image = cv2.imread(file_path)
            if image is None:
                raise ValueError(f"Could not load image: {file_path}")
            
            # Detect table regions
            table_regions = await self._detect_table_regions(image)
            
            # Extract tables from detected regions
            tables = []
            for region in table_regions:
                table_data = await self._extract_table_from_region(image, region)
                if table_data:
                    tables.append(table_data)
            
            return tables
            
        except Exception as e:
            raise Exception(f"Error extracting tables from image: {str(e)}")
    
    async def _extract_with_pdfplumber(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract tables using pdfplumber"""
        try:
            tables = []
            
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    # Extract tables from page
                    page_tables = page.extract_tables()
                    
                    for table_idx, table_data in enumerate(page_tables):
                        if table_data and len(table_data) > 1:  # At least 2 rows
                            # Convert to pandas DataFrame for easier manipulation
                            df = pd.DataFrame(table_data[1:], columns=table_data[0])
                            
                            # Calculate confidence based on table structure
                            confidence = self._calculate_table_confidence(table_data)
                            
                            if confidence >= self.min_confidence:
                                tables.append({
                                    "page": page_num + 1,
                                    "table_index": table_idx,
                                    "data": table_data,
                                    "dataframe": df.to_dict('records'),
                                    "columns": df.columns.tolist(),
                                    "rows": len(df),
                                    "confidence": confidence,
                                    "extraction_method": "pdfplumber",
                                    "bbox": page.find_tables()[table_idx].bbox if page.find_tables() else None
                                })
            
            return tables
            
        except Exception as e:
            print(f"Warning: Error with pdfplumber extraction: {e}")
            return []
    
    async def _extract_with_camelot(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract tables using camelot"""
        try:
            tables = []
            
            # Extract tables from all pages
            table_list = camelot.read_pdf(file_path, pages='all')
            
            for table_idx, table in enumerate(table_list):
                if table.parsing_report['accuracy'] >= self.min_confidence * 100:
                    # Get table data
                    table_data = table.df.values.tolist()
                    
                    if table_data and len(table_data) > 1:
                        # Convert to pandas DataFrame
                        df = pd.DataFrame(table_data[1:], columns=table_data[0])
                        
                        tables.append({
                            "page": table.parsing_report.get('page', 1),
                            "table_index": table_idx,
                            "data": table_data,
                            "dataframe": df.to_dict('records'),
                            "columns": df.columns.tolist(),
                            "rows": len(df),
                            "confidence": table.parsing_report['accuracy'] / 100,
                            "extraction_method": "camelot",
                            "bbox": table._bbox if hasattr(table, '_bbox') else None,
                            "whitespace": table.parsing_report.get('whitespace', 0)
                        })
            
            return tables
            
        except Exception as e:
            print(f"Warning: Error with camelot extraction: {e}")
            return []
    
    async def _detect_table_regions(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detect potential table regions in an image"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply edge detection
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter contours that could be tables
            table_regions = []
            for contour in contours:
                # Approximate contour to polygon
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                # Check if it's a rectangle (4 corners)
                if len(approx) == 4:
                    # Get bounding rectangle
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Filter by size and aspect ratio
                    if w > 100 and h > 50:  # Minimum size
                        aspect_ratio = w / h
                        if 0.5 < aspect_ratio < 3:  # Reasonable table aspect ratio
                            # Check if region contains text-like patterns
                            roi = gray[y:y+h, x:x+w]
                            if self._has_table_structure(roi):
                                table_regions.append({
                                    "x": x,
                                    "y": y,
                                    "width": w,
                                    "height": h,
                                    "contour": contour,
                                    "confidence": self._calculate_region_confidence(roi)
                                })
            
            return table_regions
            
        except Exception as e:
            raise Exception(f"Error detecting table regions: {str(e)}")
    
    async def _extract_table_from_region(self, image: np.ndarray, region: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract table data from a detected region"""
        try:
            x, y, w, h = region["x"], region["y"], region["width"], region["height"]
            roi = image[y:y+h, x:x+w]
            
            # Convert to grayscale
            gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            
            # Apply thresholding
            _, thresh = cv2.threshold(gray_roi, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            
            # Find horizontal and vertical lines
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
            vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 25))
            
            horizontal_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel)
            vertical_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel)
            
            # Combine lines
            table_structure = cv2.addWeighted(horizontal_lines, 0.5, vertical_lines, 0.5, 0.0)
            
            # Find cells
            contours, _ = cv2.findContours(table_structure, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            # Extract cell data (simplified - in practice, you'd need more sophisticated OCR)
            cells = []
            for contour in contours:
                if cv2.contourArea(contour) > 100:  # Filter small contours
                    x_cell, y_cell, w_cell, h_cell = cv2.boundingRect(contour)
                    cells.append({
                        "x": x_cell,
                        "y": y_cell,
                        "width": w_cell,
                        "height": h_cell
                    })
            
            # Sort cells by position to reconstruct table structure
            cells.sort(key=lambda c: (c["y"], c["x"]))
            
            # For now, return a simplified table structure
            # In a full implementation, you'd extract text from each cell using OCR
            return {
                "bbox": [x, y, w, h],
                "cells": cells,
                "confidence": region["confidence"],
                "extraction_method": "opencv",
                "data": [],  # Would contain actual cell text
                "columns": [],
                "rows": 0
            }
            
        except Exception as e:
            print(f"Warning: Error extracting table from region: {e}")
            return None
    
    def _has_table_structure(self, roi: np.ndarray) -> bool:
        """Check if a region has table-like structure"""
        try:
            # Apply edge detection
            edges = cv2.Canny(roi, 50, 150)
            
            # Count horizontal and vertical lines
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 1))
            vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 20))
            
            horizontal_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, horizontal_kernel)
            vertical_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, vertical_kernel)
            
            # Count non-zero pixels (lines)
            h_count = np.count_nonzero(horizontal_lines)
            v_count = np.count_nonzero(vertical_lines)
            
            # Check if there are enough lines to suggest a table
            total_pixels = roi.shape[0] * roi.shape[1]
            h_ratio = h_count / total_pixels
            v_ratio = v_count / total_pixels
            
            return h_ratio > 0.01 and v_ratio > 0.01
            
        except Exception:
            return False
    
    def _calculate_region_confidence(self, roi: np.ndarray) -> float:
        """Calculate confidence score for a table region"""
        try:
            # Simple confidence based on edge density
            edges = cv2.Canny(roi, 50, 150)
            edge_density = np.count_nonzero(edges) / (roi.shape[0] * roi.shape[1])
            
            # Normalize to 0-1 range
            confidence = min(edge_density * 100, 1.0)
            
            return confidence
            
        except Exception:
            return 0.0
    
    def _calculate_table_confidence(self, table_data: List[List[str]]) -> float:
        """Calculate confidence score for extracted table data"""
        try:
            if not table_data or len(table_data) < 2:
                return 0.0
            
            # Check for consistent column count
            column_counts = [len(row) for row in table_data]
            if len(set(column_counts)) > 1:
                return 0.3  # Inconsistent structure
            
            # Check for empty cells
            total_cells = sum(len(row) for row in table_data)
            empty_cells = sum(1 for row in table_data for cell in row if not cell.strip())
            empty_ratio = empty_cells / total_cells if total_cells > 0 else 1.0
            
            # Check for numeric content (tables often contain numbers)
            numeric_cells = 0
            for row in table_data:
                for cell in row:
                    if cell.strip():
                        try:
                            float(cell.strip().replace(',', '').replace('%', ''))
                            numeric_cells += 1
                        except ValueError:
                            pass
            
            numeric_ratio = numeric_cells / total_cells if total_cells > 0 else 0.0
            
            # Calculate overall confidence
            structure_score = 0.7 if len(set(column_counts)) == 1 else 0.3
            content_score = 1.0 - empty_ratio
            numeric_score = numeric_ratio
            
            confidence = (structure_score + content_score + numeric_score) / 3
            
            return max(0.0, min(1.0, confidence))
            
        except Exception:
            return 0.0
    
    async def _deduplicate_tables(self, tables: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate tables based on content similarity"""
        try:
            if not tables:
                return []
            
            unique_tables = []
            seen_content = set()
            
            for table in tables:
                # Create a hash of table content for deduplication
                if 'data' in table and table['data']:
                    content_hash = hash(str(table['data']))
                    
                    if content_hash not in seen_content:
                        seen_content.add(content_hash)
                        unique_tables.append(table)
                else:
                    # Tables without data are kept
                    unique_tables.append(table)
            
            return unique_tables
            
        except Exception as e:
            print(f"Warning: Error deduplicating tables: {e}")
            return tables
    
    async def export_table_to_csv(self, table: Dict[str, Any], output_path: str) -> bool:
        """Export table data to CSV file"""
        try:
            if 'dataframe' in table and table['dataframe']:
                df = pd.DataFrame(table['dataframe'])
                df.to_csv(output_path, index=False)
                return True
            elif 'data' in table and table['data']:
                df = pd.DataFrame(table['data'][1:], columns=table['data'][0])
                df.to_csv(output_path, index=False)
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Error exporting table to CSV: {e}")
            return False
    
    async def export_table_to_json(self, table: Dict[str, Any], output_path: str) -> bool:
        """Export table data to JSON file"""
        try:
            # Prepare table data for JSON export
            export_data = {
                "metadata": {
                    "page": table.get("page"),
                    "confidence": table.get("confidence"),
                    "extraction_method": table.get("extraction_method"),
                    "rows": table.get("rows"),
                    "columns": table.get("columns")
                },
                "data": table.get("dataframe", table.get("data", []))
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Error exporting table to JSON: {e}")
            return False 