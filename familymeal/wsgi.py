"""
WSGI config for familymeal project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'familymeal.settings')

application = get_wsgi_application()
