# local settings

import sys, os

DEBUG=True
TEMPLATE_DEBUG=DEBUG

ADMINS = (
    ('Your Name', 'name@email.com'),
)
SERVER_EMAIL='servername@email.com'
SEND_BROKEN_LINK_EMAILS=True

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        #'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        #'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Make this unique, and don't share it with anybody.
SECRET_KEY = ''