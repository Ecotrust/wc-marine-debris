import sys
import os

sys.stdout = sys.stderr

sys.path.append('/usr/local/django-trunk')
sys.path.append('/usr/local/django-apps')
sys.path.append('/usr/local/apps')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
