"""Lightweight test settings that override database to use SQLite in-memory.

This file imports the project's normal settings and then overrides the
DATABASES configuration so Django's test runner doesn't try to contact the
remote Supabase/Postgres database during tests. Use by running:

    python manage.py test --settings=weather_prediction.test_settings

It's intentionally small and reuses most settings from the real settings
module to keep behavior consistent for tests that don't need the remote DB.
"""

from .settings import *  # noqa: F401,F403

# Use an in-memory SQLite DB for tests to avoid network calls to remote DBs.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Running tests in-memory; ensure migrations behave deterministically
# (Django will create the test DB automatically).
