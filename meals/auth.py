import jwt
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import permissions


class ReaderUser:
    """Objet utilisateur minimal pour les lecteurs authentifiés."""
    is_authenticated = True
    is_staff = False
    is_reader = True

    def __init__(self, membre_id=None):
        self.membre_id = membre_id
        self.pk = f'reader:{membre_id}'


class ReaderJWTAuthentication(BaseAuthentication):
    """Authentification par token lecteur (JWT signé, rôle='lecteur')."""

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Reader '):
            return None

        token = auth_header[7:]
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            if payload.get('role') != 'lecteur':
                raise AuthenticationFailed('Token invalide.')
            return (ReaderUser(membre_id=payload.get('membre_id')), token)
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token expiré.')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Token invalide.')


class IsAdminUser(permissions.BasePermission):
    """Seul le superuser Django a accès."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class IsReaderOrAdmin(permissions.BasePermission):
    """Lecteur ou admin."""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return True


class IsReader(permissions.BasePermission):
    """Lecteur uniquement (pas admin seulement)."""
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated
            and getattr(request.user, 'is_reader', False)
        )
