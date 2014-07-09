# Orignal version taken from http://www.djangosnippets.org/snippets/186/
# Original author: udfalkso
# Modified by: Shwagroo Team and Gun.io
# pulled from gun.io/blog/fast-as-fuck-django-part-1-using-a-profiler/
 
import sys
import os
import re
import datetime
import cProfile
import tempfile
import StringIO
 
from django.conf import settings
 
words_re = re.compile( r'\s+' )
 
group_prefix_re = [
    re.compile( "^.*/django/[^/]+" ),
    re.compile( "^(.*)/[^/]+$" ), # extract module path
    re.compile( ".*" ),           # catch strange entries
]
 
class ProfileMiddleware(object):
    """
    Displays hotshot profiling for any view.
    http://yoursite.com/yourview/?prof
 
    Add the "prof" key to query string by appending ?prof (or &prof=)
    and you'll see the profiling results in your browser.
    It's set up to only be available in django's debug mode, is available for superuser otherwise,
    but you really shouldn't add this middleware to any production configuration.
 
    WARNING: It uses hotshot profiler which is not thread safe.
    """
    def should_profile(self, request):
        return (settings.DEBUG or request.user.is_superuser) and \
               ('prof' in request.GET or True)

    def process_request(self, request):
        if self.should_profile(request):
            # print "PROFILER - process_request"
            self.prof = cProfile.Profile()
 
    def process_view(self, request, callback, callback_args, callback_kwargs):
        if self.should_profile(request):
            # print "PROFILER - process_view"
            return self.prof.runcall(callback, request, *callback_args, **callback_kwargs)
 
    def get_group(self, file):
        for g in group_prefix_re:
            name = g.findall( file )
            if name:
                return name[0]
 
    def get_summary(self, results_dict, sum):
        list = [ (item[1], item[0]) for item in results_dict.items() ]
        list.sort( reverse = True )
        list = list[:40]
 
        res = "      tottime\n"
        for item in list:
            res += "%4.1f%% %7.3f %s\n" % ( 100*item[0]/sum if sum else 0, item[0], item[1] )
 
        return res
 
    def summary_for_files(self, stats_str):
        stats_str = stats_str.split("\n")[5:]
 
        mystats = {}
        mygroups = {}
 
        sum = 0
 
        for s in stats_str:
            fields = words_re.split(s);
            if len(fields) == 7:
                time = float(fields[2])
                sum += time
                file = fields[6].split(":")[0]
 
                if not file in mystats:
                    mystats[file] = 0
                mystats[file] += time
 
                group = self.get_group(file)
                if not group in mygroups:
                    mygroups[ group ] = 0
                mygroups[ group ] += time
 
        return "<pre>" + \
               " ---- By file ----\n\n" + self.get_summary(mystats,sum) + "\n" + \
               " ---- By group ---\n\n" + self.get_summary(mygroups,sum) + \
               "</pre>"
 
    def process_response(self, request, response):
        if self.should_profile(request):
            # print "PROFILER - process_response"
            stamp = datetime.datetime.strftime(datetime.datetime.now(), '%d-%h-%Y_%H-%M-%S.%s')
            import settings
            path = getattr(settings, 'PROFILER_DUMP_PATH', None) or '/tmp'
            path = os.path.join(path, '%s_request_%s.stats' % (stamp, request.method))
            self.prof.dump_stats(path)
        return response
