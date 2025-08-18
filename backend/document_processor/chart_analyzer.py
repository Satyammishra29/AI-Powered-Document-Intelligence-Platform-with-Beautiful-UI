"""
Chart analyzer for detecting and analyzing charts and graphs in documents
"""

import asyncio
import os
from typing import Dict, List, Any, Optional, Tuple
import cv2
import numpy as np
from PIL import Image
import json
import re

class ChartAnalyzer:
    """
    Detects and analyzes charts and graphs in documents and images
    """
    
    def __init__(self):
        self.chart_types = [
            'bar_chart', 'line_chart', 'pie_chart', 'scatter_plot', 
            'histogram', 'area_chart', 'box_plot', 'heatmap'
        ]
        
        # Chart detection parameters
        self.min_chart_area = 1000  # Minimum area to consider as chart
        self.color_threshold = 0.1  # Threshold for color variation
    
    async def detect_charts(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Detect charts in a document or image
        
        Args:
            file_path: Path to the file
            
        Returns:
            List of detected charts with metadata
        """
        try:
            # Check file type
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension == '.pdf':
                return await self._detect_charts_in_pdf(file_path)
            else:
                return await self._detect_charts_in_image(file_path)
                
        except Exception as e:
            raise Exception(f"Error detecting charts: {str(e)}")
    
    async def _detect_charts_in_pdf(self, file_path: str) -> List[Dict[str, Any]]:
        """Detect charts in PDF document"""
        try:
            # For now, return empty list as PDF chart detection requires more complex processing
            # In a full implementation, you'd extract images from PDF and analyze them
            return []
            
        except Exception as e:
            print(f"Warning: Error detecting charts in PDF: {e}")
            return []
    
    async def _detect_charts_in_image(self, file_path: str) -> List[Dict[str, Any]]:
        """Detect charts in image file"""
        try:
            # Load image
            image = cv2.imread(file_path)
            if image is None:
                raise ValueError(f"Could not load image: {file_path}")
            
            # Detect potential chart regions
            chart_regions = await self._detect_chart_regions(image)
            
            # Analyze each detected region
            charts = []
            for region in chart_regions:
                chart_info = await self._analyze_chart_region(image, region)
                if chart_info:
                    charts.append(chart_info)
            
            return charts
            
        except Exception as e:
            raise Exception(f"Error detecting charts in image: {str(e)}")
    
    async def _detect_chart_regions(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detect potential chart regions in an image"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply edge detection
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter contours that could be charts
            chart_regions = []
            for contour in contours:
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)
                area = cv2.contourArea(contour)
                
                # Filter by size
                if area > self.min_chart_area:
                    # Check if region has chart-like characteristics
                    roi = image[y:y+h, x:x+w]
                    if await self._has_chart_characteristics(roi):
                        chart_regions.append({
                            "x": x,
                            "y": y,
                            "width": w,
                            "height": h,
                            "area": area,
                            "contour": contour,
                            "confidence": await self._calculate_chart_confidence(roi)
                        })
            
            return chart_regions
            
        except Exception as e:
            raise Exception(f"Error detecting chart regions: {str(e)}")
    
    async def _has_chart_characteristics(self, roi: np.ndarray) -> bool:
        """Check if a region has chart-like characteristics"""
        try:
            # Convert to different color spaces for analysis
            hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            
            # Check for color variation (charts often have multiple colors)
            color_variation = np.std(hsv[:, :, 1])  # Saturation variation
            if color_variation < 20:  # Low color variation
                return False
            
            # Check for edge density (charts have structured patterns)
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.count_nonzero(edges) / (roi.shape[0] * roi.shape[1])
            
            # Check for text-like patterns (charts often have labels)
            # This is a simplified check - in practice, you'd use OCR
            text_likelihood = self._estimate_text_likelihood(gray)
            
            # Combined score
            chart_score = (color_variation / 100) + edge_density + text_likelihood
            
            return chart_score > 0.3
            
        except Exception:
            return False
    
    async def _calculate_chart_confidence(self, roi: np.ndarray) -> float:
        """Calculate confidence score for a chart region"""
        try:
            # Convert to different color spaces
            hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            
            # Color variation score
            color_score = min(np.std(hsv[:, :, 1]) / 100, 1.0)
            
            # Edge density score
            edges = cv2.Canny(gray, 50, 150)
            edge_score = min(np.count_nonzero(edges) / (roi.shape[0] * roi.shape[1]) * 10, 1.0)
            
            # Structure score (based on contour analysis)
            structure_score = self._analyze_structure(gray)
            
            # Text likelihood score
            text_score = self._estimate_text_likelihood(gray)
            
            # Weighted average
            confidence = (color_score * 0.3 + edge_score * 0.3 + 
                         structure_score * 0.2 + text_score * 0.2)
            
            return max(0.0, min(1.0, confidence))
            
        except Exception:
            return 0.0
    
    def _analyze_structure(self, gray: np.ndarray) -> float:
        """Analyze the structural patterns in a grayscale image"""
        try:
            # Apply morphological operations to find patterns
            kernel = np.ones((3, 3), np.uint8)
            dilated = cv2.dilate(gray, kernel, iterations=1)
            eroded = cv2.erode(gray, kernel, iterations=1)
            
            # Calculate structural variation
            structural_diff = np.mean(np.abs(dilated.astype(float) - eroded.astype(float)))
            structural_score = min(structural_diff / 50, 1.0)
            
            return structural_score
            
        except Exception:
            return 0.0
    
    def _estimate_text_likelihood(self, gray: np.ndarray) -> float:
        """Estimate the likelihood of text presence in an image region"""
        try:
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                         cv2.THRESH_BINARY, 11, 2)
            
            # Find contours (potential text regions)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter contours by size and aspect ratio (text-like characteristics)
            text_contours = 0
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                area = cv2.contourArea(contour)
                
                # Text-like characteristics
                if 10 < area < 1000:  # Reasonable text size
                    aspect_ratio = w / h if h > 0 else 0
                    if 0.1 < aspect_ratio < 10:  # Reasonable text aspect ratio
                        text_contours += 1
            
            # Normalize by region size
            total_pixels = gray.shape[0] * gray.shape[1]
            text_density = text_contours / (total_pixels / 10000)  # Per 10k pixels
            
            return min(text_density / 10, 1.0)  # Normalize to 0-1
            
        except Exception:
            return 0.0
    
    async def _analyze_chart_region(self, image: np.ndarray, region: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze a detected chart region to determine chart type and extract data"""
        try:
            x, y, w, h = region["x"], region["y"], region["width"], region["height"]
            roi = image[y:y+h, x:x+w]
            
            # Determine chart type
            chart_type = await self._classify_chart_type(roi)
            
            # Extract basic chart information
            chart_info = {
                "bbox": [x, y, w, h],
                "chart_type": chart_type,
                "confidence": region["confidence"],
                "area": region["area"],
                "extraction_method": "opencv",
                "metadata": await self._extract_chart_metadata(roi, chart_type)
            }
            
            return chart_info
            
        except Exception as e:
            print(f"Warning: Error analyzing chart region: {e}")
            return None
    
    async def _classify_chart_type(self, roi: np.ndarray) -> str:
        """Classify the type of chart based on visual characteristics"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            
            # Calculate various features
            features = await self._extract_chart_features(roi, gray)
            
            # Simple rule-based classification
            if features["bar_like"] > 0.6:
                return "bar_chart"
            elif features["line_like"] > 0.6:
                return "line_chart"
            elif features["pie_like"] > 0.6:
                return "pie_chart"
            elif features["scatter_like"] > 0.6:
                return "scatter_plot"
            elif features["histogram_like"] > 0.6:
                return "histogram"
            else:
                return "unknown_chart"
                
        except Exception as e:
            print(f"Warning: Error classifying chart type: {e}")
            return "unknown_chart"
    
    async def _extract_chart_features(self, roi: np.ndarray, gray: np.ndarray) -> Dict[str, float]:
        """Extract features for chart classification"""
        try:
            features = {}
            
            # Bar chart features (vertical/horizontal lines)
            edges = cv2.Canny(gray, 50, 150)
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 1))
            vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 20))
            
            horizontal_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, horizontal_kernel)
            vertical_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, vertical_kernel)
            
            h_ratio = np.count_nonzero(horizontal_lines) / (roi.shape[0] * roi.shape[1])
            v_ratio = np.count_nonzero(vertical_lines) / (roi.shape[0] * roi.shape[1])
            
            features["bar_like"] = max(h_ratio * 10, v_ratio * 10)
            
            # Line chart features (connected components)
            # This is simplified - in practice, you'd use more sophisticated algorithms
            features["line_like"] = min(h_ratio * 5, 1.0)
            
            # Pie chart features (circular patterns)
            circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 20, 
                                     param1=50, param2=30, minRadius=10, maxRadius=100)
            if circles is not None:
                features["pie_like"] = min(len(circles[0]) / 5, 1.0)
            else:
                features["pie_like"] = 0.0
            
            # Scatter plot features (point-like patterns)
            # Simplified detection based on small contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            small_contours = sum(1 for c in contours if cv2.contourArea(c) < 50)
            features["scatter_like"] = min(small_contours / 20, 1.0)
            
            # Histogram features (bar-like but more uniform)
            features["histogram_like"] = min(features["bar_like"] * 0.8, 1.0)
            
            return features
            
        except Exception as e:
            print(f"Warning: Error extracting chart features: {e}")
            return {key: 0.0 for key in ["bar_like", "line_like", "pie_like", "scatter_like", "histogram_like"]}
    
    async def _extract_chart_metadata(self, roi: np.ndarray, chart_type: str) -> Dict[str, Any]:
        """Extract metadata from a chart region"""
        try:
            metadata = {
                "chart_type": chart_type,
                "dimensions": roi.shape[:2],
                "color_count": len(np.unique(roi.reshape(-1, roi.shape[-1]), axis=0)),
                "brightness": np.mean(roi),
                "contrast": np.std(roi)
            }
            
            # Add chart-specific metadata
            if chart_type == "bar_chart":
                metadata.update(await self._extract_bar_chart_metadata(roi))
            elif chart_type == "line_chart":
                metadata.update(await self._extract_line_chart_metadata(roi))
            elif chart_type == "pie_chart":
                metadata.update(await self._extract_pie_chart_metadata(roi))
            
            return metadata
            
        except Exception as e:
            print(f"Warning: Error extracting chart metadata: {e}")
            return {"chart_type": chart_type}
    
    async def _extract_bar_chart_metadata(self, roi: np.ndarray) -> Dict[str, Any]:
        """Extract metadata specific to bar charts"""
        try:
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            
            # Count potential bars
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            bar_candidates = [c for c in contours if cv2.contourArea(c) > 50]
            
            return {
                "estimated_bars": len(bar_candidates),
                "orientation": "vertical" if roi.shape[0] > roi.shape[1] else "horizontal"
            }
            
        except Exception:
            return {}
    
    async def _extract_line_chart_metadata(self, roi: np.ndarray) -> Dict[str, Any]:
        """Extract metadata specific to line charts"""
        try:
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            
            # Count line segments
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, 
                                  minLineLength=30, maxLineGap=10)
            
            return {
                "estimated_lines": len(lines) if lines is not None else 0,
                "complexity": "high" if len(lines) > 10 else "medium" if len(lines) > 5 else "low"
            }
            
        except Exception:
            return {}
    
    async def _extract_pie_chart_metadata(self, roi: np.ndarray) -> Dict[str, Any]:
        """Extract metadata specific to pie charts"""
        try:
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            
            # Count circular segments
            circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 20, 
                                     param1=50, param2=30, minRadius=10, maxRadius=100)
            
            return {
                "estimated_segments": len(circles[0]) if circles is not None else 0,
                "center_detected": circles is not None
            }
            
        except Exception:
            return {}
    
    async def export_chart_analysis(self, charts: List[Dict[str, Any]], output_path: str) -> bool:
        """Export chart analysis results to JSON file"""
        try:
            export_data = {
                "total_charts": len(charts),
                "analysis_timestamp": asyncio.get_event_loop().time(),
                "charts": charts
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Error exporting chart analysis: {e}")
            return False 