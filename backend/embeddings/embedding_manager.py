"""
Embedding manager for generating and storing vector embeddings
"""

import asyncio
import os
from typing import Dict, List, Any, Optional, Union
import numpy as np
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings as ChromaSettings
import json
from datetime import datetime

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.config import settings

class EmbeddingManager:
    """
    Manages the generation and storage of vector embeddings for text chunks
    """
    
    def __init__(self):
        self.model_name = settings.embedding_model
        self.vector_db_type = settings.vector_db_type
        self.chroma_persist_directory = settings.chroma_persist_directory
        
        # Initialize embedding model
        self.embedding_model = None
        self.vector_db = None
        
        # Initialize components
        self._initialize_embedding_model()
        self._initialize_vector_db()
    
    def _initialize_embedding_model(self):
        """Initialize the sentence transformer model"""
        try:
            print(f"🔄 Loading embedding model: {self.model_name}")
            self.embedding_model = SentenceTransformer(self.model_name)
            print(f"✅ Embedding model loaded successfully: {self.model_name}")
        except Exception as e:
            print(f"❌ Error loading embedding model: {e}")
            # Fallback to default model
            try:
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                print("✅ Fallback embedding model loaded: all-MiniLM-L6-v2")
            except Exception as fallback_error:
                raise RuntimeError(f"Could not load any embedding model: {fallback_error}")
    
    def _initialize_vector_db(self):
        """Initialize the vector database"""
        try:
            if self.vector_db_type == "chroma":
                # Initialize ChromaDB
                chroma_settings = ChromaSettings(
                    persist_directory=self.chroma_persist_directory,
                    anonymized_telemetry=False
                )
                
                self.vector_db = chromadb.Client(chroma_settings)
                
                # Get or create collection
                self.collection = self.vector_db.get_or_create_collection(
                    name="document_chunks",
                    metadata={"hnsw:space": "cosine"}
                )
                
                print(f"✅ ChromaDB initialized: {self.chroma_persist_directory}")
                
            elif self.vector_db_type == "pinecone":
                # Pinecone initialization would go here
                # For now, we'll use ChromaDB as fallback
                print("⚠️  Pinecone not yet implemented, using ChromaDB")
                self._initialize_vector_db()
                
            else:
                raise ValueError(f"Unsupported vector database type: {self.vector_db_type}")
                
        except Exception as e:
            raise RuntimeError(f"Error initializing vector database: {e}")
    
    async def generate_embeddings(self, text_chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate embeddings for a list of text chunks
        
        Args:
            text_chunks: List of text chunks with metadata
            
        Returns:
            List of chunks with embeddings added
        """
        try:
            if not text_chunks:
                return []
            
            # Extract text from chunks
            texts = [chunk["text"] for chunk in text_chunks]
            
            # Generate embeddings
            print(f"🔄 Generating embeddings for {len(texts)} chunks...")
            embeddings = self.embedding_model.encode(
                texts, 
                show_progress_bar=True,
                convert_to_numpy=True
            )
            
            # Add embeddings to chunks
            for i, chunk in enumerate(text_chunks):
                chunk["embedding"] = embeddings[i].tolist()
                chunk["embedding_dimension"] = len(embeddings[i])
                chunk["embedding_generated_at"] = datetime.utcnow().isoformat()
            
            print(f"✅ Generated embeddings for {len(text_chunks)} chunks")
            return text_chunks
            
        except Exception as e:
            raise Exception(f"Error generating embeddings: {str(e)}")
    
    async def store_embeddings(self, chunks_with_embeddings: List[Dict[str, Any]]) -> bool:
        """
        Store embeddings in the vector database
        
        Args:
            chunks_with_embeddings: List of chunks with embeddings
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not chunks_with_embeddings:
                return True
            
            if self.vector_db_type == "chroma":
                return await self._store_in_chroma(chunks_with_embeddings)
            else:
                raise ValueError(f"Storage not implemented for {self.vector_db_type}")
                
        except Exception as e:
            print(f"Error storing embeddings: {e}")
            return False
    
    async def _store_in_chroma(self, chunks_with_embeddings: List[Dict[str, Any]]) -> bool:
        """Store embeddings in ChromaDB"""
        try:
            # Prepare data for ChromaDB
            ids = []
            embeddings = []
            documents = []
            metadatas = []
            
            for chunk in chunks_with_embeddings:
                chunk_id = chunk["chunk_id"]
                
                # Skip if already exists
                if await self._chunk_exists(chunk_id):
                    continue
                
                ids.append(chunk_id)
                embeddings.append(chunk["embedding"])
                documents.append(chunk["text"])
                
                # Prepare metadata
                metadata = {
                    "document_id": chunk["document_id"],
                    "chunk_type": chunk.get("chunk_type", "unknown"),
                    "paragraph_index": chunk.get("paragraph_index", 0),
                    "length": chunk.get("length", 0),
                    "word_count": chunk.get("metadata", {}).get("word_count", 0),
                    "has_numbers": chunk.get("metadata", {}).get("has_numbers", False),
                    "created_at": chunk.get("created_at", datetime.utcnow().isoformat()),
                    "embedding_dimension": chunk.get("embedding_dimension", 0)
                }
                metadatas.append(metadata)
            
            if ids:
                # Add to collection
                self.collection.add(
                    ids=ids,
                    embeddings=embeddings,
                    documents=documents,
                    metadatas=metadatas
                )
                
                print(f"✅ Stored {len(ids)} embeddings in ChromaDB")
                return True
            else:
                print("ℹ️  No new embeddings to store")
                return True
                
        except Exception as e:
            print(f"Error storing in ChromaDB: {e}")
            return False
    
    async def _chunk_exists(self, chunk_id: str) -> bool:
        """Check if a chunk already exists in the database"""
        try:
            # Try to get the chunk
            result = self.collection.get(ids=[chunk_id])
            return len(result["ids"]) > 0
        except Exception:
            return False
    
    async def search_similar(self, query: str, top_k: int = 5, 
                           similarity_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        Search for similar chunks based on a query
        
        Args:
            query: Search query
            top_k: Number of results to return
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of similar chunks with similarity scores
        """
        try:
            # Generate embedding for query
            query_embedding = self.embedding_model.encode([query], convert_to_numpy=True)
            
            # Search in vector database
            if self.vector_db_type == "chroma":
                results = await self._search_in_chroma(query_embedding[0], top_k)
            else:
                raise ValueError(f"Search not implemented for {self.vector_db_type}")
            
            # Filter by similarity threshold
            filtered_results = [
                result for result in results 
                if result["similarity"] >= similarity_threshold
            ]
            
            return filtered_results
            
        except Exception as e:
            raise Exception(f"Error searching similar chunks: {str(e)}")
    
    async def _search_in_chroma(self, query_embedding: np.ndarray, top_k: int) -> List[Dict[str, Any]]:
        """Search for similar chunks in ChromaDB"""
        try:
            # Query the collection
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=top_k,
                include=["documents", "metadatas", "distances"]
            )
            
            # Process results
            similar_chunks = []
            if results["ids"] and results["ids"][0]:
                for i in range(len(results["ids"][0])):
                    chunk_id = results["ids"][0][i]
                    document = results["documents"][0][i]
                    metadata = results["metadatas"][0][i]
                    distance = results["distances"][0][i]
                    
                    # Convert distance to similarity score (ChromaDB uses cosine distance)
                    similarity = 1 - distance
                    
                    similar_chunks.append({
                        "chunk_id": chunk_id,
                        "text": document,
                        "similarity": similarity,
                        "metadata": metadata
                    })
            
            return similar_chunks
            
        except Exception as e:
            print(f"Error searching in ChromaDB: {e}")
            return []
    
    async def get_chunk_by_id(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific chunk by ID"""
        try:
            if self.vector_db_type == "chroma":
                results = self.collection.get(ids=[chunk_id])
                if results["ids"]:
                    return {
                        "chunk_id": results["ids"][0],
                        "text": results["documents"][0],
                        "metadata": results["metadatas"][0]
                    }
            return None
            
        except Exception as e:
            print(f"Error getting chunk by ID: {e}")
            return None
    
    async def delete_chunk(self, chunk_id: str) -> bool:
        """Delete a chunk from the database"""
        try:
            if self.vector_db_type == "chroma":
                self.collection.delete(ids=[chunk_id])
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Error deleting chunk: {e}")
            return False
    
    async def delete_document_chunks(self, document_id: str) -> bool:
        """Delete all chunks for a specific document"""
        try:
            if self.vector_db_type == "chroma":
                # Get all chunks for the document
                results = self.collection.get(
                    where={"document_id": document_id}
                )
                
                if results["ids"]:
                    # Delete all chunks
                    self.collection.delete(ids=results["ids"])
                    print(f"✅ Deleted {len(results['ids'])} chunks for document {document_id}")
                
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Error deleting document chunks: {e}")
            return False
    
    async def get_database_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector database"""
        try:
            if self.vector_db_type == "chroma":
                # Get collection count
                count = self.collection.count()
                
                # Get some sample metadata for analysis
                results = self.collection.get(limit=100)
                
                # Analyze metadata
                chunk_types = {}
                document_ids = set()
                
                if results["metadatas"]:
                    for metadata in results["metadatas"]:
                        chunk_type = metadata.get("chunk_type", "unknown")
                        chunk_types[chunk_type] = chunk_types.get(chunk_type, 0) + 1
                        
                        document_id = metadata.get("document_id")
                        if document_id:
                            document_ids.add(document_id)
                
                return {
                    "total_chunks": count,
                    "unique_documents": len(document_ids),
                    "chunk_type_distribution": chunk_types,
                    "embedding_dimension": self.embedding_model.get_sentence_embedding_dimension(),
                    "model_name": self.model_name,
                    "vector_db_type": self.vector_db_type
                }
            else:
                return {"error": f"Stats not implemented for {self.vector_db_type}"}
                
        except Exception as e:
            return {"error": f"Error getting database stats: {e}"}
    
    async def update_embedding_model(self, new_model_name: str) -> bool:
        """Update the embedding model"""
        try:
            print(f"🔄 Updating embedding model to: {new_model_name}")
            
            # Load new model
            new_model = SentenceTransformer(new_model_name)
            
            # Test the new model
            test_embedding = new_model.encode(["test"], convert_to_numpy=True)
            
            # Update the model
            self.embedding_model = new_model
            self.model_name = new_model_name
            
            print(f"✅ Embedding model updated successfully: {new_model_name}")
            return True
            
        except Exception as e:
            print(f"❌ Error updating embedding model: {e}")
            return False
    
    async def export_embeddings(self, output_path: str) -> bool:
        """Export all embeddings to a file (for backup/analysis)"""
        try:
            if self.vector_db_type == "chroma":
                # Get all data
                results = self.collection.get()
                
                export_data = {
                    "export_timestamp": datetime.utcnow().isoformat(),
                    "total_chunks": len(results["ids"]),
                    "chunks": []
                }
                
                for i in range(len(results["ids"])):
                    chunk_data = {
                        "chunk_id": results["ids"][i],
                        "text": results["documents"][i],
                        "metadata": results["metadatas"][i]
                    }
                    export_data["chunks"].append(chunk_data)
                
                # Save to file
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                
                print(f"✅ Exported {len(results['ids'])} embeddings to {output_path}")
                return True
            else:
                print(f"Export not implemented for {self.vector_db_type}")
                return False
                
        except Exception as e:
            print(f"Error exporting embeddings: {e}")
            return False
    
    async def cleanup_old_embeddings(self, days_old: int = 30) -> int:
        """Clean up old embeddings based on age"""
        try:
            if self.vector_db_type == "chroma":
                cutoff_date = datetime.utcnow().timestamp() - (days_old * 24 * 3600)
                
                # Get all chunks
                results = self.collection.get()
                
                chunks_to_delete = []
                for i, metadata in enumerate(results["metadatas"]):
                    created_at = metadata.get("created_at")
                    if created_at:
                        try:
                            chunk_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                            if chunk_date.timestamp() < cutoff_date:
                                chunks_to_delete.append(results["ids"][i])
                        except:
                            continue
                
                if chunks_to_delete:
                    self.collection.delete(ids=chunks_to_delete)
                    print(f"✅ Cleaned up {len(chunks_to_delete)} old embeddings")
                    return len(chunks_to_delete)
                else:
                    print("ℹ️  No old embeddings to clean up")
                    return 0
            else:
                print(f"Cleanup not implemented for {self.vector_db_type}")
                return 0
                
        except Exception as e:
            print(f"Error cleaning up old embeddings: {e}")
            return 0 