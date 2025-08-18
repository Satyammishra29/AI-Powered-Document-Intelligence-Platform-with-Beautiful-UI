"""
Test script for Theme Manager
Run this to verify the theme manager is working correctly
"""

import streamlit as st
from utils.theme_manager import theme_manager

def test_theme_manager():
    """Test the theme manager functionality"""
    st.title("🎨 Theme Manager Test")
    
    st.write("### Current Theme Info")
    theme_info = theme_manager.get_theme_info()
    st.json(theme_info)
    
    st.write("### Theme Selection")
    selected_theme = theme_manager.render_theme_selector()
    st.write(f"Selected theme: {selected_theme}")
    
    st.write("### Theme Preview")
    st.markdown(theme_manager.get_theme_preview(), unsafe_allow_html=True)
    
    st.write("### CSS Variables")
    st.code(theme_manager.get_css_variables(), language="css")
    
    st.write("### Test Theme Switching")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🌙 Dark Mode"):
            theme_manager.set_theme("dark")
            st.success("Switched to Dark Mode!")
            st.rerun()
    
    with col2:
        if st.button("☀️ Light Mode"):
            theme_manager.set_theme("light")
            st.success("Switched to Light Mode!")
            st.rerun()
    
    with col3:
        if st.button("🔄 Auto Mode"):
            theme_manager.set_theme("auto")
            st.success("Switched to Auto Mode!")
            st.rerun()

if __name__ == "__main__":
    test_theme_manager()
