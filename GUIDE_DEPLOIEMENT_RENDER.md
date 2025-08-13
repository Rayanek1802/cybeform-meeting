# 🚀 Guide de Déploiement CybeMeeting sur Render

## 📋 Prérequis

### 1. Créer les comptes nécessaires

#### A. Compte Render (Hébergement)
1. Allez sur https://render.com
2. Cliquez sur **"Get Started for Free"**
3. Créez un compte avec votre email ou GitHub
4. Confirmez votre email

#### B. Compte Cloudinary (Stockage fichiers)
1. Allez sur https://cloudinary.com
2. Cliquez sur **"Sign up for free"**
3. Créez un compte (plan gratuit = 25GB de stockage)
4. Une fois connecté, allez dans **"Dashboard"**
5. **IMPORTANT** : Notez ces informations (vous en aurez besoin) :
   - **Cloud Name** : (ex: dxxxxx)
   - **API Key** : (série de chiffres)
   - **API Secret** : (série de caractères)

#### C. Compte GitHub
1. Allez sur https://github.com
2. Créez un compte si vous n'en avez pas
3. Connectez-vous

---

## 🔧 Étape 1 : Préparer votre code sur GitHub

### 1.1 Créer un nouveau repository GitHub

1. Sur GitHub, cliquez sur le **"+"** en haut à droite
2. Sélectionnez **"New repository"**
3. Configuration :
   - **Repository name** : `cybeform-meeting`
   - **Public** (IMPORTANT : Render gratuit nécessite un repo public)
   - **NE PAS** initialiser avec README
4. Cliquez sur **"Create repository"**

### 1.2 Uploader votre code sur GitHub

Ouvrez un terminal dans le dossier **CYBEFORM-MEETING** et exécutez :

```bash
# Initialiser git
git init

# Ajouter tous les fichiers
git add .

# Faire un premier commit
git commit -m "Premier déploiement CybeMeeting"

# Ajouter le repository distant (remplacez YOUR_USERNAME par votre nom d'utilisateur GitHub)
git remote add origin https://github.com/YOUR_USERNAME/cybeform-meeting.git

# Pousser le code
git branch -M main
git push -u origin main
```

Si vous avez une erreur, essayez :
```bash
git push --force -u origin main
```

---

## 🗄️ Étape 2 : Créer la base de données sur Render

### 2.1 Créer une base PostgreSQL

1. Connectez-vous sur https://dashboard.render.com
2. Cliquez sur **"New +"** en haut
3. Sélectionnez **"PostgreSQL"**
4. Configuration :
   - **Name** : `cybeform-db`
   - **Database** : `cybeform`
   - **User** : `cybeform`
   - **Region** : Frankfurt (EU) ou Oregon (US)
   - **Plan** : Free
5. Cliquez sur **"Create Database"**
6. Attendez que le statut passe à **"Available"** (≈2 minutes)
7. **IMPORTANT** : Cliquez sur votre base de données et copiez :
   - **Internal Database URL** (commence par `postgresql://`)

---

## 🖥️ Étape 3 : Déployer le Backend

### 3.1 Créer le service Backend

1. Sur Render Dashboard, cliquez sur **"New +"**
2. Sélectionnez **"Web Service"**
3. Connectez votre GitHub si demandé
4. Cherchez et sélectionnez votre repo **cybeform-meeting**
5. Configuration :
   - **Name** : `cybeform-backend`
   - **Region** : Même que la base de données
   - **Branch** : main
   - **Root Directory** : `MVP/backend`
   - **Runtime** : Python 3
   - **Build Command** : `pip install -r requirements.txt && python app/init_db.py`
   - **Start Command** : `gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:$PORT`
   - **Plan** : Free

### 3.2 Ajouter les variables d'environnement

Cliquez sur **"Environment"** et ajoutez :

#### Variables de base de données
- **DATABASE_URL** : Collez l'URL de votre base PostgreSQL (de l'étape 2.1)

#### Variables OpenAI
- **OPENAI_API_KEY** : Votre clé API OpenAI
- **MODEL_NAME** : `gpt-4o`
- **WHISPER_API** : `on`

#### Variables Cloudinary (de votre dashboard Cloudinary)
- **CLOUDINARY_CLOUD_NAME** : Votre Cloud Name
- **CLOUDINARY_API_KEY** : Votre API Key
- **CLOUDINARY_API_SECRET** : Votre API Secret

#### Variables application
- **JWT_SECRET_KEY** : Cliquez sur **"Generate"** pour créer une clé aléatoire
- **DATA_PATH** : `/tmp/data`
- **PYTHONPATH** : `/opt/render/project/src/MVP/backend`
- **DEBUG** : `False`
- **LOG_LEVEL** : `INFO`

### 3.3 Déployer

1. Cliquez sur **"Create Web Service"**
2. Attendez que le déploiement se termine (5-10 minutes)
3. Une fois terminé, notez l'URL de votre backend (ex: `https://cybeform-backend.onrender.com`)

---

## 🌐 Étape 4 : Déployer le Frontend

### 4.1 Créer le service Frontend

1. Sur Render Dashboard, cliquez sur **"New +"**
2. Sélectionnez **"Static Site"**
3. Sélectionnez votre repo **cybeform-meeting**
4. Configuration :
   - **Name** : `cybeform-frontend`
   - **Branch** : main
   - **Root Directory** : `MVP/frontend/btp-meeting-ui`
   - **Build Command** : `npm install && npm run build`
   - **Publish Directory** : `dist`
   - **Plan** : Free

### 4.2 Ajouter la variable d'environnement

Ajoutez :
- **VITE_API_BASE_URL** : L'URL de votre backend (ex: `https://cybeform-backend.onrender.com`)

### 4.3 Déployer

1. Cliquez sur **"Create Static Site"**
2. Attendez le déploiement (3-5 minutes)
3. Votre application sera accessible à l'URL fournie !

---

## ✅ Étape 5 : Vérification et Tests

### 5.1 Tester l'application

1. Allez sur l'URL de votre frontend
2. Créez un compte utilisateur
3. Créez un projet test
4. Uploadez un fichier audio test
5. Vérifiez que tout fonctionne

### 5.2 Débuggage si problèmes

Si quelque chose ne fonctionne pas :

1. **Vérifier les logs du backend** :
   - Sur Render Dashboard, cliquez sur votre service backend
   - Allez dans l'onglet **"Logs"**
   - Cherchez les erreurs

2. **Erreurs communes** :
   - **"Database connection failed"** : Vérifiez DATABASE_URL
   - **"Cloudinary not configured"** : Vérifiez les variables Cloudinary
   - **"CORS error"** : L'URL du frontend dans VITE_API_BASE_URL est incorrecte

---

## 🔄 Étape 6 : Mises à jour futures

Pour mettre à jour votre application :

```bash
# Dans votre dossier local
git add .
git commit -m "Description des changements"
git push origin main
```

Render redéploiera automatiquement !

---

## 📝 Notes importantes

### Limitations du plan gratuit Render

- **Base de données** : Supprimée après 90 jours d'inactivité
- **Services** : S'arrêtent après 15 min d'inactivité (redémarrent à la première requête)
- **Ressources** : 512 MB RAM, CPU partagé

### Sauvegardes recommandées

1. Faites des sauvegardes régulières de votre base de données
2. Gardez une copie locale des fichiers importants

### Pour passer en production

Si votre client est satisfait et veut une version plus performante :
1. Passez au plan **Starter** de Render (7$/mois par service)
2. Ou migrez vers un autre hébergeur (AWS, Google Cloud, etc.)

---

## 🆘 Besoin d'aide ?

Si vous rencontrez des problèmes :
1. Vérifiez les logs sur Render Dashboard
2. Assurez-vous que toutes les variables d'environnement sont correctes
3. Vérifiez que votre code est bien poussé sur GitHub

---

## 🎉 Félicitations !

Votre application CybeMeeting est maintenant en ligne et accessible depuis n'importe où !

URL de votre application : `https://cybeform-frontend.onrender.com`

Partagez cette URL avec votre client pour qu'il puisse tester l'application.
