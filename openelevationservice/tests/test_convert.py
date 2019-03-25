# -*- coding: utf-8 -*-

from openelevationservice.server.utils import convert

from unittest import TestCase
from shapely.geometry import LineString, Point

valid_coords = [[13.331302, 38.108433], [13.331273, 38.10849]]

valid_geojson = {"coordinates": valid_coords,
                 "type": "LineString"}


class TestConvert(TestCase):
        
    def test_geojson_to_geometry(self):
        geom = convert.geojson_to_geometry(valid_geojson)
        self.assertIsInstance(geom, LineString)
        
    def test_point_to_geometry(self):
        geom = convert.point_to_geometry(valid_coords[0])
        self.assertIsInstance(geom, Point)
        
        
    def test_polyline_to_geometry(self):
        geom = convert.polyline_to_geometry(valid_coords)
        self.assertIsInstance(geom, LineString)
