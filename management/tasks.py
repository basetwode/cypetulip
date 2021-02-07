from celery import shared_task
from django.core import management


@shared_task
def clean_database_sessions():
    management.call_command('clean_sessions', verbosity=0)
    print("Sessions cleaned")
