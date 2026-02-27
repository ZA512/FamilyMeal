"""
Algorithme de génération du planning hebdomadaire.
"""
from datetime import date, timedelta
from collections import defaultdict
import random

from .models import (
    Plat, DisponibilitePlat, Preference, HistoriquePlat,
    SemaineMenu, CreneauPlanning, Config, Membre, JOUR_CHOICES,
)

JOURS_FR_TO_WEEKDAY = {
    'lundi': 0, 'mardi': 1, 'mercredi': 2, 'jeudi': 3,
    'vendredi': 4, 'samedi': 5, 'dimanche': 6,
}
WEEKDAY_TO_JOUR_FR = {v: k for k, v in JOURS_FR_TO_WEEKDAY.items()}


def get_slots_semaine(semaine: SemaineMenu, config: Config):
    """Retourne la liste des créneaux actifs pour la semaine, dans l'ordre."""
    creneaux_actifs = set(
        (ca.jour, ca.creneau) for ca in config.creneaux_actifs.all()
    )
    if not creneaux_actifs:
        # Valeurs par défaut si rien n'est configuré
        creneaux_actifs = {
            ('samedi', 'soir'), ('dimanche', 'midi'), ('dimanche', 'soir'),
            ('lundi', 'soir'), ('mardi', 'soir'), ('mercredi', 'soir'),
            ('jeudi', 'soir'), ('vendredi', 'soir'),
        }

    slots = []
    date_debut = semaine.date_debut
    # On itère sur 7 jours à partir de la date de début
    for i in range(7):
        d = date_debut + timedelta(days=i)
        jour_fr = WEEKDAY_TO_JOUR_FR[d.weekday()]
        for creneau in ['midi', 'soir']:
            if (jour_fr, creneau) in creneaux_actifs:
                slots.append({'date': d, 'jour': jour_fr, 'creneau': creneau})

    return sorted(slots, key=lambda s: (s['date'], 0 if s['creneau'] == 'midi' else 1))


def get_plats_recemment_cuisines(intervalle_jours: int, date_ref: date):
    """Retourne les IDs des plats cuisinés dans les X derniers jours."""
    seuil = date_ref - timedelta(days=intervalle_jours)
    return set(
        HistoriquePlat.objects.filter(date__gte=seuil).values_list('plat_id', flat=True)
    )


def get_candidats_pour_slot(
    slot: dict,
    plats_deja_places: list,  #[(plat, date, creneau), ...]
    plats_recents: set,
    config: Config,
    membres_actifs: list,
    preferences: dict,  # {(membre_id, plat_id): note}
):
    """
    Retourne une liste scorée de plats candidats pour un créneau donné.
    Score positif = meilleur choix.
    """
    jour = slot['jour']
    creneau = slot['creneau']
    date_slot = slot['date']

    # Plats disponibles ce jour/créneau
    dispo_ids = set(
        DisponibilitePlat.objects.filter(jour=jour, creneau=creneau)
        .values_list('plat_id', flat=True)
    )

    # Plats actifs, non secours, en saison
    candidats = []
    for plat in Plat.objects.filter(statut='actif', est_secours=False).prefetch_related('historique'):
        if plat.id in dispo_ids and plat.est_en_saison(date_slot):
            candidats.append(plat)

    # Filtrer les plats récemment cuisinés
    candidats_filtres = [p for p in candidats if p.id not in plats_recents]
    if not candidats_filtres:
        candidats_filtres = candidats  # Fallback si trop restrictif

    # Éviter l'ingrédient principal identique au créneau précédent
    dernier_ingredient = None
    if plats_deja_places:
        dernier_plat = plats_deja_places[-1][0]
        dernier_ingredient = dernier_plat.ingredient_principal

    scored = []
    for plat in candidats_filtres:
        # Pénalité si même ingrédient principal que le créneau précédent
        if dernier_ingredient and plat.ingredient_principal == dernier_ingredient:
            continue

        score = 0

        # Favoriser les plats aimés par le plus grand nombre
        nb_aime = sum(
            1 for m in membres_actifs
            if preferences.get((m.id, plat.id), 'neutre') == 'aime'
        )
        nb_deteste = sum(
            1 for m in membres_actifs
            if preferences.get((m.id, plat.id), 'neutre') == 'deteste'
        )
        score += nb_aime * 2
        score -= nb_deteste * 1

        # Favoriser les plats les moins récemment cuisinés
        dernier = plat.historique.first()
        if dernier:
            jours_depuis = (date_slot - dernier.date).days
            score += min(jours_depuis // 7, 10)  # cap à 10
        else:
            score += 15  # Jamais cuisiné → priorité

        # Petite randomisation pour éviter les résultats trop déterministes
        score += random.uniform(-0.5, 0.5)

        scored.append((plat, score))

    scored.sort(key=lambda x: -x[1])
    return scored


def trouver_plat_secours(membres_detestent: list, plats_deja_places_ids: set):
    """Trouve le meilleur plat de secours disponible."""
    secours_candidats = Plat.objects.filter(statut='actif', est_secours=True)
    if plats_deja_places_ids:
        # Éviter de répéter le même plat de secours
        secours_candidats = secours_candidats.exclude(id__in=plats_deja_places_ids)
    return secours_candidats.first()


def generer_planning_auto(semaine: SemaineMenu):
    """
    Génère automatiquement le planning pour une semaine.
    Retourne la liste des créneaux créés/modifiés.
    """
    config = Config.get()
    membres_actifs = list(Membre.objects.filter(actif=True))

    # Construire le dictionnaire de préférences
    prefs_qs = Preference.objects.filter(membre__actif=True).select_related('membre', 'plat')
    preferences = {(p.membre_id, p.plat_id): p.note for p in prefs_qs}

    slots = get_slots_semaine(semaine, config)
    plats_recents = get_plats_recemment_cuisines(config.intervalle_min_jours, semaine.date_debut)

    plats_deja_places = []  # (plat, date, creneau)
    plats_secours_deja_places_ids = set()
    creneaux_crees = []

    # Tracker les plats aimés par membre sur la semaine
    plats_aimes_par_membre = defaultdict(set)

    for slot in slots:
        scored = get_candidats_pour_slot(
            slot, plats_deja_places, plats_recents, config, membres_actifs, preferences,
        )

        if not scored:
            plat_choisi = None
        else:
            plat_choisi = scored[0][0]

        plat_secours = None
        membres_secours_ids = []

        if plat_choisi and not plat_choisi.est_obligatoire:
            # Membres qui détestent ce plat
            membres_qui_detestent = [
                m for m in membres_actifs
                if preferences.get((m.id, plat_choisi.id), 'neutre') == 'deteste'
            ]
            if membres_qui_detestent:
                plat_secours = trouver_plat_secours(
                    membres_qui_detestent, plats_secours_deja_places_ids,
                )
                membres_secours_ids = [m.id for m in membres_qui_detestent]
                if plat_secours:
                    plats_secours_deja_places_ids.add(plat_secours.id)

        # Enregistrer le créneau
        creneau_obj, _ = CreneauPlanning.objects.update_or_create(
            semaine=semaine,
            date=slot['date'],
            creneau=slot['creneau'],
            defaults={
                'plat_principal': plat_choisi,
                'plat_secours': plat_secours,
            },
        )
        if membres_secours_ids:
            creneau_obj.membres_secours.set(membres_secours_ids)
        else:
            creneau_obj.membres_secours.clear()

        creneaux_crees.append(creneau_obj)

        if plat_choisi:
            plats_deja_places.append((plat_choisi, slot['date'], slot['creneau']))
            plats_recents.add(plat_choisi.id)
            for m in membres_actifs:
                if preferences.get((m.id, plat_choisi.id), 'neutre') == 'aime':
                    plats_aimes_par_membre[m.id].add(plat_choisi.id)

    return creneaux_crees


def get_top3_candidats(semaine_id: int, date_str: str, creneau: str):
    """
    Mode interactif : retourne les 3 meilleurs candidats pour un créneau donné,
    en tenant compte de ce qui est déjà placé dans la semaine.
    """
    from datetime import date as date_type
    from .serializers import PlatListSerializer

    semaine = SemaineMenu.objects.get(pk=semaine_id)
    config = Config.get()
    membres_actifs = list(Membre.objects.filter(actif=True))

    prefs_qs = Preference.objects.filter(membre__actif=True)
    preferences = {(p.membre_id, p.plat_id): p.note for p in prefs_qs}

    plats_recents = get_plats_recemment_cuisines(config.intervalle_min_jours, semaine.date_debut)

    # Récupérer ce qui est déjà placé dans la semaine
    creneaux_existants = list(
        semaine.creneaux.filter(plat_principal__isnull=False)
        .order_by('date', 'creneau')
        .select_related('plat_principal')
    )
    plats_deja_places = [
        (c.plat_principal, c.date, c.creneau) for c in creneaux_existants
    ]

    slot_date = date_type.fromisoformat(date_str)
    jour_fr = WEEKDAY_TO_JOUR_FR[slot_date.weekday()]

    slot = {'date': slot_date, 'jour': jour_fr, 'creneau': creneau}
    scored = get_candidats_pour_slot(
        slot, plats_deja_places, plats_recents, config, membres_actifs, preferences,
    )

    return [plat for plat, _ in scored[:3]]
