# 🔧 Correction du Problème Frontend sur Railway

## ❌ Le Problème

L'erreur "Blocked request" apparaît car :
1. Le frontend est mal configuré pour Railway
2. Confusion possible entre backend et frontend

## ✅ Solution Complète

### 1️⃣ Vérifiez votre configuration Railway

Vous devez avoir **2 services séparés** :
- **Backend** (FastAPI) 
- **Frontend** (React)

### 2️⃣ Si vous avez déployé SEULEMENT le backend

Le backend FastAPI ne sert pas le frontend. Vous devez :

#### Option A : Déployer le Frontend sur Vercel (RECOMMANDÉ)

1. Allez sur https://vercel.com
2. **Import Git Repository**
3. Sélectionnez `cybeform-meeting`
4. Configuration :
   ```
   Root Directory: MVP/frontend/btp-meeting-ui
   Build Command: npm run build
   Output Directory: dist
   ```
5. Variables d'environnement :
   ```
   VITE_API_BASE_URL=https://cybeform-meeting-production.up.railway.app
   ```

#### Option B : Déployer le Frontend sur Railway aussi

1. Dans Railway, cliquez **"+ New"** → **"GitHub Repo"**
2. Sélectionnez encore `cybeform-meeting`
3. **Settings** :
   ```
   Root Directory: MVP/frontend/btp-meeting-ui
   Dockerfile Path: Dockerfile.production
   ```
4. Variables :
   ```
   VITE_API_BASE_URL=https://cybeform-meeting-production.up.railway.app
   PORT=3000
   ```

### 3️⃣ Si vous voulez tout sur un seul service (Moins recommandé)

Modifiez le backend pour servir le frontend :

#### Créez ce fichier :

**`MVP/backend/app/serve_frontend.py`** :

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

def setup_frontend(app: FastAPI):
    """Configure FastAPI to serve React frontend"""
    
    # Path to built frontend files
    frontend_path = "/app/frontend_build"
    
    if os.path.exists(frontend_path):
        # Serve static files
        app.mount("/assets", StaticFiles(directory=f"{frontend_path}/assets"), name="assets")
        
        # Serve index.html for all other routes
        @app.get("/{full_path:path}")
        async def serve_spa(full_path: str):
            file_path = os.path.join(frontend_path, full_path)
            if os.path.exists(file_path) and os.path.isfile(file_path):
                return FileResponse(file_path)
            return FileResponse(f"{frontend_path}/index.html")
```

#### Nouveau Dockerfile combiné :

**`MVP/Dockerfile.combined`** :

```dockerfile
# Build frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app
COPY frontend/btp-meeting-ui/package*.json ./
RUN npm ci
COPY frontend/btp-meeting-ui .
RUN npm run build

# Build backend
FROM python:3.11-slim
RUN apt-get update && apt-get install -y ffmpeg curl && rm -rf /var/lib/apt/lists/*
WORKDIR /app

# Copy backend
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend .

# Copy frontend build
COPY --from=frontend-builder /app/dist /app/frontend_build

# Start
CMD ["gunicorn", "app.main_production:app", "-w", "2", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"]
```

## 🎯 Recommandation

**Utilisez l'Option A : Frontend sur Vercel**

C'est :
- ✅ Gratuit
- ✅ Optimisé pour React
- ✅ CDN global
- ✅ Déploiement automatique

## 📝 Variables d'Environnement Importantes

### Sur le Frontend (Vercel ou Railway) :
```
VITE_API_BASE_URL=https://cybeform-meeting-production.up.railway.app
```

### Sur le Backend (Railway) :
```
ALLOWED_ORIGINS=https://votre-frontend.vercel.app,http://localhost:5173
```

## 🔄 Pour Redéployer

```bash
# Committez les changements
git add .
git commit -m "Fix frontend configuration for Railway"
git push origin main
```

Railway redéploiera automatiquement.

## ✅ Vérification

1. Backend API : https://cybeform-meeting-production.up.railway.app/docs
2. Frontend : Votre URL Vercel ou Railway frontend

---

**Le problème vient du fait que vous essayez d'accéder au backend directement, mais le backend ne sert pas le frontend !**

