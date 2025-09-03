#!/usr/bin/env python3
"""
Deployment script for RAG Application
Helps prepare the application for Vercel deployment
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_requirements():
    """Check if all required files exist"""
    required_files = [
        "vercel.json",
        "requirements.txt",
        "frontend/main_app.py",
        "frontend/requirements.txt"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ All required files present")
    return True

def check_dependencies():
    """Check if requirements.txt is valid"""
    try:
        with open("requirements.txt", "r") as f:
            requirements = f.read()
        
        if not requirements.strip():
            print("❌ requirements.txt is empty")
            return False
        
        print("✅ requirements.txt is valid")
        return True
    except Exception as e:
        print(f"❌ Error reading requirements.txt: {e}")
        return False

def create_env_template():
    """Create .env.template file"""
    env_template = """# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Backend Configuration (if using external backend)
BACKEND_URL=https://your-backend-url.vercel.app

# Streamlit Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Optional: Database Configuration
DATABASE_URL=your_database_url_here
"""
    
    with open(".env.template", "w") as f:
        f.write(env_template)
    
    print("✅ Created .env.template file")

def check_git_status():
    """Check git status"""
    try:
        result = subprocess.run(["git", "status", "--porcelain"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            if result.stdout.strip():
                print("⚠️  Uncommitted changes detected:")
                print(result.stdout)
                return False
            else:
                print("✅ Git repository is clean")
                return True
        else:
            print("⚠️  Not a git repository or git not available")
            return False
    except FileNotFoundError:
        print("⚠️  Git not found. Please ensure git is installed.")
        return False

def main():
    """Main deployment preparation function"""
    print("🚀 RAG Application Deployment Preparation")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Deployment preparation failed: Missing required files")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Deployment preparation failed: Invalid requirements.txt")
        sys.exit(1)
    
    # Create env template
    create_env_template()
    
    # Check git status
    git_clean = check_git_status()
    
    print("\n" + "=" * 50)
    print("📋 Deployment Checklist:")
    print("✅ Required files present")
    print("✅ Dependencies configured")
    print("✅ Environment template created")
    
    if git_clean:
        print("✅ Git repository clean")
    else:
        print("⚠️  Git repository has uncommitted changes")
    
    print("\n🎯 Next Steps:")
    print("1. Set up your environment variables in Vercel")
    print("2. Push your code to GitHub")
    print("3. Connect your repository to Vercel")
    print("4. Deploy!")
    
    print("\n📖 For detailed instructions, see DEPLOYMENT_GUIDE.md")
    
    if not git_clean:
        print("\n⚠️  Remember to commit your changes before deploying!")

if __name__ == "__main__":
    main()
