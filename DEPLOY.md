# Deployment Guide - KiCad AI Generator

This guide explains how to deploy the KiCad AI Generator application to Render.

## Prerequisites

1. A Render account (sign up at https://render.com)
2. An OpenAI API key
3. This repository connected to your Render account

## Architecture

The application consists of two services:
- **Backend**: FastAPI application (Python 3.12 + Poetry)
- **Frontend**: React + Vite static site

## Deployment Steps

### Option 1: Deploy via Render Dashboard (Recommended)

1. **Connect Repository**
   - Go to https://render.com/dashboard
   - Click "New" → "Blueprint"
   - Connect your GitHub account if not already connected
   - Select the `Matluc88/dev` repository
   - Render will automatically detect the `render.yaml` file

2. **Configure Environment Variables**
   - During setup, you'll be prompted to set the `OPENAI_API_KEY`
   - Enter your OpenAI API key
   - All other environment variables are configured automatically

3. **Deploy**
   - Click "Apply" to start the deployment
   - Render will:
     - Deploy the backend service first
     - Build and deploy the frontend with the backend URL automatically configured
     - Set up health checks and automatic deployments

4. **Access Your Application**
   - Once deployed, you'll receive two URLs:
     - Backend API: `https://kicad-ai-backend.onrender.com`
     - Frontend: `https://kicad-ai-frontend.onrender.com`
   - The frontend is automatically configured to use the backend URL

### Option 2: Deploy via Render CLI

```bash
# Install Render CLI
npm install -g @render/cli

# Login to Render
render login

# Deploy from repository root
render blueprint launch
```

## Configuration Details

### Backend Service
- **Runtime**: Python 3.12
- **Build Command**: Installs Poetry and dependencies
- **Start Command**: Runs uvicorn server
- **Health Check**: `/healthz` endpoint
- **Required Environment Variable**: `OPENAI_API_KEY`

### Frontend Service
- **Runtime**: Static site
- **Build Command**: `npm install && npm run build`
- **Publish Path**: `kicad-ai-frontend/dist`
- **Environment Variable**: `VITE_API_URL` (automatically set from backend service)

## Environment Variables

### Backend
- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `PYTHON_VERSION`: 3.12.0 (automatically set)

### Frontend
- `VITE_API_URL`: Backend API URL (automatically set from backend service)

## Monitoring

- View logs in the Render dashboard for each service
- Backend health check: `GET /healthz`
- Monitor API usage in your OpenAI dashboard

## Updating the Application

Render automatically deploys when you push to your main branch. To deploy manually:
1. Go to the Render dashboard
2. Select the service
3. Click "Manual Deploy" → "Deploy latest commit"

## Troubleshooting

### Backend fails to start
- Check that `OPENAI_API_KEY` is set correctly
- View logs in Render dashboard
- Verify Poetry dependencies are installing correctly

### Frontend can't connect to backend
- Verify backend service is running and healthy
- Check that `VITE_API_URL` is set correctly
- Check CORS settings in backend (already configured for all origins)

### Build failures
- Check that all dependencies are listed in `pyproject.toml` (backend)
- Check that all dependencies are listed in `package.json` (frontend)
- View build logs in Render dashboard

## Local Development

### Backend
```bash
cd kicad-ai-backend
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
poetry install
poetry run uvicorn app.main:app --reload
```

### Frontend
```bash
cd kicad-ai-frontend
npm install
# Set backend URL (optional, defaults to http://localhost:8000)
export VITE_API_URL=http://localhost:8000
npm run dev
```

## Cost Considerations

- Render free tier includes 750 hours/month for web services
- Backend will use a web service (always running)
- Frontend is a static site (free)
- OpenAI API costs depend on usage

## Support

For issues with:
- Render deployment: https://render.com/docs
- OpenAI API: https://platform.openai.com/docs
- Application bugs: Open an issue in the GitHub repository
