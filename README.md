# openelevationservice

A GeoJSON based service to query SRTM elevation for points/lines.

## PG setup

Will install Postgis 2.5 and PGSQL 10:

`sudo apt-get install postgis`

Create system user to be able to connect to PG via psql:

`sudo adduser --no-create-home --system gis`

Create PG user:

`sudo -u postgres createuser --interactive`

- username: gis
- superuser: yes

Create database for user:

`sudo -u postgres createdb -O gis gis`

Example raster2pgsql command:

`raster2pgsql -a -I -C -F -P -M *.tif public.oes_cgiar | psql -U docker -h localhost -p 5432 -d gis`


## ENV variables

OES_LOGPATH
OES_LOGLEVEL
TESTING