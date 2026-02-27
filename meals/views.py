import jwt
import json
from datetime import timedelta

from django.utils import timezone
from django.contrib.auth import authenticate
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.conf import settings

from .auth import IsAdminUser, IsReaderOrAdmin
from .models import (
    Membre, CategorieIngredient, Ingredient, HistoriqueAchat,
    Plat, PlatIngredient, Preference, DemandeModification,
    HistoriquePlat, Config, CreneauActif, SemaineMenu, CreneauPlanning,
    ListeCourses, ItemListeCourses,
)
from .serializers import (
    MembreSerializer, CategorieIngredientSerializer, IngredientSerializer,
    HistoriqueAchatSerializer, PlatListSerializer, PlatDetailSerializer, PlatWriteSerializer,
    PreferenceSerializer, DemandeModificationSerializer, HistoriquePlatSerializer,
    ConfigSerializer, ConfigWriteSerializer, CreneauPlanningSerializer,
    SemaineMenuSerializer, SemaineMenuListSerializer,
    ListeCoursesSerializer, ItemListeCoursesSerializer,
)


# ─────────────────────────────────────────
# Authentification
# ─────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
def admin_login(request):
    """Login admin Django — retourne un JWT SimpleJWT."""
    username = request.data.get('username', '')
    password = request.data.get('password', '')
    user = authenticate(request, username=username, password=password)
    if not user or not user.is_staff:
        return Response({'detail': 'Identifiants invalides ou accès refusé.'}, status=401)
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(user)
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'username': user.username,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def lecteur_login(request):
    """
    Login lecteur — valide le mot de passe partagé, retourne un JWT lecteur.
    """
    mot_de_passe = request.data.get('mot_de_passe', '')
    membre_id = request.data.get('membre_id')
    config = Config.get()

    if mot_de_passe != config.mot_de_passe_lecteur:
        return Response({'detail': 'Mot de passe incorrect.'}, status=401)

    if membre_id:
        if not Membre.objects.filter(pk=membre_id, actif=True).exists():
            return Response({'detail': 'Membre introuvable.'}, status=400)

    payload = {
        'role': 'lecteur',
        'membre_id': membre_id,
        'exp': timezone.now() + timedelta(hours=12),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return Response({'access': token, 'membre_id': membre_id})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def lecteur_choisir_membre(request):
    """Affecte un membre au token lecteur existant."""
    if not getattr(request.user, 'is_reader', False):
        return Response({'detail': 'Réservé aux lecteurs.'}, status=403)
    membre_id = request.data.get('membre_id')
    if not Membre.objects.filter(pk=membre_id, actif=True).exists():
        return Response({'detail': 'Membre introuvable.'}, status=400)
    payload = {
        'role': 'lecteur',
        'membre_id': membre_id,
        'exp': timezone.now() + timedelta(hours=12),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return Response({'access': token, 'membre_id': membre_id})


# ─────────────────────────────────────────
# Membres
# ─────────────────────────────────────────

class MembreViewSet(viewsets.ModelViewSet):
    queryset = Membre.objects.all()
    serializer_class = MembreSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsReaderOrAdmin()]
        return [IsAdminUser()]


# ─────────────────────────────────────────
# Ingrédients & Catégories
# ─────────────────────────────────────────

class CategorieIngredientViewSet(viewsets.ModelViewSet):
    queryset = CategorieIngredient.objects.all()
    serializer_class = CategorieIngredientSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsReaderOrAdmin()]
        return [IsAdminUser()]


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.select_related('categorie').all()
    serializer_class = IngredientSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsReaderOrAdmin()]
        return [IsAdminUser()]

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def enregistrer_achat(self, request, pk=None):
        ingredient = self.get_object()
        date_achat = request.data.get('date_achat')
        HistoriqueAchat.objects.create(ingredient=ingredient, date_achat=date_achat)
        return Response({'status': 'achat enregistré'})


# ─────────────────────────────────────────
# Plats
# ─────────────────────────────────────────

class PlatViewSet(viewsets.ModelViewSet):
    queryset = Plat.objects.prefetch_related('disponibilites', 'plat_ingredients__ingredient').all()

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return PlatWriteSerializer
        if self.action == 'list':
            return PlatListSerializer
        return PlatDetailSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsReaderOrAdmin()]
        if self.action == 'proposer':
            return [IsAuthenticated()]
        return [IsAdminUser()]

    def get_queryset(self):
        qs = super().get_queryset()
        if getattr(self.request.user, 'is_reader', False):
            qs = qs.filter(statut='actif')
        statut = self.request.query_params.get('statut')
        if statut:
            qs = qs.filter(statut=statut)
        est_secours = self.request.query_params.get('est_secours')
        if est_secours is not None:
            qs = qs.filter(est_secours=est_secours.lower() == 'true')
        return qs

    @action(detail=True, methods=['get'], permission_classes=[IsReaderOrAdmin])
    def historique(self, request, pk=None):
        plat = self.get_object()
        s = HistoriquePlatSerializer(plat.historique.all()[:20], many=True)
        return Response(s.data)

    @action(detail=False, methods=['post'], url_path='proposer')
    def proposer(self, request):
        membre_id = getattr(request.user, 'membre_id', None)
        if not membre_id:
            return Response({'detail': 'Vous devez d\'abord choisir votre profil.'}, status=400)
        DemandeModification.objects.create(
            type='nouveau_plat',
            membre_id=membre_id,
            data_json=request.data,
        )
        return Response({'status': 'Proposition soumise, en attente de validation.'}, status=201)


# ─────────────────────────────────────────
# Préférences
# ─────────────────────────────────────────

class PreferenceViewSet(viewsets.ModelViewSet):
    queryset = Preference.objects.select_related('membre', 'plat').all()
    serializer_class = PreferenceSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'proposer_modification'):
            return [IsReaderOrAdmin()]
        return [IsAdminUser()]

    def get_queryset(self):
        qs = super().get_queryset()
        membre_id = self.request.query_params.get('membre')
        if membre_id:
            qs = qs.filter(membre_id=membre_id)
        plat_id = self.request.query_params.get('plat')
        if plat_id:
            qs = qs.filter(plat_id=plat_id)
        return qs

    @action(detail=False, methods=['post'], url_path='proposer')
    def proposer_modification(self, request):
        membre_id = getattr(request.user, 'membre_id', None)
        if not membre_id:
            return Response({'detail': 'Vous devez d\'abord choisir votre profil.'}, status=400)

        plat_id = request.data.get('plat')
        nouvelle_note = request.data.get('note')
        if not plat_id or not nouvelle_note:
            return Response({'detail': 'plat et note sont requis.'}, status=400)

        pref = Preference.objects.filter(membre_id=membre_id, plat_id=plat_id).first()
        ancienne_note = pref.note if pref else 'neutre'

        DemandeModification.objects.create(
            type='preference',
            membre_id=membre_id,
            plat_id=plat_id,
            ancienne_note=ancienne_note,
            nouvelle_note=nouvelle_note,
        )
        return Response({'status': 'Proposition soumise, en attente de validation.'}, status=201)


# ─────────────────────────────────────────
# Demandes de modification
# ─────────────────────────────────────────

class DemandeModificationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DemandeModification.objects.select_related('membre', 'plat').all()
    serializer_class = DemandeModificationSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        qs = super().get_queryset()
        statut = self.request.query_params.get('statut', 'en_attente')
        if statut:
            qs = qs.filter(statut=statut)
        return qs

    @action(detail=True, methods=['post'])
    def valider(self, request, pk=None):
        demande = self.get_object()
        if demande.statut != 'en_attente':
            return Response({'detail': 'Demande déjà traitée.'}, status=400)

        if demande.type == 'preference':
            Preference.objects.update_or_create(
                membre=demande.membre,
                plat=demande.plat,
                defaults={'note': demande.nouvelle_note},
            )
        elif demande.type == 'nouveau_plat':
            data = demande.data_json or {}
            Plat.objects.create(
                nom=data.get('nom', 'Nouveau plat'),
                description=data.get('description', ''),
                statut='actif',
                propose_par=demande.membre,
            )

        demande.statut = 'validee'
        demande.traite_at = timezone.now()
        demande.save()
        return Response({'status': 'Demande validée.'})

    @action(detail=True, methods=['post'])
    def refuser(self, request, pk=None):
        demande = self.get_object()
        if demande.statut != 'en_attente':
            return Response({'detail': 'Demande déjà traitée.'}, status=400)
        demande.statut = 'refusee'
        demande.message_admin = request.data.get('message', '')
        demande.traite_at = timezone.now()
        demande.save()
        return Response({'status': 'Demande refusée.'})


# ─────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────

@api_view(['GET', 'PUT', 'PATCH'])
def config_view(request):
    config = Config.get()
    if request.method == 'GET':
        perm = IsReaderOrAdmin()
        if not perm.has_permission(request, None):
            return Response(status=403)
        return Response(ConfigSerializer(config).data)

    perm = IsAdminUser()
    if not perm.has_permission(request, None):
        return Response(status=403)

    s = ConfigWriteSerializer(config, data=request.data, partial=(request.method == 'PATCH'))
    s.is_valid(raise_exception=True)
    s.save()
    return Response(ConfigSerializer(Config.get()).data)


# ─────────────────────────────────────────
# Planning (Semaines Menu)
# ─────────────────────────────────────────

class SemaineMenuViewSet(viewsets.ModelViewSet):
    queryset = SemaineMenu.objects.prefetch_related(
        'creneaux__plat_principal', 'creneaux__plat_secours', 'creneaux__membres_secours',
    ).all()

    def get_serializer_class(self):
        if self.action == 'list':
            return SemaineMenuListSerializer
        return SemaineMenuSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'courante'):
            return [IsReaderOrAdmin()]
        return [IsAdminUser()]

    @action(detail=False, methods=['get'])
    def courante(self, request):
        semaine = SemaineMenu.objects.filter(statut='publie').order_by('-date_debut').first()
        if not semaine:
            return Response({'detail': 'Aucun planning publié.'}, status=404)
        return Response(SemaineMenuSerializer(semaine).data)

    @action(detail=True, methods=['post'])
    def publier(self, request, pk=None):
        semaine = self.get_object()
        semaine.statut = 'publie'
        semaine.publie_at = timezone.now()
        semaine.save()
        for creneau in semaine.creneaux.filter(plat_principal__isnull=False):
            HistoriquePlat.objects.get_or_create(
                plat=creneau.plat_principal,
                date=creneau.date,
                defaults={'creneau_planning': creneau},
            )
        from .tasks import programmer_alertes_semaine
        programmer_alertes_semaine.delay(semaine.id)
        return Response(SemaineMenuSerializer(semaine).data)

    @action(detail=True, methods=['post'])
    def depublier(self, request, pk=None):
        semaine = self.get_object()
        semaine.statut = 'brouillon'
        semaine.publie_at = None
        semaine.save()
        return Response(SemaineMenuSerializer(semaine).data)

    @action(detail=False, methods=['post'])
    def generer(self, request):
        from .planning_generator import generer_planning_auto
        semaine_id = request.data.get('semaine_id')
        if not semaine_id:
            return Response({'detail': 'semaine_id requis.'}, status=400)
        semaine = SemaineMenu.objects.get(pk=semaine_id)
        generer_planning_auto(semaine)
        return Response(SemaineMenuSerializer(semaine).data)

    @action(detail=False, methods=['post'])
    def candidats(self, request):
        from .planning_generator import get_top3_candidats
        semaine_id = request.data.get('semaine_id')
        date_str = request.data.get('date')
        creneau = request.data.get('creneau')
        if not all([semaine_id, date_str, creneau]):
            return Response({'detail': 'semaine_id, date et creneau sont requis.'}, status=400)
        plats = get_top3_candidats(semaine_id, date_str, creneau)
        return Response(PlatListSerializer(plats, many=True).data)


# ─────────────────────────────────────────
# Créneaux Planning (modification manuelle)
# ─────────────────────────────────────────

class CreneauPlanningViewSet(viewsets.ModelViewSet):
    queryset = CreneauPlanning.objects.select_related(
        'plat_principal', 'plat_secours',
    ).prefetch_related('membres_secours').all()
    serializer_class = CreneauPlanningSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        qs = super().get_queryset()
        semaine_id = self.request.query_params.get('semaine')
        if semaine_id:
            qs = qs.filter(semaine_id=semaine_id)
        return qs


# ─────────────────────────────────────────
# Liste de Courses
# ─────────────────────────────────────────

class ListeCoursesViewSet(viewsets.ModelViewSet):
    queryset = ListeCourses.objects.prefetch_related('items__ingredient__categorie').all()
    serializer_class = ListeCoursesSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsReaderOrAdmin()]
        return [IsAdminUser()]

    @action(detail=False, methods=['post'])
    def generer(self, request):
        from datetime import date as date_type, timedelta
        from collections import defaultdict

        semaine_id = request.data.get('semaine_id')
        semaine = SemaineMenu.objects.get(pk=semaine_id)

        ListeCourses.objects.filter(semaine=semaine).delete()
        liste = ListeCourses.objects.create(semaine=semaine)

        ingredients_plats = defaultdict(lambda: {'quantite': 0, 'unite': '', 'ingredient': None})
        for creneau in semaine.creneaux.filter(plat_principal__isnull=False):
            for pi in creneau.plat_principal.plat_ingredients.select_related('ingredient'):
                key = pi.ingredient_id
                if pi.quantite_par_portion:
                    ingredients_plats[key]['quantite'] += pi.quantite_par_portion
                ingredients_plats[key]['unite'] = pi.unite or pi.ingredient.unite
                ingredients_plats[key]['ingredient'] = pi.ingredient

        for ing_id, info in ingredients_plats.items():
            ItemListeCourses.objects.create(
                liste=liste,
                ingredient=info['ingredient'],
                quantite=info['quantite'] or None,
                unite=info['unite'],
                source='plat',
            )

        for ingredient in Ingredient.objects.filter(achat_systematique=True):
            if ingredient.id not in ingredients_plats:
                ItemListeCourses.objects.create(
                    liste=liste, ingredient=ingredient, source='systematique',
                )

        aujourd_hui = date_type.today()
        for ingredient in Ingredient.objects.filter(
            lie_a_plat=False, achat_systematique=False,
        ).prefetch_related('historique_achats'):
            achats = list(ingredient.historique_achats.values_list('date_achat', flat=True)[:5])
            if len(achats) < 2:
                continue
            deltas = [(achats[i] - achats[i + 1]).days for i in range(len(achats) - 1)]
            freq_moyenne = sum(deltas) / len(deltas)
            prochain_besoin = achats[0] + timedelta(days=freq_moyenne)
            if prochain_besoin <= aujourd_hui + timedelta(days=7):
                ItemListeCourses.objects.create(
                    liste=liste, ingredient=ingredient, source='suggestion',
                )

        return Response(ListeCoursesSerializer(liste).data, status=201)

    @action(detail=True, methods=['post'])
    def valider(self, request, pk=None):
        from datetime import date as date_type
        liste = self.get_object()
        liste.statut = 'validee'
        liste.date_validation = timezone.now()
        liste.save()
        today = date_type.today()
        for item in liste.items.filter(ingredient__isnull=False, coche=True):
            HistoriqueAchat.objects.create(
                ingredient=item.ingredient, date_achat=today, liste_courses=liste,
            )
        return Response(ListeCoursesSerializer(liste).data)


class ItemListeCoursesViewSet(viewsets.ModelViewSet):
    queryset = ItemListeCourses.objects.all()
    serializer_class = ItemListeCoursesSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        qs = super().get_queryset()
        liste_id = self.request.query_params.get('liste')
        if liste_id:
            qs = qs.filter(liste_id=liste_id)
        return qs

    @action(detail=True, methods=['patch'])
    def cocher(self, request, pk=None):
        item = self.get_object()
        item.coche = not item.coche
        item.save()
        return Response(ItemListeCoursesSerializer(item).data)


# ─────────────────────────────────────────
# Outils — Import HAR / Scraping Coursesu
# ─────────────────────────────────────────

def _coursesu_product_url(external_id: str) -> str:
    """URL canonique utilisée comme clé de déduplication en base."""
    return f'https://www.coursesu.com/p/{external_id}'


def _already_imported_ids() -> set:
    """Renvoie l'ensemble des external_id déjà présents dans Ingredient."""
    ids = set()
    for url in Ingredient.objects.filter(
        url_produit__startswith='https://www.coursesu.com/p/'
    ).values_list('url_produit', flat=True):
        pid = url.split('/')[-1]
        if pid:
            ids.add(pid)
    return ids


@api_view(['POST'])
@permission_classes([IsAdminUser])
@parser_classes([MultiPartParser])
def parse_har(request):
    """Reçoit un fichier HAR, extrait les produits favoris Coursesu non encore importés."""
    from bs4 import BeautifulSoup
    har_file = request.FILES.get('har')
    if not har_file:
        return Response({'detail': 'Fichier HAR manquant.'}, status=400)
    try:
        har = json.loads(har_file.read().decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        return Response({'detail': f'Fichier HAR invalide : {e}'}, status=400)

    products = {}
    for entry in har.get('log', {}).get('entries', []):
        url = entry.get('request', {}).get('url', '')
        if 'mes-listes' not in url or 'isPref=true' not in url:
            continue
        body = entry.get('response', {}).get('content', {}).get('text', '')
        if not body:
            continue
        try:
            soup = BeautifulSoup(body, 'html.parser')
        except Exception:
            continue
        for item in soup.find_all(attrs={'data-info-id': True}):
            pid = item.get('data-info-id', '').strip()
            name = item.get('data-info-name', '').strip()
            img = item.get('data-info-img', '').strip()
            img = img.replace('sw=90&sh=90', 'sw=200&sh=200')
            if pid and name:
                products[pid] = {
                    'external_id': pid,
                    'name': name,
                    'image_url': img,
                    'product_url': _coursesu_product_url(pid),
                }

    already = _already_imported_ids()
    new_products = [p for pid, p in products.items() if pid not in already]
    return Response({
        'products': new_products,
        'count': len(new_products),
        'total': len(products),
        'already_imported': len(already & products.keys()),
    })


@api_view(['POST'])
@permission_classes([IsAdminUser])
def scrape_coursesu(request):
    """Se connecte directement à coursesu.com et retourne les favoris non encore importés."""
    import re as _re
    import requests as req
    from bs4 import BeautifulSoup

    config = Config.get()
    login_email = config.coursesu_login.strip()
    password = config.coursesu_password.strip()
    if not login_email or not password:
        return Response(
            {'detail': 'Identifiants coursesu.com non configurés dans les Paramètres.'},
            status=400,
        )

    # Headers complets imitant Chrome 122 pour passer les protections anti-bot
    BROWSER_HEADERS = {
        'User-Agent': (
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        ),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Sec-Ch-Ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Linux"',
        'DNT': '1',
    }

    session = req.Session()
    session.headers.update(BROWSER_HEADERS)

    # ── Étape 1 : charger la page d'accueil pour obtenir les cookies de session ──
    try:
        r = session.get('https://www.coursesu.com/', timeout=20)
        # On ignore le statut (certains CDN renvoient 403 même pour la home sans cookies)
    except Exception as e:
        return Response({'detail': f'Impossible de contacter coursesu.com : {e}'}, status=503)

    # ── Étape 2 : récupérer la page de login pour le CSRF ──────────────
    try:
        login_headers = {**BROWSER_HEADERS, 'Referer': 'https://www.coursesu.com/'}
        r = session.get('https://www.coursesu.com/login', timeout=20, headers=login_headers)
        if r.status_code == 403:
            return Response(
                {'detail': (
                    'coursesu.com bloque la connexion automatisée (erreur 403). '
                    'Utilisez l\'import via fichier HAR à la place : '
                    'F12 → Réseau → recharger la page "Mes listes" → clic droit → Enregistrer en HAR.'
                )},
                status=503,
            )
        r.raise_for_status()
    except req.exceptions.HTTPError:
        raise
    except Exception as e:
        return Response({'detail': f'Impossible de contacter coursesu.com : {e}'}, status=503)

    soup = BeautifulSoup(r.text, 'html.parser')

    # Trouver le formulaire de login (contient un champ e-mail)
    login_form = None
    for f in soup.find_all('form'):
        if f.find('input', {'name': _re.compile(r'(loginEmail|email)', _re.I)}):
            login_form = f
            break

    if not login_form:
        return Response({'detail': 'Formulaire de connexion introuvable sur coursesu.com.'}, status=503)

    action = login_form.get('action', '')
    if not action.startswith('http'):
        action = 'https://www.coursesu.com' + action

    # Collecter tous les champs cachés (CSRF, tokens, etc.)
    post_data: dict = {}
    for inp in login_form.find_all('input'):
        name = inp.get('name')
        val = inp.get('value', '')
        if name:
            post_data[name] = val

    # Injecter les identifiants
    for key in list(post_data.keys()):
        if 'email' in key.lower():
            post_data[key] = login_email
        if 'password' in key.lower():
            post_data[key] = password

    # ── Étape 3 : soumettre le formulaire ──────────────────────────────
    try:
        post_headers = {
            **BROWSER_HEADERS,
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://www.coursesu.com',
            'Referer': 'https://www.coursesu.com/login',
            'Sec-Fetch-Site': 'same-origin',
        }
        r = session.post(action, data=post_data, timeout=20, allow_redirects=True, headers=post_headers)
        r.raise_for_status()
    except Exception as e:
        return Response({'detail': f'Erreur lors de la connexion : {e}'}, status=503)

    # Vérifier l'échec de connexion (URL de login toujours présente)
    if '/login' in r.url.lower() and 'mon-compte' not in r.url.lower():
        return Response(
            {'detail': 'Connexion échouée. Vérifiez vos identifiants dans les Paramètres.'},
            status=401,
        )

    # ── Étape 4 : scraper les pages de favoris ─────────────────────────
    products: dict = {}
    offset = 0
    sz = 20
    ajax_headers = {
        **BROWSER_HEADERS,
        'Accept': 'text/html, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'https://www.coursesu.com/mon-compte/mes-listes',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
    }
    while True:
        fav_url = (
            f'https://www.coursesu.com/mon-compte/mes-listes'
            f'?srule=shoplist-default&isPref=true'
            f'&start={offset}&sz={sz}&listProducts=true&format=ajax'
        )
        try:
            r = session.get(fav_url, timeout=20, headers=ajax_headers)
        except Exception:
            break
        if not r.ok or not r.text.strip():
            break
        page_soup = BeautifulSoup(r.text, 'html.parser')
        items = page_soup.find_all(attrs={'data-info-id': True})
        if not items:
            break
        for item in items:
            pid = item.get('data-info-id', '').strip()
            name = item.get('data-info-name', '').strip()
            img = item.get('data-info-img', '').strip()
            img = img.replace('sw=90&sh=90', 'sw=200&sh=200')
            if pid and name:
                products[pid] = {
                    'external_id': pid,
                    'name': name,
                    'image_url': img,
                    'product_url': _coursesu_product_url(pid),
                }
        if len(items) < sz:
            break
        offset += sz

    if not products:
        return Response(
            {'detail': 'Aucun produit trouvé. La liste des favoris est peut-être vide.'},
            status=200,
        )

    # ── Étape 5 : filtrer les déjà importés ────────────────────────────
    already = _already_imported_ids()
    new_products = [p for pid, p in products.items() if pid not in already]
    return Response({
        'products': new_products,
        'count': len(new_products),
        'total': len(products),
        'already_imported': len(already & products.keys()),
    })


@api_view(['POST'])
@permission_classes([IsAdminUser])
def import_ingredients(request):
    """Importe une liste de produits sélectionnés en ingrédients."""
    items = request.data.get('items', [])
    if not isinstance(items, list):
        return Response({'detail': 'Le champ "items" doit être une liste.'}, status=400)
    created_names, skipped_names = [], []
    for item in items:
        name = (item.get('name') or '').strip()
        if not name:
            continue
        product_url = (item.get('product_url') or '').strip()
        achat_sys = bool(item.get('achat_systematique', False))
        ing, was_created = Ingredient.objects.get_or_create(
            nom__iexact=name,
            defaults={
                'nom': name,
                'url_produit': product_url,
                'achat_systematique': achat_sys,
            },
        )
        if was_created:
            created_names.append(ing.nom)
        else:
            skipped_names.append(ing.nom)
    return Response({
        'created': len(created_names),
        'skipped': len(skipped_names),
        'created_names': created_names,
    })
