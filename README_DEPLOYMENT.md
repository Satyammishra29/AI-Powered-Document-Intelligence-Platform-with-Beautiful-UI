# 🚀 RAG Application - Vercel Deployment

This document provides a complete guide for deploying your RAG (Retrieval-Augmented Generation) application to Vercel.

## 📁 Project Structure

```
RAG-APPLICATION/
├── frontend/
│   ├── main_app.py          # Main Streamlit application
│   ├── pages/               # Application pages
│   ├── utils/               # Utility modules
│   ├── config/              # Configuration files
│   └── requirements.txt     # Python dependencies
├── vercel.json              # Vercel configuration
├── requirements.txt         # Root dependencies
├── .vercelignore           # Files to ignore in deployment
├── .gitignore              # Git ignore file
├── deploy.py               # Deployment preparation script
├── quick-deploy.bat        # Windows deployment script
├── quick-deploy.sh         # Linux/Mac deployment script
└── DEPLOYMENT_GUIDE.md     # Detailed deployment guide
```

## 🚀 Quick Start

### Option 1: Automated Deployment (Recommended)

**For Windows:**
```bash
quick-deploy.bat
```

**For Linux/Mac:**
```bash
./quick-deploy.sh
```

### Option 2: Manual Deployment

1. **Install Vercel CLI:**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel:**
   ```bash
   vercel login
   ```

3. **Deploy:**
   ```bash
   vercel --prod
   ```

### Option 3: GitHub Integration

1. Push your code to GitHub
2. Connect your repository to Vercel
3. Configure environment variables
4. Deploy automatically

## ⚙️ Configuration Files

### vercel.json
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

### Environment Variables

Set these in your Vercel dashboard:

```env
OPENAI_API_KEY=your_openai_api_key_here
BACKEND_URL=https://your-backend-url.vercel.app
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

## 📋 Pre-Deployment Checklist

- [ ] All files committed to Git
- [ ] Environment variables configured
- [ ] Dependencies listed in requirements.txt
- [ ] vercel.json configured correctly
- [ ] Application tested locally

## 🔧 Troubleshooting

### Common Issues:

1. **Import Errors:**
   - Ensure all `__init__.py` files are present
   - Check import paths are correct

2. **Missing Dependencies:**
   - Verify requirements.txt includes all packages
   - Check for version conflicts

3. **Environment Variables:**
   - Ensure all required env vars are set in Vercel
   - Check variable names match your code

4. **Function Timeout:**
   - Default timeout is 10s for Hobby plan
   - Upgrade to Pro for longer timeouts

### Debug Commands:

```bash
# Test locally
vercel dev

# Check build logs
vercel logs

# View function details
vercel inspect
```

## 📊 Post-Deployment

1. **Test Your Application:**
   - Visit your Vercel URL
   - Test all functionality
   - Check file uploads
   - Verify AI features work

2. **Monitor Performance:**
   - Use Vercel Analytics
   - Monitor function execution times
   - Check error rates

3. **Set Up Custom Domain:**
   - Go to Project Settings → Domains
   - Add your custom domain
   - Configure DNS settings

## 🔒 Security Best Practices

1. **Never commit API keys to Git**
2. **Use Vercel's environment variable system**
3. **Implement file upload validation**
4. **Consider rate limiting for production**

## 📈 Scaling Considerations

- **Hobby Plan:** 100GB bandwidth, 1000 serverless function invocations
- **Pro Plan:** Unlimited bandwidth, 1000GB-hours execution time
- **Enterprise:** Custom limits and features

## 🆘 Support

If you encounter issues:

1. Check the detailed [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
2. Review Vercel documentation
3. Check build logs in Vercel dashboard
4. Test locally first
5. Contact Vercel support if needed

## 🎉 Success!

Once deployed, your RAG application will be available at:
`https://your-project-name.vercel.app`

Share the URL with users and start processing documents with AI!

---

**Need help?** Check the [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed instructions.
