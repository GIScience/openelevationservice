.. image:: https://travis-ci.org/GIScience/openelevationservice.svg?branch=master
    :target: https://travis-ci.com/GIScience/openelevationservice
    :alt: Build status

.. image:: https://readthedocs.org/projects/openelevationservice/badge/?version=latest
   :target: https://openelevationservice.readthedocs.io/en/latest/
   :alt: Documentation Status

Quickstart
==================================================

Description
--------------------------------------------------

openelevationservice is a Flask application which extracts elevation from various elevation datasets for `Point` or `LineString` 2D geometries and returns 3D geometries in various formats.

Supported formats are:

- GeoJSON
- Polyline, i.e. list of vertices
- Google's `encoded polyline`_
- Point, i.e. one vertex

For general support and questions, please contact our forum_. After successful installation, you can also find a API documentation locally at https://localhost:5000/apidocs, provided via flasgger_.

For issues and improvement suggestions, use the repo's `issue tracker`_.

This service is part of the GIScience_ software stack, crafted at `HeiGIT institute`_ at the University of Heidelberg.

You can also use our `free API`_ via (also check Endpoints_ for usage):

- https://api.openrouteservice.org/elevation/point?api_key=YOUR_KEY
- https://api.openrouteservice.org/elevation/line?api_key=YOUR_KEY

.. _GIScience: https://github.com/GIScience
.. _`HeiGIT institute`: https://heigit.org
.. _`SRTM v4.1`: http://srtm.csi.cgiar.org
.. _`encoded polyline`: https://developers.google.com/maps/documentation/utilities/polylinealgorithm
.. _forum: https://ask.openrouteservice.org/c/elevation
.. _`issue tracker`: https://github.com/GIScience/openelevationservice/issues
.. _flasgger: https://github.com/rochacbruno/flasgger
.. _`free API`: https://openrouteservice.org/sign-up

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

1. Customize ``ops_settings_docker.sample.yml`` to your needs and name it ``ops_settings_docker.yml``

2. Build container
   ``sudo docker-compose up -d``

3. Create the database

.. code-block:: bash

    sudo docker exec -it <container ID> bash -c "source /oes_venv/bin/activate; export OES_LOGLEVEL=DEBUG; flask create"

4. Download SRTM data

.. code-block:: bash

    sudo docker exec -it <container ID> bash -c "source /oes_venv/bin/activate; export OES_LOGLEVEL=DEBUG; flask download --xyrange=0,0,73,25"

The optional ``xyrange`` parameter specfies the ``minx,miny,maxx,maxy`` indices of the available tiles, default is ``0,0,73,25``. You can see a representation of indices in the map on the `CGIAR website`_.

**Note**, that you need to have credentials to access the `FTP site`_ , which you can request here_.

5. Import SRTM data

.. code-block:: bash

    sudo docker exec  -it <container ID> bash -c "source /oes_venv/bin/activate; flask importdata"

The import command will import whatever ``.tif`` files it finds in ``./tiles``. Now, it's time to grab a coffee, this might take a while. Expect a few hours for a remote database connection with HDD's and the global dataset.

After it's all finished, the service will listen on port ``5020`` of your host machine, unless specified differently in ``docker-compose.yml``.


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
   # Either via virtualenv, venv package or conda
   python3.6 -m venv .venv
   # or
   virtualenv python=python3.6 .venv
   # or
   conda create -n oes python=3.6

   # Activate virtual env (or equivalent conda command)
   source .venv/bin/activate
   # Add FLASK_APP environment variable
   # For conda, see here: https://conda.io/docs/user-guide/tasks/manage-environments.html#macos-and-linux
   echo "export FLASK_APP=manage" >> .venv/bin/activate
   # Install required packages
   pip install -r requirements.txt

When your environment is set up, you can run the import process and start the server:

.. code-block:: bash

   # inside the repo root directory
   flask create
   # rather as a background/nohup job, will download 27 GB
   flask download --xyrange=0,0,73,25
   flask importdata

   # Start the server
   flask run

The service will now listen on ``http://localhost:5000``.


Windows with remote PostGIS set up
+++++++++++++++++++++++++++++++++++++++++++++++++++++

Rename ``./openelevationservice/server/ops_settings.sample.yml`` to ``ops_settings.yml``:

- Set ``coord_precision`` to ``0.000833333333``.
- The part of ``srtm_parameters`` need not be changed.
- For part of ``provider_parameters``, write the connection properties to the remote database server.

Steps to establish the environment and run the server:

.. code-block:: bash

   # Python virtual environment setup and activate
   python -m venv .venv
   cd .\.venv\Scripts
   activate
   cd ..\..
 
   # Install required packages
   # If a sequence of errors occurs, in "requirements.txt", replace the last line:
   # - "psycopg2-binary==2.8.4" by "psycopg2-binary>=2.8.4"
   pip install -r requirements.txt
 
   # Run the server
   flask --app manage run

Endpoints
----------------------------------------------------------

The default base url is ``http://localhost:5000/``.

The openelevationservice exposes 2 endpoints:

- ``/elevation/polygon``: used for Polygon geometries
- ``/elevation/line``: used for LineString geometries
- ``/elevation/point``: used for single Point geometries

+-----------------------+-------------------+------------+---------+---------------------------------------------------------+
|       Endpoint        | Method(s) allowed | Parameter  | Default | Values                                                  |
+=======================+===================+============+=========+=========================================================+
| ``/elevation/polygon``| POST              | format_in  |    --   | geojson, polygon                                        |
|                       |                   +------------+---------+---------------------------------------------------------+
|                       |                   | geometry   |    --   | depends on ``format_in``                                |
|                       |                   +------------+---------+---------------------------------------------------------+
|                       |                   | format_out | geojson | geojson, polygon                                        |
|                       |                   +------------+---------+---------------------------------------------------------+
|                       |                   | dataset    | srtm    | srtm (so far)                                           |
+-----------------------+-------------------+------------+---------+---------------------------------------------------------+
| ``/elevation/line``   | POST              | format_in  |    --   | geojson, polyline, encodedpolyline5, encodedpolyline6   |
|                       |                   +------------+---------+---------------------------------------------------------+
|                       |                   | geometry   |    --   | depends on ``format_in``                                |
|                       |                   +------------+---------+---------------------------------------------------------+
|                       |                   | format_out | geojson | geojson, polyline, encodedpolyline5, encodedpolyline6   |
|                       |                   +------------+---------+---------------------------------------------------------+
|                       |                   | dataset    | srtm    | srtm (so far)                                           |
+-----------------------+-------------------+------------+---------+---------------------------------------------------------+
| ``/elevation/point``  | GET, POST         | format_in  |    --   | geojson, point                                          |
|                       |                   +------------+---------+---------------------------------------------------------+
|                       |                   | geometry   |    --   | depends on ``format_in``                                |
|                       |                   +------------+---------+---------------------------------------------------------+
|                       |                   | format_out | geojson | geojson, point                                          |
|                       |                   +------------+---------+---------------------------------------------------------+
|                       |                   | dataset    | srtm    | srtm (so far)                                           |
+-----------------------+-------------------+------------+---------+---------------------------------------------------------+

For more detailed information, please visit the `API documentation`_.

When hosted locally, visit ``https://localhost:5000/apidocs``.

.. _`API documentation`: https://coming.soon

Environment variables
##########################################################

openelevationservice recognizes the following environment variables:

+-----------------+-----------------------------------------+-------------------------------------------------------+-----------------------------+
|     variable    |       function                          |     Default                                           |  Values                     |
+=================+=========================================+=======================================================+=============================+
| OES_LOGLEVEL    | Sets the level of logging output        | INFO                                                  | DEBUG, INFO, WARNING, ERROR |
+-----------------+-----------------------------------------+-------------------------------------------------------+-----------------------------+
| APP_SETTINGS    | Controls the behavior of ``config.py``  | openelevationservice.server.config.ProductionConfig   | ProductionConfig,           |
|                 |                                         |                                                       |                             |
|                 |                                         |                                                       | DevelopmentConfig           |
+-----------------+-----------------------------------------+-------------------------------------------------------+-----------------------------+
| FLASK_APP       | Sets the app                            | manage                                                |                             |
+-----------------+-----------------------------------------+-------------------------------------------------------+-----------------------------+
| FLASK_ENV       | Development/Production server           | development                                           | production, development     |
+-----------------+-----------------------------------------+-------------------------------------------------------+-----------------------------+
| TESTING         | Sets flask testing environment          | None                                                  | true                        |
+-----------------+-----------------------------------------+-------------------------------------------------------+-----------------------------+

In the case of the Docker setup, you don't need to worry about environment variables for the most part.

CLI
##########################################################

The flask command line interface has a few additional commands:

-  ``flask create``: creates a table for CGIAR data
- ```flask download --xyrange=0,73,0,25``: downloads CGIAR data and limits the X, Y indices optionally with ``xyrange``
- ``flask importdata``: imports CGIAR tiles it finds in ``./tiles/``
- ``flask drop``: drops CGIAR table

Testing
########################################################

The testing framework is `nosetests`, which makes it very easy to run the tests:

.. code-block:: bash

    TESTING=true nosetests -v


Usage
--------------------------------------------------------

GET point
#########################################################

.. code-block:: bash

  curl -XGET https://localhost:5000/elevation/point?geometry=13.349762,38.11295

POST point as GeoJSON
#########################################################

.. code-block:: bash

  curl -XPOST http://localhost:5000/elevation/point \
    -H 'Content-Type: application/json' \
    -d '{
      "format_in": "geojson",
      "format_out": "geojson",
      "geometry": {
        "coordinates": [13.349762, 38.11295],
        "type": "Point"
      }
    }'

POST LineString as polyline
#########################################################

.. code-block:: bash

  curl -XPOST http://localhost:5000/elevation/line \
    -H 'Content-Type: application/json' \
    -d '{
      "format_in": "polyline",
      "format_out": "encodedpolyline",
      "geometry": [[13.349762, 38.11295],
                   [12.638397, 37.645772]]
    }'

POST Polygon
#########################################################

.. code-block:: bash

  curl -XPOST http://localhost:5000/elevation/polygon \
    -H 'Content-Type: application/json' \
    -d '{
      "format_in": "polygon",
      "format_out": "polygon",
      "geometry": [
        [75, 29], 
        [75.003, 29],
        [75.003, 29.002],
        [75, 29.002],
        [75, 29]
      ]
    }'
