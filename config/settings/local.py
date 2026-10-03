"""
Development settings for CareerHunt.
"""
from .base import *  # noqa: F403

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0", "testserver"]

# Ensure debug static files storage during local dev
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
