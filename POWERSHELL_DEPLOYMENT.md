# 🚀 PowerShell Deployment Guide for RAG Application

This guide is specifically designed for Windows PowerShell users deploying to Vercel.

## 📋 Prerequisites

### 1. Install Node.js
```powershell
# Option 1: Download from official website
# Visit: https://nodejs.org/

# Option 2: Install via Chocolatey (if you have it)
choco install nodejs

# Option 3: Install via Winget
winget install OpenJS.NodeJS
```

### 2. Verify Installation
```powershell
# Check Node.js version
node --version

# Check npm version
npm --version
```

## 🚀 Quick Deployment

### Method 1: Automated PowerShell Script (Recommended)

```powershell
# Run the PowerShell deployment script
.\deploy.ps1
```

### Method 2: Manual PowerShell Commands

```powershell
# 1. Install Vercel CLI
npm install -g vercel

# 2. Login to Vercel
vercel login

# 3. Run deployment preparation
python deploy.py

# 4. Deploy to Vercel
vercel --prod
```

## ⚙️ PowerShell-Specific Commands

### Check System Requirements
```powershell
# Check Python version
python --version

# Check if Git is available
git --version

# Check PowerShell execution policy
Get-ExecutionPolicy

# If needed, set execution policy for current user
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Environment Setup
```powershell
# Create virtual environment (optional)
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Deactivate virtual environment
deactivate
```

### Git Operations
```powershell
# Initialize git repository (if not already done)
git init

# Add all files
git add .

# Commit changes
git commit -m "Prepare for Vercel deployment"

# Add remote origin (replace with your GitHub repo)
git remote add origin https://github.com/yourusername/your-repo.git

# Push to GitHub
git push -u origin main
```

## 🔧 Troubleshooting PowerShell Issues

### Execution Policy Issues
```powershell
# Check current execution policy
Get-ExecutionPolicy

# Set execution policy for current user
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or run script with bypass
PowerShell -ExecutionPolicy Bypass -File .\deploy.ps1
```

### Node.js/npm Issues
```powershell
# Clear npm cache
npm cache clean --force

# Update npm
npm install -g npm@latest

# Reinstall Vercel CLI
npm uninstall -g vercel
npm install -g vercel
```

### Python Issues
```powershell
# Check Python installation
python --version
py --version

# Install pip if missing
python -m ensurepip --upgrade

# Upgrade pip
python -m pip install --upgrade pip
```

## 📁 File Structure for PowerShell

```
RAG-APPLICATION/
├── deploy.ps1              # PowerShell deployment script
├── deploy.py               # Python deployment preparation
├── quick-deploy.bat        # Windows batch file
├── vercel.json             # Vercel configuration
├── requirements.txt        # Python dependencies
├── .gitignore              # Git ignore file
├── .vercelignore           # Vercel ignore file
└── frontend/               # Application code
    ├── main_app.py
    ├── pages/
    ├── utils/
    ├── config/
    └── requirements.txt
```

## 🎯 Step-by-Step PowerShell Deployment

### Step 1: Prepare Your Environment
```powershell
# Navigate to your project directory
cd "C:\Users\Infer\OneDrive\Documents\RAG-APPLICATION"

# Check if all files are present
Get-ChildItem -Name
```

### Step 2: Set Up Git (if not already done)
```powershell
# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit for Vercel deployment"
```

### Step 3: Run Deployment
```powershell
# Run the PowerShell script
.\deploy.ps1
```

### Step 4: Set Environment Variables in Vercel
1. Go to your Vercel dashboard
2. Select your project
3. Go to Settings → Environment Variables
4. Add the following variables:

```env
OPENAI_API_KEY=your_openai_api_key_here
BACKEND_URL=https://your-backend-url.vercel.app
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

## 🔍 PowerShell Debugging

### Check Deployment Status
```powershell
# Check Vercel project status
vercel ls

# View deployment logs
vercel logs

# Inspect function details
vercel inspect
```

### Test Locally
```powershell
# Test with Vercel dev
vercel dev

# Test with Streamlit directly
cd frontend
streamlit run main_app.py
```

## 📊 Post-Deployment PowerShell Commands

### Monitor Your Deployment
```powershell
# Check deployment status
vercel ls

# View recent deployments
vercel ls --limit 5

# Get deployment URL
vercel inspect --json | ConvertFrom-Json | Select-Object -ExpandProperty url
```

### Update Deployment
```powershell
# Make changes to your code
# Commit changes
git add .
git commit -m "Update application"

# Deploy updates
vercel --prod
```

## 🆘 Common PowerShell Issues & Solutions

### Issue: "Execution of scripts is disabled"
**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue: "Node.js not found"
**Solution:**
```powershell
# Install Node.js from https://nodejs.org/
# Or use Chocolatey: choco install nodejs
```

### Issue: "Python not found"
**Solution:**
```powershell
# Install Python from https://python.org/
# Or use Chocolatey: choco install python
```

### Issue: "Vercel command not found"
**Solution:**
```powershell
npm install -g vercel
```

## 🎉 Success!

Once deployed, your RAG application will be available at:
`https://your-project-name.vercel.app`

### Next Steps:
1. Test your deployed application
2. Set up custom domain (optional)
3. Monitor performance in Vercel dashboard
4. Share your app with users!

---

**Need help?** Check the main [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for additional details.
