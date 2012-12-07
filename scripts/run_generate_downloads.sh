#!/bin/bash
 
# Activate with crontab
# sudo crontab -e
# 0 3 * * * sh /usr/local/apps/wc-marine-debris/scripts/run_generate_downloads.sh

. /usr/local/apps/wc-marine-debris/env/bin/activate
python /usr/local/apps/wc-marine-debris/marine_debris/manage.py generate_downloads clear
