#!/usr/bin/env bash

python manage.py migrate

if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] ; then
    python manage.py createsuperuser --no-input
fi

python manage.py initiate_player_data -l -c 5
python manage.py adjust_ranks -c 5

python manage.py tailwind install
python manage.py tailwind build
python manage.py collectstatic --noinput

gunicorn projectmarswar.wsgi --bind 0.0.0.0:8080 --workers 3