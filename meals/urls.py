from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'membres', views.MembreViewSet)
router.register(r'categories-ingredients', views.CategorieIngredientViewSet)
router.register(r'ingredients', views.IngredientViewSet)
router.register(r'plats', views.PlatViewSet)
router.register(r'preferences', views.PreferenceViewSet)
router.register(r'demandes', views.DemandeModificationViewSet)
router.register(r'semaines', views.SemaineMenuViewSet)
router.register(r'creneaux', views.CreneauPlanningViewSet)
router.register(r'courses', views.ListeCoursesViewSet)
router.register(r'items-courses', views.ItemListeCoursesViewSet)

urlpatterns = [
    path('auth/admin/login/', views.admin_login, name='admin-login'),
    path('auth/lecteur/login/', views.lecteur_login, name='lecteur-login'),
    path('auth/lecteur/choisir-membre/', views.lecteur_choisir_membre, name='lecteur-choisir-membre'),
    path('config/', views.config_view, name='config'),
    path('tools/parse-har/', views.parse_har, name='parse-har'),
    path('tools/scrape-coursesu/', views.scrape_coursesu, name='scrape-coursesu'),
    path('tools/import-ingredients/', views.import_ingredients, name='import-ingredients'),
    path('tools/backup/', views.backup_download, name='backup-download'),
    path('tools/restore/', views.backup_restore, name='backup-restore'),
    path('', include(router.urls)),
]
