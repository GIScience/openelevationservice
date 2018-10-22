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
++++++++++++++++++++++++++++++++++++++++++++++++++++

1. Customize `ops_settings_docker.yml` to your needs.

2. Build container
   ``sudo docker-compose up -d``

3. Create the database
   ``sudo docker exec run -t flask create``

4. Download SRTM data ``sudo docker exec -dt flask download --xyrange=0,0,73,25``
    
   The optional ``xyrange`` parameter specfies the ``minx,miny,maxx,maxy`` indices of the available tiles, default is ``0,0,73,25``. You can see a representation of indices in the map on the `CGIAR website`_.

   **Note**, that you need to have credentials to access the `FTP site`_ , which you can request here_.

    
5. Import SRTM data ``sudo docker exec -d flask importdata --xyrange=0,0,73,25``

   Now, it's time to grab a coffee, this might take a while. Expect 12 hours for a remote database connection with HDD's and the global dataset.

After it's all finished, the service will listen on port ``5020`` of you host machine, unless specified differently in ``docker-compose.yml``


.. _`Kartoza's docker`: https://github.com/kartoza/docker-postgis
.. _here: https://harvestchoice.wufoo.com/forms/download-cgiarcsi-srtm/
.. _`FTP site`: http://data.cgiar-csi.org/srtm/tiles/GeoTIFF/
.. _`CGIAR website`: http://srtm.csi.cgiar.org/SELECTION/inputCoord.asp


Conventional installation
####################################################

This tutorial assumes a Ubuntu system. 

Max OSX should be similar, if not the same. Windows is of course possible, but many of the commands will have to be altered.

Prerequisites
++++++++++++++++++++++++++++++++++++++++++++++++++++

- Python 3.6 or higher
- PostGIS installation on the host machine (solely needed for `raster2pgsql`)
- (Optional) Remote PostGIS installation (if you want to use a different data server)

Create virtual environment
+++++++++++++++++++++++++++++++++++++++++++++++++++++

First, customize ``./openelevationservice/server/ops_settings.sample.yml`` and name it ``ops_settings.yml``.

Then you can set up the environment:

.. code-block:: bash

   cd openelevationservice
   # Either via virtualenv or venv package
   python3.6 -m venv .venv
   virtualenv python=python3.6 .venv
   
   # Add FLASK_APP environment variable
   echo "FLASK_APP=manage" >> .venv/bin/activate
   # Activate virtual env
   source .venv/bin/activate
   # Install required packages
   pip install -r requirements.txt
   
When your environment is set up, you can start the import process and start the server:

.. code-block:: bash
   
   # inside the repo root directory
   flask create
   # rather as a background/nohup job, will download 27 GB
   flask download --xyrange=0,0,73,25
   flask importdata
   
   # Start the server
   flask run
   

Endpoints
----------------------------------------------------------

The openelevationservice exposes 2 endpoints:

- ``/elevation/line``: used for Polyline geometries
- ``/elevation/point``: used for single Point geometries

Quick overview:

``elevation/line``
###########################################################

sample text