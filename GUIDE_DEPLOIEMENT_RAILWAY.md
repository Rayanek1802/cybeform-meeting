# 🚂 Guide de Déploiement sur Railway (Alternative à Render)

## ✅ Pourquoi Railway ?

- **8GB RAM** même en gratuit (vs 512MB sur Render)
- **5$ de crédits gratuits** par mois
- **Support Docker natif**
- **Déploiement depuis GitHub**
- **PostgreSQL inclus**

## 📋 Étapes de Déploiement

### 1️⃣ Créer un compte Railway

1. Allez sur https://railway.app
2. Connectez-vous avec GitHub
3. Autorisez Railway à accéder à vos repos

### 2️⃣ Déployer le Backend

1. **New Project** → **Deploy from GitHub repo**
2. Sélectionnez `cybeform-meeting`
3. Railway détectera automatiquement le Dockerfile

#### Configuration :
- **Root Directory** : `MVP/backend`
- **Dockerfile Path** : `Dockerfile.production`
- **Start Command** : (laissez vide, utilisera le CMD du Dockerfile)

### 3️⃣ Ajouter PostgreSQL

1. Dans votre projet, cliquez **"+ New"**
2. Sélectionnez **Database** → **PostgreSQL**
3. Railway créera automatiquement la base

### 4️⃣ Variables d'Environnement

Cliquez sur votre service backend → **Variables** :

```env
# Connexion DB (automatique avec Railway)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# OpenAI
OPENAI_API_KEY=votre_cle_openai
MODEL_NAME=gpt-4o
WHISPER_API=on

# Cloudinary
CLOUDINARY_CLOUD_NAME=votre_cloud_name
CLOUDINARY_API_KEY=votre_api_key
CLOUDINARY_API_SECRET=votre_api_secret

# App
JWT_SECRET_KEY=votre_secret_key
DATA_PATH=/tmp/data
PYTHONPATH=/app
```

### 5️⃣ Déployer le Frontend

#### Option A : Sur Vercel (Recommandé pour React)
1. Allez sur https://vercel.com
2. Import Git Repository → `cybeform-meeting`
3. Configuration :
   - **Root Directory** : `MVP/frontend/btp-meeting-ui`
   - **Build Command** : `npm run build`
   - **Output Directory** : `dist`
   - **Environment Variable** :
     - `VITE_API_BASE_URL` = URL de votre backend Railway

#### Option B : Sur Railway aussi
1. New Service dans le même projet
2. Deploy from GitHub
3. Root Directory : `MVP/frontend/btp-meeting-ui`
4. Utilisez le Dockerfile.production

### 6️⃣ URLs de Production

Railway génère automatiquement des URLs :
- Backend : `cybeform-backend.up.railway.app`
- Frontend : Votre URL Vercel ou Railway

## 💰 Coûts

- **Gratuit** : 5$ de crédits/mois (≈500 heures d'exécution)
- **Si dépassement** : 0.01$/heure (≈7$/mois en continu)

## ✅ Avantages vs Render

| Feature | Render Free | Railway Free |
|---------|------------|--------------|
| RAM | 512MB ❌ | 8GB ✅ |
| CPU | Partagé | 8 vCPU |
| Stockage | Éphémère | 1GB persistant |
| PostgreSQL | 90 jours | Illimité |
| Sleep | Après 15min | Jamais |

## 🚀 Commandes Utiles

```bash
# Installer Railway CLI (optionnel)
npm install -g @railway/cli

# Login
railway login

# Déployer manuellement
railway up
```

## 🔧 Debugging

Si erreurs, vérifiez :
1. Logs : Dashboard → Service → View Logs
2. Metrics : Voir consommation RAM/CPU
3. Variables : Toutes bien configurées ?

---

**Railway est PARFAIT pour votre app avec PyTorch/Whisper car il offre assez de RAM !**

