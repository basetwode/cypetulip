#!/bin/bash

#chown -R app:app /opt/cypetulip
#chown -R app:app /var/cypetulip
python manage.py migrate
python manage.py createcachetable
python manage.py compilemessages --ignore=venv/*
python manage.py collectstatic --noinput
exec "$@"