"""
RAG Engine for coordinating retrieval and generation
"""

import asyncio
import os
from typing import Dict, List, Any, Optional
import json
from datetime import datetime

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: OpenAI not available. Install with: pip install openai")

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.embeddings.embedding_manager import EmbeddingManager
from backend.config import settings

class RAGEngine:
    """
    Main RAG engine that coordinates retrieval and generation
    """
    
    def __init__(self):
        self.embedding_manager = EmbeddingManager()
        self.openai_client = None
        self.initialized = False
        
        # Initialize OpenAI client if available
        if OPENAI_AVAILABLE and settings.openai_api_key:
            try:
                self.openai_client = OpenAI(api_key=settings.openai_api_key)
                print("✅ OpenAI client initialized")
            except Exception as e:
                print(f"❌ Error initializing OpenAI client: {e}")
    
    async def initialize(self):
        """Initialize the RAG engine"""
        try:
            # Check if embedding manager is ready
            if not self.embedding_manager.embedding_model:
                raise RuntimeError("Embedding manager not ready")
            
            # Check if vector database is ready
            if not self.embedding_manager.vector_db:
                raise RuntimeError("Vector database not ready")
            
            self.initialized = True
            print("✅ RAG engine initialized successfully")
            
        except Exception as e:
            print(f"❌ Error initializing RAG engine: {e}")
            raise
    
    async def query(self, query: str, limit: int = 5, 
                   similarity_threshold: float = 0.7) -> Dict[str, Any]:
        """
        Process a query using RAG pipeline
        
        Args:
            query: User query
            limit: Maximum number of results to return
            similarity_threshold: Minimum similarity score for retrieval
            
        Returns:
            Dictionary containing query results and generated answer
        """
        try:
            if not self.initialized:
                raise RuntimeError("RAG engine not initialized")
            
            print(f"🔍 Processing query: {query}")
            
            # Step 1: Retrieve relevant chunks
            retrieved_chunks = await self.embedding_manager.search_similar(
                query, 
                top_k=limit, 
                similarity_threshold=similarity_threshold
            )
            
            if not retrieved_chunks:
                return {
                    "query": query,
                    "retrieved_chunks": [],
                    "generated_answer": "No relevant information found for your query.",
                    "confidence": 0.0,
                    "processing_time": 0.0
                }
            
            # Step 2: Generate answer using retrieved context
            generated_answer = await self._generate_answer(query, retrieved_chunks)
            
            # Step 3: Prepare response
            response = {
                "query": query,
                "retrieved_chunks": retrieved_chunks,
                "generated_answer": generated_answer["answer"],
                "confidence": generated_answer["confidence"],
                "processing_time": generated_answer["processing_time"],
                "total_chunks_retrieved": len(retrieved_chunks),
                "similarity_scores": [chunk["similarity"] for chunk in retrieved_chunks]
            }
            
            print(f"✅ Query processed successfully. Retrieved {len(retrieved_chunks)} chunks.")
            return response
            
        except Exception as e:
            raise Exception(f"Error processing query: {str(e)}")
    
    async def _generate_answer(self, query: str, retrieved_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate answer using retrieved context and language model"""
        try:
            start_time = asyncio.get_event_loop().time()
            
            if not self.openai_client:
                # Fallback: return a simple answer based on retrieved chunks
                return await self._fallback_answer_generation(query, retrieved_chunks)
            
            # Prepare context from retrieved chunks
            context = self._prepare_context(retrieved_chunks)
            
            # Create prompt for the language model
            prompt = self._create_prompt(query, context)
            
            # Generate answer using OpenAI
            try:
                response = self.openai_client.chat.completions.create(
                    model=settings.openai_model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful assistant that answers questions based on the provided context. Always base your answers on the given context and be accurate and helpful."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=settings.openai_temperature,
                    max_tokens=settings.openai_max_tokens
                )
                
                answer = response.choices[0].message.content
                confidence = self._calculate_answer_confidence(retrieved_chunks)
                
            except Exception as e:
                print(f"Warning: OpenAI generation failed: {e}")
                # Fallback to simple answer generation
                return await self._fallback_answer_generation(query, retrieved_chunks)
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            return {
                "answer": answer,
                "confidence": confidence,
                "processing_time": processing_time,
                "model_used": settings.openai_model
            }
            
        except Exception as e:
            print(f"Error generating answer: {e}")
            return await self._fallback_answer_generation(query, retrieved_chunks)
    
    def _prepare_context(self, retrieved_chunks: List[Dict[str, Any]]) -> str:
        """Prepare context string from retrieved chunks"""
        try:
            context_parts = []
            
            for i, chunk in enumerate(retrieved_chunks):
                chunk_text = chunk["text"]
                similarity = chunk["similarity"]
                metadata = chunk.get("metadata", {})
                
                # Add chunk with metadata
                context_part = f"--- Chunk {i+1} (Similarity: {similarity:.3f}) ---\n"
                context_part += f"Source: Document {metadata.get('document_id', 'unknown')}\n"
                context_part += f"Type: {metadata.get('chunk_type', 'unknown')}\n"
                context_part += f"Text: {chunk_text}\n"
                
                context_parts.append(context_part)
            
            return "\n".join(context_parts)
            
        except Exception as e:
            print(f"Error preparing context: {e}")
            return "Context preparation failed."
    
    def _create_prompt(self, query: str, context: str) -> str:
        """Create a prompt for the language model"""
        try:
            prompt = f"""Based on the following context, please answer the user's question. 

Context:
{context}

User Question: {query}

Please provide a comprehensive answer based on the context above. If the context doesn't contain enough information to answer the question, please say so. Be accurate and helpful."""
            
            return prompt
            
        except Exception as e:
            print(f"Error creating prompt: {e}")
            return f"Question: {query}\n\nContext: {context}"
    
    async def _fallback_answer_generation(self, query: str, retrieved_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Fallback answer generation when language model is not available"""
        try:
            start_time = asyncio.get_event_loop().time()
            
            # Simple answer based on most relevant chunk
            if retrieved_chunks:
                best_chunk = max(retrieved_chunks, key=lambda x: x["similarity"])
                
                # Create a simple answer
                answer = f"Based on the most relevant information found:\n\n{best_chunk['text']}\n\nThis information has a relevance score of {best_chunk['similarity']:.3f}."
                confidence = best_chunk["similarity"]
            else:
                answer = "No relevant information found for your query."
                confidence = 0.0
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            return {
                "answer": answer,
                "confidence": confidence,
                "processing_time": processing_time,
                "model_used": "fallback"
            }
            
        except Exception as e:
            print(f"Error in fallback answer generation: {e}")
            return {
                "answer": "Sorry, I encountered an error while processing your query.",
                "confidence": 0.0,
                "processing_time": 0.0,
                "model_used": "error"
            }
    
    def _calculate_answer_confidence(self, retrieved_chunks: List[Dict[str, Any]]) -> float:
        """Calculate confidence score for the generated answer"""
        try:
            if not retrieved_chunks:
                return 0.0
            
            # Calculate weighted average of similarity scores
            total_weight = 0
            weighted_sum = 0
            
            for i, chunk in enumerate(retrieved_chunks):
                # Give higher weight to more relevant chunks
                weight = 1.0 / (i + 1)
                total_weight += weight
                weighted_sum += chunk["similarity"] * weight
            
            if total_weight > 0:
                return weighted_sum / total_weight
            else:
                return 0.0
                
        except Exception:
            return 0.0
    
    async def list_documents(self) -> List[Dict[str, Any]]:
        """List all processed documents"""
        try:
            if not self.initialized:
                raise RuntimeError("RAG engine not initialized")
            
            # Get database stats
            stats = await self.embedding_manager.get_database_stats()
            
            if "error" in stats:
                return []
            
            # Get unique documents
            document_ids = set()
            if "unique_documents" in stats:
                # This would require additional implementation to get actual document details
                # For now, return basic stats
                return [{
                    "total_documents": stats.get("unique_documents", 0),
                    "total_chunks": stats.get("total_chunks", 0),
                    "chunk_types": stats.get("chunk_type_distribution", {}),
                    "embedding_model": stats.get("model_name", "unknown"),
                    "vector_db_type": stats.get("vector_db_type", "unknown")
                }]
            
            return []
            
        except Exception as e:
            print(f"Error listing documents: {e}")
            return []
    
    async def get_document_content(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed content of a specific document"""
        try:
            if not self.initialized:
                raise RuntimeError("RAG engine not initialized")
            
            # Get all chunks for the document
            if self.embedding_manager.vector_db_type == "chroma":
                results = self.embedding_manager.collection.get(
                    where={"document_id": document_id}
                )
                
                if results["ids"]:
                    chunks = []
                    for i in range(len(results["ids"])):
                        chunk = {
                            "chunk_id": results["ids"][i],
                            "text": results["documents"][i],
                            "metadata": results["metadatas"][i]
                        }
                        chunks.append(chunk)
                    
                    # Group chunks by type
                    chunk_groups = {}
                    for chunk in chunks:
                        chunk_type = chunk["metadata"].get("chunk_type", "unknown")
                        if chunk_type not in chunk_groups:
                            chunk_groups[chunk_type] = []
                        chunk_groups[chunk_type].append(chunk)
                    
                    return {
                        "document_id": document_id,
                        "total_chunks": len(chunks),
                        "chunk_groups": chunk_groups,
                        "retrieved_at": datetime.utcnow().isoformat()
                    }
            
            return None
            
        except Exception as e:
            print(f"Error getting document content: {e}")
            return None
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete a document and all its chunks"""
        try:
            if not self.initialized:
                raise RuntimeError("RAG engine not initialized")
            
            # Delete all chunks for the document
            success = await self.embedding_manager.delete_document_chunks(document_id)
            
            if success:
                print(f"✅ Document {document_id} deleted successfully")
            else:
                print(f"❌ Failed to delete document {document_id}")
            
            return success
            
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics and health information"""
        try:
            if not self.initialized:
                return {"status": "not_initialized"}
            
            # Get embedding manager stats
            embedding_stats = await self.embedding_manager.get_database_stats()
            
            # Get OpenAI status
            openai_status = "available" if self.openai_client else "not_available"
            
            # Get system info
            system_info = {
                "rag_engine_status": "initialized",
                "embedding_model": self.embedding_manager.model_name,
                "vector_db_type": self.embedding_manager.vector_db_type,
                "openai_status": openai_status,
                "openai_model": settings.openai_model if openai_status == "available" else "none",
                "chunk_size": settings.chunk_size,
                "chunk_overlap": settings.chunk_overlap,
                "similarity_threshold": settings.similarity_threshold,
                "retrieval_top_k": settings.retrieval_top_k
            }
            
            # Combine stats
            stats = {
                "system_info": system_info,
                "embedding_stats": embedding_stats,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return stats
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def optimize_retrieval(self, query: str, target_chunks: int = 5) -> Dict[str, Any]:
        """Optimize retrieval parameters for better results"""
        try:
            if not self.initialized:
                raise RuntimeError("RAG engine not initialized")
            
            # Try different similarity thresholds
            thresholds = [0.5, 0.6, 0.7, 0.8, 0.9]
            results = {}
            
            for threshold in thresholds:
                chunks = await self.embedding_manager.search_similar(
                    query, 
                    top_k=target_chunks, 
                    similarity_threshold=threshold
                )
                
                results[threshold] = {
                    "chunks_retrieved": len(chunks),
                    "avg_similarity": sum(chunk["similarity"] for chunk in chunks) / len(chunks) if chunks else 0,
                    "chunks": chunks
                }
            
            # Find optimal threshold
            optimal_threshold = max(
                results.keys(),
                key=lambda t: results[t]["chunks_retrieved"] > 0 and results[t]["avg_similarity"]
            )
            
            return {
                "query": query,
                "results_by_threshold": results,
                "optimal_threshold": optimal_threshold,
                "recommendation": f"Use similarity threshold {optimal_threshold} for optimal retrieval"
            }
            
        except Exception as e:
            raise Exception(f"Error optimizing retrieval: {str(e)}")
    
    async def export_query_results(self, query: str, output_path: str) -> bool:
        """Export query results to a file"""
        try:
            # Process the query
            results = await self.query(query)
            
            # Prepare export data
            export_data = {
                "export_timestamp": datetime.utcnow().isoformat(),
                "query": query,
                "results": results
            }
            
            # Save to file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Query results exported to {output_path}")
            return True
            
        except Exception as e:
            print(f"Error exporting query results: {e}")
            return False 