# Deployment Guide

This guide will help you deploy the ReActEnviro application using free hosting services.

## Architecture

- **Frontend**: React app deployed on GitHub Pages
- **Backend**: FastAPI server deployed on Railway (free tier)

## Prerequisites

1. GitHub account
2. Railway account (sign up at https://railway.app/)
3. Google AI Studio account for Gemini API key (https://makersuite.google.com/app/apikey)

## Step 1: Deploy Backend to Railway

### 1.1 Prepare the Repository
1. Push your code to a GitHub repository
2. Make sure your `.env` file is not committed (it should be in `.gitignore`)

### 1.2 Deploy to Railway
1. Go to https://railway.app/
2. Sign up/log in with your GitHub account
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Railway will automatically detect it's a Python project using the root-level configuration files
6. The deployment will take a few minutes to build and start

### 1.3 Set Environment Variables
1. In your Railway project dashboard, go to "Variables"
2. Add the following environment variables:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   PORT=8000
   TEMPERATURE=0.2
   MAX_OUTPUT_TOKENS=1000
   REQUEST_TIMEOUT=30
   ```

### 1.4 Get Your Backend URL
1. After deployment, Railway will provide you with a URL like `https://your-app-name-production.up.railway.app`
2. Note this URL - you'll need it for the frontend configuration

## Step 2: Deploy Frontend to GitHub Pages

### 2.1 Update Package.json
1. Open `frontend/package.json`
2. Update the `homepage` field with your GitHub username and repository name:
   ```json
   "homepage": "https://yourusername.github.io/repository-name"
   ```

### 2.2 Configure Environment Variables for GitHub Actions
1. Go to your GitHub repository
2. Go to Settings → Secrets and Variables → Actions
3. Add the following secrets:
   ```
   REACT_APP_API_URL=https://your-railway-app-url
   REACT_APP_WS_URL=wss://your-railway-app-url/ws/agent
   ```

### 2.3 Enable GitHub Pages
1. Go to your repository Settings → Pages
2. Select "GitHub Actions" as the source
3. The GitHub Actions workflow will automatically deploy your app

### 2.4 Manual Deployment (Alternative)
If you prefer manual deployment:

1. Install gh-pages:
   ```bash
   cd frontend
   npm install gh-pages --save-dev
   ```

2. Build and deploy:
   ```bash
   npm run build
   npm run deploy
   ```

## Step 3: Test Your Deployment

1. Visit your GitHub Pages URL: `https://yourusername.github.io/repository-name`
2. Test the application by entering an environmental assessment goal
3. Check that the WebSocket connection works (you should see real-time updates)

## Troubleshooting

### Backend Issues
- Check Railway logs in the project dashboard
- Ensure all environment variables are set correctly
- Verify the Gemini API key is valid
- If you see "Python 3 could not be found" errors, make sure the root-level `requirements.txt`, `nixpacks.toml`, and `Procfile` are present in your repository

### Frontend Issues
- Check browser console for errors
- Ensure CORS is configured correctly in the backend
- Verify the API URLs in environment variables

### WebSocket Issues
- Make sure you're using `wss://` (not `ws://`) for the production WebSocket URL
- Check that the backend WebSocket endpoint is accessible

## Environment Variables Reference

### Backend (Railway)
- `GEMINI_API_KEY`: Your Google AI Studio API key
- `PORT`: Port number (Railway sets this automatically)
- `TEMPERATURE`: LLM temperature setting (0.0-1.0)
- `MAX_OUTPUT_TOKENS`: Maximum tokens in LLM response
- `REQUEST_TIMEOUT`: API request timeout in seconds

### Frontend (GitHub Actions Secrets)
- `REACT_APP_API_URL`: Full URL to your Railway backend
- `REACT_APP_WS_URL`: WebSocket URL to your Railway backend

## Cost Considerations

Both GitHub Pages and Railway offer generous free tiers:
- **GitHub Pages**: Unlimited for public repositories
- **Railway**: $5 credit monthly (sufficient for light usage)

For production usage with higher traffic, consider upgrading to paid plans.
