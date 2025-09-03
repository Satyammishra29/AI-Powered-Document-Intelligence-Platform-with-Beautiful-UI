# 🚀 Vercel Deployment Guide

This guide will help you deploy your RAG Application to Vercel.

## 📋 Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **GitHub Account**: Your code should be in a GitHub repository
3. **Python Environment**: Ensure your local environment works

## 🔧 Pre-Deployment Setup

### 1. Environment Variables

Create a `.env` file in your project root with the following variables:

```env
# OpenAI Configuration
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
```

### 2. Update Configuration Files

Make sure your `frontend/config/settings.py` file has the correct backend URL:

```python
class app_config:
    BACKEND_URL = os.getenv("BACKEND_URL", "https://your-backend-url.vercel.app")
    # ... other settings
```

## 🚀 Deployment Steps

### Method 1: Deploy via Vercel CLI

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy from your project directory**:
   ```bash
   vercel
   ```

4. **Follow the prompts**:
   - Link to existing project or create new
   - Set up environment variables
   - Deploy

### Method 2: Deploy via GitHub Integration

1. **Push your code to GitHub**:
   ```bash
   git add .
   git commit -m "Prepare for Vercel deployment"
   git push origin main
   ```

2. **Connect to Vercel**:
   - Go to [vercel.com/dashboard](https://vercel.com/dashboard)
   - Click "New Project"
   - Import your GitHub repository
   - Configure settings (see below)

3. **Configure Project Settings**:
   - **Framework Preset**: Other
   - **Root Directory**: `./` (or leave empty)
   - **Build Command**: Leave empty
   - **Output Directory**: Leave empty
   - **Install Command**: `pip install -r requirements.txt`

4. **Set Environment Variables**:
   - Go to Project Settings → Environment Variables
   - Add all variables from your `.env` file

5. **Deploy**:
   - Click "Deploy"
   - Wait for deployment to complete

## ⚙️ Vercel Configuration

The `vercel.json` file is already configured with:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "frontend/main_app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "frontend/main_app.py"
    }
  ],
  "env": {
    "STREAMLIT_SERVER_PORT": "8501",
    "STREAMLIT_SERVER_ADDRESS": "0.0.0.0",
    "STREAMLIT_SERVER_HEADLESS": "true",
    "STREAMLIT_BROWSER_GATHER_USAGE_STATS": "false"
  },
  "functions": {
    "frontend/main_app.py": {
      "maxDuration": 30
    }
  }
}
```

## 🔍 Troubleshooting

### Common Issues:

1. **Import Errors**:
   - Ensure all `__init__.py` files are present
   - Check that import paths are correct

2. **Missing Dependencies**:
   - Verify `requirements.txt` includes all packages
   - Check for version conflicts

3. **Environment Variables**:
   - Ensure all required env vars are set in Vercel
   - Check that variable names match your code

4. **File Size Limits**:
   - Vercel has file size limits
   - Consider using external storage for large files

5. **Function Timeout**:
   - Default timeout is 10s for Hobby plan
   - Upgrade to Pro for longer timeouts

### Debug Steps:

1. **Check Build Logs**:
   - Go to Vercel Dashboard → Your Project → Functions
   - Check build and runtime logs

2. **Test Locally**:
   ```bash
   vercel dev
   ```

3. **Check Dependencies**:
   ```bash
   pip install -r requirements.txt
   streamlit run frontend/main_app.py
   ```

## 📊 Post-Deployment

### 1. Test Your Application

- Visit your Vercel URL
- Test all functionality
- Check file uploads
- Verify AI features work

### 2. Monitor Performance

- Use Vercel Analytics
- Monitor function execution times
- Check error rates

### 3. Set Up Custom Domain (Optional)

- Go to Project Settings → Domains
- Add your custom domain
- Configure DNS settings

## 🔒 Security Considerations

1. **API Keys**: Never commit API keys to Git
2. **Environment Variables**: Use Vercel's env var system
3. **File Uploads**: Consider size limits and validation
4. **Rate Limiting**: Implement if needed

## 📈 Scaling Considerations

1. **Hobby Plan**: 100GB bandwidth, 1000 serverless function invocations
2. **Pro Plan**: Unlimited bandwidth, 1000GB-hours execution time
3. **Enterprise**: Custom limits and features

## 🆘 Support

If you encounter issues:

1. Check Vercel documentation
2. Review build logs
3. Test locally first
4. Contact Vercel support if needed

## 🎉 Success!

Once deployed, your RAG application will be available at:
`https://your-project-name.vercel.app`

Share the URL with users and start processing documents with AI!