"""
Simple test app for Vercel deployment
"""

import streamlit as st

def main():
    st.title("🚀 RAG Application Test")
    st.write("This is a test deployment to verify Vercel configuration.")
    st.success("✅ Deployment successful!")
    
    st.markdown("""
    ## Features:
    - ✅ Streamlit working
    - ✅ Vercel deployment
    - ✅ Python environment
    """)

if __name__ == "__main__":
    main()
