@echo off
echo ====================================
echo Installation de FamilyMeal
echo ====================================

echo.
echo [1/6] Création de l'environnement virtuel...
python -m venv venv
if %errorlevel% neq 0 (
    echo Erreur lors de la création de l'environnement virtuel.
    exit /b %errorlevel%
)

echo.
echo [2/6] Activation de l'environnement virtuel...
call venv\Scripts\activate
if %errorlevel% neq 0 (
    echo Erreur lors de l'activation de l'environnement virtuel.
    exit /b %errorlevel%
)

echo.
echo [3/6] Installation des dépendances backend...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Erreur lors de l'installation des dépendances backend.
    exit /b %errorlevel%
)

echo.
echo [4/6] Application des migrations...
python manage.py migrate
if %errorlevel% neq 0 (
    echo Erreur lors de l'application des migrations.
    exit /b %errorlevel%
)

echo.
echo [5/6] Installation des dépendances frontend...
cd frontend
npm install
if %errorlevel% neq 0 (
    echo Erreur lors de l'installation des dépendances frontend.
    exit /b %errorlevel%
)
cd ..

echo.
echo [6/6] Création d'un fichier .env à partir de .env.example...
copy .env.example .env
if %errorlevel% neq 0 (
    echo Erreur lors de la création du fichier .env.
    exit /b %errorlevel%
)

echo.
echo ====================================
echo Installation terminée avec succès !
echo ====================================
echo.
echo Pour lancer l'application :
echo.
echo 1. Démarrer le backend : python manage.py runserver
echo 2. Dans un autre terminal, démarrer le frontend : cd frontend ^&^& npm run serve
echo.
echo Vous pourrez ensuite accéder à :
echo - Backend API : http://localhost:8000/api/
echo - Frontend : http://localhost:8080/
echo.
echo Merci d'utiliser FamilyMeal !
echo ====================================
