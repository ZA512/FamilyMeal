from django.contrib import admin
from .models import (
    Membre, CategorieIngredient, Ingredient, HistoriqueAchat,
    Plat, DisponibilitePlat, PlatIngredient, Preference, DemandeModification,
    HistoriquePlat, Config, CreneauActif, SemaineMenu, CreneauPlanning,
    ListeCourses, ItemListeCourses,
)


@admin.register(Membre)
class MembreAdmin(admin.ModelAdmin):
    list_display = ['prenom', 'annee_naissance', 'telephone', 'actif']
    list_filter = ['actif']


@admin.register(CategorieIngredient)
class CategorieIngredientAdmin(admin.ModelAdmin):
    list_display = ['nom', 'ordre']
    ordering = ['ordre']


class PlatIngredientInline(admin.TabularInline):
    model = PlatIngredient
    extra = 1


class DisponibilitePlatInline(admin.TabularInline):
    model = DisponibilitePlat
    extra = 3


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['nom', 'categorie', 'unite', 'achat_systematique', 'lie_a_plat']
    list_filter = ['categorie', 'achat_systematique', 'lie_a_plat']
    search_fields = ['nom']


@admin.register(Plat)
class PlatAdmin(admin.ModelAdmin):
    list_display = ['nom', 'ingredient_principal', 'temps_preparation', 'est_secours', 'est_obligatoire', 'statut']
    list_filter = ['statut', 'est_secours', 'est_obligatoire', 'ingredient_principal']
    search_fields = ['nom']
    inlines = [DisponibilitePlatInline, PlatIngredientInline]


@admin.register(Preference)
class PreferenceAdmin(admin.ModelAdmin):
    list_display = ['membre', 'plat', 'note']
    list_filter = ['note', 'membre']


@admin.register(DemandeModification)
class DemandeModificationAdmin(admin.ModelAdmin):
    list_display = ['type', 'membre', 'plat', 'nouvelle_note', 'statut', 'created_at']
    list_filter = ['statut', 'type']
    readonly_fields = ['created_at']


class CreneauActifInline(admin.TabularInline):
    model = CreneauActif
    extra = 0


@admin.register(Config)
class ConfigAdmin(admin.ModelAdmin):
    inlines = [CreneauActifInline]

    def has_add_permission(self, request):
        return not Config.objects.exists()


class CreneauPlanningInline(admin.TabularInline):
    model = CreneauPlanning
    extra = 0


@admin.register(SemaineMenu)
class SemaineMenuAdmin(admin.ModelAdmin):
    list_display = ['date_debut', 'statut', 'created_at']
    list_filter = ['statut']
    inlines = [CreneauPlanningInline]


@admin.register(HistoriquePlat)
class HistoriquePlatAdmin(admin.ModelAdmin):
    list_display = ['plat', 'date']
    list_filter = ['plat']


class ItemListeCoursesInline(admin.TabularInline):
    model = ItemListeCourses
    extra = 1


@admin.register(ListeCourses)
class ListeCoursesAdmin(admin.ModelAdmin):
    list_display = ['semaine', 'statut', 'date_creation']
    inlines = [ItemListeCoursesInline]
