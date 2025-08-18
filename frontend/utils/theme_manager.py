"""
Theme Manager for DocumentAI Pro
Enterprise-level theme switching with persistent state and smooth transitions
"""

import streamlit as st
from typing import Dict, Any, Optional
import json
from datetime import datetime

class ThemeManager:
    """Enterprise theme manager with advanced features"""
    
    def __init__(self):
        self.themes = {
            "light": {
                "name": "Light Mode",
                "icon": "☀️",
                "description": "Clean, professional light theme",
                "colors": {
                    "bg_primary": "#ffffff",
                    "bg_secondary": "#f8fafc",
                    "bg_tertiary": "#f1f5f9",
                    "bg_card": "#ffffff",
                    "bg_overlay": "rgba(255, 255, 255, 0.95)",
                    "text_primary": "#0f172a",
                    "text_secondary": "#475569",
                    "text_muted": "#64748b",
                    "text_accent": "#3b82f6",
                    "border_light": "#e2e8f0",
                    "border_medium": "#cbd5e1",
                    "border_dark": "#94a3b8",
                    "primary_500": "#3b82f6",
                    "primary_600": "#2563eb",
                    "primary_700": "#1d4ed8",
                    "secondary_500": "#8b5cf6",
                    "success_500": "#10b981",
                    "warning_500": "#f59e0b",
                    "error_500": "#ef4444",
                    "shadow_sm": "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
                    "shadow_md": "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
                    "shadow_lg": "0 10px 15px -3px rgba(0, 0, 0, 0.1)",
                    "shadow_xl": "0 20px 25px -5px rgba(0, 0, 0, 0.1)",
                    "glass_bg": "rgba(255, 255, 255, 0.1)",
                    "glass_border": "rgba(255, 255, 255, 0.2)",
                    "glass_shadow": "0 8px 32px rgba(0, 0, 0, 0.1)"
                }
            },
            "dark": {
                "name": "Dark Mode",
                "icon": "🌙",
                "description": "Sophisticated dark theme for professionals",
                "colors": {
                    "bg_primary": "#0f172a",
                    "bg_secondary": "#1e293b",
                    "bg_tertiary": "#334155",
                    "bg_card": "#1e293b",
                    "bg_overlay": "rgba(15, 23, 42, 0.95)",
                    "text_primary": "#f8fafc",
                    "text_secondary": "#cbd5e1",
                    "text_muted": "#94a3b8",
                    "text_accent": "#60a5fa",
                    "border_light": "#334155",
                    "border_medium": "#475569",
                    "border_dark": "#64748b",
                    "primary_500": "#60a5fa",
                    "primary_600": "#3b82f6",
                    "primary_700": "#2563eb",
                    "secondary_500": "#a78bfa",
                    "success_500": "#34d399",
                    "warning_500": "#fbbf24",
                    "error_500": "#f87171",
                    "shadow_sm": "0 1px 2px 0 rgba(0, 0, 0, 0.3)",
                    "shadow_md": "0 4px 6px -1px rgba(0, 0, 0, 0.4)",
                    "shadow_lg": "0 10px 15px -3px rgba(0, 0, 0, 0.5)",
                    "shadow_xl": "0 20px 25px -5px rgba(0, 0, 0, 0.6)",
                    "glass_bg": "rgba(15, 23, 42, 0.8)",
                    "glass_border": "rgba(148, 163, 184, 0.2)",
                    "glass_shadow": "0 8px 32px rgba(0, 0, 0, 0.5)"
                }
            },
            "auto": {
                "name": "Auto Theme",
                "icon": "🔄",
                "description": "Follows system preference",
                "colors": None  # Will be determined dynamically
            }
        }
        
        self.current_theme = self.get_current_theme()
        self.system_preference = self.detect_system_theme()
    
    def get_current_theme(self) -> str:
        """Get current theme from session state or default"""
        if 'current_theme' not in st.session_state:
            st.session_state.current_theme = "dark"  # Default to dark
        return st.session_state.current_theme
    
    def set_theme(self, theme: str) -> None:
        """Set theme and update session state"""
        if theme in self.themes:
            st.session_state.current_theme = theme
            st.session_state.theme_changed = True
            st.session_state.theme_change_time = datetime.now().isoformat()
    
    def get_effective_theme(self) -> str:
        """Get the effective theme (handles auto mode)"""
        current = self.get_current_theme()
        if current == "auto":
            return self.system_preference
        return current
    
    def get_theme_colors(self) -> Dict[str, str]:
        """Get colors for current theme"""
        effective_theme = self.get_effective_theme()
        return self.themes[effective_theme]["colors"]
    
    def detect_system_theme(self) -> str:
        """Detect system theme preference (simplified)"""
        # In a real implementation, you might use JavaScript to detect this
        # For now, we'll default to dark mode
        return "dark"
    
    def get_theme_info(self) -> Dict[str, Any]:
        """Get comprehensive theme information"""
        current = self.get_current_theme()
        effective = self.get_effective_theme()
        
        return {
            "current": current,
            "effective": effective,
            "is_dark": effective == "dark",
            "is_light": effective == "light",
            "is_auto": current == "auto",
            "colors": self.get_theme_colors(),
            "theme_data": self.themes[current],
            "last_changed": st.session_state.get('theme_change_time'),
            "system_preference": self.system_preference
        }
    
    def render_theme_selector(self) -> str:
        """Render theme selector component"""
        st.markdown("### 🌈 Theme Selection")
        
        # Theme options with descriptions
        theme_options = []
        for key, theme in self.themes.items():
            theme_options.append(f"{theme['icon']} {theme['name']}")
        
        current_index = list(self.themes.keys()).index(self.get_current_theme())
        
        selected_theme = st.selectbox(
            "Choose your preferred theme:",
            options=theme_options,
            index=current_index,
            help="Select the visual theme for your application"
        )
        
        # Extract theme key from selection
        selected_key = selected_theme.split(" ", 1)[1].lower().replace(" mode", "").replace(" theme", "")
        if selected_key == "auto":
            selected_key = "auto"
        
        # Update theme if changed
        if selected_key != self.get_current_theme():
            self.set_theme(selected_key)
            st.success(f"🎉 Theme updated to {self.themes[selected_key]['name']}!")
            st.rerun()
        
        return selected_key
    
    def get_css_variables(self) -> str:
        """Generate CSS variables for current theme"""
        colors = self.get_theme_colors()
        
        css_vars = []
        for key, value in colors.items():
            css_vars.append(f"    --{key}: {value};")
        
        return "\n".join(css_vars)
    
    def apply_theme_styles(self) -> None:
        """Apply theme-specific styles to the application"""
        theme_info = self.get_theme_info()
        
        # Generate CSS for current theme
        css = f"""
        <style>
        :root {{
        {self.get_css_variables()}
        }}
        
        /* Theme-specific overrides */
        .stApp {{
            background-color: var(--bg_primary) !important;
            color: var(--text_primary) !important;
        }}
        
        .main .block-container {{
            background-color: var(--bg_primary) !important;
        }}
        
        /* Enhanced dark mode specific styles */
        {self._get_dark_mode_enhancements() if theme_info['is_dark'] else ''}
        
        /* Enhanced light mode specific styles */
        {self._get_light_mode_enhancements() if theme_info['is_light'] else ''}
        
        /* Smooth theme transitions */
        * {{
            transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
        }}
        </style>
        """
        
        st.markdown(css, unsafe_allow_html=True)
    
    def _get_dark_mode_enhancements(self) -> str:
        """Get enhanced styles for dark mode"""
        return """
        /* Dark Mode Enhancements */
        .stButton > button {
            background: rgba(59, 130, 246, 0.1) !important;
            border: 1px solid rgba(59, 130, 246, 0.3) !important;
            color: #60a5fa !important;
        }
        
        .stButton > button:hover {
            background: rgba(59, 130, 246, 0.2) !important;
            border-color: rgba(59, 130, 246, 0.5) !important;
            box-shadow: 0 0 20px rgba(59, 130, 246, 0.3) !important;
        }
        
        .stTextInput > div > div > input {
            background: rgba(30, 41, 59, 0.8) !important;
            border: 1px solid rgba(71, 85, 105, 0.5) !important;
            color: #f8fafc !important;
        }
        
        .stSelectbox > div > div > div {
            background: rgba(30, 41, 59, 0.8) !important;
            border: 1px solid rgba(71, 85, 105, 0.5) !important;
        }
        
        .stMetric {
            background: rgba(30, 41, 59, 0.8) !important;
            border: 1px solid rgba(71, 85, 105, 0.3) !important;
        }
        
        /* Enhanced glassmorphism for dark mode */
        .glass {
            background: rgba(15, 23, 42, 0.8) !important;
            border: 1px solid rgba(148, 163, 184, 0.2) !important;
            backdrop-filter: blur(20px) !important;
        }
        
        /* Dark mode shadows */
        .shadow-enhanced {
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.6) !important;
        }
        """
    
    def _get_light_mode_enhancements(self) -> str:
        """Get enhanced styles for light mode"""
        return """
        /* Light Mode Enhancements */
        .stButton > button {
            background: rgba(59, 130, 246, 0.1) !important;
            border: 1px solid rgba(59, 130, 246, 0.3) !important;
            color: #1d4ed8 !important;
        }
        
        .stButton > button:hover {
            background: rgba(59, 130, 246, 0.2) !important;
            border-color: rgba(59, 130, 246, 0.5) !important;
            box-shadow: 0 0 20px rgba(59, 130, 246, 0.2) !important;
        }
        
        .stTextInput > div > div > input {
            background: rgba(255, 255, 255, 0.9) !important;
            border: 1px solid rgba(203, 213, 225, 0.5) !important;
            color: #0f172a !important;
        }
        
        .stSelectbox > div > div > div {
            background: rgba(255, 255, 255, 0.9) !important;
            border: 1px solid rgba(203, 213, 225, 0.5) !important;
        }
        
        .stMetric {
            background: rgba(255, 255, 255, 0.9) !important;
            border: 1px solid rgba(226, 232, 240, 0.5) !important;
        }
        
        /* Enhanced glassmorphism for light mode */
        .glass {
            background: rgba(255, 255, 255, 0.1) !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            backdrop-filter: blur(20px) !important;
        }
        
        /* Light mode shadows */
        .shadow-enhanced {
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.15) !important;
        }
        """
    
    def get_theme_preview(self) -> str:
        """Get theme preview HTML"""
        theme_info = self.get_theme_info()
        colors = theme_info['colors']
        
        return f"""
        <div style="
            background: {colors['bg_card']};
            border: 1px solid {colors['border_light']};
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
            color: {colors['text_primary']};
        ">
            <h4 style="color: {colors['text_primary']}; margin-bottom: 1rem;">
                {theme_info['theme_data']['icon']} {theme_info['theme_data']['name']}
            </h4>
            <p style="color: {colors['text_secondary']}; margin-bottom: 1rem;">
                {theme_info['theme_data']['description']}
            </p>
            <div style="
                display: flex;
                gap: 0.5rem;
                flex-wrap: wrap;
            ">
                <div style="
                    width: 20px;
                    height: 20px;
                    background: {colors['primary_500']};
                    border-radius: 4px;
                    border: 1px solid {colors['border_light']};
                "></div>
                <div style="
                    width: 20px;
                    height: 20px;
                    background: {colors['secondary_500']};
                    border-radius: 4px;
                    border: 1px solid {colors['border_light']};
                "></div>
                <div style="
                    width: 20px;
                    height: 20px;
                    background: {colors['success_500']};
                    border-radius: 4px;
                    border: 1px solid {colors['border_light']};
                "></div>
                <div style="
                    width: 20px;
                    height: 20px;
                    background: {colors['warning_500']};
                    border-radius: 4px;
                    border: 1px solid {colors['border_light']};
                "></div>
                <div style="
                    width: 20px;
                    height: 20px;
                    background: {colors['error_500']};
                    border-radius: 4px;
                    border: 1px solid {colors['border_light']};
                "></div>
            </div>
        </div>
        """

# Global theme manager instance
theme_manager = ThemeManager()
