# 🚀 DocumentAI Pro - Deployment Guide

## 📋 **Table of Contents**
1. [GitHub Setup](#github-setup)
2. [Local Git Configuration](#local-git-configuration)
3. [Deployment Options](#deployment-options)
4. [Streamlit Cloud Deployment](#streamlit-cloud-deployment)
5. [Heroku Deployment](#heroku-deployment)
6. [Docker Deployment](#docker-deployment)
7. [Troubleshooting](#troubleshooting)

---

## 🐙 **GitHub Setup**

### **Step 1: Create GitHub Repository**
1. Go to [GitHub.com](https://github.com) and sign in
2. Click the **"+"** icon → **"New repository"**
3. Fill in repository details:
   - **Name**: `DocumentAI-Pro`
   - **Description**: `Enterprise AI-powered document intelligence platform with RAG capabilities`
   - **Visibility**: Public or Private
   - **Initialize with**: README, .gitignore (Python), License (MIT)

### **Step 2: Clone Repository**
```bash
git clone https://github.com/YOUR_USERNAME/DocumentAI-Pro.git
cd DocumentAI-Pro
```

---

## ⚙️ **Local Git Configuration**

### **Step 1: Initialize Git (if not already done)**
```bash
git init
git remote add origin https://github.com/YOUR_USERNAME/DocumentAI-Pro.git
```

### **Step 2: Add Files to Git**
```bash
# Add all files
git add .

# Or add specific directories
git add frontend/
git add backend/
git add requirements.txt
git add README.md
git add .gitignore
git add SETUP_GUIDE.md
git add start_app.py
```

### **Step 3: Make First Commit**
```bash
git commit -m "🚀 Initial commit: DocumentAI Pro - Enterprise Document Intelligence Platform"
```

### **Step 4: Push to GitHub**
```bash
git branch -M main
git push -u origin main
```

---

## 🌐 **Deployment Options**

### **Option 1: Streamlit Cloud (Recommended for Demo)**
- **Free tier available**
- **Easy deployment**
- **Automatic updates from GitHub**
- **Perfect for showcasing**

### **Option 2: Heroku**
- **Free tier available**
- **Good for production**
- **Easy scaling**

### **Option 3: Docker + Cloud Platforms**
- **Maximum flexibility**
- **Professional deployment**
- **Cost-effective for production**

---

## ☁️ **Streamlit Cloud Deployment**

### **Step 1: Prepare for Streamlit Cloud**
1. **Ensure your app has a main entry point**
   - Your `start_app.py` should work as the main entry
   - Or rename `frontend/main_app.py` to `main.py`

2. **Create a requirements.txt in the root directory**
   ```bash
   # Make sure requirements.txt is in the root
   cp frontend/requirements.txt ./requirements.txt
   ```

3. **Create a .streamlit/config.toml file**
   ```bash
   mkdir -p .streamlit
   ```

### **Step 2: Create Streamlit Configuration**
Create `.streamlit/config.toml`:
```toml
[server]
headless = true
port = $PORT
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#3b82f6"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f8fafc"
textColor = "#0f172a"
```

### **Step 3: Deploy to Streamlit Cloud**
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. **Sign in with GitHub**
3. **Click "New app"**
4. **Select your repository**: `YOUR_USERNAME/DocumentAI-Pro`
5. **Set the path to your app**: `frontend/main_app.py`
6. **Click "Deploy!"**

---

## 🐳 **Docker Deployment**

### **Step 1: Create Dockerfile**
Create `Dockerfile` in the root directory:
```dockerfile
# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8501

# Set environment variables
ENV PYTHONPATH=/app
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_HEADLESS=true

# Run the application
CMD ["streamlit", "run", "frontend/main_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### **Step 2: Create Docker Compose**
Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  documentai-pro:
    build: .
    ports:
      - "8501:8501"
    environment:
      - STREAMLIT_SERVER_PORT=8501
      - STREAMLIT_SERVER_HEADLESS=true
    volumes:
      - ./uploads:/app/uploads
      - ./chroma_db:/app/frontend/chroma_db
    restart: unless-stopped

  # Optional: Add backend service
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
    restart: unless-stopped
```

### **Step 3: Build and Run**
```bash
# Build the image
docker build -t documentai-pro .

# Run with Docker Compose
docker-compose up -d

# Or run directly
docker run -p 8501:8501 documentai-pro
```

---

## 🚀 **Heroku Deployment**

### **Step 1: Install Heroku CLI**
```bash
# macOS
brew install heroku/brew/heroku

# Windows
# Download from: https://devcenter.heroku.com/articles/heroku-cli

# Linux
curl https://cli-assets.heroku.com/install.sh | sh
```

### **Step 2: Create Heroku App**
```bash
heroku login
heroku create your-documentai-pro-app
```

### **Step 3: Create Procfile**
Create `Procfile` in the root directory:
```
web: streamlit run frontend/main_app.py --server.port=$PORT --server.address=0.0.0.0
```

### **Step 4: Deploy**
```bash
git add .
git commit -m "🚀 Deploy to Heroku"
git push heroku main
```

---

## 🔧 **Environment Configuration**

### **Create .env file for local development**
```bash
# .env (don't commit this file)
OPENAI_API_KEY=your_openai_api_key_here
CHROMA_DB_PATH=./frontend/chroma_db
ENVIRONMENT=development
DEBUG=true
```

### **Set environment variables in deployment platforms**
```bash
# Streamlit Cloud
# Go to app settings → Secrets and add your environment variables

# Heroku
heroku config:set OPENAI_API_KEY=your_key_here

# Docker
docker run -e OPENAI_API_KEY=your_key_here documentai-pro
```

---

## 📱 **Mobile and Responsive Considerations**

### **Update CSS for mobile**
Ensure your CSS includes mobile-friendly styles:
```css
@media (max-width: 768px) {
    .hero-title-enhanced {
        font-size: 2rem !important;
    }
    
    .hero-stats {
        grid-template-columns: 1fr 1fr !important;
    }
}
```

---

## 🚨 **Troubleshooting**

### **Common Issues and Solutions**

#### **1. Import Errors**
```bash
# Ensure all dependencies are in requirements.txt
pip freeze > requirements.txt
```

#### **2. Port Issues**
```bash
# Check if port is already in use
lsof -i :8501
# Kill process if needed
kill -9 <PID>
```

#### **3. Environment Variables**
```bash
# Check environment variables
echo $OPENAI_API_KEY
# Set if missing
export OPENAI_API_KEY=your_key_here
```

#### **4. Git Issues**
```bash
# Reset git if needed
git reset --hard HEAD
git clean -fd
git pull origin main
```

---

## 📊 **Monitoring and Analytics**

### **Add Streamlit Analytics**
```python
# In your main app
import streamlit as st

# Enable analytics
st.set_page_config(
    page_title="DocumentAI Pro",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Add custom analytics
if st.button("Track Usage"):
    # Your analytics code here
    pass
```

---

## 🔒 **Security Considerations**

### **Production Security Checklist**
- [ ] **API Keys**: Never commit API keys to Git
- [ ] **Environment Variables**: Use platform-specific secret management
- [ ] **HTTPS**: Ensure all deployments use HTTPS
- [ ] **Rate Limiting**: Implement API rate limiting
- [ ] **Input Validation**: Validate all user inputs
- [ ] **File Upload Limits**: Set reasonable file size limits

---

## 📈 **Performance Optimization**

### **Streamlit Performance Tips**
```python
# Use caching for expensive operations
@st.cache_data
def expensive_function():
    # Your expensive computation here
    pass

# Use st.empty() for dynamic content
placeholder = st.empty()
with placeholder.container():
    # Your dynamic content here
    pass
```

---

## 🎯 **Next Steps After Deployment**

1. **Test the deployed application**
2. **Set up monitoring and analytics**
3. **Configure custom domain (optional)**
4. **Set up CI/CD pipeline**
5. **Monitor performance and usage**
6. **Gather user feedback**

---

## 📞 **Support and Resources**

- **Streamlit Documentation**: [docs.streamlit.io](https://docs.streamlit.io)
- **GitHub Help**: [help.github.com](https://help.github.com)
- **Heroku Dev Center**: [devcenter.heroku.com](https://devcenter.heroku.com)
- **Docker Documentation**: [docs.docker.com](https://docs.docker.com)

---

**🚀 Happy Deploying! Your DocumentAI Pro application is ready to go live!**

*For additional support, please refer to the main README.md or create an issue in the GitHub repository.*
