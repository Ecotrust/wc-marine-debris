# remove csvs older than 30 days
find /usr/local/apps/wc-marine-debris/marine_debris/media/WCGA_downloads -name "*.csv" -mtime +2 -exec rm {} \; 
