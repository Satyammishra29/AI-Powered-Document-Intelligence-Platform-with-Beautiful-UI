"""
Configuration settings for the Visual Document Analysis RAG System
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class AppConfig:
    """Application configuration settings"""
    
    # App Information
    APP_NAME: str = "Visual Document Analysis RAG System"
    APP_VERSION: str = "2.0.0"
    APP_DESCRIPTION: str = "Enterprise-grade document analysis with AI-powered insights"
    
    # Backend Configuration
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000")
    API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "30"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    
    # File Processing
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "52428800"))  # 50MB
    SUPPORTED_FORMATS: list = None
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    
    # Performance Settings
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour
    MAX_CONCURRENT_UPLOADS: int = int(os.getenv("MAX_CONCURRENT_UPLOADS", "5"))
    BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", "10"))
    
    # UI Settings
    THEME: str = os.getenv("THEME", "dark")
    ANIMATIONS_ENABLED: bool = os.getenv("ANIMATIONS_ENABLED", "true").lower() == "true"
    # Sidebar removed - navigation now in header
    
    # Security
    ENABLE_LOGGING: bool = os.getenv("ENABLE_LOGGING", "true").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    def __post_init__(self):
        if self.SUPPORTED_FORMATS is None:
            self.SUPPORTED_FORMATS = [".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".docx", ".txt"]

@dataclass
class ThemeConfig:
    """Theme configuration for the application"""
    
    # Color Palette
    PRIMARY_COLOR: str = "#8B5CF6"  # Purple
    SECONDARY_COLOR: str = "#3B82F6"  # Blue
    ACCENT_COLOR: str = "#10B981"  # Green
    WARNING_COLOR: str = "#F59E0B"  # Amber
    ERROR_COLOR: str = "#EF4444"  # Red
    
    # Dark Theme Colors
    DARK_BG_PRIMARY: str = "#0F172A"
    DARK_BG_SECONDARY: str = "#1E293B"
    DARK_BG_CARD: str = "#334155"
    DARK_TEXT_PRIMARY: str = "#F8FAFC"
    DARK_TEXT_SECONDARY: str = "#CBD5E1"
    DARK_BORDER: str = "#475569"
    
    # Light Theme Colors
    LIGHT_BG_PRIMARY: str = "#FFFFFF"
    LIGHT_BG_SECONDARY: str = "#F8FAFC"
    LIGHT_BG_CARD: str = "#FFFFFF"
    LIGHT_TEXT_PRIMARY: str = "#0F172A"
    LIGHT_TEXT_SECONDARY: str = "#475569"
    LIGHT_BORDER: str = "#E2E8F0"
    
    # Gradients
    GRADIENT_PRIMARY: str = "linear-gradient(135deg, #8B5CF6 0%, #3B82F6 100%)"
    GRADIENT_SECONDARY: str = "linear-gradient(135deg, #10B981 0%, #3B82F6 100%)"
    GRADIENT_ACCENT: str = "linear-gradient(135deg, #F59E0B 0%, #EF4444 100%)"
    
    # Shadows
    SHADOW_SM: str = "0 1px 2px 0 rgba(0, 0, 0, 0.05)"
    SHADOW_MD: str = "0 4px 6px -1px rgba(0, 0, 0, 0.1)"
    SHADOW_LG: str = "0 10px 15px -3px rgba(0, 0, 0, 0.1)"
    SHADOW_XL: str = "0 20px 25px -5px rgba(0, 0, 0, 0.1)"
    
    # Border Radius
    RADIUS_SM: str = "0.375rem"
    RADIUS_MD: str = "0.5rem"
    RADIUS_LG: str = "0.75rem"
    RADIUS_XL: str = "1rem"
    
    # Transitions
    TRANSITION_FAST: str = "0.15s ease"
    TRANSITION_NORMAL: str = "0.3s ease"
    TRANSITION_SLOW: str = "0.5s ease"

@dataclass
class UIConfig:
    """UI-specific configuration"""
    
    # Layout
    MAX_WIDTH: str = "1200px"
    # Sidebar width removed - full width layout
    HEADER_HEIGHT: str = "64px"
    
    # Spacing (8px grid system)
    SPACING_XS: str = "0.5rem"    # 8px
    SPACING_SM: str = "1rem"      # 16px
    SPACING_MD: str = "1.5rem"    # 24px
    SPACING_LG: str = "2rem"      # 32px
    SPACING_XL: str = "3rem"      # 48px
    
    # Typography
    FONT_FAMILY_PRIMARY: str = "'Inter', -apple-system, BlinkMacSystemFont, sans-serif"
    FONT_FAMILY_DISPLAY: str = "'Poppins', -apple-system, BlinkMacSystemFont, sans-serif"
    
    # Font Sizes
    FONT_SIZE_XS: str = "0.75rem"   # 12px
    FONT_SIZE_SM: str = "0.875rem"  # 14px
    FONT_SIZE_MD: str = "1rem"      # 16px
    FONT_SIZE_LG: str = "1.125rem"  # 18px
    FONT_SIZE_XL: str = "1.25rem"   # 20px
    FONT_SIZE_2XL: str = "1.5rem"   # 24px
    FONT_SIZE_3XL: str = "2rem"     # 32px

# Global configuration instances
app_config = AppConfig()
theme_config = ThemeConfig()
ui_config = UIConfig()

def get_config() -> Dict[str, Any]:
    """Get all configuration as a dictionary"""
    return {
        "app": app_config.__dict__,
        "theme": theme_config.__dict__,
        "ui": ui_config.__dict__
    }

def update_theme(theme: str):
    """Update the current theme"""
    app_config.THEME = theme

def is_dark_theme() -> bool:
    """Check if dark theme is enabled"""
    return app_config.THEME.lower() == "dark"
