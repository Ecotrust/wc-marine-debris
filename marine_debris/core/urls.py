from django.conf.urls.defaults import *
from django.contrib.auth.views import *

from views import *

urlpatterns = patterns('',
    url(r'^search/', include('haystack.urls')),
    (r'^accounts/login/$', login, {'template_name': 'login.html'}),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout_then_login', {'login_url': '/accounts/login/'}),
    (r'^$', index ),
    url(r'^events$', events),
    url(r'^event/create/data/([A-Za-z0-9_-]+)$', event_data),
    url(r'^event/create/location$', event_location),
    url(r'^event/create$', create_event),
    url(r'^event/edit/([A-Za-z0-9_-]+)$', edit_event),
    url(r'^event/view/([A-Za-z0-9_-]+)$', view_event),
    url(r'^event/delete/([A-Za-z0-9_-]+)$', delete_event),
    url(r'^organizations$', organizations),
    url(r'^projects$', projects),
    url(r'^datasheets$', datasheets),
    url(r'^site-media/(?P<path>.*)$','django.views.static.serve',{'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    url(r'^map-test$', map_test)
        
)