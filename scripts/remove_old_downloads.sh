# remove csvs older than 30 days
find /usr/local/src/wc-marine-debris/marine_debris/media/WCGA_downloads -name "*.csv" -mtime +30 -exec rm {} \; 
