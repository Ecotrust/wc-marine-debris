wc-marine-debris
================

West Coast Governor's Alliance marine debris database

# Vagrant
Bring up the vagrant vm with
```
vagrant up
```

## Database options
The base provisioning will create a database with postgis to be used with the django config.  You can log in to the vm with 'vagrant ssh' and then run the following commands.
```
source /usr/local/venv/debris/bin/activate
cd /vagrant/marine_debris
python manage.py syncdb
python manage.py migrate
```

## Database Restore
You can also restore a binary database dump from dionysus.  This machine is running postgres 8.4 and the vagrant is running 9.1.  In order to restore, copy the dump created with pg_dump using the option "-Fc" to so specify the format.  The following command will load the database and handle the postgis upgrade.  You will need to be sshed into the vm.
```
dropdb debris
/usr/share/postgresql-9.1-postgis/utils/postgis_restore.pl /usr/share/postgresql/9.1/contrib/postgis-1.5/postgis.sql debris /vagrant/marine_debris_20140529.dump
```

## Running the server
The standard django management commands are available.  From the vm, you may run the dev server.
```
source /usr/local/venv/debris/bin/activate
cd /vagrant/marine_debris
python manage.py runserver 0.0.0.0:8000
```
