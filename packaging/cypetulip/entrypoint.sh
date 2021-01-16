#!/bin/bash

python manage.py migrate
python manage.py createcachetable
python manage.py compilemessages --ignore=venv/*
python manage.py collectstatic --noinput
daphne -b 0.0.0.0 -p 8000 home.asgi:application