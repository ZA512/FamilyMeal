from rest_framework import serializers
from .models import (
    Membre, CategorieIngredient, Ingredient, HistoriqueAchat,
    Plat, DisponibilitePlat, PlatIngredient, Preference, DemandeModification,
    HistoriquePlat, Config, CreneauActif, SemaineMenu, CreneauPlanning,
    ListeCourses, ItemListeCourses,
)


class MembreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membre
        fields = ['id', 'prenom', 'annee_naissance', 'telephone', 'couleur', 'actif', 'created_at']
        read_only_fields = ['created_at']


class CategorieIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategorieIngredient
        fields = ['id', 'nom', 'ordre']


class IngredientSerializer(serializers.ModelSerializer):
    categorie_nom = serializers.CharField(source='categorie.nom', read_only=True)
    dernier_achat = serializers.SerializerMethodField()

    class Meta:
        model = Ingredient
        fields = [
            'id', 'nom', 'categorie', 'categorie_nom', 'unite', 'url_produit',
            'achat_systematique', 'lie_a_plat', 'dernier_achat',
        ]

    def get_dernier_achat(self, obj):
        achat = obj.historique_achats.first()
        return achat.date_achat.isoformat() if achat else None


class HistoriqueAchatSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoriqueAchat
        fields = ['id', 'ingredient', 'date_achat']


class DisponibilitePlatSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisponibilitePlat
        fields = ['id', 'jour', 'creneau']


class PlatIngredientSerializer(serializers.ModelSerializer):
    ingredient_nom = serializers.CharField(source='ingredient.nom', read_only=True)
    ingredient_unite = serializers.CharField(source='ingredient.unite', read_only=True)

    class Meta:
        model = PlatIngredient
        fields = ['id', 'ingredient', 'ingredient_nom', 'ingredient_unite',
                  'quantite_par_portion', 'unite', 'notes']


class PlatListSerializer(serializers.ModelSerializer):
    """Serializer léger pour les listes."""
    class Meta:
        model = Plat
        fields = ['id', 'nom', 'temps_preparation', 'ingredient_principal',
                  'est_secours', 'est_obligatoire', 'statut', 'photo']


class PlatDetailSerializer(serializers.ModelSerializer):
    disponibilites = DisponibilitePlatSerializer(many=True, read_only=True)
    plat_ingredients = PlatIngredientSerializer(many=True, read_only=True)
    nb_fois_cuisine = serializers.SerializerMethodField()

    class Meta:
        model = Plat
        fields = [
            'id', 'nom', 'description', 'photo', 'temps_preparation',
            'ingredient_principal', 'est_secours', 'est_obligatoire',
            'saison_debut', 'saison_fin', 'statut', 'propose_par',
            'disponibilites', 'plat_ingredients', 'nb_fois_cuisine', 'created_at',
        ]
        read_only_fields = ['created_at']

    def get_nb_fois_cuisine(self, obj):
        return obj.historique.count()


class PlatWriteSerializer(serializers.ModelSerializer):
    disponibilites = DisponibilitePlatSerializer(many=True, required=False)
    plat_ingredients = PlatIngredientSerializer(many=True, required=False)

    class Meta:
        model = Plat
        fields = [
            'id', 'nom', 'description', 'photo', 'temps_preparation',
            'ingredient_principal', 'est_secours', 'est_obligatoire',
            'saison_debut', 'saison_fin', 'statut', 'propose_par',
            'disponibilites', 'plat_ingredients',
        ]

    def _save_disponibilites(self, plat, disponibilites_data):
        plat.disponibilites.all().delete()
        for d in disponibilites_data:
            DisponibilitePlat.objects.create(plat=plat, **d)

    def _save_ingredients(self, plat, ingredients_data):
        plat.plat_ingredients.all().delete()
        for i in ingredients_data:
            PlatIngredient.objects.create(plat=plat, **i)

    def create(self, validated_data):
        disponibilites_data = validated_data.pop('disponibilites', [])
        ingredients_data = validated_data.pop('plat_ingredients', [])
        plat = Plat.objects.create(**validated_data)
        self._save_disponibilites(plat, disponibilites_data)
        self._save_ingredients(plat, ingredients_data)
        return plat

    def update(self, instance, validated_data):
        disponibilites_data = validated_data.pop('disponibilites', None)
        ingredients_data = validated_data.pop('plat_ingredients', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if disponibilites_data is not None:
            self._save_disponibilites(instance, disponibilites_data)
        if ingredients_data is not None:
            self._save_ingredients(instance, ingredients_data)
        return instance


class PreferenceSerializer(serializers.ModelSerializer):
    membre_prenom = serializers.CharField(source='membre.prenom', read_only=True)
    plat_nom = serializers.CharField(source='plat.nom', read_only=True)

    class Meta:
        model = Preference
        fields = ['id', 'membre', 'membre_prenom', 'plat', 'plat_nom', 'note']


class DemandeModificationSerializer(serializers.ModelSerializer):
    membre_prenom = serializers.CharField(source='membre.prenom', read_only=True)
    plat_nom = serializers.CharField(source='plat.nom', read_only=True, allow_null=True)

    class Meta:
        model = DemandeModification
        fields = [
            'id', 'type', 'membre', 'membre_prenom', 'plat', 'plat_nom',
            'ancienne_note', 'nouvelle_note', 'data_json',
            'statut', 'message_admin', 'created_at', 'traite_at',
        ]
        read_only_fields = ['statut', 'message_admin', 'created_at', 'traite_at']


class HistoriquePlatSerializer(serializers.ModelSerializer):
    plat_nom = serializers.CharField(source='plat.nom', read_only=True)

    class Meta:
        model = HistoriquePlat
        fields = ['id', 'plat', 'plat_nom', 'date', 'notes']


class CreneauActifSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreneauActif
        fields = ['id', 'jour', 'creneau']


class ConfigSerializer(serializers.ModelSerializer):
    creneaux_actifs = CreneauActifSerializer(many=True, read_only=True)
    coursesu_configured = serializers.SerializerMethodField()

    class Meta:
        model = Config
        fields = [
            'jour_debut_semaine', 'intervalle_min_jours', 'nb_plats_aimes_min',
            'heure_midi', 'heure_soir', 'mot_de_passe_lecteur', 'sms_actif',
            'creneaux_actifs', 'coursesu_login', 'coursesu_configured',
        ]

    def get_coursesu_configured(self, obj):
        return bool(obj.coursesu_login and obj.coursesu_password)


class ConfigWriteSerializer(serializers.ModelSerializer):
    creneaux_actifs = CreneauActifSerializer(many=True, required=False)

    class Meta:
        model = Config
        fields = [
            'jour_debut_semaine', 'intervalle_min_jours', 'nb_plats_aimes_min',
            'heure_midi', 'heure_soir', 'mot_de_passe_lecteur', 'sms_actif',
            'brevo_api_key', 'creneaux_actifs', 'coursesu_login', 'coursesu_password',
        ]

    def update(self, instance, validated_data):
        creneaux_data = validated_data.pop('creneaux_actifs', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if creneaux_data is not None:
            instance.creneaux_actifs.all().delete()
            for c in creneaux_data:
                CreneauActif.objects.create(config=instance, **c)
        return instance


class CreneauPlanningSerializer(serializers.ModelSerializer):
    plat_principal_detail = PlatListSerializer(source='plat_principal', read_only=True)
    plat_secours_detail = PlatListSerializer(source='plat_secours', read_only=True)
    membres_secours_detail = MembreSerializer(source='membres_secours', many=True, read_only=True)
    jour_semaine = serializers.SerializerMethodField()

    class Meta:
        model = CreneauPlanning
        fields = [
            'id', 'date', 'creneau', 'jour_semaine',
            'plat_principal', 'plat_principal_detail',
            'plat_secours', 'plat_secours_detail',
            'membres_secours', 'membres_secours_detail', 'notes',
        ]

    def get_jour_semaine(self, obj):
        JOURS_FR = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
        return JOURS_FR[obj.date.weekday()]


class SemaineMenuSerializer(serializers.ModelSerializer):
    creneaux = CreneauPlanningSerializer(many=True, read_only=True)

    class Meta:
        model = SemaineMenu
        fields = ['id', 'date_debut', 'statut', 'created_at', 'publie_at', 'creneaux']
        read_only_fields = ['created_at', 'publie_at']


class SemaineMenuListSerializer(serializers.ModelSerializer):
    nb_creneaux = serializers.SerializerMethodField()

    class Meta:
        model = SemaineMenu
        fields = ['id', 'date_debut', 'statut', 'created_at', 'publie_at', 'nb_creneaux']

    def get_nb_creneaux(self, obj):
        return obj.creneaux.filter(plat_principal__isnull=False).count()


class ItemListeCoursesSerializer(serializers.ModelSerializer):
    ingredient_nom = serializers.CharField(source='ingredient.nom', read_only=True, allow_null=True)
    ingredient_url = serializers.CharField(source='ingredient.url_produit', read_only=True, allow_null=True)
    categorie_nom = serializers.CharField(
        source='ingredient.categorie.nom', read_only=True, allow_null=True,
    )

    class Meta:
        model = ItemListeCourses
        fields = [
            'id', 'ingredient', 'ingredient_nom', 'ingredient_url', 'categorie_nom',
            'nom_libre', 'quantite', 'unite', 'source', 'coche', 'notes',
        ]


class ListeCoursesSerializer(serializers.ModelSerializer):
    items = ItemListeCoursesSerializer(many=True, read_only=True)

    class Meta:
        model = ListeCourses
        fields = ['id', 'semaine', 'statut', 'date_creation', 'date_validation', 'items']
        read_only_fields = ['date_creation', 'date_validation']
