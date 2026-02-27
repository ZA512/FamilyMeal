@echo off
echo ====================================
echo Démarrage de FamilyMeal
echo ====================================

if not exist venv (
    echo L'environnement virtuel n'existe pas. Veuillez exécuter setup.bat d'abord.
    exit /b 1
)

echo.
echo [1/2] Démarrage du backend Django...
start cmd /k "call venv\Scripts\activate && python manage.py runserver"

echo.
echo [2/2] Démarrage du frontend Vue.js...
start cmd /k "cd frontend && npm run serve"

echo.
echo ====================================
echo FamilyMeal est en cours de démarrage !
echo ====================================
echo.
echo Vous pourrez accéder à :
echo - Backend API : http://localhost:8000/api/
echo - Frontend : http://localhost:8080/
echo.
echo Pour arrêter l'application, fermez les fenêtres de terminal ouvertes.
echo ====================================
