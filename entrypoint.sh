#!/bin/bash
set -e

echo "==> Waiting for database..."
python -c "
import time, os, psycopg2, dj_database_url
db = dj_database_url.parse(os.environ['DATABASE_URL'])
for i in range(30):
    try:
        c = psycopg2.connect(host=db['HOST'], port=db['PORT'], user=db['USER'], password=db['PASSWORD'], dbname=db['NAME'])
        c.close()
        print('Database ready.')
        break
    except Exception as e:
        print(f'  Not ready ({i+1}/30): {e}')
        time.sleep(2)
"

echo "==> Running migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "==> Creating default superuser if needed..."
python manage.py shell -c "
import os
from django.contrib.auth import get_user_model
User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'Admin1234!')
email    = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@familymeal.local')
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f'  Superuser created: {username}')
else:
    print('  Superuser already exists.')
"

echo "==> Initialising app config..."
python manage.py shell -c "
from meals.models import Config, CategorieIngredient
Config.get()

defaults = [
    ('Fruits & Légumes', 1), ('Viandes & Charcuterie', 2), ('Poissons & Fruits de mer', 3),
    ('Produits laitiers', 4), ('Épicerie salée', 5), ('Épicerie sucrée', 6),
    ('Surgelés', 7), ('Boissons', 8), ('Hygiène & Entretien', 9), ('Autre', 10),
]
for nom, ordre in defaults:
    CategorieIngredient.objects.get_or_create(nom=nom, defaults={'ordre': ordre})
print('  Config & catégories initialisées.')
"

echo "==> Collecting static files..."
python manage.py collectstatic --noinput

exec "$@"
