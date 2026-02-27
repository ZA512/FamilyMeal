# Changelog

Toutes les modifications notables apportées au projet FamilyMeal seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Non publié]

### Ajouté
- Structure initiale du projet avec Django pour le backend et Vue.js pour le frontend
- Modèles Django pour `Membre`, `Plat`, `Ingredient`, `Preference`, `OutilCuisine`, et `Planning`
- Serializers Django REST Framework pour tous les modèles
- Viewsets pour les opérations CRUD sur les modèles
- Configuration des URL pour les endpoints API
- Vue d'accueil (HomeView) avec navigation vers les différentes sections
- Vue de gestion des plats (PlatsView) avec affichage et filtrage
- Vue de gestion des membres (MembresView) avec liste et formulaire d'édition
- Vue de gestion des ingrédients (IngredientsView) avec liste et recherche
- Vue de gestion des préférences (PreferencesView) avec sélection par membre
- Vue de planning hebdomadaire (PlanningView) avec génération automatique
- Vue de gestion des outils de cuisine (OutilsView) avec inventaire
- Vue de liste de courses (CoursesView) avec différents modes d'affichage
- Composants modaux pour l'ajout et la modification de plats, membres et ingrédients
- Composant de détails de plat pour afficher les informations complètes
- Store Vuex avec actions et mutations pour toutes les entités
- Système de thème clair/sombre avec persistance des préférences
- Navigation responsive avec Bootstrap
- Migrations Django et initialisation de la base de données
- Script d'installation et de lancement automatisé (setup.bat et run.bat)
- Superutilisateur par défaut pour l'administration

### Modifié
- Mise à jour des dépendances pour utiliser les versions les plus récentes
- Amélioration de l'interface utilisateur avec Bootstrap 5 et Bootstrap Icons
- Refonte de la page d'accueil avec des cartes pour chaque section
- Amélioration de la navigation principale avec des icônes et une meilleure organisation

### Corrigé
- Aucun correctif pour l'instant

## [0.1.0] - 2023-12-01

### Ajouté
- Initialisation du projet
