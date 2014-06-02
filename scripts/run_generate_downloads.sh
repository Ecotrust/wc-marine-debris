#!/bin/bash
 
# Activate with crontab
# sudo crontab -e
# 0 3 * * * sh /usr/local/apps/wc-marine-debris/scripts/run_generate_downloads.sh

echo "$(date) -- " >> /usr/local/apps/WCGA/wc-marine-debris/logs/downloads.log
. /usr/local/apps/WCGA/wc-marine-debris/env/bin/activate
python /vagrant/marine_debris/manage.py generate_downloads clear >> /usr/local/apps/WCGA/wc-marine-debris/logs/downloads.log
status=$?
if [ $status -ne "0" ]; then
    echo "$(date) -- ERROR: Creating downloads failed with a status code of $status" >> /usr/local/apps/WCGA/wc-marine-debris/logs/downloads.log
    exit 1
fi
