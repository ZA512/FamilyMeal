# DevBook – Application d’Aide au Planning de Cuisine Hebdomadaire pour Famille

## 1. Introduction

### 1.1 Contexte
- **Contexte familial :** Application destinée à une famille de plusieurs personnes où la planification des repas est effectuée chaque samedi.
- **Problématique :** Éviter la répétition des plats sur deux semaines, tenir compte des goûts variés de chaque membre et gérer les contraintes de préparation liées aux équipements de cuisine.

### 1.2 Objectif
- **But principal :** Faciliter la création d’un planning de repas varié et adapté aux préférences de chaque membre.
- **Fonctionnalités clés :**
  - Saisie détaillée des plats (ingrédients, temps de préparation, temps d'attention, contraintes d’outils…).
  - Gestion des préférences individuelles (aime, neutre, ne mange pas).
  - Planification hebdomadaire avec création automatique et modifications manuelles.
  - Génération automatique d’une liste de courses.
  - Gestion d’un inventaire des outils de cuisine (nombre de brûleurs, posséde un ou deux four, micro-ondes, ou tout autre appareil qui compte pour gerer des repas).

---

## 2. Description Générale

### 2.1 Public Cible
- **Responsable de la planification** (souvent le parent en charge).
- **Membres de la famille** participant à l’évaluation des plats et donnant leurs préférences.

### 2.2 Besoins Utilisateurs
- **Saisie des recettes/plats** avec leurs caractéristiques techniques.
- **Indication des préférences** pour chaque membre.
- **Planification souple :** possibilité de prévoir des créneaux vides (ex. midi en semaine) et de proposer un plat de secours.
- **Contraintes de préparation :** gestion des temps, équipements utilisés et capacité simultanée (ex. utilisation du four).
- **Flexibilité :** possibilité de proposer un double plat (élément principal et accompagnant).

---

## 3. Cas d’Usage et Fonctionnalités

### 3.1 Gestion des Plats
- **Création / Modification / Suppression d’un Plat :**
  - Saisie des informations suivantes :
    - Nom et description.
    - Liste des ingrédients avec quantités.
    - Attributs techniques : temps de préparation, temps d’attention, nombre de brûleurs nécessaires, utilisation du four (et si le four est « bloqué » pour un autre plat).
    - Type de plat : plat principal, plat secondaire ou plat de secours.
    - Possibilité de distinguer un élément principal et un accompagnement (ex. steak et frites, poulet tikka masala avec riz ou pâtes).
- **Cas particuliers :**
  - Intégrer des plats "mythiques" réservés à un jour précis (ex. un plat traditionnel du mercredi). ou comme le dimanche midi c'est toujours un plat à base de poulet mais on fait des recettes différentes (poulet roti, poulet à la crème, poulet tikka masala...)

### 3.2 Gestion des Préférences des Membres
- **Pour chaque plat :**
  - Enregistrer le statut de chaque membre : "Aime", "Neutre", "Ne mange pas".
- **Utilisation :**
  - L’algorithme de planification se base sur ces préférences pour maximiser la satisfaction de chacun. on n'élimine pas un plat car 2 ou 3 personnes n'aime pas, dans ce cas là on ajoute un plat de secours (boite de ravioli, ramens, donc il faut pouvoir identifier les plats secours) l'idée de l'algorithme est de faire en sorte qu'il y a une bonne répartition des plats aimé et neutre.

### 3.3 Planning Hebdomadaire
- **Saisie du Planning :**
  - Création d’un planning par jour de la semaine avec deux créneaux (midi et soir).
  - Possibilité de laisser un créneau vide (ex. midi en semaine) ou de le remplir par un plat de secours.
  - Option pour un double plat (ex. associer un plat principal et un accompagnement selon les préférences).
- **Planification Automatique :**
  - Proposition d’un planning hebdomadaire en tenant compte :
    - De la rotation des plats (éviter la répétition sur deux semaines).
    - Des préférences individuelles.
    - Des contraintes d’équipement (nombre de brûleurs, usage du four).
  - Possibilité de modification manuelle de la proposition.

### 3.4 Gestion de l’Inventaire des Outils de Cuisine
- **Saisie et Configuration :**
  - Enregistrer la liste des équipements disponibles : nombre de brûleurs, four (avec notion d’espace occupé), micro-ondes, etc.
- **Utilisation dans la planification :**
  - L’algorithme vérifie que les plats planifiés respectent les contraintes matérielles (par exemple, ne pas surcharger le four).

### 3.5 Génération de la Liste de Courses
- **Fonctionnalité :**
  - Extraction automatique des ingrédients en fonction des plats du planning.
  - Agrégation des quantités nécessaires.
  - Option de modification manuelle pour ajuster la liste de courses selon les stocks ou préférences d’achat.

---

## 4. Exigences Fonctionnelles

### 4.1 Interface de Gestion des Plats
- Formulaire de saisie complet pour chaque plat.
- Possibilité d’ajouter/modifier les attributs (ingrédients, temps de préparation, équipements requis, etc.).
- Interface intuitive pour associer un plat à un ou plusieurs types (principal, secondaire, secours).

### 4.2 Interface de Gestion des Préférences
- Liste des membres de la famille avec options par plat.
- Saisie rapide des préférences (ex. boutons radio ou menus déroulants).

### 4.3 Interface de Planning Hebdomadaire
- Grille ou calendrier affichant chaque jour et créneau (midi/soir).
- Fonction drag-and-drop ou sélection via menus pour ajouter ou retirer des plats.
- Option pour marquer un créneau comme « vide » ou « plat de secours ».

### 4.4 Interface d’Inventaire des Outils
- Saisie et mise à jour de la liste des équipements.
- Indication des capacités (nombre de brûleurs, disponibilité du four, etc.).

### 4.5 Interface de Génération de la Liste de Courses
- Affichage clair de la liste des ingrédients à acheter.
- Fonction d’export (PDF, imprimable, etc.) et possibilité de modifier la liste avant validation.

### 4.6 Module de Planification Automatique
- Algorithme intégrant :
  - La rotation des plats (éviter les répétitions sur deux semaines).
  - Les préférences des membres.
  - Les contraintes matérielles (temps, équipements).
- Option de validation et modification du planning généré.

### 4.7 Notifications et Alertes
- Rappel de la planification hebdomadaire à l’approche du samedi.
- Alertes en cas de conflit (ex. trop de plats nécessitant simultanément l’usage du four).

---

## 5. Exigences Techniques

### 5.1 Architecture Logicielle
- **Type d’application :** Application web responsive, accessible sur ordinateur et mobile.
- **Backend :** API RESTful pour la gestion des données (plats, planning, préférences, inventaire, liste de courses).
- **Base de Données :** PostgreSQL 16 (via `DATABASE_URL`).

### 5.2 Stack implémentée ✅

| Couche | Technologie |
|---|---|
| Backend | Django 5.2.11 + DRF 3.16.1 |
| Auth admin | SimpleJWT (8h access token) |
| Auth lecteur | PyJWT custom (`role:'lecteur'`, `Authorization: Reader <token>`) |
| Tâches async | Celery 5.6.2 + Redis 7 + django-celery-beat |
| SMS | Brevo REST API via httpx (SDK `brevo-python` 4.0.5) |
| Base de données | PostgreSQL 16 (`dj-database-url`) |
| Frontend | Nuxt 3 (SPA, ssr:false) + Tailwind CSS + Pinia |
| Conteneurs | Docker Compose 6 services |
| Reverse proxy | Nginx (port 80) |

### 5.3 Lancer l'application

```bash
# 1. Copier et remplir les variables d'environnement
cp .env.example .env

# 2. Démarrer tous les services
docker compose up -d

# L'app est accessible sur http://localhost
# Admin Django : http://localhost/django-admin/   (admin / Admin1234!)
# API : http://localhost/api/
```

**Variables .env importantes :**
```
SECRET_KEY=...
DATABASE_URL=postgresql://user:pass@db:5432/familymeal
REDIS_URL=redis://redis:6379/0
BREVO_API_KEY=...           # optionnel
SMS_ACTIF=false
CORS_ALLOWED_ORIGINS=http://localhost
```

### 5.4 Structure des services Docker

```
nginx (port 80)
  ├── /api/ → backend:8000  (Django + Gunicorn)
  ├── /static/ → volume static
  ├── /media/  → volume media
  └── /        → frontend:3000  (Nuxt 3)

backend   ← entrypoint.sh (waitDB → migrate → superuser → Config init)
celery    ← worker + beat (SMS alerts every 5 min check)
redis     ← broker + cache
db        ← PostgreSQL 16
```

### 5.5 Sécurité
- Authentification et autorisation (accès administrateur pour la planification).
- Sauvegarde régulière des données et conformité aux normes RGPD.

### 5.6 Performance et Scalabilité
- Optimisation de l’algorithme de planification pour garantir une réponse rapide.
- Interface réactive et intuitive, même avec une grande quantité de données (historique des plats, préférences multiples…).

---

## 6. Contraintes et Limites

- **Multi-utilisateurs :** Gestion des profils admin et des profils utilisateurs.
- **Créneaux Variables :** Gestion de créneaux vides (ex. midi en semaine) et de créneaux fixes (plats mythiques à un jour précis).
- **Rotation des Plats :** Éviter de répéter le même plat dans deux semaines consécutives.
- **Contraintes de Cuisine :** Vérification en temps réel des disponibilités des outils de cuisine (four, brûleurs, etc.). mais aussi pouvoir noter les soirs ou l'on ne peut pas lancer de plat ou il faut plus d'une heure de préparation. je n'ai pas encore définit les limites donc ça doit etre paramétrable par l'admin
- **Flexibilité :** Possibilité de modifier manuellement le planning généré automatiquement.

---

## 7. Cas d'Utilisation

### UC1 – Ajout d’un Plat
- **En tant qu’organisateur,** je souhaite ajouter un nouveau plat avec l’ensemble de ses attributs (ingrédients, temps de préparation, contraintes techniques) pour pouvoir l’intégrer dans le planning.

### UC2 – Gestion des Préférences
- **En tant que membre de la famille,** je souhaite indiquer mon appréciation (aime, neutre, ne mange pas) pour chaque plat, afin que le système prenne en compte mes goûts lors de la génération du planning.

### UC3 – Planification Automatique
- **En tant qu’organisateur,** je souhaite générer automatiquement un planning hebdomadaire qui respecte la rotation des plats, les préférences des membres et les contraintes matérielles, afin de gagner du temps.

### UC4 – Modification du Planning
- **En tant qu’organisateur,** je souhaite pouvoir modifier manuellement le planning généré (changer un plat, ajouter un plat de secours, marquer un créneau comme vide) afin d’adapter le planning aux contraintes spécifiques de la semaine.

### UC5 – Gestion de l’Inventaire des Outils de Cuisine
- **En tant qu’organisateur,** je souhaite gérer l’inventaire des équipements (nombre de brûleurs, capacité du four, etc.) pour garantir que les plats planifiés puissent être préparés sans conflit d’usage.

### UC6 – Génération de la Liste de Courses
- **En tant qu’organisateur,** je souhaite générer automatiquement une liste de courses basée sur les plats retenus dans le planning, avec la possibilité d’ajuster manuellement les quantités ou les articles.

---

## 8. Diagrammes (Optionnel)

### 8.1 Diagramme de Cas d’Utilisation
- Représentation graphique des interactions entre l’organisateur, les membres de la famille et le système (saisie des plats, gestion des préférences, planification, etc.).

### 8.2 Schéma de la Base de Données
- **Entités principales :**
  - **Utilisateurs** (identifiants, rôles, préférences globales)
  - **Plats** (nom, description, type, attributs techniques)
  - **Ingrédients** (nom, quantité par plat)
  - **Préférences** (lien entre utilisateur et plat, statut)
  - **Planning** (créneaux par jour, association aux plats)
  - **Outils de Cuisine** (type, nombre, contraintes d’utilisation)

---

## 9. Stratégie de Tests et Validation

### 9.1 Tests Unitaires
- Vérifier les modules de saisie/modification des plats, gestion des préférences, et vérification des contraintes d’outils.

### 9.2 Tests Fonctionnels
- Simulation complète du cycle de planification : saisie des plats, affectation des préférences, génération automatique du planning, modification manuelle et génération de la liste de courses.

### 9.3 Tests d’Interface Utilisateur
- Vérifier la réactivité et l’ergonomie de l’interface (grille de planning, formulaires, etc.) sur différents appareils (desktop, mobile).

### 9.4 Tests d’Intégration
- Assurer l’interaction correcte entre le frontend, l’API backend et la base de données.

### 9.5 Tests de Performance
- Valider la rapidité de l’algorithme de planification et la fluidité de l’interface, même avec un volume important de données.

---

## 10. Architecture Frontend (Nuxt 3)

### 10.1 Pages et routes

| Route | Fichier | Layout | Auth |
|---|---|---|---|
| `/` | `pages/index.vue` | none | auto-redirect |
| `/login` | `pages/login.vue` | none | public |
| `/lecteur-login` | `pages/lecteur-login.vue` | none | public |
| `/planning` | `pages/planning.vue` | `default` | `reader` |
| `/admin` | `pages/admin/index.vue` | `admin` | `admin` |
| `/admin/planning` | `pages/admin/planning/index.vue` | `admin` | `admin` |
| `/admin/plats` | `pages/admin/plats/index.vue` | `admin` | `admin` |
| `/admin/membres` | `pages/admin/membres/index.vue` | `admin` | `admin` |
| `/admin/ingredients` | `pages/admin/ingredients/index.vue` | `admin` | `admin` |
| `/admin/courses` | `pages/admin/courses/index.vue` | `admin` | `admin` |
| `/admin/demandes` | `pages/admin/demandes/index.vue` | `admin` | `admin` |
| `/admin/parametres` | `pages/admin/parametres/index.vue` | `admin` | `admin` |

### 10.2 Flux d'authentification

```
Lecteur : /lecteur-login → saisir mot de passe famille → choisir membre → /planning
Admin   : /login → saisir identifiant/mot de passe → /admin
```

Tokens stockés dans `localStorage` via le store Pinia `auth`.

### 10.3 Modules Nuxt utilisés
- `@nuxtjs/tailwindcss` — CSS utilitaire
- `@pinia/nuxt` — state management
- Composable `useApi` — fetch wrappé avec header auth + gestion 401

---

## 11. API Backend — Endpoints clés

```
POST   /api/auth/admin/login/           → {access, refresh, username}
POST   /api/auth/lecteur/login/         → {access}
POST   /api/auth/lecteur/choisir-membre/ → {access, membre_id}

GET    /api/membres/
GET    /api/plats/
GET    /api/ingredients/
GET    /api/categories/
GET    /api/config/                     (GET/PUT/PATCH)

GET    /api/semaines/
GET    /api/semaines/courante/
POST   /api/semaines/{id}/publier/
POST   /api/semaines/{id}/generer/      → génération automatique du planning
POST   /api/semaines/{id}/candidats/    → top 3 plats pour un créneau (mode interactif)

GET    /api/courses/
POST   /api/courses/generer/            → génère la liste de courses d'une semaine
POST   /api/courses/{id}/valider/       → archive les achats

GET    /api/demandes/?statut=en_attente
POST   /api/demandes/{id}/valider/
POST   /api/demandes/{id}/refuser/

PATCH  /api/items-courses/{id}/cocher/
```

---

## 12. Algorithme de planification (`meals/planning_generator.py`)

1. **`get_slots_semaine(semaine)`** — génère la liste ordonnée des créneaux actifs de la semaine
2. **`get_plats_recemment_cuisines(date, jours)`** — plats cuisinés dans la fenêtre `intervalle_min_jours`
3. **`get_candidats_pour_slot(slot, semaine_en_cours, recents)`** — score pour chaque plat :
   - +2 par membre qui aime, -1 par membre qui déteste
   - bonus récence (dernière date de cuisine)
   - +15 si jamais cuisiné
   - bruit aléatoire faible
   - filtres : disponibilité, saison, intervalle min, pas deux fois le même ingrédient principal consécutif
4. **`trouver_plat_secours(slot, exclus)`** — meilleur plat de secours disponible
5. **`generer_planning_auto(semaine)`** — boucle sur tous les slots, assigne plat principal + plat de secours pour les membres qui détestent (sauf si plat obligatoire)
6. **`get_top3_candidats(slot, semaine_en_cours)`** — mode interactif : retourne top 3

---

## 13. Notifications SMS (`meals/tasks.py`)

- `verifier_et_envoyer_alertes` — tâche Celery toutes les 5 minutes, envoie SMS 2h avant chaque repas publié aux membres avec numéro de téléphone
- `send_sms_repas(membre_id, message)` — appel Brevo REST API via `httpx`, 3 retries automatiques
- `programmer_alertes_semaine(semaine)` — appelé à la publication, crée un `PeriodicTask` Celery Beat

**Activer les SMS :** dans `Paramètres → SMS`, cocher "Activer" et saisir la clé API Brevo.

> **Note technique :** Le SDK `brevo-python` 4.0.5 a introduit une régression (paramètre `content` manquant). L'implémentation utilise directement `httpx.post()` contre `https://api.brevo.com/v3/transactionalSMS/sms`.

---



