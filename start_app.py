#!/usr/bin/env python3
"""
Startup script for Simplified Document Analysis RAG System
This script helps you start both the backend and frontend components
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        "fastapi", "uvicorn", "streamlit", "chromadb", "PIL"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Please install them using: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed!")
    return True

def check_environment():
    """Check environment configuration"""
    print("\n🔧 Checking environment configuration...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found")
        print("Please copy env_example.txt to .env and configure your settings")
        return False
    
    print("✅ Environment configuration looks good!")
    return True

def start_backend():
    """Start the simplified FastAPI backend server"""
    print("\n🚀 Starting simplified backend server...")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return None
    
    try:
        # Start backend server
        backend_process = subprocess.Popen(
            [sys.executable, "main.py"],
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait a bit for server to start
        time.sleep(3)
        
        if backend_process.poll() is None:
            print("✅ Simplified backend server started successfully on http://localhost:8000")
            print("⚠️  Note: This backend has limited functionality (no AI/ML features)")
            return backend_process
        else:
            print("❌ Failed to start backend server")
            return None
            
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return None

def start_frontend():
    """Start the Streamlit frontend"""
    print("\n🎨 Starting frontend...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return None
    
    try:
        # Start Streamlit
        frontend_process = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", "main_app.py", "--server.port", "8501"],
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait a bit for server to start
        time.sleep(5)
        
        if frontend_process.poll() is None:
            print("✅ Frontend started successfully on http://localhost:8501")
            return frontend_process
        else:
            print("❌ Failed to start frontend")
            return None
            
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")
        return None

def open_browsers():
    """Open web browsers to the application"""
    print("\n🌐 Opening web browsers...")
    
    try:
        # Open backend API docs
        webbrowser.open("http://localhost:8000/docs")
        print("✅ Opened backend API documentation")
        
        # Open frontend
        webbrowser.open("http://localhost:8501")
        print("✅ Opened frontend application")
        
    except Exception as e:
        print(f"⚠️  Could not open browsers automatically: {e}")
        print("Please manually open:")
        print("  - Backend API: http://localhost:8000/docs")
        print("  - Frontend: http://localhost:8501")

def main():
    """Main startup function"""
    print("🚀 Visual Document Analysis RAG System - Startup Script")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check environment
    if not check_environment():
        print("\n⚠️  Please fix environment configuration and try again")
        sys.exit(1)
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        print("\n❌ Failed to start backend. Exiting.")
        sys.exit(1)
    
    # Start frontend
    frontend_process = start_frontend()
    if not frontend_process:
        print("\n❌ Failed to start frontend. Exiting.")
        backend_process.terminate()
        sys.exit(1)
    
    # Open browsers
    open_browsers()
    
    print("\n🎉 Application started successfully!")
    print("\n📱 Access your application:")
    print("  - Frontend: http://localhost:8501")
    print("  - Backend API: http://localhost:8000")
    print("  - API Docs: http://localhost:8000/docs")
    
    print("\n⏹️  Press Ctrl+C to stop all services")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if backend_process.poll() is not None:
                print("\n❌ Backend server stopped unexpectedly")
                break
                
            if frontend_process.poll() is not None:
                print("\n❌ Frontend stopped unexpectedly")
                break
                
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down services...")
        
        # Terminate processes
        if backend_process:
            backend_process.terminate()
            print("✅ Backend server stopped")
        
        if frontend_process:
            frontend_process.terminate()
            print("✅ Frontend stopped")
        
        print("👋 Goodbye!")

if __name__ == "__main__":
    main() 