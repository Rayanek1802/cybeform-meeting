# 🚀 CybeMeeting - Guide de Déploiement sur Render

## 📝 Résumé du Projet

CybeMeeting est une application complète d'analyse de réunions pour le BTP qui permet :
- 🎙️ Upload et transcription automatique d'audio
- 👥 Identification des intervenants (diarisation)
- 🤖 Analyse IA des discussions
- 📄 Génération automatique de comptes-rendus Word
- 🔐 Authentification sécurisée des utilisateurs

## 🏗️ Architecture de Déploiement

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│   Frontend      │────▶│    Backend      │────▶│   PostgreSQL    │
│   (React)       │     │   (FastAPI)     │     │   (Database)    │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │                 │
                        │   Cloudinary    │
                        │  (File Storage) │
                        │                 │
                        └─────────────────┘
```

## 🔄 Changements pour le Déploiement

### Avant (Local)
- ❌ Données utilisateurs dans fichiers JSON
- ❌ Fichiers audio stockés localement
- ❌ Pas de persistance des données

### Après (Production)
- ✅ Base de données PostgreSQL
- ✅ Stockage cloud sur Cloudinary
- ✅ Données persistantes et sécurisées
- ✅ Accessible depuis n'importe où

## 📋 Étapes de Déploiement Simplifiées

### 1️⃣ Créer les Comptes (15 minutes)
1. **Render** : https://render.com (hébergement)
2. **Cloudinary** : https://cloudinary.com (stockage fichiers)
3. **GitHub** : https://github.com (code source)

### 2️⃣ Préparer le Code (10 minutes)
```bash
# Dans votre dossier CYBEFORM-MEETING
git init
git add .
git commit -m "Déploiement initial"
git remote add origin https://github.com/VOTRE_USERNAME/cybeform-meeting.git
git push -u origin main
```

### 3️⃣ Déployer sur Render (30 minutes)
1. Créer la base de données PostgreSQL
2. Déployer le backend avec les variables d'environnement
3. Déployer le frontend
4. Tester l'application

## 📚 Documentation Complète

Pour le guide détaillé étape par étape, consultez :
👉 **[GUIDE_DEPLOIEMENT_RENDER.md](./GUIDE_DEPLOIEMENT_RENDER.md)**

Pour la checklist de vérification :
👉 **[CHECKLIST_DEPLOIEMENT.md](./CHECKLIST_DEPLOIEMENT.md)**

## 🧪 Tester la Configuration

Avant de déployer, testez votre configuration :
```bash
python test_config.py
```

## 🆘 Support et Dépannage

### Problèmes Courants

**1. Erreur de connexion à la base de données**
- Vérifiez que DATABASE_URL est correcte dans Render

**2. Fichiers audio ne s'uploadent pas**
- Vérifiez les credentials Cloudinary
- Assurez-vous que les variables CLOUDINARY_* sont définies

**3. Erreur CORS**
- Vérifiez que VITE_API_BASE_URL pointe vers votre backend

### Logs et Debugging

Sur Render Dashboard :
1. Cliquez sur votre service
2. Allez dans l'onglet "Logs"
3. Cherchez les messages d'erreur

## 🎯 URLs de Production

Une fois déployé, votre application sera accessible à :

- **Frontend** : `https://cybeform-frontend.onrender.com`
- **Backend API** : `https://cybeform-backend.onrender.com`
- **Documentation API** : `https://cybeform-backend.onrender.com/docs`

## 📊 Limites du Plan Gratuit

| Ressource | Limite |
|-----------|--------|
| RAM | 512 MB |
| CPU | Partagé |
| Base de données | 90 jours d'inactivité |
| Stockage Cloudinary | 25 GB |
| Temps d'arrêt | 15 min d'inactivité |

## 🚀 Prochaines Étapes

Une fois déployé avec succès :

1. **Testez** toutes les fonctionnalités
2. **Partagez** l'URL avec votre client
3. **Surveillez** les logs pour détecter les problèmes
4. **Sauvegardez** régulièrement la base de données

## 💡 Conseils Pro

- 🔒 Changez les clés API en production
- 📈 Surveillez l'utilisation des ressources
- 🔄 Faites des sauvegardes régulières
- 📝 Documentez les changements

---

**Bonne chance avec votre déploiement ! 🎉**

Si vous avez des questions, référez-vous au guide complet ou contactez le support Render.
