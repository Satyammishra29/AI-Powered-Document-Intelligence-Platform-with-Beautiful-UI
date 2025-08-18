# 🚀 Visual Document Analysis RAG System - Setup Guide

This guide will walk you through setting up and running the Visual Document Analysis RAG system step by step.

## 📋 Prerequisites

Before you begin, ensure you have:

- **Python 3.8+** installed on your system
- **Git** for cloning the repository
- **At least 4GB RAM** available
- **Internet connection** for downloading models and dependencies

## 🛠️ Installation Steps

### Step 1: Clone the Repository

```bash
git clone <your-repository-url>
cd RAG-APPLICATION
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Install PaddleOCR (for OCR functionality)
pip install paddlepaddle paddleocr
```

### Step 4: Download Required Models

```bash
# Download PaddleOCR models
python -c "from paddleocr import PaddleOCR; PaddleOCR(use_angle_cls=True, lang='en')"

# Download sentence transformer model
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

### Step 5: Configure Environment

```bash
# Copy environment template
cp env_example.txt .env

# Edit .env file with your settings
# Most importantly, add your OpenAI API key:
# OPENAI_API_KEY=your_actual_api_key_here
```

**Required Configuration:**
- `OPENAI_API_KEY`: Your OpenAI API key (get one from [OpenAI Platform](https://platform.openai.com/))
- Other settings can use defaults for now

## 🚀 Running the Application

### Option 1: Automated Startup (Recommended)

```bash
# Run the startup script
python start_app.py
```

This script will:
- Check dependencies
- Validate configuration
- Start backend server
- Start frontend
- Open browsers automatically

### Option 2: Manual Startup

#### Start Backend Server

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Start Frontend (in new terminal)

```bash
cd frontend
streamlit run app.py
```

## 🌐 Accessing the Application

Once running, you can access:

- **Frontend Application**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📱 Using the Application

### 1. Upload Documents

1. Go to the **Upload Documents** page
2. Drag and drop your files (PDF, PNG, JPG, etc.)
3. Click **Process Documents**
4. Wait for processing to complete

### 2. Query Documents

1. Go to the **Query Documents** page
2. Enter your question in natural language
3. Click **Search Documents**
4. View the AI-generated answer and relevant chunks

### 3. Analyze Results

1. Go to the **Document Analysis** page
2. View statistics about processed documents
3. Explore chunk distributions and metadata

## 🔧 Troubleshooting

### Common Issues

#### 1. Import Errors

```bash
# Ensure virtual environment is activated
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### 2. PaddleOCR Issues

```bash
# Reinstall PaddleOCR
pip uninstall paddleocr paddlepaddle
pip install paddlepaddle paddleocr
```

#### 3. Port Already in Use

```bash
# Check what's using the port
# On Windows:
netstat -ano | findstr :8000
# On macOS/Linux:
lsof -i :8000

# Kill the process or change ports in .env
```

#### 4. Memory Issues

- Reduce `CHUNK_SIZE` in `.env`
- Process fewer documents at once
- Close other applications

### Backend Connection Issues

If the frontend can't connect to the backend:

1. Check if backend is running: `http://localhost:8000/health`
2. Verify firewall settings
3. Check if antivirus is blocking connections

## 📊 System Requirements

### Minimum Requirements

- **CPU**: 2 cores
- **RAM**: 4GB
- **Storage**: 2GB free space
- **OS**: Windows 10+, macOS 10.14+, Ubuntu 18.04+

### Recommended Requirements

- **CPU**: 4+ cores
- **RAM**: 8GB+
- **Storage**: 5GB+ free space
- **GPU**: NVIDIA GPU with CUDA support (optional, for faster processing)

## 🔒 Security Considerations

### Production Deployment

1. **Change default ports** in `.env`
2. **Set up proper CORS** origins
3. **Use HTTPS** in production
4. **Implement authentication** if needed
5. **Secure API keys** and sensitive data

### API Key Security

- Never commit `.env` files to version control
- Use environment variables in production
- Rotate API keys regularly
- Monitor API usage

## 📈 Performance Optimization

### For Large Documents

1. **Increase chunk size** in `.env`
2. **Use batch processing** for multiple documents
3. **Enable async processing**
4. **Monitor memory usage**

### For Better Search Results

1. **Adjust similarity threshold** in `.env`
2. **Optimize chunk overlap**
3. **Use better embedding models**
4. **Implement caching**

## 🧪 Testing the System

### Test with Sample Documents

1. **PDF with tables**: Test table extraction
2. **Image with text**: Test OCR functionality
3. **Document with charts**: Test chart detection
4. **Mixed content**: Test overall processing

### Verify Functionality

1. **Upload test document**
2. **Check processing results**
3. **Query the document**
4. **Verify answer quality**

## 📚 Additional Resources

### Documentation

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [PaddleOCR Documentation](https://github.com/PaddlePaddle/PaddleOCR)
- [ChromaDB Documentation](https://docs.trychroma.com/)

### Support

- Check the [README.md](README.md) for detailed information
- Review error logs in the terminal
- Check system requirements and dependencies

## 🎯 Next Steps

After successful setup:

1. **Process your first documents**
2. **Experiment with different query types**
3. **Customize the system** for your needs
4. **Deploy to production** if needed
5. **Contribute to the project** if interested

## 🆘 Getting Help

If you encounter issues:

1. **Check this setup guide** first
2. **Review error messages** carefully
3. **Check system requirements**
4. **Verify all dependencies** are installed
5. **Check configuration** in `.env` file

---

**Happy Document Analysis! 📚🔍**

For more information, see the main [README.md](README.md) file. 