# 🍽️ FamilyMeal

Application web de planning de repas hebdomadaire pour famille — gestion des plats, préférences, liste de courses et import depuis coursesu.com.

---

## Fonctionnalités

- **Planning hebdomadaire** — créneaux configurables (midi/soir, jours actifs), publication et consultation par les membres
- **Gestion des plats** — ingrédients, temps de préparation, jours autorisés, plat de saison, plat de secours, historique
- **Préférences par membre** — aime / neutre / déteste, plats de secours automatiques
- **Ingrédients** — associés ou non à des plats, achat systématique, URL produit
- **Liste de courses** — générée depuis le planning, historique des achats, récurrence estimée
- **Import Coursesu.com** — connexion directe ou import via fichier HAR, filtre des doublons, noms éditables avant import
- **Demandes de plats** — les membres peuvent proposer des nouveau plats
- **SMS de rappel** — intégration Brevo, envoi 2 h avant chaque repas (Celery)
- **Double accès** — interface admin complète + vue lecteur (planning + ingrédients)
- **Responsive** — adapté desktop et smartphone

---

## Stack technique

| Couche | Technologie |
|---|---|
| Backend | Django 5 + Django REST Framework |
| Auth | JWT (SimpleJWT) — admin & lecteur |
| Base de données | PostgreSQL (Docker) / SQLite (dev) |
| Tâches asynchrones | Celery + Redis + django-celery-beat |
| SMS | Brevo API |
| Frontend | Nuxt 3 (Vue 3, TypeScript, SPA) |
| CSS | Tailwind CSS |
| Scraping courses | requests + BeautifulSoup4 |
| Conteneurisation | Docker + Docker Compose + Nginx |

---

## Prérequis

- **Docker** et **Docker Compose** (déploiement)
- **Python 3.12+** et **Node.js 20+** (développement local)

---

## Installation rapide — Docker

```bash
git clone https://github.com/ZA512/FamilyMeal.git
cd FamilyMeal

# Copier et adapter les variables d'environnement
cp .env.example .env
# Éditer .env : SECRET_KEY, POSTGRES_PASSWORD, etc.

docker compose up -d
```

L'application est accessible sur **http://localhost**.

Créer le premier compte administrateur :

```bash
docker compose exec backend python manage.py createsuperuser
```

---

## Installation développement local

### Backend

```bash
cd FamilyMeal
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .venv\Scripts\activate         # Windows

pip install -r requirements.txt
cp .env.example .env             # adapter si besoin

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
npm run dev         # http://localhost:3000
```

### Worker Celery (SMS, tâches planifiées)

```bash
source .venv/bin/activate
celery -A familymeal worker -l info -B \
  --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

---

## Variables d'environnement (`.env`)

| Variable | Description | Défaut |
|---|---|---|
| `SECRET_KEY` | Clé secrète Django | ⚠️ À changer |
| `DEBUG` | Mode debug | `False` |
| `ALLOWED_HOSTS` | Hôtes autorisés | `localhost,127.0.0.1` |
| `DATABASE_URL` | URL PostgreSQL | SQLite si absent |
| `REDIS_URL` | URL Redis | `redis://redis:6379/0` |
| `POSTGRES_DB` | Nom de la BDD | `familymeal` |
| `POSTGRES_USER` | Utilisateur PostgreSQL | `familymeal` |
| `POSTGRES_PASSWORD` | Mot de passe PostgreSQL | ⚠️ À changer |
| `NUXT_PUBLIC_API_BASE` | URL de l'API (frontend) | `/api` |

---

## Structure du projet

```
FamilyMeal/
├── familymeal/          # Configuration Django (settings, urls, celery)
├── meals/               # Application principale
│   ├── models.py        # Modèles : Plat, Ingrédient, Membre, Config…
│   ├── serializers.py   # Serializers DRF
│   ├── views.py         # ViewSets + vues fonctionnelles (tools, auth)
│   └── urls.py          # Routes API
├── frontend/            # Application Nuxt 3
│   ├── pages/
│   │   ├── admin/       # Dashboard, planning, plats, ingrédients…
│   │   │   └── outils/  # Import favoris Coursesu (direct + HAR)
│   │   ├── planning.vue # Vue lecteur
│   │   └── login.vue    # Connexion admin / lecteur
│   ├── layouts/         # Layouts admin et default
│   ├── stores/auth.ts   # Store Pinia — authentification
│   └── composables/     # useApi (fetch authentifié)
├── nginx/               # Reverse-proxy (Docker)
├── docker-compose.yml
├── Dockerfile
└── .env.example
```

---

## API REST

Base URL : `http://localhost:8000/api/`

| Endpoint | Description |
|---|---|
| `POST /auth/admin/login/` | Connexion administrateur |
| `POST /auth/lecteur/login/` | Connexion lecteur (mot de passe partagé) |
| `GET /config/` | Paramètres globaux |
| `GET/POST /plats/` | Gestion des plats |
| `GET/POST /ingredients/` | Gestion des ingrédients |
| `GET/POST /membres/` | Gestion des membres |
| `GET/POST /semaines/` | Semaines de planning |
| `GET/POST /courses/` | Listes de courses |
| `POST /tools/scrape-coursesu/` | Import favoris Coursesu (connexion directe) |
| `POST /tools/parse-har/` | Import favoris Coursesu (fichier HAR) |
| `POST /tools/import-ingredients/` | Enregistrement des produits sélectionnés |

---

## Accès

| URL | Description |
|---|---|
| `http://localhost` | Application (via Docker/Nginx) |
| `http://localhost:3000` | Frontend dev (Nuxt) |
| `http://localhost:8000/api/` | API REST |
| `http://localhost:8000/admin/` | Interface Django admin |

---

## Licence

[MIT](https://choosealicense.com/licenses/mit/)


## Description

FamilyMeal est une application web qui aide à planifier les repas hebdomadaires pour une famille en tenant compte des préférences de chaque membre, des contraintes d'équipement de cuisine, et en évitant la répétition des plats sur deux semaines.

## Fonctionnalités principales

- Gestion des plats (ingrédients, temps de préparation, équipements nécessaires)
- Gestion des préférences des membres de la famille
- Planification automatique des repas hebdomadaires
- Gestion de l'inventaire des outils de cuisine
- Génération automatique de listes de courses

## Installation

### Backend (Django)

1. Cloner le dépôt :
```
git clone https://github.com/votre-nom/FamilyMeal.git
cd FamilyMeal
```

2. Créer un environnement virtuel et l'activer :
```
python -m venv venv
venv\Scripts\activate  # Sur Windows
```

3. Installer les dépendances :
```
pip install -r requirements.txt
```

4. Initialiser la base de données :
```
python manage.py migrate
```

5. Créer un superutilisateur (administrateur) :
```
python manage.py createsuperuser
```

6. Lancer le serveur de développement :
```
python manage.py runserver
```

### Frontend (Nuxt 3)

1. Installer les dépendances :
```
cd frontend
npm install
```

2. Lancer le serveur de développement :
```
npm run dev
```

## Utilisation

Une fois l'application lancée, vous pouvez accéder à :

- L'interface d'administration Django : http://localhost:8000/admin/
- L'API REST : http://localhost:8000/api/
- L'interface utilisateur Vue.js : http://localhost:8080/

### Fonctionnalités principales

1. **Gestion des plats** : Ajoutez, modifiez et supprimez des plats avec leurs ingrédients, temps de préparation et équipements nécessaires.
2. **Gestion des préférences** : Définissez les préférences de chaque membre de la famille pour chaque plat (aime, neutre, n'aime pas).
3. **Planning hebdomadaire** : Générez automatiquement un planning de repas pour la semaine en tenant compte des préférences et des contraintes d'équipement.
4. **Gestion des outils** : Inventoriez les outils de cuisine disponibles pour la planification des repas.
5. **Liste de courses** : Générez automatiquement une liste de courses basée sur le planning hebdomadaire.

## Structure du projet

### Backend (Django)

- `meals/` : Application principale contenant les modèles, vues et serializers
  - `models.py` : Définition des modèles de données
  - `serializers.py` : Serializers pour l'API REST
  - `views.py` : Viewsets pour les opérations CRUD
  - `urls.py` : Configuration des URL pour l'API
- `familymeal/` : Configuration du projet Django
  - `settings.py` : Paramètres du projet
  - `urls.py` : Configuration des URL principales

### Frontend (Vue.js)

- `src/` : Code source de l'application Vue.js
  - `views/` : Composants de vue pour chaque page
  - `components/` : Composants réutilisables
  - `store/` : Store Vuex pour la gestion de l'état
  - `router/` : Configuration du routeur Vue
  - `App.vue` : Composant racine de l'application
  - `main.js` : Point d'entrée de l'application

## Développement

L'application est développée avec :
- Django 4.2.10 (backend)
- Django REST Framework 3.14.0 (API)
- SQLite (base de données)
- Vue.js 3.2 (frontend)
- Bootstrap 5.3 (UI)

## Contribution

Les contributions sont les bienvenues ! Veuillez suivre ces étapes :

1. Forker le projet
2. Créer une branche pour votre fonctionnalité (`git checkout -b feature/amazing-feature`)
3. Commiter vos changements (`git commit -m 'Add some amazing feature'`)
4. Pousser vers la branche (`git push origin feature/amazing-feature`)
5. Ouvrir une Pull Request

## Licence

[MIT](https://choosealicense.com/licenses/mit/)




* ce qu'il y a au dessus c'était le projet au départ, ce qui arrive après c'est mon besoin aujourd'hui *

création d'un plat :
 - liste des ingredients
 - temps de préparation
 - les jours de la semaine où il peut être mis (car il y a des emplacements cultes ou à cause des peremptions, exemple merguez fraiche acheté le samedi ne peux pas être fait après le lundi soir et les enfants s'attendent à certain plat à jour fixe par habitude)
 - est-ce un plat de secours (si un enfant ou adulte deteste un plat, il y a des plats facile style raviolis en conserve, plat préparé, sandwich...)
 - historique des fois ou le plat a été fait.
 - il peut y avoir des plats de saison à définir (entre date de début et date de fin) exemple soupe, raclette, bbq...
 - indication si plat obligatoire meme si pas aimé
 
 habitant de la maison :
 - Prénom
 - Age
 - numéro de téléphone

 Aime ou pas :
 - Prénom + plat = Aime, neutre, deteste

planning de la semaine :
 - Samedi soir
 - Dimanche midi & Soir
 - Lundi à Vendredi Soir.

paramétrage :
 - Planning débute par le jour X
 - pour chaque jour de la semaine indiquer si on fait le midi et ou soir (case à cocher)
 - un plat peut revenir tous les X jours
 - définir heure du repas du midi, et heure du repas du soir

ingredient :
 - associé à des plats
 - non associé (sel, poivre, épice, lait, céréale, beurre, fromage à raper, yaourt...) il s'agit d'aliment qui permet de compléter la liste de course
 - achat systématique chaque semaine
 - permettre de copier l'url du produit pour faciliter la liste de course dans le supermarché en ligne.

liste de course :
 - liste des ingredients pour les plats
 - liste des ingredients sans lien avec les plats (on garde la date des x derniers achats afin de trouver la reccurence et de pouvoir indiquer que ce produit pourrait manquer, bon sauf les achats systématiques, mais oui le sel c'est pas toute les semaines ainsi que le lait, mais on doit avoir une idée de ce qu'il reste en fonction de l'écart entre les dates d'achat)
 - une fois la liste validé on peut au choix présenter le liste avec checkbox pour valider pendant les courses, afficher une version de la liste pret a être imprimé ou pour les courses en ligne voir juste après.

 pour course en ligne :
 - permettre après connexion à la plateforme d'ajouter les produits avec les bonnes quantités.
 - je ne connais pas ce qui peut être fait pour automatiser, à faire pour chaque solution? on verra, moi j'utilise courseu.com

 génération du planning : 
 - séparer d'au moins X jours de paramétrage les plats 
 - respecter les jours de semaine ou il peut être fait
 - il faut mettre au point un calcul pour que chaque enfant/adulte est au moins un plat aimé par semaine ou deux plats ou plus, et s'il y a des plats qui sont detesté, il faut un plat de secours (raviolis, saucisse lentille, salade de thon, ...) après cette partie n'est pas simple  car ça va dépendre du nombre de plat possible et des préférences de chacun. et s'il y a un plat detesté mais qu'on veut forcer, on ne prévoit pas de plat de secours, mais on s'arrange pour mettre d'autres plats dans la semaine que l'enfant aime.
 - ou alors tu proposes deux ou trois plats par repas et une fois selectionné tu proposes deux ou trois plats pour le choix suivant.
 - on évite d'avoir deux fois à suivre des pates ou du poulet, bref il faut éviter d'avoir à suivre un repas avec des memes aliments

 chaque utilisateur peut proposer des nouveaux plats qui seront étudié par le cuisinier de la famille.

 Alerte, tous les jours deux heures avant le repas l'app envoie une alerte par sms (je vais utiliser brevo)



 Alors, tu peux changer la stack technique, ce que je veux c'est mettre l'app en docker, qu'elles soient accessible via navigateur (desktop mais aussi smartphone donc il faut que ce soit adapté au device) il faut une entrée lecteur ou l'on voit le planning et les ingredients et une entrée admin pour la gestion de l'app.

 Tu as le droit de tout casser et de proposer une autre stack technique.
