"""
WSGI config for eve_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eve_project.settings')

application = get_wsgi_application()

# Ensure database tables exist upon server startup (vital for ephemeral containers on Render)
try:
    from django.core.management import call_command
    from django.db import connection

    tables = connection.introspection.table_names()
    if 'auth_user' not in tables:
        print('[Startup] auth_user table missing. Running database migrations...')
        call_command('migrate', interactive=False)
        print('[Startup] Seeding initial accounts and demo data...')
        try:
            call_command('seed_demo_data')
        except Exception as seed_err:
            print(f'[Startup Warning] seed_demo_data failed: {seed_err}')
        print('[Startup] Database initialization complete.')
except Exception as exc:
    print(f'[Startup Warning] Auto-migrate check failed: {exc}')

