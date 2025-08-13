# 🔐 CRÉEZ VOTRE FICHIER .env MAINTENANT !

## ⚠️ IMPORTANT : Votre application ne fonctionnera pas sans ce fichier !

### Étape 1 : Créez le fichier backend/.env

```bash
cd backend
touch .env
```

### Étape 2 : Copiez ce contenu dans le fichier .env

```env
# OpenAI Configuration (METTEZ VOTRE VRAIE CLÉ ICI)
OPENAI_API_KEY=sk-proj-XXXX_VOTRE_CLE_OPENAI_ICI
MODEL_NAME=gpt-4o
WHISPER_API=on

# Hugging Face (optionnel)
HUGGINGFACE_TOKEN=

# Authentication
SECRET_KEY=cybeform-secret-key-dev-2024

# Application settings
DATA_PATH=./data
MAX_AUDIO_SIZE_MB=500
ALLOWED_AUDIO_FORMATS=mp3,wav,m4a,webm,opus
DEBUG=True
LOG_LEVEL=INFO
```

### Étape 3 : Remplacez la clé OpenAI

⚠️ **IMPORTANT** : Remplacez `sk-proj-XXXX_VOTRE_CLE_OPENAI_ICI` par votre vraie clé OpenAI !

### Votre vraie clé OpenAI (à copier) :

Vous l'aviez dans votre ancien code. Si vous l'avez perdue, vous devez :
1. Aller sur https://platform.openai.com/api-keys
2. Créer une nouvelle clé
3. La copier dans le fichier .env

### ✅ Vérification

Le fichier `.env` ne sera JAMAIS envoyé sur GitHub (il est dans .gitignore).

---

**Une fois fait, votre application fonctionnera parfaitement en local !**
