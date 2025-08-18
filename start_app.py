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
        print("⚠️  .env file not found - creating default configuration")
        print("📝 You can customize settings by editing the .env file later")
        
        # Create basic .env with defaults
        try:
            with open(".env", "w") as f:
                f.write("# Default environment configuration\n")
                f.write("OPENAI_API_KEY=your_openai_api_key_here\n")
                f.write("HOST=0.0.0.0\n")
                f.write("PORT=8000\n")
                f.write("DEBUG=true\n")
            print("✅ Created default .env file")
        except Exception as e:
            print(f"⚠️  Could not create .env file: {e}")
            print("Continuing with default settings...")
    
    print("✅ Environment configuration ready!")
    return True

def start_backend():
    """Start the simplified FastAPI backend server"""
    print("\n🚀 Starting simplified backend server...")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return None
    
    try:
        # Change to backend directory
        os.chdir(backend_dir)
        
        # Start backend server with better error handling
        print(f"📍 Starting backend from: {os.getcwd()}")
        
        backend_process = subprocess.Popen(
            [sys.executable, "main.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for server to start and check for errors
        time.sleep(5)
        
        if backend_process.poll() is None:
            print("✅ Simplified backend server started successfully on http://localhost:8000")
            print("⚠️  Note: This backend has limited functionality (no AI/ML features)")
            return backend_process
        else:
            # Get error output
            stdout, stderr = backend_process.communicate()
            print(f"❌ Backend failed to start")
            if stderr:
                print(f"Error details: {stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return None
    finally:
        # Change back to original directory
        os.chdir("..")

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