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


