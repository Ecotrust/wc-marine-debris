import sys
import site
import os

project = '/usr/local/apps/WCGA/wc-marine-debris/marine_debris/'
ve = '/usr/local/apps/WCGA/wc-marine-debris/env'
vepath = os.path.join(ve, 'lib/python2.6/site-packages')

prev_sys_path = list(sys.path)
# add the site-packages of our virtualenv as a site dir
site.addsitedir(vepath)
# add the app's directory to the PYTHONPATH
sys.path.append(project)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# reorder sys.path so new directories from the addsitedir show up first
new_sys_path = [p for p in sys.path if p not in prev_sys_path]
for item in new_sys_path:
    sys.path.remove(item)
sys.path[:0] = new_sys_path

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from django.core.handlers.wsgi import WSGIHandler
application = WSGIHandler()
