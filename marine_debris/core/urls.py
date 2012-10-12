from django.conf.urls.defaults import *
from django.contrib.auth.views import *

from views import *

urlpatterns = patterns('',
    url(r'^accounts/login/$', login, {'template_name': 'login.html'}),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout_then_login', {'login_url': '/accounts/login/'}),
    url(r'^datasheets$', datasheets),
    url(r'^datasheet/edit/([A-Za-z0-9_-]+)$', edit_datasheet),
    url(r'^datasheet/csv_header/([A-Za-z0-9_-]+)$', bulk_csv_header),
    url(r'^datasheet/bulk_import/$', bulk_import),
    url(r'^events/get$', get_events),
    url(r'^events/get_locations$', get_locations),
    url(r'^events/([A-Za-z0-9_-]+)$', events),
    url(r'^events$', events),
    url(r'^event/create/location$', event_location),
    url(r'^event/create/save$', event_save),
    url(r'^event/create$', create_event),  
    url(r'^event/edit/([A-Za-z0-9_-]+)$', edit_event),
    url(r'^event/view/([A-Za-z0-9_-]+)$', view_event),
    url(r'^event/delete/([A-Za-z0-9_-]+)$', delete_event),
    url(r'^map-test$', map_test),
    url(r'^organizations$', organizations),
    url(r'^projects$', projects),
    url(r'^search/', include('haystack.urls')),
    url(r'^site/create$', create_site),  
    url(r'^site-media/(?P<path>.*)$','django.views.static.serve',{'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    url(r'^$', index )
)
