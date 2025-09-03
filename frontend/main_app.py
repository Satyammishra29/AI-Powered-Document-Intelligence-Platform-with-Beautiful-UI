"""
Main Application - Visual Document Analysis RAG System
Enterprise-grade Streamlit application with clean, professional interface
"""

import streamlit as st
import sys
import os
import importlib

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our custom modules
try:
    from utils.session_state import get_session_manager
except ImportError:
    # Fallback if modules don't exist
    def get_session_manager():
        return None

try:
    from config.settings import app_config, theme_config, ui_config
except ImportError:
    # Fallback if modules don't exist
    class app_config:
        BACKEND_URL = "http://localhost:8000"
        SUPPORTED_FORMATS = ["pdf", "docx", "txt", "jpg", "png", "jpeg"]
    
    class theme_config:
        PRIMARY_COLOR = "#8B5CF6"
        SECONDARY_COLOR = "#3B82F6"
    
    class ui_config:
        ENABLE_ANIMATIONS = True
        SHOW_PROGRESS_BARS = True

# Page configuration
st.set_page_config(
    page_title="Document Analysis RAG",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Add custom HTML to hide sidebar completely
st.markdown("""
<style>
/* Hide sidebar completely */
section[data-testid="stSidebar"] { display: none !important; }
[data-testid="stSidebar"] { display: none !important; }
.stSidebar { display: none !important; }
.sidebar { display: none !important; }
.sidebar-content { display: none !important; }

/* Force full width */
.main .block-container { max-width: 100% !important; margin-left: 0 !important; }
.main { margin-left: 0 !important; width: 100% !important; }
</style>
""", unsafe_allow_html=True)

# Initialize session manager
session_manager = get_session_manager()

def load_custom_css():
    """Load custom CSS files and hide sidebar"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    css_files = [
        os.path.join(base_dir, "assets", "styles.css"),
        os.path.join(base_dir, "assets", "animations.css")
    ]
    for css_file in css_files:
        try:
            with open(css_file, 'r', encoding='utf-8') as f:
                st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        except FileNotFoundError:
            st.warning(f"CSS file {css_file} not found")
        except Exception as e:
            st.error(f"Error loading CSS file {css_file}: {str(e)}")

def check_backend_connection():
    """Check if backend is connected"""
    try:
        import requests
        response = requests.get(f"{app_config.BACKEND_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def render_enterprise_logo():
    """Render the enterprise-level logo with modern design"""
    st.markdown("""
    <div class="logo-container">
        <div class="logo-icon">
            <div class="logo-inner">
                <div style="font-size: 3rem; color: white; font-weight: 900; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">AI</div>
            </div>
        </div>
        <div class="logo-text-container">
            <div class="logo-badge">🚀 Enterprise Grade</div>
            <h1 class="app-title">DocumentAI Pro</h1>
            <p class="app-subtitle">Enterprise Document Intelligence Platform</p>
            <div class="logo-features">
                <span class="feature-pill">🔒 Secure</span>
                <span class="feature-pill">⚡ Fast</span>
                <span class="feature-pill">🤖 AI-Powered</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_header():
    """Render the modern, enterprise-level header with enhanced navigation"""
    
    # Enterprise Logo Section
    render_enterprise_logo()
    

    
    # Theme Toggle Button
    try:
        from utils.theme_manager import theme_manager
        theme_info = theme_manager.get_theme_info()
        current_theme = theme_info['current']
        
        # Create theme toggle button
        if current_theme == "dark":
            if st.button("☀️ Light Mode", key="theme_toggle", help="Switch to light mode"):
                theme_manager.set_theme("light")
                st.rerun()
        else:
            if st.button("🌙 Dark Mode", key="theme_toggle", help="Switch to dark mode"):
                theme_manager.set_theme("dark")
                st.rerun()
    except ImportError:
        pass
    
    st.markdown("---")
    
    # Streamlit navigation buttons
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("🏠 Home", key="nav_home", use_container_width=True):
            st.session_state.current_page = "🏠 Home"
            st.rerun()
    
    with col2:
        if st.button("📤 Upload", key="nav_upload", use_container_width=True):
            st.session_state.current_page = "📤 Upload"
            st.rerun()
    
    with col3:
        if st.button("📊 Analysis", key="nav_analysis", use_container_width=True):
            st.session_state.current_page = "📊 Analysis"
            st.rerun()
    
    with col4:
        if st.button("🔍 Query", key="nav_query", use_container_width=True):
            st.session_state.current_page = "🔍 Query"
            st.rerun()
    
    with col5:
        if st.button("⚙️ Settings", key="nav_settings", use_container_width=True):
            st.session_state.current_page = "⚙️ Settings"
            st.rerun()
    
    st.markdown("---")

def render_home_page():
    """Render the beautiful, enterprise-level home page with enhanced UI"""
    
    # Welcome message for first-time users
    if "first_visit" not in st.session_state:
        st.session_state.first_visit = True
        st.success("🎉 Welcome to DocumentAI Pro! Your enterprise-grade document intelligence platform is ready.")
    
    # Hero Section with Enterprise Design
    st.markdown("""
    <div class="hero-section-enhanced">
        <div class="hero-content">
            <div class="hero-badge">🚀 Enterprise AI Platform</div>
            <h1 class="hero-title-enhanced" style="color: #1e293b; text-shadow: 0 2px 8px rgba(0,0,0,0.3), 0 4px 16px rgba(0,0,0,0.2); font-weight: 800; font-size: 3.5rem; letter-spacing: -0.02em; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.4));">Transform Documents into Actionable Intelligence</h1>
            <p class="hero-subtitle-enhanced" style="color: #475569; font-weight: 600; line-height: 1.7; font-size: 1.3rem; text-shadow: 0 1px 3px rgba(0,0,0,0.2); filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));">
                Leverage cutting-edge AI technology to extract insights, discover patterns, and unlock the hidden value 
                in your document collection. Built for enterprise-scale operations with bank-level security.
            </p>
            <div class="hero-stats">
                <div class="stat-item">
                    <span class="stat-number" style="color: var(--primary-500); font-weight: 800; font-size: 2.5rem; text-shadow: 0 2px 8px rgba(59, 130, 246, 0.4); filter: drop-shadow(0 4px 12px rgba(59, 130, 246, 0.3));">99.9%</span>
                    <span class="stat-label" style="color: #1e293b; font-weight: 700; font-size: 1.1rem; text-shadow: 0 1px 3px rgba(0,0,0,0.2);">Accuracy Rate</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number" style="color: var(--secondary-500); font-weight: 800; font-size: 2.5rem; text-shadow: 0 2px 8px rgba(139, 92, 246, 0.4); filter: drop-shadow(0 4px 12px rgba(139, 92, 246, 0.3));">50+</span>
                    <span class="stat-label" style="color: #1e293b; font-weight: 700; font-size: 1.1rem; text-shadow: 0 1px 3px rgba(0,0,0,0.2);">File Formats</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number" style="color: var(--success-500); font-weight: 800; font-size: 2.5rem; text-shadow: 0 2px 8px rgba(16, 185, 129, 0.4); filter: drop-shadow(0 4px 12px rgba(16, 185, 129, 0.3));">24/7</span>
                    <span class="stat-label" style="color: #1e293b; font-weight: 700; font-size: 1.1rem; text-shadow: 0 1px 3px rgba(0,0,0,0.2);">Availability</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number" style="color: var(--warning-500); font-weight: 800; font-size: 2.5rem; text-shadow: 0 2px 8px rgba(245, 158, 11, 0.4); filter: drop-shadow(0 4px 12px rgba(245, 158, 11, 0.3));">1M+</span>
                    <span class="stat-label" style="color: #1e293b; font-weight: 700; font-size: 1.1rem; text-shadow: 0 1px 3px rgba(0,0,0,0.2);">Documents Processed</span>
                </div>
            </div>
        </div>
        <div class="hero-visual">
            <div class="floating-card card-1">
                <div class="card-icon">📊</div>
                <div class="card-text" style="color: #1e293b; font-weight: 600;">Smart Analytics</div>
            </div>
            <div class="floating-card card-2">
                <div class="card-icon">🔍</div>
                <div class="card-text" style="color: #1e293b; font-weight: 600;">AI Search</div>
            </div>
            <div class="floating-card card-3">
                <div class="card-icon">⚡</div>
                <div class="card-text" style="color: #1e293b; font-weight: 600;">Fast Processing</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Actions Section
    st.markdown("""
    <div class="quick-actions-section">
        <h2 class="section-title" style="color: #1e293b; font-weight: 800; font-size: 2.2rem; text-shadow: 0 2px 8px rgba(0,0,0,0.3), 0 4px 16px rgba(0,0,0,0.2); filter: drop-shadow(0 4px 8px rgba(0,0,0,0.4)); letter-spacing: -0.01em;">🚀 Quick Start</h2>
        <p class="section-subtitle" style="color: #475569; font-weight: 600; line-height: 1.6; font-size: 1.2rem; text-shadow: 0 1px 3px rgba(0,0,0,0.2); filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));">Choose your path to get started with enterprise document intelligence</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced Action Cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="action-card upload-card">
            <div class="card-header">
                <div class="card-icon-large">📤</div>
                <h3 style="color: #1e293b; font-weight: 800; font-size: 1.5rem; text-shadow: 0 2px 6px rgba(0,0,0,0.3); filter: drop-shadow(0 3px 6px rgba(0,0,0,0.4));">Upload Documents</h3>
            </div>
            <p style="color: #475569; line-height: 1.7; font-weight: 600; font-size: 1.1rem; text-shadow: 0 1px 3px rgba(0,0,0,0.2);">Start by uploading your documents. We support PDFs, images, scanned documents, and more with intelligent format detection.</p>
            <div class="card-features">
                <span class="feature-tag" style="color: white; background: var(--primary-500); font-weight: 700; font-size: 0.9rem; padding: 0.5rem 1rem; border-radius: 20px; text-shadow: 0 1px 2px rgba(0,0,0,0.3); box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);">Multi-format</span>
                <span class="feature-tag" style="color: white; background: var(--secondary-500); font-weight: 700; font-size: 0.9rem; padding: 0.5rem 1rem; border-radius: 20px; text-shadow: 0 1px 2px rgba(0,0,0,0.3); box-shadow: 0 2px 8px rgba(139, 92, 246, 0.3);">Drag & Drop</span>
                <span class="feature-tag" style="color: white; background: var(--success-500); font-weight: 700; font-size: 0.9rem; padding: 0.5rem 1rem; border-radius: 20px; text-shadow: 0 1px 2px rgba(0,0,0,0.3); box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);">Batch Upload</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Start Uploading", key="upload_btn", use_container_width=True):
            st.session_state.current_page = "📤 Upload"
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="action-card query-card">
            <div class="card-header">
                <div class="card-icon-large">🔍</div>
                <h3 style="color: #1e293b; font-weight: 800; font-size: 1.5rem; text-shadow: 0 2px 6px rgba(0,0,0,0.3); filter: drop-shadow(0 3px 6px rgba(0,0,0,0.4));">Ask Questions</h3>
            </div>
            <p style="color: #475569; line-height: 1.7; font-weight: 600; font-size: 1.1rem; text-shadow: 0 1px 3px rgba(0,0,0,0.2);">Query your documents using natural language. Get instant answers with source citations and confidence scores.</p>
            <div class="card-features">
                <span class="feature-tag" style="color: white; background: var(--primary-500); font-weight: 700; font-size: 0.9rem; padding: 0.5rem 1rem; border-radius: 20px; text-shadow: 0 1px 2px rgba(0,0,0,0.3); box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);">AI Chat</span>
                <span class="feature-tag" style="color: white; background: var(--secondary-500); font-weight: 700; font-size: 0.9rem; padding: 0.5rem 1rem; border-radius: 20px; text-shadow: 0 1px 2px rgba(0,0,0,0.3); box-shadow: 0 2px 8px rgba(139, 92, 246, 0.3);">Smart Search</span>
                <span class="feature-tag" style="color: white; background: var(--success-500); font-weight: 700; font-size: 0.9rem; padding: 0.5rem 1rem; border-radius: 20px; text-shadow: 0 1px 2px rgba(0,0,0,0.3); box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);">Citations</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔍 Try Querying", key="query_btn", use_container_width=True):
            st.session_state.current_page = "🔍 Query"
            st.rerun()
    
    with col3:
        st.markdown("""
        <div class="action-card analysis-card">
            <div class="card-header">
                <div class="card-icon-large">📊</div>
                <h3 style="color: #1e293b; font-weight: 800; font-size: 1.5rem; text-shadow: 0 2px 6px rgba(0,0,0,0.3); filter: drop-shadow(0 3px 6px rgba(0,0,0,0.4));">View Analytics</h3>
            </div>
            <p style="color: #475569; line-height: 1.7; font-weight: 600; font-size: 1.1rem; text-shadow: 0 1px 3px rgba(0,0,0,0.2);">Explore comprehensive analytics and insights from your document collection with interactive visualizations.</p>
            <div class="card-features">
                <span class="feature-tag" style="color: white; background: var(--primary-500); font-weight: 700; font-size: 0.9rem; padding: 0.5rem 1rem; border-radius: 20px; text-shadow: 0 1px 2px rgba(0,0,0,0.3); box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);">Visualizations</span>
                <span class="feature-tag" style="color: white; background: var(--secondary-500); font-weight: 700; font-size: 0.9rem; padding: 0.5rem 1rem; border-radius: 20px; text-shadow: 0 1px 2px rgba(0,0,0,0.3); box-shadow: 0 2px 8px rgba(139, 92, 246, 0.3);">Trends</span>
                <span class="feature-tag" style="color: white; background: var(--success-500); font-weight: 700; font-size: 0.9rem; padding: 0.5rem 1rem; border-radius: 20px; text-shadow: 0 1px 2px rgba(0,0,0,0.3); box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);">Reports</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📊 View Analysis", key="analysis_btn", use_container_width=True):
            st.session_state.current_page = "📊 Analysis"
            st.rerun()
    
    # Features Section
    st.markdown("""
    <div class="features-section">
        <h2 class="section-title" style="color: #1e293b; font-weight: 800; font-size: 2.2rem; text-shadow: 0 2px 8px rgba(0,0,0,0.3), 0 4px 16px rgba(0,0,0,0.2); filter: drop-shadow(0 4px 8px rgba(0,0,0,0.4)); letter-spacing: -0.01em;">✨ Advanced Features</h2>
        <p class="section-subtitle" style="color: #475569; font-weight: 600; line-height: 1.6; font-size: 1.2rem; text-shadow: 0 1px 3px rgba(0,0,0,0.2); filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));">Discover the power of our AI-driven document analysis platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature Grid
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📄</div>
            <div class="feature-content">
                <h4 style="color: #1e293b; font-weight: 800; font-size: 1.3rem; text-shadow: 0 2px 6px rgba(0,0,0,0.3); filter: drop-shadow(0 3px 6px rgba(0,0,0,0.4));">Multi-Format Support</h4>
                <p style="color: #475569; line-height: 1.7; font-weight: 600; font-size: 1rem; text-shadow: 0 1px 3px rgba(0,0,0,0.2);">Handle PDFs, images, scanned documents, Word files, and more with intelligent format detection and processing.</p>
            </div>
        </div>
        
        <div class="feature-card">
            <div class="feature-icon">🤖</div>
            <div class="feature-content">
                <h4 style="color: #1e293b; font-weight: 800; font-size: 1.3rem; text-shadow: 0 2px 6px rgba(0,0,0,0.3); filter: drop-shadow(0 3px 6px rgba(0,0,0,0.4));">AI-Powered OCR</h4>
                <p style="color: #475569; line-height: 1.7; font-weight: 600; font-size: 1rem; text-shadow: 0 1px 3px rgba(0,0,0,0.2);">High-accuracy text extraction from any source using state-of-the-art optical character recognition technology.</p>
            </div>
        </div>
        
        <div class="feature-card">
            <div class="feature-icon">🔒</div>
            <div class="feature-content">
                <h4 style="color: #1e293b; font-weight: 800; font-size: 1.3rem; text-shadow: 0 2px 6px rgba(0,0,0,0.3); filter: drop-shadow(0 3px 6px rgba(0,0,0,0.4));">Enterprise Security</h4>
                <p style="color: #475569; line-height: 1.7; font-weight: 600; font-size: 1rem; text-shadow: 0 1px 3px rgba(0,0,0,0.2);">Bank-level security with encrypted storage, secure API endpoints, and compliance with industry standards.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <div class="feature-content">
                <h4 style="color: #1e293b; font-weight: 800; font-size: 1.3rem; text-shadow: 0 2px 6px rgba(0,0,0,0.3); filter: drop-shadow(0 3px 6px rgba(0,0,0,0.4));">Smart Extraction</h4>
                <p style="color: #475569; line-height: 1.7; font-weight: 600; font-size: 1rem; text-shadow: 0 1px 3px rgba(0,0,0,0.2);">Automatically detect and extract tables, charts, and structured data from complex documents with high precision.</p>
            </div>
        </div>
        
        <div class="feature-card">
            <div class="feature-icon">🔍</div>
            <div class="feature-content">
                <h4 style="color: #1e293b; font-weight: 800; font-size: 1.3rem; text-shadow: 0 2px 6px rgba(0,0,0,0.3); filter: drop-shadow(0 3px 6px rgba(0,0,0,0.4));">Intelligent Queries</h4>
                <p style="color: #475569; line-height: 1.7; font-weight: 600; font-size: 1rem; text-shadow: 0 1px 3px rgba(0,0,0,0.2);">Ask natural language questions and get instant answers with source citations and confidence scores.</p>
            </div>
        </div>
        
        <div class="feature-card">
            <div class="feature-icon">📈</div>
            <div class="feature-content">
                <h4 style="color: #1e293b; font-weight: 800; font-size: 1.3rem; text-shadow: 0 2px 6px rgba(0,0,0,0.3); filter: drop-shadow(0 3px 6px rgba(0,0,0,0.4));">Advanced Analytics</h4>
                <p style="color: #475569; line-height: 1.7; font-weight: 600; font-size: 1rem; text-shadow: 0 1px 3px rgba(0,0,0,0.2);">Comprehensive insights, trend analysis, and customizable reports for data-driven decision making.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Technology Stack Section
    st.markdown("""
    <div class="tech-stack-section">
        <h2 class="section-title" style="color: #1e293b; font-weight: 800; font-size: 2.2rem; text-shadow: 0 2px 8px rgba(0,0,0,0.3), 0 4px 16px rgba(0,0,0,0.2); filter: drop-shadow(0 4px 8px rgba(0,0,0,0.4)); letter-spacing: -0.01em;">🛠️ Built with Modern Technology</h2>
        <p class="section-subtitle" style="color: #475569; font-weight: 600; line-height: 1.6; font-size: 1.2rem; text-shadow: 0 1px 3px rgba(0,0,0,0.2); filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));">Powered by cutting-edge AI and machine learning technologies</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tech Stack Grid
    tech_cols = st.columns(4)
    
    with tech_cols[0]:
        st.markdown("""
        <div class="tech-item">
            <div class="tech-icon">🤖</div>
            <h5 style="color: #1e293b; font-weight: 800; font-size: 1.2rem; text-shadow: 0 2px 6px rgba(0,0,0,0.3); filter: drop-shadow(0 3px 6px rgba(0,0,0,0.4));">OpenAI GPT</h5>
            <p style="color: #475569; line-height: 1.7; font-weight: 600; font-size: 0.95rem; text-shadow: 0 1px 3px rgba(0,0,0,0.2);">Advanced language models for intelligent document understanding and natural language processing</p>
        </div>
        """, unsafe_allow_html=True)
    
    with tech_cols[1]:
        st.markdown("""
        <div class="tech-item">
            <div class="tech-icon">🔍</div>
            <h5 style="color: #1e293b; font-weight: 800; font-size: 1.2rem; text-shadow: 0 2px 6px rgba(0,0,0,0.3); filter: drop-shadow(0 3px 6px rgba(0,0,0,0.4));">ChromaDB</h5>
            <p style="color: #475569; line-height: 1.7; font-weight: 600; font-size: 0.95rem; text-shadow: 0 1px 3px rgba(0,0,0,0.2);">Vector database for semantic search and similarity matching with high performance</p>
        </div>
        """, unsafe_allow_html=True)
    
    with tech_cols[2]:
        st.markdown("""
        <div class="tech-item">
            <div class="tech-icon">📊</div>
            <h5 style="color: #1e293b; font-weight: 800; font-size: 1.2rem; text-shadow: 0 2px 6px rgba(0,0,0,0.3); filter: drop-shadow(0 3px 6px rgba(0,0,0,0.4));">PaddleOCR</h5>
            <p style="color: #475569; line-height: 1.7; font-weight: 600; font-size: 0.95rem; text-shadow: 0 1px 3px rgba(0,0,0,0.2);">High-performance OCR for text extraction from images and scanned documents</p>
        </div>
        """, unsafe_allow_html=True)
    
    with tech_cols[3]:
        st.markdown("""
        <div class="tech-item">
            <div class="tech-icon">⚡</div>
            <h5 style="color: #1e293b; font-weight: 800; font-size: 1.2rem; text-shadow: 0 2px 6px rgba(0,0,0,0.3); filter: drop-shadow(0 3px 6px rgba(0,0,0,0.4));">FastAPI</h5>
            <p style="color: #475569; line-height: 1.7; font-weight: 600; font-size: 0.95rem; text-shadow: 0 1px 3px rgba(0,0,0,0.2);">High-performance backend API for real-time processing and scalable architecture</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Call to Action Section
    st.markdown("""
    <div class="cta-section">
        <h2 class="cta-title" style="color: #1e293b; font-weight: 800; font-size: 2.2rem; text-shadow: 0 2px 8px rgba(0,0,0,0.3), 0 4px 16px rgba(0,0,0,0.2); filter: drop-shadow(0 4px 8px rgba(0,0,0,0.4)); letter-spacing: -0.01em;">Ready to Transform Your Documents?</h2>
        <p class="cta-subtitle" style="color: #475569; font-weight: 600; line-height: 1.6; font-size: 1.2rem; text-shadow: 0 1px 3px rgba(0,0,0,0.2); filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));">Join thousands of enterprise users who are already leveraging AI-powered document intelligence</p>
        <div class="cta-buttons">
            <button class="cta-primary" onclick="window.parent.postMessage({type: 'streamlit:setComponentValue', key: 'cta_get_started', value: true}, '*')">🚀 Get Started Now</button>
            <button class="cta-secondary" onclick="window.parent.postMessage({type: 'streamlit:setComponentValue', key: 'cta_docs', value: true}, '*')">📚 View Documentation</button>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # CTA Buttons (Streamlit fallback)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Get Started Now", key="cta_get_started", use_container_width=True):
            st.session_state.current_page = "📤 Upload"
            st.rerun()
    with col2:
        if st.button("📚 View Documentation", key="cta_docs", use_container_width=True):
            st.info("📚 Documentation will be available soon!")

def render_footer():
    """Render enterprise-level footer"""
    st.markdown("---")
    
    # Footer content
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        # Left side empty for balance
        pass
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <p style="color: #64748b; margin: 0; font-size: 0.875rem;">
                © 2024 DocumentAI Pro | Enterprise AI Solutions | Built with ❤️ for the Future of Work
            </p>
            <p style="color: #94a3b8; margin: 0.5rem 0 0 0; font-size: 0.75rem;">
                Session: {current_page} | Backend: {status}
            </p>
        </div>
        """.format(
            current_page=st.session_state.get('current_page', '🏠 Home'),
            status="🟢 Online" if check_backend_connection() else "🔴 Offline"
        ), unsafe_allow_html=True)
    
    with col3:
        # Session info
        pass

def ensure_home_page():
    """Ensure the application always has a valid home page setting"""
    valid_pages = ["🏠 Home", "📤 Upload", "📊 Analysis", "🔍 Query", "⚙️ Settings"]
    
    # Check if current_page exists and is valid
    if "current_page" not in st.session_state:
        st.session_state.current_page = "🏠 Home"
    elif st.session_state.current_page not in valid_pages:
        st.session_state.current_page = "🏠 Home"
    
    return st.session_state.current_page

def reset_to_home():
    """Reset the application to the home page"""
    st.session_state.current_page = "🏠 Home"
    st.rerun()

def main():
    """Main application function"""
    # Initialize session state
    if session_manager:
        session_manager.init_session_state()
    
    # Ensure we always start with home page
    current_page = ensure_home_page()
    
    # Load custom CSS
    load_custom_css()
    
    # Initialize and apply theme
    try:
        from utils.theme_manager import theme_manager
        theme_manager.apply_theme_styles()
        
        # Set data-theme attribute for CSS targeting
        theme_info = theme_manager.get_theme_info()
        effective_theme = theme_info['effective']
        
        # Apply theme to the page
        st.markdown(f"""
        <script>
        document.documentElement.setAttribute('data-theme', '{effective_theme}');
        </script>
        """, unsafe_allow_html=True)
        
    except ImportError:
        pass
    
    # Render header
    render_header()
    
    # Main content area - ensure we always start with home page
    current_page = st.session_state.get("current_page", "🏠 Home")
    
    # Force home page if current_page is not set or invalid
    if not current_page or current_page not in ["🏠 Home", "📤 Upload", "📊 Analysis", "🔍 Query", "⚙️ Settings"]:
        current_page = "🏠 Home"
        st.session_state.current_page = "🏠 Home"
    
    # Page routing with fallback to home page
    try:
        if current_page == "🏠 Home":
            render_home_page()
        elif current_page == "📤 Upload":
            # Import and render upload page
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location(
                    "upload_page", 
                    "pages/01_Upload.py"
                )
                upload_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(upload_module)
                upload_module.render_upload_page()
            except Exception as e:
                st.error(f"Error loading upload page: {e}")
                st.error(f"Error type: {type(e).__name__}")
                import traceback
                st.error(f"Traceback: {traceback.format_exc()}")
                if "ImportError" in str(type(e)) or "ModuleNotFoundError" in str(type(e)):
                    st.session_state.current_page = "🏠 Home"
                    st.rerun()
                else:
                    st.error("⚠️ Upload page encountered an error but will remain open. Please try again.")
        elif current_page == "📊 Analysis":
            # Import and render analysis page
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location(
                    "analysis_page", 
                    "pages/02_Analysis.py"
                )
                analysis_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(analysis_module)
                analysis_module.render_analysis_page()
            except Exception as e:
                st.error(f"Error loading analysis page: {e}")
                st.session_state.current_page = "🏠 Home"
                st.rerun()
        elif current_page == "🔍 Query":
            # Import and render query page
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location(
                    "query_page", 
                    "pages/03_Query.py"
                )
                query_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(query_module)
                query_module.render_query_page()
            except Exception as e:
                st.error(f"Error loading query page: {e}")
                st.session_state.current_page = "🏠 Home"
                st.rerun()
        elif current_page == "⚙️ Settings":
            # Import and render settings page
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location(
                    "settings_page", 
                    "pages/04_Settings.py"
                )
                settings_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(settings_module)
                settings_module.render_settings_page()
            except Exception as e:
                st.error(f"Error loading settings page: {e}")
                st.session_state.current_page = "🏠 Home"
                st.rerun()
        else:
            # Invalid page - fallback to home
            st.session_state.current_page = "🏠 Home"
            st.rerun()
    except Exception as e:
        # Global error handling - fallback to home page
        st.error(f"Application error: {e}")
        st.session_state.current_page = "🏠 Home"
        st.rerun()
    
    # Render footer
    render_footer()

if __name__ == "__main__":
    main()
