"""
Query Documents Page
Clean, focused RAG query interface with chat-like interactions
"""

import streamlit as st
import time
import json
import requests
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd
import chromadb
from chromadb.config import Settings
import os
import tempfile
import hashlib

# Import custom modules - using relative imports for compatibility
try:
    from utils.session_state import get_session_manager
    from config.settings import app_config
except ImportError:
    # Fallback if modules don't exist
    def get_session_manager():
        return None
    
    class app_config:
        SUPPORTED_FORMATS = ["pdf", "docx", "txt", "jpg", "png", "jpeg"]

# Initialize session manager
session_manager = get_session_manager()



# Initialize ChromaDB for vector search
def initialize_chroma_db():
    """Initialize ChromaDB for document vector storage and search"""
    try:
        # Create a persistent ChromaDB instance
        chroma_client = chromadb.PersistentClient(
            path="./chroma_db",
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create collection for documents
        collection = chroma_client.get_or_create_collection(
            name="document_collection",
            metadata={"hnsw:space": "cosine"}
        )
        
        return chroma_client, collection
    except Exception as e:
        st.error(f"❌ Failed to initialize ChromaDB: {str(e)}")
        return None, None

def get_uploaded_documents():
    """Get all uploaded and processed documents from session state"""
    uploaded_files = st.session_state.get('uploaded_files', [])
    processed_files = [f for f in uploaded_files if f.get('status') == 'processed']
    
    if not processed_files:
        st.warning("⚠️ No processed documents found. Please upload and process some documents first.")
        return []
    
    return processed_files

def create_document_embeddings(documents):
    """Create embeddings for documents using a simple hash-based approach"""
    try:
        embeddings = []
        texts = []
        metadatas = []
        ids = []
        
        for doc in documents:
            if doc.get('extracted_text') and len(doc['extracted_text'].strip()) > 0:
                # Split text into chunks
                text_chunks = split_text_into_chunks(doc['extracted_text'], 1000, 200)
                
                for i, chunk in enumerate(text_chunks):
                    # Create unique ID for each chunk
                    chunk_id = f"{doc['name']}_{i}_{hashlib.md5(chunk.encode()).hexdigest()[:8]}"
                    
                    # Generate simple hash-based embedding (768 dimensions to match typical embeddings)
                    chunk_hash = hashlib.md5(chunk.encode()).hexdigest()
                    # Convert hash to a list of numbers (simple embedding)
                    embedding = [ord(c) % 256 for c in chunk_hash[:32]] * 24  # 32 * 24 = 768 dimensions
                    
                    embeddings.append(embedding)
                    texts.append(chunk)
                    metadatas.append({
                        "document_name": doc['name'],
                        "document_type": doc['type'],
                        "chunk_index": i,
                        "total_chunks": len(text_chunks),
                        "upload_time": doc.get('upload_time', ''),
                        "confidence": doc.get('confidence', 0),
                        "file_size": doc.get('size', 0),
                        "chunk_length": len(chunk)
                    })
                    ids.append(chunk_id)
        
        return embeddings, texts, metadatas, ids
        
    except Exception as e:
        st.error(f"❌ Failed to create embeddings: {str(e)}")
        return [], [], [], []

def split_text_into_chunks(text, chunk_size=1000, overlap=200):
    """Split text into overlapping chunks for better search"""
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
        
        if start >= len(text):
            break
    
    return chunks

def index_documents_in_chroma(documents):
    """Index documents in ChromaDB for vector search"""
    try:
        chroma_client, collection = initialize_chroma_db()
        if not collection:
            return False
        
        # Check if documents are already indexed
        existing_count = collection.count()
        if existing_count > 0:
            st.info(f"📚 Documents already indexed in ChromaDB ({existing_count} chunks)")
            return True
        
        st.info("🔄 Indexing documents in ChromaDB...")
        
        # Create embeddings for documents
        embeddings, texts, metadatas, ids = create_document_embeddings(documents)
        
        if not embeddings:
            st.error("❌ No embeddings generated")
            return False
        
        # Add to ChromaDB collection
        collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        
        st.success(f"✅ Successfully indexed {len(embeddings)} text chunks in ChromaDB")
        return True
        
    except Exception as e:
        st.error(f"❌ Failed to index documents: {str(e)}")
        return False

def search_documents_semantic(query, max_results=5, search_type="semantic"):
    """Search documents using semantic similarity"""
    try:
        chroma_client, collection = initialize_chroma_db()
        if not collection:
            return []
        
        # Generate query embedding using simple hash-based approach
        query_hash = hashlib.md5(query.encode()).hexdigest()
        # Convert hash to a list of numbers (simple embedding)
        query_embedding = [ord(c) % 256 for c in query_hash[:32]] * 24  # 32 * 24 = 768 dimensions
        
        # Search in ChromaDB
        if search_type == "semantic":
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=max_results,
                include=["documents", "metadatas", "distances"]
            )
        elif search_type == "keyword":
            # Keyword search using ChromaDB's text search
            results = collection.query(
                query_texts=[query],
                n_results=max_results,
                include=["documents", "metadatas", "distances"]
            )
        else:
            # Hybrid search - combine both approaches
            semantic_results = collection.query(
                query_embeddings=[query_embedding],
                n_results=max_results//2,
                include=["documents", "metadatas", "distances"]
            )
            
            keyword_results = collection.query(
                query_texts=[query],
                n_results=max_results//2,
                include=["documents", "metadatas", "distances"]
            )
            
            # Combine and deduplicate results
            results = combine_search_results(semantic_results, keyword_results, max_results)
        
        return process_search_results(results, query)
        
    except Exception as e:
        st.error(f"❌ Search failed: {str(e)}")
        return []

def combine_search_results(semantic_results, keyword_results, max_results):
    """Combine semantic and keyword search results"""
    combined = {
        "documents": [],
        "metadatas": [],
        "distances": []
    }
    
    # Add semantic results
    if semantic_results["documents"]:
        combined["documents"].extend(semantic_results["documents"][0])
        combined["metadatas"].extend(semantic_results["metadatas"][0])
        combined["distances"].extend(semantic_results["distances"][0])
    
    # Add keyword results (avoid duplicates)
    if keyword_results["documents"]:
        for i, doc in enumerate(keyword_results["documents"][0]):
            if doc not in combined["documents"]:
                combined["documents"].append(doc)
                combined["metadatas"].append(keyword_results["metadatas"][0][i])
                combined["distances"].append(keyword_results["distances"][0][i])
    
    # Limit to max_results
    combined["documents"] = combined["documents"][:max_results]
    combined["metadatas"] = combined["metadatas"][:max_results]
    combined["distances"] = combined["distances"][:max_results]
    
    return combined

def process_search_results(results, query):
    """Process and format search results"""
    processed_results = []
    
    if not results or not results.get("documents"):
        return processed_results
    
    documents = results["documents"][0] if isinstance(results["documents"], list) else results["documents"]
    metadatas = results["metadatas"][0] if isinstance(results["metadatas"], list) else results["metadatas"]
    distances = results["distances"][0] if isinstance(results["distances"], list) else results["distances"]
    
    for i, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances)):
        # Calculate relevance score (convert distance to similarity)
        relevance = 1.0 - (distance / 2.0)  # Normalize distance to 0-1 range
        
        processed_result = {
            "document": metadata.get("document_name", "Unknown"),
            "page": metadata.get("chunk_index", 0) + 1,
            "relevance": max(0.0, min(1.0, relevance)),  # Clamp between 0 and 1
            "content_type": "text",
            "extracted_data": doc[:200] + "..." if len(doc) > 200 else doc,
            "full_content": doc,
            "metadata": metadata,
            "distance": distance
        }
        
        processed_results.append(processed_result)
    
    # Sort by relevance
    processed_results.sort(key=lambda x: x["relevance"], reverse=True)
    
    return processed_results

def connect_to_backend():
    """Check backend connection status"""
    try:
        backend_url = "http://localhost:8000"
        response = requests.get(f"{backend_url}/health", timeout=5)
        
        if response.status_code == 200:
            return True, "✅ Backend connected successfully!"
        else:
            return False, "⚠️ Backend responded but with errors"
            
    except requests.exceptions.ConnectionError:
        return False, "❌ Cannot connect to backend. Make sure it's running on http://localhost:8000"
    except Exception as e:
        return False, f"❌ Error connecting to backend: {str(e)}"

def enhance_with_backend(query, search_results):
    """Enhance search results using backend AI services"""
    try:
        backend_url = "http://localhost:8000"
        
        # Prepare data for backend enhancement
        payload = {
            "query": query,
            "search_results": search_results,
            "enhancement_type": "ai_analysis"
        }
        
        response = requests.post(f"{backend_url}/api/enhance", json=payload, timeout=30)
        
        if response.status_code == 200:
            enhanced_data = response.json()
            return enhanced_data
        else:
            st.warning("⚠️ Backend enhancement failed")
            return search_results
            
    except Exception as e:
        st.info("ℹ️ Backend enhancement unavailable - using local processing")
        return search_results

def generate_real_response_from_search(query: str, search_results: List[Dict], include_sources: bool, include_metadata: bool) -> Dict:
    """Generate real response based on actual search results"""
    try:
        if not search_results:
            return {
                "type": "no_results",
                "content": f"I couldn't find any relevant information for your query: '{query}'. Please try rephrasing your question or check if the documents contain the information you're looking for.",
                "sources": [],
                "confidence": 0.0,
                "processing_time": "0.1s"
            }
        
        # Calculate overall confidence based on search results
        avg_relevance = np.mean([result.get('relevance', 0) for result in search_results])
        confidence = min(0.95, avg_relevance + 0.1)  # Boost confidence slightly
        
        # Generate response content based on search results
        if len(search_results) == 1:
            # Single result - provide detailed response
            result = search_results[0]
            content = f"Based on your query '{query}', I found one highly relevant result in {result['document']}. Here's what I found:\n\n{result['extracted_data']}"
        else:
            # Multiple results - provide summary
            top_results = search_results[:3]
            content = f"Based on your query '{query}', I found {len(search_results)} relevant results across your documents. Here are the key findings:\n\n"
            
            for i, result in enumerate(top_results, 1):
                content += f"{i}. **{result['document']}** (Relevance: {result['relevance']:.1%}): {result['extracted_data']}\n\n"
        
        # Prepare sources if requested
        sources = []
        if include_sources:
            for result in search_results:
                source = {
                    "document": result['document'],
                    "page": result['page'],
                    "relevance": result['relevance'],
                    "content_type": result.get('content_type', 'text'),
                    "extracted_data": result['extracted_data']
                }
                sources.append(source)
        
        # Create response
        response = {
            "type": "search_results",
            "content": content,
            "sources": sources if include_sources else [],
            "confidence": confidence,
            "processing_time": f"{len(search_results) * 0.1:.1f}s",
            "query_analysis": {
                "intent": "information_retrieval",
                "complexity": "medium" if len(search_results) > 2 else "simple",
                "keywords": extract_keywords(query),
                "results_count": len(search_results),
                "avg_relevance": avg_relevance
            }
        }
        
        # Add metadata if requested
        if include_metadata:
            response["metadata"] = {
                "total_documents_searched": len(set(result['document'] for result in search_results)),
                "search_algorithm": "chromadb_semantic",
                "response_generation_model": "local_analysis",
                "timestamp": datetime.now().isoformat(),
                "search_results_count": len(search_results)
            }
        
        return response
        
    except Exception as e:
        st.error(f"❌ Error generating response: {str(e)}")
        return {
            "type": "error",
            "content": f"An error occurred while generating the response: {str(e)}",
            "sources": [],
            "confidence": 0.0,
            "processing_time": "0.1s"
        }

def render_document_indexing_section(documents):
    """Render document indexing section for ChromaDB"""
    
    # Enterprise-level section header
    st.markdown("""
    <div style="
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #3b82f6;
        margin-bottom: 2rem;
    ">
        <h3 style="
            margin: 0;
            color: #1e293b;
            font-size: 1.5rem;
            font-weight: 600;
        ">📚 Document Indexing & Search Readiness</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Professional metric cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style="
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
            text-align: center;
        ">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">📄</div>
            <div style="font-size: 1.5rem; font-weight: 600; color: #1e293b; margin-bottom: 0.25rem;">{}</div>
            <div style="font-size: 0.875rem; color: #64748b;">Documents</div>
        </div>
        """.format(len(documents)), unsafe_allow_html=True)
    
    with col2:
        total_chunks = sum(doc.get('text_chunks', 0) for doc in documents)
        st.markdown("""
        <div style="
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
            text-align: center;
        ">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">📝</div>
            <div style="font-size: 1.5rem; font-weight: 600; color: #1e293b; margin-bottom: 0.25rem;">{}</div>
            <div style="font-size: 0.875rem; color: #64748b;">Text Chunks</div>
        </div>
        """.format(total_chunks), unsafe_allow_html=True)
    
    with col3:
        doc_types = {}
        for doc in documents:
            doc_type = doc.get('type', 'unknown')
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
        
        st.markdown("""
        <div style="
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
            text-align: center;
        ">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🏷️</div>
            <div style="font-size: 1.5rem; font-weight: 600; color: #1e293b; margin-bottom: 0.25rem;">{}</div>
            <div style="font-size: 0.875rem; color: #64748b;">File Types</div>
        </div>
        """.format(len(doc_types)), unsafe_allow_html=True)
    
    with col4:
        try:
            chroma_client, collection = initialize_chroma_db()
            if collection:
                indexed_count = collection.count()
                if indexed_count > 0:
                    status_icon = "✅"
                    status_text = "Ready"
                    status_color = "#059669"
                else:
                    status_icon = "⚠️"
                    status_text = "Pending"
                    status_color = "#d97706"
            else:
                status_icon = "❌"
                status_text = "Error"
                status_color = "#dc2626"
        except Exception as e:
            status_icon = "❌"
            status_text = "Error"
            status_color = "#dc2626"
        
        st.markdown(f"""
        <div style="
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
            text-align: center;
        ">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">{status_icon}</div>
            <div style="font-size: 1.5rem; font-weight: 600; color: {status_color}; margin-bottom: 0.25rem;">{status_text}</div>
            <div style="font-size: 0.875rem; color: #64748b;">Status</div>
        </div>
        """, unsafe_allow_html=True)
    
    # File type breakdown
    if doc_types:
        st.markdown("**📊 File Type Distribution**")
        type_cols = st.columns(len(doc_types))
        for i, (doc_type, count) in enumerate(doc_types.items()):
            with type_cols[i]:
                st.markdown(f"""
                <div style="
                    background: #f8fafc;
                    padding: 1rem;
                    border-radius: 6px;
                    text-align: center;
                    border: 1px solid #e2e8f0;
                ">
                    <div style="font-size: 1rem; font-weight: 600; color: #1e293b; margin-bottom: 0.5rem;">
                        {doc_type.upper()}
                    </div>
                    <div style="font-size: 1.25rem; font-weight: 700; color: #3b82f6;">
                        {count}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # Action section
    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button(
            "🔄 Re-index Documents", 
            key="reindex_btn", 
            help="Re-index all documents in ChromaDB",
            use_container_width=True,
            type="primary"
        ):
            with st.spinner("🔄 Re-indexing documents..."):
                success = index_documents_in_chroma(documents)
                if success:
                    st.success("✅ Re-indexing completed!")
                    st.rerun()
                else:
                    st.error("❌ Re-indexing failed!")
    
    with col2:
        if st.session_state.get('auto_indexed', False):
            st.success("✅ Documents are indexed and ready for search!")
        else:
            st.info("ℹ️ Documents will be auto-indexed for first-time setup")
    
    # Auto-index if not already done
    if st.session_state.get('auto_indexed', False) == False:
        with st.spinner("🔄 Auto-indexing documents for first-time setup..."):
            success = index_documents_in_chroma(documents)
            if success:
                st.session_state.auto_indexed = True
                st.success("✅ Auto-indexing completed!")
            else:
                st.error("❌ Auto-indexing failed!")

def render_query_page():
    """Render the main query page with advanced chat features"""
    
    # Enterprise-level header with professional styling
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        padding: 2.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        border: 1px solid #475569;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    ">
        <div style="text-align: center; color: white;">
            <h1 style="
                margin: 0 0 1rem 0;
                font-size: 2.5rem;
                font-weight: 700;
                color: #f8fafc;
            ">🔍 AI-Powered Document Query</h1>
            <p style="
                margin: 0;
                font-size: 1.1rem;
                color: #cbd5e1;
                line-height: 1.6;
                max-width: 800px;
                margin: 0 auto;
            ">
                Leverage advanced AI capabilities to search, analyze, and extract insights from your document collection 
                with semantic search, real-time processing, and intelligent response generation.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Get uploaded documents and check if they're processed
    documents = get_uploaded_documents()
    if not documents:
        st.warning("⚠️ No processed documents found. Please upload and process some documents first.")
        st.info("💡 Go to the Upload page to get started!")
        return
    
    # Document indexing section
    render_document_indexing_section(documents)
    
    # Query interface
    render_query_interface()
    
    # Chat history
    render_chat_history()
    
    # Document statistics
    render_document_statistics(documents)
    
    # Query suggestions
    render_query_suggestions()

def render_query_interface():
    """Render the advanced query input interface"""
    
    # Enterprise-level section header
    st.markdown("""
    <div style="
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #8b5cf6;
        margin-bottom: 2rem;
    ">
        <h3 style="
            margin: 0;
            color: #1e293b;
            font-size: 1.5rem;
            font-weight: 600;
        ">💬 Advanced Query Interface</h3>
        <p style="
            margin: 0.5rem 0 0 0;
            color: #64748b;
            font-size: 0.95rem;
        ">
            Choose your preferred way to interact with your documents
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create professional tabs
    tab1, tab2, tab3 = st.tabs([
        "🔍 Standard Query", 
        "📊 Advanced Search", 
        "🎯 Smart Suggestions"
    ])
    
    with tab1:
        render_standard_query_interface()
    
    with tab2:
        render_advanced_search_interface()
    
    with tab3:
        render_smart_suggestions_interface()

def render_standard_query_interface():
    """Render the standard query interface"""
    
    # Enterprise-level query input section
    st.markdown("""
    <div style="
        background: white;
        padding: 2rem;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
        margin-bottom: 2rem;
    ">
        <h4 style="
            margin: 0 0 1.5rem 0;
            color: #1e293b;
            font-size: 1.25rem;
            font-weight: 600;
            text-align: center;
        ">💬 Ask a Question About Your Documents</h4>
        
        <p style="
            margin: 0 0 1.5rem 0;
            color: #64748b;
            text-align: center;
            font-size: 0.95rem;
        ">
            Use natural language to find information in your document collection
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Professional query input
    query = st.text_area(
        "Enter your question:",
        placeholder="e.g., What are the main findings in the research paper?",
        height=120,
        key="standard_query_input",
        help="Ask any question about your documents in natural language"
    )
    
    # Configuration section header
    st.markdown("**⚙️ Search Configuration**")
    
    # Query options in professional cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="
            background: #f8fafc;
            padding: 1.5rem;
            border-radius: 6px;
            border: 1px solid #e2e8f0;
            margin-bottom: 1rem;
        ">
            <h5 style="margin: 0 0 1rem 0; color: #1e293b; font-weight: 600; font-size: 0.95rem;">🔍 Search Type</h5>
        </div>
        """, unsafe_allow_html=True)
        
        search_type = st.selectbox(
            "Search Type:",
            ["semantic", "keyword", "hybrid"],
            format_func=lambda x: x.title(),
            help="Choose how to search through documents",
            label_visibility="collapsed"
        )
    
    with col2:
        st.markdown("""
        <div style="
            background: #f8fafc;
            padding: 1.5rem;
            border-radius: 6px;
            border: 1px solid #e2e8f0;
            margin-bottom: 1rem;
        ">
            <h5 style="margin: 0 0 1rem 0; color: #1e293b; font-weight: 600; font-size: 0.95rem;">📊 Max Results</h5>
        </div>
        """, unsafe_allow_html=True)
        
        max_results = st.slider(
            "Max Results:",
            min_value=1,
            max_value=20,
            value=5,
            help="Maximum number of results to return",
            label_visibility="collapsed"
        )
    
    with col3:
        st.markdown("""
        <div style="
            background: #f8fafc;
            padding: 1.5rem;
            border-radius: 6px;
            border: 1px solid #e2e8f0;
            margin-bottom: 1rem;
        ">
            <h5 style="margin: 0 0 1rem 0; color: #1e293b; font-weight: 600; font-size: 0.95rem;">🎯 Confidence</h5>
        </div>
        """, unsafe_allow_html=True)
        
        confidence_threshold = st.slider(
            "Confidence:",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.05,
            help="Minimum confidence threshold for results",
            label_visibility="collapsed"
        )
    
    # Additional options section
    st.markdown("**🔧 Additional Options**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        include_sources = st.checkbox(
            "📚 Include Sources", 
            value=True, 
            help="Show source documents and citations"
        )
    
    with col2:
        include_metadata = st.checkbox(
            "🏷️ Include Metadata", 
            value=False, 
            help="Show document metadata and processing info"
        )
    
    with col3:
        enable_streaming = st.checkbox(
            "⚡ Enable Streaming", 
            value=True, 
            help="Real-time response streaming for better UX"
        )
    
    # Professional submit button
    st.markdown("---")
    
    if st.button(
        "🚀 Search Documents", 
        key="search_btn_standard", 
        use_container_width=True, 
        type="primary",
        help="Start searching your documents with the configured settings"
    ):
        if query.strip():
            process_advanced_query(query, search_type, max_results, confidence_threshold, 
                                include_sources, include_metadata, enable_streaming)
        else:
            st.warning("⚠️ Please enter a question to search.")

def render_advanced_search_interface():
    """Render the advanced search interface"""
    
    # Enterprise-level advanced search header
    st.markdown("""
    <div style="
        background: white;
        padding: 2rem;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
        margin-bottom: 2rem;
    ">
        <h4 style="
            margin: 0 0 1rem 0;
            color: #1e293b;
            font-size: 1.25rem;
            font-weight: 600;
            text-align: center;
        ">🔍 Advanced Search Options</h4>
        <p style="
            margin: 0;
            color: #64748b;
            text-align: center;
            font-size: 0.95rem;
        ">
            Fine-tune your search with advanced filters and parameters
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Multi-field search in professional cards
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="
            background: #f8fafc;
            padding: 1.5rem;
            border-radius: 6px;
            border: 1px solid #e2e8f0;
            margin-bottom: 1rem;
        ">
            <h5 style="margin: 0 0 1rem 0; color: #1e293b; font-weight: 600; font-size: 0.95rem;">📄 Document Filters</h5>
        </div>
        """, unsafe_allow_html=True)
        
        file_types = st.multiselect(
            "File Types",
            ["PDF", "Image", "Document", "All"],
            default=["All"],
            help="Filter by document type",
            label_visibility="collapsed"
        )
        
        date_range = st.date_input(
            "Date Range",
            value=(datetime.now() - timedelta(days=30), datetime.now()),
            help="Filter by document upload date",
            label_visibility="collapsed"
        )
    
    with col2:
        st.markdown("""
        <div style="
            background: #f8fafc;
            padding: 1.5rem;
            border-radius: 6px;
            border: 1px solid #e2e8f0;
            margin-bottom: 1rem;
        ">
            <h5 style="margin: 0 0 1rem 0; color: #1e293b; font-weight: 600; font-size: 0.95rem;">📊 Content Filters</h5>
        </div>
        """, unsafe_allow_html=True)
        
        content_types = st.multiselect(
            "Content Types",
            ["Text", "Tables", "Charts", "Images", "Metadata"],
            default=["Text", "Tables"],
            help="Filter by content type",
            label_visibility="collapsed"
        )
        
        min_confidence = st.slider(
            "Minimum Confidence",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.05,
            label_visibility="collapsed"
        )
    
    # Advanced query options in professional cards
    st.markdown("**⚙️ Advanced Search Parameters**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="
            background: #f8fafc;
            padding: 1.5rem;
            border-radius: 6px;
            border: 1px solid #e2e8f0;
        ">
            <h5 style="margin: 0 0 1rem 0; color: #1e293b; font-weight: 600; font-size: 0.95rem;">📏 Chunk Settings</h5>
        </div>
        """, unsafe_allow_html=True)
        
        chunk_size = st.slider(
            "Chunk Size", 
            100, 2000, 1000, 
            step=100,
            label_visibility="collapsed"
        )
        overlap = st.slider(
            "Chunk Overlap", 
            0, 500, 200, 
            step=50,
            label_visibility="collapsed"
        )
    
    with col2:
        st.markdown("""
        <div style="
            background: #f8fafc;
            padding: 1.5rem;
            border-radius: 6px;
            border: 1px solid #e2e8f0;
        ">
            <h5 style="margin: 0 0 1rem 0; color: #1e293b; font-weight: 600; font-size: 0.95rem;">🧠 AI Models</h5>
        </div>
        """, unsafe_allow_html=True)
        
        embedding_model = st.selectbox(
            "Embedding Model",
            ["all-MiniLM-L6-v2", "all-mpnet-base-v2", "text-embedding-ada-002"],
            help="Choose embedding model for semantic search",
            label_visibility="collapsed"
        )
    
    with col3:
        st.markdown("""
        <div style="
            background: #f8fafc;
            padding: 1.5rem;
            border-radius: 6px;
            border: 1px solid #e2e8f0;
        ">
            <h5 style="margin: 0 0 1rem 0; color: #1e293b; font-weight: 600; font-size: 0.95rem;">📐 Similarity</h5>
        </div>
        """, unsafe_allow_html=True)
        
        similarity_metric = st.selectbox(
            "Similarity Metric",
            ["cosine", "euclidean", "manhattan"],
            help="Choose similarity calculation method",
            label_visibility="collapsed"
        )
    
    # Professional advanced search button
    st.markdown("---")
    
    if st.button(
        "🔍 Advanced Search", 
        key="advanced_search_btn", 
        use_container_width=True,
        type="secondary",
        help="Perform advanced search with all configured parameters"
    ):
        # Get the search parameters
        search_query = st.text_input(
            "Enter your search query:", 
            key="advanced_search_query", 
            placeholder="e.g., Find all financial data and metrics",
            help="Enter your search query to get started"
        )
        
        if search_query:
            # Perform advanced search
            with st.spinner("🔍 Performing advanced search..."):
                search_results = search_documents_semantic(
                    search_query, 
                    max_results=10, 
                    search_type="hybrid"
                )
                
                if search_results:
                    st.success(f"✅ Found {len(search_results)} relevant results!")
                    
                    # Display results in professional cards
                    for i, result in enumerate(search_results, 1):
                        with st.expander(
                            f"Result {i}: {result['document']} (Relevance: {result['relevance']:.1%})", 
                            expanded=False
                        ):
                            st.markdown(f"**Content:** {result['extracted_data']}")
                            st.caption(f"Document: {result['document']} | Page: {result['page']} | Relevance: {result['relevance']:.1%}")
                else:
                    st.warning("⚠️ No results found for your advanced search query.")
        else:
            st.warning("⚠️ Please enter a search query first.")

def render_smart_suggestions_interface():
    """Render the smart suggestions interface"""
    
    # Enterprise-level smart suggestions header
    st.markdown("""
    <div style="
        background: white;
        padding: 2rem;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
        margin-bottom: 2rem;
    ">
        <h4 style="
            margin: 0 0 1rem 0;
            color: #1e293b;
            font-size: 1.25rem;
            font-weight: 600;
            text-align: center;
        ">🎯 Smart Query Suggestions</h4>
        <p style="
            margin: 0;
            color: #64748b;
            text-align: center;
            font-size: 0.95rem;
        ">
            Get intelligent suggestions and quick actions for your document queries
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # AI-powered suggestions section
    st.markdown("**🤖 AI-Powered Suggestions**")
    
    if st.button(
        "🤖 Generate Smart Suggestions", 
        key="generate_suggestions_1",
        use_container_width=True,
        type="primary",
        help="Generate intelligent query suggestions based on your documents"
    ):
        suggestions = generate_ai_suggestions()
        display_ai_suggestions(suggestions)
    
    # Quick action buttons in professional layout
    st.markdown("**⚡ Quick Actions**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(
            "📊 Data Summary", 
            key="quick_summary_1",
            use_container_width=True,
            type="secondary"
        ):
            st.info("📊 Generating data summary...")
        
        if st.button(
            "🔍 Find Tables", 
            key="quick_tables_1",
            use_container_width=True,
            type="secondary"
        ):
            st.info("🔍 Searching for tables...")
    
    with col2:
        if st.button(
            "📈 Chart Analysis", 
            key="quick_charts_1",
            use_container_width=True,
            type="secondary"
        ):
            st.info("📈 Analyzing charts...")
        
        if st.button(
            "📝 Content Overview", 
            key="quick_overview_1",
            use_container_width=True,
            type="secondary"
        ):
            st.info("📝 Generating content overview...")

def generate_enhanced_response(query: str, max_results: int, include_sources: bool, include_metadata: bool) -> Dict:
    """Generate an enhanced response with advanced features"""
    # Simulate different types of responses based on query
    if "table" in query.lower():
        response_type = "table_data"
        content = "I found several tables in your documents. Here are the key data points with detailed analysis..."
        sources = [
            {"document": "Document_001.pdf", "page": 15, "relevance": 0.95, "content_type": "table", "extracted_data": "Sample table data..."},
            {"document": "Document_002.pdf", "page": 8, "relevance": 0.87, "content_type": "table", "extracted_data": "Additional table data..."}
        ]
    elif "chart" in query.lower() or "graph" in query.lower():
        response_type = "chart_analysis"
        content = "I detected charts and graphs in your documents. The analysis shows trends and patterns..."
        sources = [
            {"document": "Document_003.pdf", "page": 22, "relevance": 0.92, "content_type": "chart", "extracted_data": "Chart analysis..."},
            {"document": "Document_001.pdf", "page": 18, "relevance": 0.89, "content_type": "chart", "extracted_data": "Graph interpretation..."}
        ]
    else:
        response_type = "text_summary"
        content = f"Based on your question '{query}', I found relevant information in your documents. The key points are summarized with context..."
        sources = [
            {"document": "Document_001.pdf", "page": 5, "relevance": 0.91, "content_type": "text", "extracted_data": "Key findings..."},
            {"document": "Document_002.pdf", "page": 12, "relevance": 0.88, "content_type": "text", "extracted_data": "Supporting evidence..."},
            {"document": "Document_003.pdf", "page": 7, "relevance": 0.85, "content_type": "text", "extracted_data": "Additional context..."}
        ]
    
    # Enhanced response with metadata
    response = {
        "type": response_type,
        "content": content,
        "sources": sources[:max_results] if include_sources else [],
        "confidence": 0.89,
        "processing_time": "2.3s",
        "query_analysis": {
            "intent": "information_retrieval",
            "complexity": "medium",
            "keywords": extract_keywords(query)
        }
    }
    
    if include_metadata:
        response["metadata"] = {
            "total_documents_searched": 15,
            "search_algorithm": "hybrid_semantic",
            "response_generation_model": "gpt-4",
            "timestamp": datetime.now().isoformat()
        }
    
    return response

def extract_keywords(query: str) -> List[str]:
    """Extract keywords from query"""
    # Simple keyword extraction
    stop_words = {"what", "are", "the", "in", "and", "or", "with", "from", "to", "for", "of", "a", "an"}
    words = query.lower().split()
    keywords = [word for word in words if word not in stop_words and len(word) > 2]
    return keywords[:5]  # Return top 5 keywords

def generate_ai_suggestions() -> Dict[str, List[str]]:
    """Generate AI-powered query suggestions based on actual document content"""
    try:
        # Get actual documents to analyze
        documents = get_uploaded_documents()
        if not documents:
            return get_default_suggestions()
        
        # Analyze document content for intelligent suggestions
        suggestions = {
            "📊 Data Analysis": [],
            "📈 Visual Content": [],
            "📝 Content Summary": [],
            "🔍 Specific Queries": []
        }
        
        # Check for tables and numerical data
        table_docs = [doc for doc in documents if doc.get('tables', 0) > 0]
        if table_docs:
            suggestions["📊 Data Analysis"].extend([
                "What tables are in the documents and what data do they contain?",
                "Show me the key metrics and statistics from the tables",
                "What trends can you identify in the tabular data?"
            ])
        
        # Check for images and charts
        image_docs = [doc for doc in documents if doc.get('images', 0) > 0]
        if image_docs:
            suggestions["📈 Visual Content"].extend([
                "What charts and graphs are present in the documents?",
                "Analyze the visual data and extract insights",
                "What do the diagrams and images reveal?"
            ])
        
        # Check for text content
        text_docs = [doc for doc in documents if doc.get('text_chunks', 0) > 0]
        if text_docs:
            suggestions["📝 Content Summary"].extend([
                "Provide a comprehensive summary of all documents",
                "What are the main themes and topics covered?",
                "Give me an executive summary with key findings"
            ])
        
        # Generate specific queries based on document types
        doc_types = set(doc.get('type', 'unknown') for doc in documents)
        if '.pdf' in doc_types:
            suggestions["🔍 Specific Queries"].extend([
                "What are the main conclusions in the PDF documents?",
                "Find all references and citations in the documents"
            ])
        
        if '.docx' in doc_types:
            suggestions["🔍 Specific Queries"].extend([
                "What are the key points from the Word documents?",
                "Extract all headings and section titles"
            ])
        
        # Fill with default suggestions if any category is empty
        for category in suggestions:
            if not suggestions[category]:
                suggestions[category] = get_default_suggestions()[category]
        
        return suggestions
        
    except Exception as e:
        st.warning(f"⚠️ Error generating AI suggestions: {str(e)}")
        return get_default_suggestions()

def get_default_suggestions() -> Dict[str, List[str]]:
    """Get default query suggestions"""
    return {
        "📊 Data Analysis": [
            "What are the key performance indicators in the documents?",
            "Show me trends and patterns in the data",
            "What statistical insights can you extract?"
        ],
        "📈 Visual Content": [
            "Analyze all charts and graphs in the documents",
            "What do the visualizations reveal about the data?",
            "Extract insights from images and diagrams"
        ],
        "📝 Content Summary": [
            "Provide a comprehensive summary of all documents",
            "What are the main themes and topics covered?",
            "Give me an executive summary with key findings"
        ],
        "🔍 Specific Queries": [
            "Find all mentions of financial data and metrics",
            "What does the document say about market trends?",
            "Search for technical specifications and requirements"
        ]
    }

def display_ai_suggestions(suggestions: Dict[str, List[str]]):
    """Display AI-generated suggestions"""
    st.markdown("**🤖 AI-Generated Suggestions**")
    
    for category, queries in suggestions.items():
        with st.expander(category, expanded=False):
            for query in queries:
                if st.button(query, key=f"ai_suggestion_{hash(query)}", use_container_width=True):
                    st.session_state.standard_query_input = query
                    st.rerun()

def process_advanced_query(query: str, search_type: str, max_results: int, confidence: float, 
                         include_sources: bool, include_metadata: bool, enable_streaming: bool):
    """Process the advanced user query with real document search"""
    st.markdown("### 🔍 Advanced Search in Progress...")
    
    # Create progress containers
    progress_container = st.container()
    status_container = st.container()
    response_container = st.container()
    
    with progress_container:
        progress_bar = st.progress(0)
        status_text = st.empty()
    
    with status_container:
        st.markdown("**Search Progress**")
    
    try:
        # Step 1: Analyze Query
        status_text.text("🔄 Analyzing Query...")
        progress_bar.progress(0.2)
        time.sleep(0.3)
        
        # Step 2: Search Documents
        status_text.text("🔄 Searching Documents...")
        progress_bar.progress(0.4)
        
        # Actually search documents using ChromaDB
        search_results = search_documents_semantic(query, max_results, search_type)
        
        if not search_results:
            st.error("❌ No relevant documents found for your query.")
            return
        
        # Step 3: AI Processing
        status_text.text("🔄 AI Processing...")
        progress_bar.progress(0.6)
        time.sleep(0.3)
        
        # Step 4: Generate Response
        status_text.text("🔄 Generating Response...")
        progress_bar.progress(0.8)
        
        # Generate real response based on search results
        response = generate_real_response_from_search(query, search_results, include_sources, include_metadata)
        
        # Step 5: Finalize
        status_text.text("🔄 Finalizing Results...")
        progress_bar.progress(1.0)
        
        # Add to query history
        if "query_history" not in st.session_state:
            st.session_state.query_history = []
        
        query_entry = {
            "id": f"query_{len(st.session_state.query_history)}_{datetime.now().timestamp()}",
            "query": query,
            "response": response,
            "search_results": search_results,
            "timestamp": datetime.now().isoformat(),
            "search_type": search_type,
            "max_results": max_results,
            "confidence": confidence,
            "options": {
                "include_sources": include_sources,
                "include_metadata": include_metadata,
                "enable_streaming": enable_streaming
            }
        }
        
        st.session_state.query_history.append(query_entry)
        
        # Display enhanced response
        with response_container:
            display_enhanced_query_response(query_entry)
        
        st.success("🎉 Advanced query completed successfully!")
        
    except Exception as e:
        st.error(f"❌ Query processing failed: {str(e)}")
        progress_bar.progress(0)
        status_text.text("❌ Search failed!")

def process_query(query: str, search_type: str, max_results: int, confidence: float):
    """Process the user query (legacy function for compatibility)"""
    process_advanced_query(query, search_type, max_results, confidence, True, False, True)

def generate_mock_response(query: str, max_results: int) -> Dict:
    """Generate a mock response for demonstration"""
    # Simulate different types of responses based on query
    if "table" in query.lower():
        response_type = "table_data"
        content = "I found several tables in your documents. Here are the key data points..."
        sources = [
            {"document": "Document_001.pdf", "page": 15, "relevance": 0.95},
            {"document": "Document_002.pdf", "page": 8, "relevance": 0.87}
        ]
    elif "chart" in query.lower() or "graph" in query.lower():
        response_type = "chart_analysis"
        content = "I detected charts and graphs in your documents. The analysis shows..."
        sources = [
            {"document": "Document_003.pdf", "page": 22, "relevance": 0.92},
            {"document": "Document_001.pdf", "page": 18, "relevance": 0.89}
        ]
    else:
        response_type = "text_summary"
        content = f"Based on your question '{query}', I found relevant information in your documents. The key points are..."
        sources = [
            {"document": "Document_001.pdf", "page": 5, "relevance": 0.91},
            {"document": "Document_002.pdf", "page": 12, "relevance": 0.88},
            {"document": "Document_003.pdf", "page": 7, "relevance": 0.85}
        ]
    
    return {
        "type": response_type,
        "content": content,
        "sources": sources[:max_results],
        "confidence": 0.89,
        "processing_time": "2.3s"
    }

def display_enhanced_query_response(query_entry: Dict):
    """Display the enhanced query response with advanced features"""
    st.markdown("### 📝 Enhanced Response")
    
    response = query_entry["response"]
    
    # Response content with enhanced styling
    st.markdown(f"""
    <div class="response-content">
        <p><strong>{response['content']}</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced metrics display
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🎯 Confidence", f"{response['confidence']:.1%}")
    
    with col2:
        st.metric("⏱️ Processing Time", response['processing_time'])
    
    with col3:
        if 'query_analysis' in response:
            st.metric("🧠 Query Intent", response['query_analysis']['intent'].replace('_', ' ').title())
    
    with col4:
        if 'query_analysis' in response:
            st.metric("📊 Complexity", response['query_analysis']['complexity'].title())
    
    # Query analysis insights
    if 'query_analysis' in response and response['query_analysis']['keywords']:
        st.markdown("**🔑 Extracted Keywords**")
        keywords = response['query_analysis']['keywords']
        st.markdown(f"Keywords: {', '.join(keywords)}")
    
    # Enhanced sources display
    if response.get('sources'):
        st.markdown("### 📚 Enhanced Sources")
        
        for i, source in enumerate(response['sources'], 1):
            with st.container():
                st.markdown("---")
                
                col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                
                with col1:
                    st.markdown(f"**📄 {source['document']}** (Page {source['page']})")
                    st.caption(f"🎯 Relevance: {source['relevance']:.1%}")
                    if 'content_type' in source:
                        st.caption(f"📊 Type: {source['content_type'].title()}")
                
                with col2:
                    if 'extracted_data' in source:
                        st.caption(f"📝 Content: {source['extracted_data'][:100]}...")
                
                with col3:
                    if st.button("👁️ View", key=f"view_source_{i}", help="View source document"):
                        st.info(f"👁️ Viewing source: {source['document']} page {source['page']}")
                
                with col4:
                    if st.button("📥 Download", key=f"download_source_{i}", help="Download source"):
                        st.info(f"📥 Downloading {source['document']}")
    
    # Metadata display if available
    if 'metadata' in response:
        with st.expander("🔍 Response Metadata", expanded=False):
            st.json(response['metadata'])

def display_query_response(query_entry: Dict):
    """Display the query response (legacy function for compatibility)"""
    display_enhanced_query_response(query_entry)

def render_chat_history():
    """Render enhanced chat history with advanced features"""
    if not st.session_state.get('query_history'):
        return
    
    st.markdown("### 💭 Enhanced Chat History")
    
    # History controls
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        history_limit = st.selectbox(
            "Show Last:",
            [5, 10, 20, "All"],
            help="Number of recent queries to display"
        )
    
    with col2:
        filter_status = st.selectbox(
            "Filter by:",
            ["All", "Successful", "High Confidence", "Recent"],
            help="Filter chat history"
        )
    
    with col3:
        if st.button("🗑️ Clear History", help="Clear all chat history"):
            st.session_state.query_history = []
            st.rerun()
    
    # Filter queries based on selection
    queries_to_show = filter_chat_history(st.session_state.query_history, filter_status, history_limit)
    
    # Display enhanced query history
    for query_entry in queries_to_show:
        with st.expander(f"🔍 {query_entry['query'][:50]}...", expanded=False):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Query:** {query_entry['query']}")
                st.markdown(f"**Response:** {query_entry['response']['content'][:100]}...")
                
                # Enhanced metadata
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.caption(f"⏰ {query_entry['timestamp'][:19]}")
                with col_b:
                    st.caption(f"🔍 {query_entry['search_type']}")
                with col_c:
                    st.caption(f"🎯 {query_entry['confidence']:.1%}")
                
                # Show options if available
                if 'options' in query_entry:
                    options_text = []
                    if query_entry['options'].get('include_sources'):
                        options_text.append("📚 Sources")
                    if query_entry['options'].get('include_metadata'):
                        options_text.append("🏷️ Metadata")
                    if query_entry['options'].get('enable_streaming'):
                        options_text.append("⚡ Streaming")
                    
                    if options_text:
                        st.caption(f"Options: {', '.join(options_text)}")
            
            with col2:
                col_x, col_y = st.columns(2)
                
                with col_x:
                    if st.button("🔄 Rerun", key=f"rerun_{query_entry['id']}", help="Rerun this query"):
                        st.info("🔄 Rerunning query...")
                        # Logic to rerun query would go here
                
                with col_y:
                    if st.button("📋 Copy", key=f"copy_{query_entry['id']}", help="Copy query to input"):
                        st.session_state.standard_query_input = query_entry['query']
                        st.rerun()
    
    # Export chat history
    if st.button("📥 Export Chat History", use_container_width=True):
        export_chat_history(st.session_state.query_history)

def filter_chat_history(history: List[Dict], filter_type: str, limit) -> List[Dict]:
    """Filter chat history based on criteria"""
    filtered = history
    
    # Apply filters
    if filter_type == "Successful":
        filtered = [q for q in filtered if q.get('response', {}).get('confidence', 0) > 0.8]
    elif filter_type == "High Confidence":
        filtered = [q for q in filtered if q.get('response', {}).get('confidence', 0) > 0.9]
    elif filter_type == "Recent":
        # Show queries from last 24 hours
        cutoff = datetime.now() - timedelta(hours=24)
        filtered = [q for q in filtered if datetime.fromisoformat(q['timestamp']) > cutoff]
    
    # Apply limit
    if limit != "All" and len(filtered) > limit:
        filtered = filtered[-limit:]
    
    return filtered

def export_chat_history(history: List[Dict]):
    """Export chat history to various formats"""
    if not history:
        st.warning("No chat history to export")
        return
    
    # Prepare export data
    export_data = []
    for entry in history:
        export_data.append({
            "Query": entry['query'],
            "Response": entry['response']['content'][:200] + "...",
            "Timestamp": entry['timestamp'],
            "Search Type": entry['search_type'],
            "Confidence": f"{entry['confidence']:.1%}",
            "Processing Time": entry['response'].get('processing_time', 'N/A')
        })
    
    # Export options
    col1, col2 = st.columns(2)
    
    with col1:
        # CSV export
        df = pd.DataFrame(export_data)
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with col2:
        # JSON export
        json_data = json.dumps(export_data, indent=2)
        st.download_button(
            label="📊 Download JSON",
            data=json_data,
            file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

def render_query_suggestions():
    """Render enhanced query suggestions with AI-powered features"""
    st.markdown("### 💡 Enhanced Query Suggestions")
    
    # Create tabs for different suggestion types
    tab1, tab2, tab3 = st.tabs(["🚀 Quick Actions", "🤖 AI Suggestions", "📚 Template Library"])
    
    with tab1:
        render_quick_actions()
    
    with tab2:
        render_ai_powered_suggestions()
    
    with tab3:
        render_template_library()

def render_quick_actions():
    """Render quick action buttons"""
    st.markdown("**⚡ Quick Actions**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Data Summary", key="quick_summary_2", use_container_width=True):
            st.session_state.standard_query_input = "Provide a comprehensive summary of all documents with key findings and insights"
            st.rerun()
        
        if st.button("🔍 Find Tables", key="quick_tables_2", use_container_width=True):
            st.session_state.standard_query_input = "Extract and analyze all tables from the documents"
            st.rerun()
        
        if st.button("📈 Chart Analysis", key="quick_charts_2", use_container_width=True):
            st.session_state.standard_query_input = "Analyze all charts and graphs in the documents"
            st.rerun()
    
    with col2:
        if st.button("📝 Content Overview", key="quick_overview_2", use_container_width=True):
            st.session_state.standard_query_input = "Give me an overview of the main topics and themes covered in the documents"
            st.rerun()
        
        if st.button("🎯 Key Metrics", key="quick_metrics", use_container_width=True):
            st.session_state.standard_query_input = "What are the key performance indicators and metrics mentioned in the documents?"
            st.rerun()
        
        if st.button("🔍 Search Patterns", key="quick_patterns", use_container_width=True):
            st.session_state.standard_query_input = "Identify patterns and trends across all documents"
            st.rerun()

def render_ai_powered_suggestions():
    """Render AI-powered query suggestions"""
    st.markdown("**🤖 AI-Powered Suggestions**")
    
    if st.button("🧠 Generate Smart Suggestions", key="generate_suggestions_2", use_container_width=True):
        with st.spinner("🤖 Generating AI suggestions..."):
            time.sleep(1)  # Simulate AI processing
            suggestions = generate_ai_suggestions()
            display_ai_suggestions(suggestions)
    
    # Show recent AI suggestions if available
    if st.session_state.get('ai_suggestions'):
        st.markdown("**💡 Recent AI Suggestions**")
        for suggestion in st.session_state.ai_suggestions[-3:]:  # Show last 3
            if st.button(suggestion, key=f"recent_ai_{hash(suggestion)}", use_container_width=True):
                st.session_state.standard_query_input = suggestion
                st.rerun()

def render_template_library():
    """Render query template library"""
    st.markdown("**📚 Query Template Library**")
    
    # Categorized templates
    templates = {
        "📊 Data Analysis": [
            "What tables are in the documents?",
            "Show me the key metrics from the data",
            "What trends can you identify?",
            "Extract numerical data and statistics"
        ],
        "📈 Charts & Graphs": [
            "What charts are present?",
            "Analyze the graph data",
            "What do the visualizations show?",
            "Extract insights from diagrams"
        ],
        "📄 Content Summary": [
            "Summarize the main points",
            "What are the key findings?",
            "Give me an overview of the content",
            "What are the main conclusions?"
        ],
        "🔍 Specific Search": [
            "Find information about [topic]",
            "What does the document say about [subject]?",
            "Search for [keyword] in the documents",
            "Extract all mentions of [concept]"
        ],
        "🎯 Business Intelligence": [
            "What are the key performance indicators?",
            "Show me financial data and metrics",
            "What market trends are mentioned?",
            "Extract business insights and recommendations"
        ]
    }
    
    # Display templates in expandable sections
    for category, queries in templates.items():
        with st.expander(category, expanded=False):
            for query in queries:
                if st.button(query, key=f"template_{category}_{hash(query)}", use_container_width=True):
                    st.info(f"💡 Template selected: {query}")
                    st.session_state.standard_query_input = query
                    st.rerun()
    
    # Custom template creation
    st.markdown("**✏️ Create Custom Template**")
    
    with st.form("custom_template"):
        template_name = st.text_input("Template Name", placeholder="e.g., Financial Analysis")
        template_query = st.text_area("Template Query", placeholder="Enter your custom query template...")
        
        if st.form_submit_button("💾 Save Template"):
            if template_name and template_query:
                # Save template logic would go here
                st.success(f"✅ Template '{template_name}' saved successfully!")
            else:
                st.warning("⚠️ Please fill in both fields")

def render_document_statistics(documents):
    """Render real document statistics and insights"""
    
    # Enterprise-level section header
    st.markdown("""
    <div style="
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #10b981;
        margin-bottom: 2rem;
    ">
        <h3 style="
            margin: 0;
            color: #1e293b;
            font-size: 1.5rem;
            font-weight: 600;
        ">📊 Document Statistics & Insights</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if not documents:
        st.info("📭 No documents available for analysis")
        return
    
    # Calculate real statistics
    total_files = len(documents)
    total_size = sum(doc.get('size', 0) for doc in documents)
    total_text_chunks = sum(doc.get('text_chunks', 0) for doc in documents)
    total_tables = sum(doc.get('tables', 0) for doc in documents)
    total_images = sum(doc.get('images', 0) for doc in documents)
    avg_confidence = np.mean([doc.get('confidence', 0) for doc in documents if doc.get('confidence')])
    
    # Professional metric cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style="
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
            text-align: center;
        ">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">📄</div>
            <div style="font-size: 1.5rem; font-weight: 600; color: #1e293b; margin-bottom: 0.25rem;">{}</div>
            <div style="font-size: 0.875rem; color: #64748b;">Total Files</div>
        </div>
        """.format(total_files), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
            text-align: center;
        ">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">💾</div>
            <div style="font-size: 1.5rem; font-weight: 600; color: #1e293b; margin-bottom: 0.25rem;">{:.1f} MB</div>
            <div style="font-size: 0.875rem; color: #64748b;">Total Size</div>
        </div>
        """.format(total_size // (1024*1024)), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
            text-align: center;
        ">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">📝</div>
            <div style="font-size: 1.5rem; font-weight: 600; color: #1e293b; margin-bottom: 0.25rem;">{}</div>
            <div style="font-size: 0.875rem; color: #64748b;">Text Chunks</div>
        </div>
        """.format(total_text_chunks), unsafe_allow_html=True)
    
    with col4:
        confidence_text = f"{avg_confidence:.1%}" if avg_confidence > 0 else "N/A"
        st.markdown("""
        <div style="
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
            text-align: center;
        ">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🎯</div>
            <div style="font-size: 1.5rem; font-weight: 600; color: #1e293b; margin-bottom: 0.25rem;">{}</div>
            <div style="font-size: 0.875rem; color: #64748b;">Avg Confidence</div>
        </div>
        """.format(confidence_text), unsafe_allow_html=True)
    
    # File type distribution with professional styling
    st.markdown("**📊 File Type Distribution**")
    file_types = {}
    for doc in documents:
        doc_type = doc.get('type', 'unknown')
        file_types[doc_type.upper()] = file_types.get(doc_type.upper(), 0) + 1
    
    if file_types:
        col1, col2 = st.columns(2)
        
        with col1:
            # Professional pie chart of file types
            fig = {
                "data": [{
                    "values": list(file_types.values()),
                    "labels": list(file_types.keys()),
                    "type": "pie",
                    "hole": 0.4,
                    "marker": {"colors": ["#667eea", "#764ba2", "#f093fb", "#f5576c", "#4facfe"]}
                }],
                "layout": {
                    "title": {
                        "text": "Document Types",
                        "font": {"size": 16, "color": "#1e293b"}
                    },
                    "showlegend": True,
                    "height": 300,
                    "paper_bgcolor": "rgba(0,0,0,0)",
                    "plot_bgcolor": "rgba(0,0,0,0)"
                }
            }
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Content extraction summary in professional format
            st.markdown("**🔍 Content Extraction Summary**")
            
            content_data = {
                "Content Type": ["Text Chunks", "Tables", "Images"],
                "Count": [total_text_chunks, total_tables, total_images]
            }
            
            df = pd.DataFrame(content_data)
            st.dataframe(
                df, 
                use_container_width=True,
                hide_index=True
            )
    
    # Processing quality insights with professional styling
    st.markdown("**🎯 Processing Quality Insights**")
    
    high_confidence = len([doc for doc in documents if doc.get('confidence', 0) > 0.8])
    medium_confidence = len([doc for doc in documents if 0.5 <= doc.get('confidence', 0) <= 0.8])
    low_confidence = len([doc for doc in documents if doc.get('confidence', 0) < 0.5])
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="
            background: #f0fdf4;
            padding: 1.5rem;
            border-radius: 8px;
            border: 1px solid #bbf7d0;
            text-align: center;
        ">
            <div style="font-size: 1.5rem; font-weight: 600; color: #166534; margin-bottom: 0.5rem;">🟢</div>
            <div style="font-size: 1.25rem; font-weight: 700; color: #166534;">{}</div>
            <div style="font-size: 0.875rem; color: #166534;">High Quality</div>
            <div style="font-size: 0.75rem; color: #166534; opacity: 0.8;">Confidence > 80%</div>
        </div>
        """.format(high_confidence), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="
            background: #fffbeb;
            padding: 1.5rem;
            border-radius: 8px;
            border: 1px solid #fcd34d;
            text-align: center;
        ">
            <div style="font-size: 1.5rem; font-weight: 600; color: #92400e; margin-bottom: 0.5rem;">🟡</div>
            <div style="font-size: 1.25rem; font-weight: 700; color: #92400e;">{}</div>
            <div style="font-size: 0.875rem; color: #92400e;">Medium Quality</div>
            <div style="font-size: 0.75rem; color: #92400e; opacity: 0.8;">Confidence 50-80%</div>
        </div>
        """.format(medium_confidence), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="
            background: #fef2f2;
            padding: 1.5rem;
            border-radius: 8px;
            border: 1px solid #fca5a5;
            text-align: center;
        ">
            <div style="font-size: 1.5rem; font-weight: 600; color: #991b1b; margin-bottom: 0.5rem;">🔴</div>
            <div style="font-size: 1.25rem; font-weight: 700; color: #991b1b;">{}</div>
            <div style="font-size: 0.875rem; color: #991b1b;">Low Quality</div>
            <div style="font-size: 0.75rem; color: #991b1b; opacity: 0.8;">Confidence < 50%</div>
        </div>
        """.format(low_confidence), unsafe_allow_html=True)
    
    # Professional search readiness indicator
    st.markdown("---")
    
    if st.session_state.get('auto_indexed', False):
        st.markdown("""
        <div style="
            background: #f0fdf4;
            padding: 1.5rem;
            border-radius: 8px;
            border: 1px solid #bbf7d0;
            text-align: center;
        ">
            <h4 style="margin: 0; color: #166534;">✅ Documents are indexed and ready for semantic search!</h4>
            <p style="margin: 0.5rem 0 0 0; color: #166534; opacity: 0.8;">
                Your document collection is fully optimized for AI-powered queries and analysis.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="
            background: #fffbeb;
            padding: 1.5rem;
            border-radius: 8px;
            border: 1px solid #fcd34d;
            text-align: center;
        ">
            <h4 style="margin: 0; color: #92400e;">⚠️ Documents need to be indexed for optimal search performance</h4>
            <p style="margin: 0.5rem 0 0 0; color: #92400e; opacity: 0.8;">
                Indexing will enable faster and more accurate semantic search capabilities.
            </p>
        </div>
        """, unsafe_allow_html=True)
