# ✅ Checklist de Déploiement CybeMeeting

Cochez chaque étape une fois complétée :

## 📋 Préparation des Comptes

- [ ] Compte Render créé et email confirmé
- [ ] Compte Cloudinary créé
- [ ] Cloud Name noté : _________________
- [ ] API Key notée : _________________
- [ ] API Secret noté : _________________
- [ ] Compte GitHub créé

## 🔧 Préparation du Code

- [ ] Repository GitHub créé (nom : cybeform-meeting)
- [ ] Repository configuré en PUBLIC
- [ ] Code poussé sur GitHub avec :
  ```bash
  git init
  git add .
  git commit -m "Premier déploiement"
  git remote add origin https://github.com/VOTRE_USERNAME/cybeform-meeting.git
  git push -u origin main
  ```

## 🗄️ Base de Données

- [ ] PostgreSQL créée sur Render
- [ ] Nom : cybeform-db
- [ ] Status : Available
- [ ] Internal Database URL copiée : _________________

## 🖥️ Backend

- [ ] Web Service créé sur Render
- [ ] Nom : cybeform-backend
- [ ] Repository GitHub connecté
- [ ] Root Directory : MVP/backend
- [ ] Build Command : `pip install -r requirements.txt && python app/init_db.py`
- [ ] Start Command : `gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:$PORT`

### Variables d'environnement Backend :
- [ ] DATABASE_URL (URL PostgreSQL)
- [ ] OPENAI_API_KEY
- [ ] CLOUDINARY_CLOUD_NAME
- [ ] CLOUDINARY_API_KEY
- [ ] CLOUDINARY_API_SECRET
- [ ] JWT_SECRET_KEY (généré)
- [ ] DATA_PATH = /tmp/data
- [ ] PYTHONPATH = /opt/render/project/src/MVP/backend

- [ ] Backend déployé avec succès
- [ ] URL du backend notée : _________________

## 🌐 Frontend

- [ ] Static Site créé sur Render
- [ ] Nom : cybeform-frontend
- [ ] Repository GitHub connecté
- [ ] Root Directory : MVP/frontend/btp-meeting-ui
- [ ] Build Command : `npm install && npm run build`
- [ ] Publish Directory : dist

### Variable d'environnement Frontend :
- [ ] VITE_API_BASE_URL (URL du backend)

- [ ] Frontend déployé avec succès
- [ ] URL du frontend notée : _________________

## ✅ Tests

- [ ] Application accessible via l'URL du frontend
- [ ] Création de compte fonctionne
- [ ] Connexion fonctionne
- [ ] Création de projet fonctionne
- [ ] Upload de fichier audio fonctionne
- [ ] Traitement IA fonctionne

## 🎉 Finalisation

- [ ] URL partagée avec le client
- [ ] Documentation remise au client
- [ ] Sauvegardes configurées (si nécessaire)

---

**URL de Production :** _________________

**Date de déploiement :** _________________

**Notes :**
_________________________________
_________________________________
_________________________________
