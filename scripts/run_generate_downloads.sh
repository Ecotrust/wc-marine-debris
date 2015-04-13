#!/bin/bash
 
# Activate with crontab
# sudo crontab -e
# 0 3 * * * sh /usr/local/apps/wc-marine-debris/scripts/run_generate_downloads.sh

APPDIR=/usr/local/apps/wc-marine-debris
ENV=/usr/local/env/marine_debris
LOG_DIR=/usr/local/apps/wc-marine-debris/logs
LOG=$LOG_DIR/downloads.log

source $ENV/bin/activate
mkdir -p $LOG_DIR
cd $APPDIR/marine_debris

echo "$(date) -- " >> $LOG

python manage.py generate_downloads clear >> $LOG
status=$?
if [ $status -ne "0" ]; then
    echo "$(date) -- ERROR: Creating downloads failed with a status code of $status" >> $LOG
    exit 1
fi
