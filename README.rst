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

This service is part of the GIScience_ software stack, crafted at `HeiGIT institute`_ at the University of Heidelberg.

To access the public API, see

Currently, **only `SRTM v4.1`_** is being used.

Supported formats are:
- GeoJSON
- Polyline
- Point
- Google's `encoded polyline`_

.. _GIScience: https://github.com/GIScience
.. _`HeiGIT institute`: https://heigit.org
.. _`SRTM v4.1`: http://srtm.csi.cgiar.org
.. _`encoded polyline`: https://developers.google.com/maps/documentation/utilities/polylinealgorithm
