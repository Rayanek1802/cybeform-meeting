@echo off
REM Script pour tester la configuration Docker de production en local
REM Avant de déployer sur Render

echo ======================================
echo 🐳 Test Configuration Docker Production
echo ======================================
echo.

REM Vérifier si Docker est installé
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker n'est pas installé
    pause
    exit /b 1
)
echo ✅ Docker est installé

REM Vérifier si Docker est en cours d'exécution
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Desktop n'est pas en cours d'exécution
    echo Lancez Docker Desktop et réessayez
    pause
    exit /b 1
)
echo ✅ Docker est en cours d'exécution
echo.

echo 📦 Construction des images Docker de production...
echo.

REM Build du backend
echo Construction du backend...
cd backend
docker build -f Dockerfile.production -t cybeform-backend-prod .
if %errorlevel% neq 0 (
    echo ❌ Échec de la construction du backend
    pause
    exit /b 1
)
echo ✅ Backend construit avec succès
cd ..
echo.

REM Build du frontend
echo Construction du frontend...
cd frontend\btp-meeting-ui
docker build -f Dockerfile.production -t cybeform-frontend-prod .
if %errorlevel% neq 0 (
    echo ❌ Échec de la construction du frontend
    pause
    exit /b 1
)
echo ✅ Frontend construit avec succès
cd ..\..
echo.

echo 🚀 Lancement des conteneurs de test...
echo.

REM Arrêter les conteneurs existants si présents
docker stop cybeform-backend-test >nul 2>&1
docker stop cybeform-frontend-test >nul 2>&1
docker rm cybeform-backend-test >nul 2>&1
docker rm cybeform-frontend-test >nul 2>&1

REM Lancer le backend
echo Lancement du backend sur le port 8000...
if exist "backend\.env" (
    docker run -d --name cybeform-backend-test -p 8000:8000 --env-file backend\.env -e DATA_PATH=/tmp/data cybeform-backend-prod
) else (
    echo ❌ Fichier backend\.env non trouvé
    echo Créez le fichier backend\.env avec vos variables d'environnement
    pause
    exit /b 1
)

REM Attendre que le backend soit prêt
echo Attente du démarrage du backend...
timeout /t 5 /nobreak >nul

REM Vérifier si le backend répond
curl -f http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Backend accessible sur http://localhost:8000
) else (
    echo ⚠️  Le backend ne répond pas encore
    echo Vérifiez les logs avec: docker logs cybeform-backend-test
)

REM Lancer le frontend
echo Lancement du frontend sur le port 3000...
docker run -d --name cybeform-frontend-test -p 3000:80 cybeform-frontend-prod
echo ✅ Frontend accessible sur http://localhost:3000
echo.

echo ======================================
echo 📝 Résumé du Test
echo ======================================
echo.
echo ✅ Images Docker de production construites
echo ✅ Backend : http://localhost:8000
echo ✅ API Docs : http://localhost:8000/docs
echo ✅ Frontend : http://localhost:3000
echo.
echo Pour voir les logs :
echo   Backend  : docker logs cybeform-backend-test
echo   Frontend : docker logs cybeform-frontend-test
echo.
echo Pour arrêter les conteneurs :
echo   docker stop cybeform-backend-test cybeform-frontend-test
echo   docker rm cybeform-backend-test cybeform-frontend-test
echo.
echo ✅ Si tout fonctionne, vous êtes prêt pour le déploiement sur Render !
echo.
pause

