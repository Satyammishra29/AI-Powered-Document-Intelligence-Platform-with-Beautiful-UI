@echo off
echo 🚀 RAG Application - Quick Deploy to Vercel
echo =============================================

REM Check if vercel CLI is installed
vercel --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Vercel CLI not found. Installing...
    npm install -g vercel
)

REM Check if user is logged in
vercel whoami >nul 2>&1
if errorlevel 1 (
    echo 🔐 Please login to Vercel:
    vercel login
)

REM Run deployment preparation
echo 📋 Running deployment preparation...
python deploy.py

REM Deploy to Vercel
echo 🚀 Deploying to Vercel...
vercel --prod

echo ✅ Deployment complete!
echo 🌐 Your app should be available at the URL shown above
pause
