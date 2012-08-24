from django.conf.urls.defaults import *
from django.contrib.auth.views import *

from views import *

urlpatterns = patterns('',                      
    (r'^accounts/login/$', login, {'template_name': 'login.html'}),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout_then_login', {'login_url': '/accounts/login/'}),
    (r'^$', index ),
    url(r'^events$', events),
    url(r'^event/create$', create_event),
    url(r'^event/edit/([A-Za-z0-9_-]+)$', edit_event),
    url(r'^event/view/([A-Za-z0-9_-]+)$', view_event),
    url(r'^organizations$', organizations),
    url(r'^projects$', projects),
    url(r'^datasheets$', datasheets),
    url(r'^datasheet/fill/([A-Za-z0-9_-]+)/([A-Za-z0-9_-]+)$', fill_datasheet),
        
)