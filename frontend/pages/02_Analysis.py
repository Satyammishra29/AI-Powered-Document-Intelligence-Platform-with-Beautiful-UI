"""
Analysis Dashboard Page
Beautiful, modern analysis dashboard with clean design and essential insights
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
import requests
from PIL import Image
import io

# Import custom modules - using relative imports for compatibility
try:
    from utils.session_state import get_session_state
    from config.settings import app_config
except ImportError:
    # Fallback if modules don't exist
    def get_session_state():
        return None
    
    class app_config:
        SUPPORTED_FORMATS = ["pdf", "docx", "txt", "jpg", "png", "jpeg"]

# Initialize session state
session_state = get_session_state()

def render_analysis_page():
    """Render the beautiful, modern analysis dashboard"""
    
    # Beautiful header with gradient
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    ">
        <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700;">📊 Analysis Dashboard</h1>
        <p style="margin: 0.5rem 0 0 0; font-size: 1.2rem; opacity: 0.9;">
            Discover insights and patterns in your documents
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if there are processed documents
    if not st.session_state.get('uploaded_files'):
        render_empty_state()
        return
    
    # Main dashboard content
    render_dashboard_overview()
    render_document_insights()
    render_content_analytics()
    render_export_section()

def render_empty_state():
    """Render beautiful empty state when no documents exist"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="
            text-align: center;
            padding: 3rem 2rem;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 20px;
            border: 2px dashed #667eea;
        ">
            <div style="font-size: 4rem; margin-bottom: 1rem;">📭</div>
            <h3 style="color: #2d3748; margin-bottom: 1rem;">No Documents to Analyze</h3>
            <p style="color: #718096; margin-bottom: 2rem;">
                Upload some documents first to see beautiful analytics and insights
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Functional Streamlit button for navigation
        if st.button("📤 Go to Upload", use_container_width=True, type="primary"):
            st.session_state.current_page = "📤 Upload"
            st.rerun()

def render_dashboard_overview():
    """Render beautiful overview metrics"""
    st.markdown("### 🎯 Dashboard Overview")
    
    # Create beautiful metric cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_files = len(st.session_state.get('uploaded_files', []))
        render_metric_card(
            "📁 Total Files",
            total_files,
            "Total uploaded documents",
            "#667eea"
        )
    
    with col2:
        processed_files = len([f for f in st.session_state.get('uploaded_files', []) 
                             if f.get('status') == 'processed'])
        render_metric_card(
            "✅ Processed",
            processed_files,
            "Successfully processed",
            "#38a169"
        )
    
    with col3:
        total_size = sum(f.get('size', 0) for f in st.session_state.get('uploaded_files', []))
        size_mb = total_size // (1024*1024)
        render_metric_card(
            "💾 Total Size",
            f"{size_mb} MB",
            "Combined file size",
            "#d69e2e"
        )
    
    with col4:
        success_rate = (processed_files / total_files * 100) if total_files > 0 else 0
        render_metric_card(
            "🎯 Success Rate",
            f"{success_rate:.1f}%",
            "Processing success rate",
            "#e53e3e" if success_rate < 80 else "#38a169"
        )

def render_metric_card(title, value, description, color):
    """Render a beautiful metric card"""
    st.markdown(f"""
    <div style="
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 4px solid {color};
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    ">
        <div style="font-size: 2rem; font-weight: 700; color: {color}; margin-bottom: 0.5rem;">
            {value}
        </div>
        <div style="font-weight: 600; color: #2d3748; margin-bottom: 0.5rem;">
            {title}
        </div>
        <div style="font-size: 0.9rem; color: #718096;">
            {description}
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_document_insights():
    """Render document insights with beautiful charts"""
    st.markdown("### 📈 Document Insights")
    
    # File type distribution
    col1, col2 = st.columns(2)
    
    with col1:
        render_file_type_chart()
    
    with col2:
        render_processing_status_chart()
    
    # Document timeline
    st.markdown("### ⏰ Processing Timeline")
    render_processing_timeline()

def render_file_type_chart():
    """Render beautiful file type distribution chart"""
    st.markdown("**📊 File Type Distribution**")
    
    files = st.session_state.get('uploaded_files', [])
    if not files:
        st.info("No files to analyze")
        return
    
    # Count file types
    file_types = {}
    for file in files:
        file_type = file.get('type', 'unknown')
        if file_type not in file_types:
            file_types[file_type] = 0
        file_types[file_type] += 1
    
    if file_types:
        # Create beautiful pie chart
        fig = px.pie(
            values=list(file_types.values()),
            names=list(file_types.keys()),
            title="",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig.update_layout(
            showlegend=True,
            height=300,
            margin=dict(l=0, r=0, t=0, b=0)
        )
        
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hole=0.4
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No file type data available")

def render_processing_status_chart():
    """Render beautiful processing status chart"""
    st.markdown("**✅ Processing Status**")
    
    files = st.session_state.get('uploaded_files', [])
    if not files:
        st.info("No files to analyze")
        return
    
    # Count processing statuses
    statuses = {}
    for file in files:
        status = file.get('status', 'unknown')
        if status not in statuses:
            statuses[status] = 0
        statuses[status] += 1
    
    if statuses:
        # Create beautiful bar chart
        fig = px.bar(
            x=list(statuses.keys()),
            y=list(statuses.values()),
            title="",
            color=list(statuses.keys()),
            color_discrete_map={
                'processed': '#38a169',
                'processing': '#d69e2e',
                'error': '#e53e3e',
                'pending': '#718096'
            }
        )
        
        fig.update_layout(
            showlegend=False,
            height=300,
            margin=dict(l=0, r=0, t=0, b=0),
            xaxis_title="Status",
            yaxis_title="Count"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No status data available")

def render_processing_timeline():
    """Render beautiful processing timeline"""
    files = st.session_state.get('uploaded_files', [])
    if not files:
        st.info("No files to analyze")
        return
    
    # Create timeline data
    timeline_data = []
    for file in files:
        if file.get('upload_time'):
            timeline_data.append({
                'file': file.get('name', 'Unknown'),
                'time': file.get('upload_time'),
                'status': file.get('status', 'unknown')
            })
    
    if timeline_data:
        # Create timeline chart
        df = pd.DataFrame(timeline_data)
        df['time'] = pd.to_datetime(df['time'])
        df = df.sort_values('time')
        
        fig = px.scatter(
            df,
            x='time',
            y='file',
            color='status',
            title="",
            color_discrete_map={
                'processed': '#38a169',
                'processing': '#d69e2e',
                'error': '#e53e3e',
                'pending': '#718096'
            }
        )
        
        fig.update_layout(
            height=400,
            margin=dict(l=0, r=0, t=0, b=0),
            xaxis_title="Upload Time",
            yaxis_title="Files"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No timeline data available")

def render_content_analytics():
    """Render content analytics section"""
    st.markdown("### 🔍 Content Analytics")
    
    # Content extraction summary
    col1, col2 = st.columns(2)
    
    with col1:
        render_content_summary()
    
    with col2:
        render_quality_metrics()

def render_content_summary():
    """Render content extraction summary"""
    st.markdown("**📊 Content Summary**")
    
    files = st.session_state.get('uploaded_files', [])
    if not files:
        st.info("No content to analyze")
        return
    
    # Calculate content metrics
    total_text_chunks = sum(f.get('text_chunks', 0) for f in files)
    total_tables = sum(f.get('tables', 0) for f in files)
    total_images = sum(f.get('images', 0) for f in files)
    
    # Create metrics
    st.metric("📝 Text Chunks", total_text_chunks)
    st.metric("📊 Tables", total_tables)
    st.metric("🖼️ Images", total_images)

def render_quality_metrics():
    """Render quality metrics"""
    st.markdown("**🎯 Quality Metrics**")
    
    files = st.session_state.get('uploaded_files', [])
    if not files:
        st.info("No quality data available")
        return
    
    # Calculate quality metrics
    processed_files = [f for f in files if f.get('status') == 'processed']
    if processed_files:
        avg_confidence = np.mean([f.get('confidence', 0) for f in processed_files])
        st.metric("🎯 Avg Confidence", f"{avg_confidence:.1f}%")
        
        # Processing efficiency
        total_size = sum(f.get('size', 0) for f in processed_files)
        avg_time = np.mean([f.get('processing_time', 0) for f in processed_files])
        if avg_time > 0:
            efficiency = total_size / (avg_time * 1024 * 1024)  # MB/s
            st.metric("⚡ Processing Speed", f"{efficiency:.2f} MB/s")
    else:
        st.info("No processed files for quality metrics")

def render_export_section():
    """Render export section"""
    st.markdown("### 📤 Export & Reports")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Export Analytics", use_container_width=True):
            export_analytics_data()
    
    with col2:
        if st.button("📋 Export Summary", use_container_width=True):
            export_summary_report()
    
    with col3:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()

def export_analytics_data():
    """Export analytics data"""
    files = st.session_state.get('uploaded_files', [])
    if files:
        df = pd.DataFrame(files)
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"analytics_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.warning("No data to export")

def export_summary_report():
    """Export summary report"""
    files = st.session_state.get('uploaded_files', [])
    if files:
        # Create summary report
        total_files = len(files)
        processed_files = len([f for f in files if f.get('status') == 'processed'])
        success_rate = (processed_files / total_files * 100) if total_files > 0 else 0
        
        report = f"""
        Document Analysis Summary Report
        Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        Total Files: {total_files}
        Processed: {processed_files}
        Success Rate: {success_rate:.1f}%
        
        File Types: {', '.join(set(f.get('type', 'unknown') for f in files))}
        """
        
        st.download_button(
            label="📥 Download Report",
            data=report,
            file_name=f"summary_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )
    else:
        st.warning("No data to export")

# Helper functions for data processing
def calculate_average_processing_time():
    """Calculate average processing time"""
    files = st.session_state.get('uploaded_files', [])
    if not files:
        return 0
    
    processing_times = [f.get('processing_time', 0) for f in files if f.get('processing_time')]
    return np.mean(processing_times) if processing_times else 0

def calculate_content_extraction_stats():
    """Calculate content extraction statistics"""
    files = st.session_state.get('uploaded_files', [])
    if not files:
        return {'total': 0, 'delta': 0}
    
    total_items = sum(f.get('text_chunks', 0) + f.get('tables', 0) + f.get('images', 0) for f in files)
    return {'total': total_items, 'delta': total_items}

def check_system_health():
    """Check system health status"""
    return {'status': 'Healthy', 'score': '100%'}
