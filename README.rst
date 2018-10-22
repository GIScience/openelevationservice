... image:: https://travis-ci.com/GIScience/openrouteservice-py.svg?branch=master
    :target: https://travis-ci.com/GIScience/openrouteservice-py
    :alt: Build status

... image:: https://readthedocs.org/projects/openrouteservice-py/badge/?version=latest
   :target: http://openrouteservice-py.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

... image:: https://coveralls.io/repos/github/GIScience/openrouteservice-py/badge.svg?branch=master
   :target: https://coveralls.io/github/GIScience/openrouteservice-py?branch=master


Quickstart
==================================================

Description
--------------------------------------------------

openelevationservice is a Flask application which extracts elevation from various elevation datasets for `Point` or `LineString` 2D geometries and returns 3D geometries in various formats.

Currently, only `SRTM v4.1`_ is supported.

This service is part of the GIScience_ software stack, crafted at `HeiGIT institute`_ at the University of Heidelberg.

Supported formats are:
- GeoJSON
- Polyline, i.e. list of vertices
- Google's `encoded polyline`_
- Point, i.e. vertex

.. _GIScience: https://github.com/GIScience
.. _`HeiGIT institute`: https://heigit.org
.. _`SRTM v4.1`: http://srtm.csi.cgiar.org
.. _`encoded polyline`: https://developers.google.com/maps/documentation/utilities/polylinealgorithm


Installation
----------------------------------------------------

You can either run this service on a host machine (like your PC) in a virtual environment or via docker (recommended).

Docker installation
####################################################

Prerequisites
++++++++++++++++++++++++++++++++++++++++++++++++++++

- Docker
- PostGIS installation (recommended `Kartoza's docker`_)

Run Docker container
+++++++++++++++++++++++++++++++++++++++++++++++++++

1. Customize `ops_settings_docker.yml` to your needs.

2. Build container
``sudo docker-compose up -d``

3. Create the database
``sudo docker exec run -t flask create``

4. Download SRTM data
    
    **Note**, that you need to have credentials to access the `FTP site`_ , which you can request here_.
    
    ``sudo docker exec -d flask download --xyrange=0,0,73,25``
    
    The optinal ``xyrange`` parameter specfies the ``minx,miny,maxx,maxy`` indices of the available tiles, default is ``0,0,73,25``. You can see a representation of indices in the map on the `CGIAR website`_.
    
5. Import SRTM data
    
    ``sudo docker exec -d flask importdata --xyrange=0,0,73,25``
    
    Now, it's time to grab a coffee, this might take a while. Expect 12 hours for a remote database connection with HDD's and the global dataset.
    

.. _`Kartoza's docker`: https://github.com/kartoza/docker-postgis
.. _here: https://harvestchoice.wufoo.com/forms/download-cgiarcsi-srtm/
.. _`FTP site`: http://data.cgiar-csi.org/srtm/tiles/GeoTIFF/
.. _`CGIAR website`: http://srtm.csi.cgiar.org/SELECTION/inputCoord.asp