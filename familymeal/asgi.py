"""
ASGI config for familymeal project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'familymeal.settings')

application = get_asgi_application()
