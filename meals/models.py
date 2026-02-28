from django.db import models
from django.utils import timezone
from datetime import date as date_type

JOUR_CHOICES = [
    ('lundi', 'Lundi'), ('mardi', 'Mardi'), ('mercredi', 'Mercredi'),
    ('jeudi', 'Jeudi'), ('vendredi', 'Vendredi'), ('samedi', 'Samedi'), ('dimanche', 'Dimanche'),
]
CRENEAU_CHOICES = [('midi', 'Midi'), ('soir', 'Soir')]
NOTE_CHOICES = [('aime', 'Aime'), ('neutre', 'Neutre'), ('deteste', 'Déteste')]
STATUT_DEMANDE_CHOICES = [
    ('en_attente', 'En attente'), ('validee', 'Validée'), ('refusee', 'Refusée'),
]
INGREDIENT_PRINCIPAL_CHOICES = [
    ('viande', 'Viande'), ('poisson', 'Poisson'), ('pates', 'Pâtes'), ('riz', 'Riz'),
    ('pommes_de_terre', 'Pommes de terre'), ('legumes', 'Légumes'), ('oeufs', 'Œufs'),
    ('pain', 'Pain'), ('pizza', 'Pizza'), ('soupe', 'Soupe'), ('salade', 'Salade'), ('autre', 'Autre'),
]


class Membre(models.Model):
    prenom = models.CharField(max_length=100)
    annee_naissance = models.IntegerField(null=True, blank=True)
    telephone = models.CharField(max_length=20, blank=True)
    couleur = models.CharField(max_length=7, default='#3B82F6', help_text='Couleur hex pour l\'affichage')
    actif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.prenom

    class Meta:
        verbose_name = 'Membre'
        ordering = ['prenom']


class CategorieIngredient(models.Model):
    nom = models.CharField(max_length=100)
    ordre = models.IntegerField(default=0, help_text='Ordre d\'affichage dans la liste de courses')

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = 'Catégorie ingrédient'
        verbose_name_plural = 'Catégories ingrédients'
        ordering = ['ordre', 'nom']


class Ingredient(models.Model):
    nom = models.CharField(max_length=200)
    categorie = models.ForeignKey(
        CategorieIngredient, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='ingredients',
    )
    unite = models.CharField(max_length=20, blank=True, help_text='g, kg, cl, ml, pièce, boîte...')
    url_produit = models.URLField(blank=True, help_text='URL sur le site de courses (ex: courseu.com)')
    image_url = models.URLField(blank=True, help_text='URL miniature du produit (import HAR)')
    prix = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True,
        help_text='Prix unitaire indicatif (€)',
    )
    achat_systematique = models.BooleanField(default=False, help_text='Toujours dans la liste de courses')
    lie_a_plat = models.BooleanField(
        default=True, help_text='False = produit de fond (sel, beurre...) sans recette associée',
    )
    nom_court = models.CharField(
        max_length=100, blank=True,
        help_text='Nom affiché dans le planning (ex: Penne). Si vide, le nom complet est utilisé.',
    )

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = 'Ingrédient'
        ordering = ['nom']


class HistoriqueAchat(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='historique_achats')
    date_achat = models.DateField()
    liste_courses = models.ForeignKey(
        'ListeCourses', on_delete=models.SET_NULL, null=True, blank=True,
    )

    class Meta:
        ordering = ['-date_achat']


class Plat(models.Model):
    STATUT_CHOICES = [
        ('actif', 'Actif'), ('en_attente', 'En attente de validation'), ('inactif', 'Inactif'),
    ]

    nom = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    photo = models.ImageField(upload_to='plats/', null=True, blank=True)
    temps_preparation = models.IntegerField(default=30, help_text='Durée en minutes')
    ingredient_principal = models.CharField(
        max_length=30, choices=INGREDIENT_PRINCIPAL_CHOICES, default='autre',
        help_text='Utilisé pour éviter deux repas consécutifs similaires',
    )
    est_secours = models.BooleanField(
        default=False, help_text='Plat de secours (rapide, boîte de conserve…)',
    )
    est_obligatoire = models.BooleanField(
        default=False, help_text='Servi même si des membres le détestent — pas de plat de secours',
    )
    saison_debut = models.CharField(max_length=5, blank=True, help_text='Format MM-JJ, ex: 11-01')
    saison_fin = models.CharField(max_length=5, blank=True, help_text='Format MM-JJ, ex: 03-31')
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='actif')
    propose_par = models.ForeignKey(
        Membre, on_delete=models.SET_NULL, null=True, blank=True, related_name='plats_proposes',
    )
    ingredients = models.ManyToManyField(Ingredient, through='PlatIngredient')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom

    def est_en_saison(self, date=None):
        if not date:
            date = date_type.today()
        if not self.saison_debut or not self.saison_fin:
            return True
        today_mmdd = date.strftime('%m-%d')
        if self.saison_debut <= self.saison_fin:
            return self.saison_debut <= today_mmdd <= self.saison_fin
        # Saison enjambant janvier (ex: nov–mars)
        return today_mmdd >= self.saison_debut or today_mmdd <= self.saison_fin

    class Meta:
        verbose_name = 'Plat'
        ordering = ['nom']


class DisponibilitePlat(models.Model):
    """Jours & créneaux où ce plat peut être planifié."""
    plat = models.ForeignKey(Plat, on_delete=models.CASCADE, related_name='disponibilites')
    jour = models.CharField(max_length=20, choices=JOUR_CHOICES)
    creneau = models.CharField(max_length=10, choices=CRENEAU_CHOICES)

    def __str__(self):
        return f'{self.plat.nom} — {self.jour} {self.creneau}'

    class Meta:
        unique_together = ('plat', 'jour', 'creneau')
        verbose_name = 'Disponibilité plat'


class PlatIngredient(models.Model):
    plat = models.ForeignKey(Plat, on_delete=models.CASCADE, related_name='plat_ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantite_par_portion = models.FloatField(null=True, blank=True)
    unite = models.CharField(max_length=20, blank=True, help_text='Remplace l\'unité par défaut de l\'ingrédient')
    notes = models.CharField(max_length=200, blank=True, help_text='Ex: 1 ou 2 packs selon appétit')
    est_variant = models.BooleanField(
        default=False,
        help_text='Ingrédient interchangeable (ex: Penne/Farfalle). Le planning en choisit un par rotation.',
    )

    def __str__(self):
        return f'{self.plat.nom} — {self.ingredient.nom}'

    class Meta:
        unique_together = ('plat', 'ingredient')
        verbose_name = 'Ingrédient du plat'


class Preference(models.Model):
    membre = models.ForeignKey(Membre, on_delete=models.CASCADE, related_name='preferences')
    plat = models.ForeignKey(Plat, on_delete=models.CASCADE, related_name='preferences')
    note = models.CharField(max_length=10, choices=NOTE_CHOICES, default='neutre')

    def __str__(self):
        return f'{self.membre.prenom} — {self.plat.nom} : {self.note}'

    class Meta:
        unique_together = ('membre', 'plat')
        verbose_name = 'Préférence'


class DemandeModification(models.Model):
    """File d'attente des propositions soumises par les lecteurs."""
    TYPE_CHOICES = [
        ('preference', 'Changement de préférence'),
        ('nouveau_plat', 'Proposition de nouveau plat'),
    ]

    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    membre = models.ForeignKey(Membre, on_delete=models.CASCADE, related_name='demandes')

    # Pour les changements de préférence
    plat = models.ForeignKey(Plat, on_delete=models.SET_NULL, null=True, blank=True)
    ancienne_note = models.CharField(max_length=10, choices=NOTE_CHOICES, blank=True)
    nouvelle_note = models.CharField(max_length=10, choices=NOTE_CHOICES, blank=True)

    # Pour les propositions de nouveaux plats
    data_json = models.JSONField(null=True, blank=True)

    statut = models.CharField(max_length=20, choices=STATUT_DEMANDE_CHOICES, default='en_attente')
    message_admin = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    traite_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Demande de modification'
        ordering = ['-created_at']


class HistoriquePlat(models.Model):
    plat = models.ForeignKey(Plat, on_delete=models.CASCADE, related_name='historique')
    date = models.DateField()
    notes = models.CharField(max_length=500, blank=True)
    creneau_planning = models.ForeignKey(
        'CreneauPlanning', on_delete=models.SET_NULL, null=True, blank=True,
    )
    variant_choisi = models.ForeignKey(
        Ingredient, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='historique_comme_variant',
        help_text='Variant de cet ingrédient qui a été servi (ex: Penne)',
    )

    class Meta:
        ordering = ['-date']
        verbose_name = 'Historique plat'


class Config(models.Model):
    """Singleton — paramètres globaux de l'application."""
    jour_debut_semaine = models.CharField(
        max_length=20, choices=JOUR_CHOICES, default='samedi',
    )
    intervalle_min_jours = models.IntegerField(
        default=14, help_text='Nombre minimum de jours entre deux fois le même plat',
    )
    nb_plats_aimes_min = models.IntegerField(
        default=2, help_text='Nombre minimum de plats aimés par membre par semaine',
    )
    heure_midi = models.TimeField(default='12:30')
    heure_soir = models.TimeField(default='19:00')
    mot_de_passe_lecteur = models.CharField(max_length=100, default='famille')
    sms_actif = models.BooleanField(default=False)
    brevo_api_key = models.CharField(max_length=200, blank=True)
    coursesu_login = models.CharField(max_length=200, blank=True, help_text='Email de connexion coursesu.com')
    coursesu_password = models.CharField(max_length=200, blank=True, help_text='Mot de passe coursesu.com (stocké en clair)')

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    class Meta:
        verbose_name = 'Configuration'


class CreneauActif(models.Model):
    """Créneaux actifs dans la semaine (paramétrage)."""
    config = models.ForeignKey(Config, on_delete=models.CASCADE, related_name='creneaux_actifs')
    jour = models.CharField(max_length=20, choices=JOUR_CHOICES)
    creneau = models.CharField(max_length=10, choices=CRENEAU_CHOICES)

    class Meta:
        unique_together = ('config', 'jour', 'creneau')
        verbose_name = 'Créneau actif'
        ordering = ['jour', 'creneau']


class SemaineMenu(models.Model):
    STATUT_CHOICES = [('brouillon', 'Brouillon'), ('publie', 'Publié')]

    date_debut = models.DateField(help_text='Date du premier jour de la semaine')
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='brouillon')
    created_at = models.DateTimeField(auto_now_add=True)
    publie_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'Semaine du {self.date_debut.strftime("%d/%m/%Y")} ({self.get_statut_display()})'

    class Meta:
        ordering = ['-date_debut']
        verbose_name = 'Semaine menu'


class CreneauPlanning(models.Model):
    semaine = models.ForeignKey(SemaineMenu, on_delete=models.CASCADE, related_name='creneaux')
    date = models.DateField()
    creneau = models.CharField(max_length=10, choices=CRENEAU_CHOICES)
    plat_principal = models.ForeignKey(
        Plat, on_delete=models.SET_NULL, null=True, blank=True, related_name='creneaux_principal',
    )
    plat_secours = models.ForeignKey(
        Plat, on_delete=models.SET_NULL, null=True, blank=True, related_name='creneaux_secours',
    )
    membres_secours = models.ManyToManyField(
        Membre, blank=True, help_text='Membres qui mangent le plat de secours',
    )
    variant_choisi = models.ForeignKey(
        Ingredient, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='creneaux_variant',
        help_text='Variant retenu pour ce créneau (ex: Penne dans une Bolognaise)',
    )
    notes = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return f'{self.date} {self.creneau} — {self.plat_principal}'

    class Meta:
        unique_together = ('semaine', 'date', 'creneau')
        ordering = ['date', 'creneau']
        verbose_name = 'Créneau planning'


class ListeCourses(models.Model):
    STATUT_CHOICES = [
        ('brouillon', 'Brouillon'), ('validee', 'Validée'), ('archivee', 'Archivée'),
    ]

    semaine = models.OneToOneField(
        SemaineMenu, on_delete=models.SET_NULL, null=True, blank=True, related_name='liste_courses',
    )
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='brouillon')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_validation = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'Liste du {self.date_creation.strftime("%d/%m/%Y")}'

    class Meta:
        verbose_name = 'Liste de courses'
        ordering = ['-date_creation']


class ItemListeCourses(models.Model):
    SOURCE_CHOICES = [
        ('plat', 'Ingrédient de plat'),
        ('systematique', 'Achat systématique'),
        ('suggestion', 'Suggestion (rupture probable)'),
        ('manuel', 'Ajout manuel'),
    ]

    liste = models.ForeignKey(ListeCourses, on_delete=models.CASCADE, related_name='items')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.SET_NULL, null=True, blank=True)
    nom_libre = models.CharField(max_length=200, blank=True)
    quantite = models.FloatField(null=True, blank=True)
    unite = models.CharField(max_length=20, blank=True)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='manuel')
    coche = models.BooleanField(default=False)
    notes = models.CharField(max_length=200, blank=True)

    def nom_affiche(self):
        return self.ingredient.nom if self.ingredient else self.nom_libre

    class Meta:
        ordering = ['source', 'ingredient__categorie__ordre', 'ingredient__nom', 'nom_libre']
        verbose_name = 'Item liste de courses'

