# Rebuilds the event_ontology table. 
# Should be run about once per day (as root)
#
# SRH 15-Aug-2014
#
# cd /etc/cron.daily
# ln -s /usr/local/apps/wc-marine-debris/marine_debris/refresh_event_ontology.sh

APPDIR=/usr/local/apps/wc-marine-debris
ENV=/usr/local/env/marine_debris



source $ENV/bin/activate
cd $APPDIR/marine_debris

# run the SQL query (takes about 15 seconds as of 15-Aug)
python manage.py dbshell < $APPDIR/scripts/event_ontology.sql

# flush the redis cache
cd $APPDIR/marine_debris
$PYTHON manage.py flush_caches
