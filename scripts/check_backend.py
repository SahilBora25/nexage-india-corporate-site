"""Run isolated Django checks, migration consistency, and core tests."""

import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / 'backend'
sys.path.insert(0, str(BACKEND))

# Deliberately avoid connecting to any configured PostgreSQL deployment database.
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
os.environ['DJANGO_DEBUG'] = 'true'
os.environ['EMAIL_BACKEND'] = 'django.core.mail.backends.locmem.EmailBackend'
os.environ.pop('DATABASE_URL', None)

from django.conf import settings

settings.DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
}

import django

django.setup()

from django.core.management import call_command

print('Django system checks:')
call_command('check')
print('\nMigration consistency:')
call_command('makemigrations', check=True, dry_run=True)
print('\nBackend core tests:')
call_command('test', 'core', verbosity=2)
