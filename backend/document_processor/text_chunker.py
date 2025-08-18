"""
Text chunker for intelligently segmenting text into chunks for vector storage
"""

import asyncio
import re
from typing import Dict, List, Any, Optional
from datetime import datetime

class TextChunker:
    """
    Intelligently chunks text into segments for vector storage while preserving context
    """
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Sentence boundary patterns
        self.sentence_patterns = [
            r'[.!?]+[\s\n]+',  # Standard sentence endings
            r'[\n]{2,}',       # Multiple newlines
            r'[;:]\s+',        # Semicolons and colons
            r'\s+[A-Z][a-z]+\s+',  # Capitalized words (potential headers)
        ]
        
        # Paragraph boundary patterns
        self.paragraph_patterns = [
            r'[\n]{2,}',       # Multiple newlines
            r'\n\s*\n',        # Newline followed by optional whitespace and newline
        ]
    
    async def chunk_text(self, text: str, document_id: str) -> List[Dict[str, Any]]:
        """
        Chunk text into segments while preserving semantic meaning
        
        Args:
            text: Text to chunk
            document_id: ID of the document
            
        Returns:
            List of text chunks with metadata
        """
        try:
            if not text or not text.strip():
                return []
            
            # Clean and normalize text
            cleaned_text = self._clean_text(text)
            
            # Split into paragraphs first
            paragraphs = self._split_into_paragraphs(cleaned_text)
            
            # Chunk paragraphs into appropriate sizes
            chunks = []
            chunk_id = 0
            
            for para_idx, paragraph in enumerate(paragraphs):
                if len(paragraph.strip()) <= self.chunk_size:
                    # Paragraph fits in one chunk
                    chunk = self._create_chunk(
                        paragraph.strip(), 
                        document_id, 
                        chunk_id, 
                        para_idx,
                        "paragraph"
                    )
                    chunks.append(chunk)
                    chunk_id += 1
                else:
                    # Paragraph needs to be split
                    para_chunks = self._split_paragraph(paragraph, document_id, chunk_id, para_idx)
                    chunks.extend(para_chunks)
                    chunk_id += len(para_chunks)
            
            # Add overlap between chunks for better context preservation
            chunks = self._add_chunk_overlap(chunks)
            
            return chunks
            
        except Exception as e:
            raise Exception(f"Error chunking text: {str(e)}")
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        try:
            # Remove excessive whitespace
            text = re.sub(r'\s+', ' ', text)
            
            # Normalize newlines
            text = re.sub(r'\n+', '\n', text)
            
            # Remove special characters that might interfere with chunking
            text = re.sub(r'[\r\t]', ' ', text)
            
            # Ensure proper spacing around punctuation
            text = re.sub(r'\s+([.!?])', r'\1', text)
            
            return text.strip()
            
        except Exception:
            return text
    
    def _split_into_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs"""
        try:
            # Split by paragraph boundaries
            paragraphs = re.split(r'[\n]{2,}', text)
            
            # Clean up paragraphs
            cleaned_paragraphs = []
            for para in paragraphs:
                para = para.strip()
                if para and len(para) > 10:  # Minimum paragraph length
                    cleaned_paragraphs.append(para)
            
            return cleaned_paragraphs
            
        except Exception:
            return [text]
    
    def _split_paragraph(self, paragraph: str, document_id: str, start_chunk_id: int, para_idx: int) -> List[Dict[str, Any]]:
        """Split a long paragraph into multiple chunks"""
        try:
            chunks = []
            chunk_id = start_chunk_id
            
            # Try to split by sentences first
            sentences = self._split_into_sentences(paragraph)
            
            current_chunk = ""
            current_sentences = []
            
            for sentence in sentences:
                # Check if adding this sentence would exceed chunk size
                if len(current_chunk) + len(sentence) <= self.chunk_size:
                    current_chunk += sentence + " "
                    current_sentences.append(sentence)
                else:
                    # Current chunk is full, save it
                    if current_chunk.strip():
                        chunk = self._create_chunk(
                            current_chunk.strip(),
                            document_id,
                            chunk_id,
                            para_idx,
                            "sentence_group",
                            current_sentences
                        )
                        chunks.append(chunk)
                        chunk_id += 1
                    
                    # Start new chunk
                    current_chunk = sentence + " "
                    current_sentences = [sentence]
            
            # Add the last chunk
            if current_chunk.strip():
                chunk = self._create_chunk(
                    current_chunk.strip(),
                    document_id,
                    chunk_id,
                    para_idx,
                    "sentence_group",
                    current_sentences
                )
                chunks.append(chunk)
            
            return chunks
            
        except Exception as e:
            print(f"Warning: Error splitting paragraph: {e}")
            # Fallback: simple character-based splitting
            return self._fallback_split(paragraph, document_id, start_chunk_id, para_idx)
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        try:
            # Use multiple patterns to split sentences
            sentences = []
            current_text = text
            
            # Split by sentence endings
            parts = re.split(r'([.!?]+[\s\n]+)', current_text)
            
            for i in range(0, len(parts) - 1, 2):
                if i + 1 < len(parts):
                    sentence = parts[i] + parts[i + 1]
                    if sentence.strip():
                        sentences.append(sentence.strip())
                else:
                    # Last part without punctuation
                    if parts[i].strip():
                        sentences.append(parts[i].strip())
            
            # If no sentences found, split by newlines
            if not sentences:
                sentences = [s.strip() for s in text.split('\n') if s.strip()]
            
            return sentences
            
        except Exception:
            return [text]
    
    def _fallback_split(self, text: str, document_id: str, start_chunk_id: int, para_idx: int) -> List[Dict[str, Any]]:
        """Fallback method for splitting text when sentence splitting fails"""
        try:
            chunks = []
            chunk_id = start_chunk_id
            
            # Simple character-based splitting
            for i in range(0, len(text), self.chunk_size):
                chunk_text = text[i:i + self.chunk_size]
                if chunk_text.strip():
                    chunk = self._create_chunk(
                        chunk_text.strip(),
                        document_id,
                        chunk_id,
                        para_idx,
                        "character_split"
                    )
                    chunks.append(chunk)
                    chunk_id += 1
            
            return chunks
            
        except Exception as e:
            print(f"Warning: Fallback splitting failed: {e}")
            return []
    
    def _create_chunk(self, text: str, document_id: str, chunk_id: int, para_idx: int, 
                      chunk_type: str, sentences: Optional[List[str]] = None) -> Dict[str, Any]:
        """Create a text chunk with metadata"""
        try:
            chunk = {
                "chunk_id": f"{document_id}_chunk_{chunk_id}",
                "document_id": document_id,
                "text": text,
                "length": len(text),
                "chunk_type": chunk_type,
                "paragraph_index": para_idx,
                "created_at": datetime.utcnow().isoformat(),
                "metadata": {
                    "word_count": len(text.split()),
                    "character_count": len(text),
                    "has_numbers": bool(re.search(r'\d', text)),
                    "has_special_chars": bool(re.search(r'[^a-zA-Z0-9\s.,!?;:]', text))
                }
            }
            
            if sentences:
                chunk["sentences"] = sentences
                chunk["sentence_count"] = len(sentences)
            
            return chunk
            
        except Exception as e:
            print(f"Warning: Error creating chunk: {e}")
            return {
                "chunk_id": f"{document_id}_chunk_{chunk_id}",
                "document_id": document_id,
                "text": text,
                "length": len(text),
                "chunk_type": chunk_type,
                "paragraph_index": para_idx,
                "created_at": datetime.utcnow().isoformat(),
                "error": str(e)
            }
    
    def _add_chunk_overlap(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add overlap between chunks for better context preservation"""
        try:
            if len(chunks) <= 1 or self.chunk_overlap <= 0:
                return chunks
            
            overlapped_chunks = []
            
            for i, chunk in enumerate(chunks):
                # Add previous chunk's end as context
                if i > 0:
                    prev_chunk = chunks[i - 1]
                    overlap_text = prev_chunk["text"][-self.chunk_overlap:]
                    chunk["context_before"] = overlap_text
                
                # Add next chunk's beginning as context
                if i < len(chunks) - 1:
                    next_chunk = chunks[i + 1]
                    overlap_text = next_chunk["text"][:self.chunk_overlap]
                    chunk["context_after"] = overlap_text
                
                overlapped_chunks.append(chunk)
            
            return overlapped_chunks
            
        except Exception as e:
            print(f"Warning: Error adding chunk overlap: {e}")
            return chunks
    
    async def merge_chunks(self, chunks: List[Dict[str, Any]], merge_strategy: str = "smart") -> str:
        """Merge chunks back into text using specified strategy"""
        try:
            if not chunks:
                return ""
            
            if merge_strategy == "simple":
                return " ".join(chunk["text"] for chunk in chunks)
            
            elif merge_strategy == "smart":
                # Smart merging with context preservation
                merged_text = ""
                for i, chunk in enumerate(chunks):
                    if i > 0:
                        # Check for overlap with previous chunk
                        prev_chunk = chunks[i - 1]
                        overlap = self._find_overlap(prev_chunk["text"], chunk["text"])
                        
                        if overlap > 0:
                            # Remove overlap from current chunk
                            chunk_text = chunk["text"][overlap:]
                        else:
                            chunk_text = chunk["text"]
                    else:
                        chunk_text = chunk["text"]
                    
                    merged_text += chunk_text + " "
                
                return merged_text.strip()
            
            else:
                raise ValueError(f"Unknown merge strategy: {merge_strategy}")
                
        except Exception as e:
            raise Exception(f"Error merging chunks: {str(e)}")
    
    def _find_overlap(self, text1: str, text2: str, max_overlap: int = 100) -> int:
        """Find the overlap between two text strings"""
        try:
            # Look for overlap at the end of text1 and beginning of text2
            for i in range(min(len(text1), len(text2), max_overlap), 0, -1):
                if text1[-i:] == text2[:i]:
                    return i
            
            return 0
            
        except Exception:
            return 0
    
    async def optimize_chunks(self, chunks: List[Dict[str, Any]], target_size: int = None) -> List[Dict[str, Any]]:
        """Optimize chunk sizes for better retrieval"""
        try:
            if not chunks:
                return []
            
            if target_size is None:
                target_size = self.chunk_size
            
            optimized_chunks = []
            current_chunk = ""
            current_metadata = []
            
            for chunk in chunks:
                # Check if adding this chunk would exceed target size
                if len(current_chunk) + len(chunk["text"]) <= target_size:
                    current_chunk += chunk["text"] + " "
                    current_metadata.append(chunk)
                else:
                    # Current chunk is full, save it
                    if current_chunk.strip():
                        optimized_chunk = self._create_optimized_chunk(current_chunk.strip(), current_metadata)
                        optimized_chunks.append(optimized_chunk)
                    
                    # Start new chunk
                    current_chunk = chunk["text"] + " "
                    current_metadata = [chunk]
            
            # Add the last chunk
            if current_chunk.strip():
                optimized_chunk = self._create_optimized_chunk(current_chunk.strip(), current_metadata)
                optimized_chunks.append(optimized_chunk)
            
            return optimized_chunks
            
        except Exception as e:
            print(f"Warning: Error optimizing chunks: {e}")
            return chunks
    
    def _create_optimized_chunk(self, text: str, source_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create an optimized chunk from multiple source chunks"""
        try:
            # Combine metadata from source chunks
            combined_metadata = {
                "source_chunk_ids": [chunk["chunk_id"] for chunk in source_chunks],
                "total_word_count": sum(chunk["metadata"]["word_count"] for chunk in source_chunks),
                "chunk_types": list(set(chunk["chunk_type"] for chunk in source_chunks)),
                "paragraph_indices": list(set(chunk["paragraph_index"] for chunk in source_chunks))
            }
            
            return {
                "chunk_id": f"optimized_{hash(text)}",
                "text": text,
                "length": len(text),
                "chunk_type": "optimized",
                "created_at": datetime.utcnow().isoformat(),
                "metadata": combined_metadata,
                "source_chunks": source_chunks
            }
            
        except Exception as e:
            print(f"Warning: Error creating optimized chunk: {e}")
            return {
                "chunk_id": f"optimized_{hash(text)}",
                "text": text,
                "length": len(text),
                "chunk_type": "optimized",
                "created_at": datetime.utcnow().isoformat(),
                "error": str(e)
            } 