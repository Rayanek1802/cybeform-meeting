# 🔐 SÉCURITÉ : Configuration des Clés API

## ⚠️ IMPORTANT : Ne JAMAIS commit vos clés API !

GitHub a bloqué votre push car votre clé API OpenAI était visible dans le code. C'est dangereux car :
- N'importe qui peut utiliser votre clé et vous faire facturer
- Votre clé peut être désactivée par OpenAI pour violation de sécurité

## ✅ Ce qui a été fait :

1. **Suppression de la clé du code source**
   - La clé API n'est plus dans `config.py`
   - Elle sera lue depuis les variables d'environnement

2. **Création d'un fichier exemple**
   - `backend/env.example.txt` montre le format sans les vraies clés

## 📝 Ce que VOUS devez faire maintenant :

### 1. Créer votre fichier .env local

Créez un fichier `backend/.env` avec vos vraies clés :

```bash
# Dans le dossier backend
cd backend
touch .env
```

Puis copiez-y ce contenu avec VOS vraies clés :

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-VOTRE_CLE_API_OPENAI_ICI
MODEL_NAME=gpt-4o
WHISPER_API=on

# Autres configurations...
SECRET_KEY=votre-secret-key-change-in-production
DATA_PATH=./data
```

### 2. Vérifier que .env est ignoré par Git

Le fichier `.gitignore` doit contenir :
```
.env
*.env
```

### 3. Sur Render (production)

Les clés seront configurées dans l'interface Render comme variables d'environnement, jamais dans le code.

## 🔑 Conseils de sécurité :

1. **Régénérez votre clé OpenAI** si elle a été exposée
   - Allez sur https://platform.openai.com/api-keys
   - Supprimez l'ancienne clé
   - Créez-en une nouvelle

2. **Utilisez différentes clés** pour dev et production

3. **Ne partagez JAMAIS** vos clés API

4. **Vérifiez toujours** avant de commit :
   ```bash
   git diff  # Vérifiez qu'aucune clé n'apparaît
   ```

---

**Note** : Votre application fonctionnera toujours localement avec le fichier .env, mais les clés ne seront jamais exposées sur GitHub.
