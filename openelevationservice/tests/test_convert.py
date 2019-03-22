# -*- coding: utf-8 -*-

from openelevationservice.tests.base import BaseTestCase
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
        # TODO: make sure coords are the same in geom as in valid_geojson
        
        
    def test_point_to_geometry(self):
        geom = convert.point_to_geometry(valid_coords[0])
        self.assertIsInstance(geom, Point)
        
        
    def test_polyline_to_geometry(self):
        geom = convert.polyline_to_geometry(valid_coords)
        self.assertIsInstance(geom, LineString)
            
        
    def test_decode_polyline(self):
        enc = 'e_c_ImtgpAosJjrv^j{h]jC'
        truth = [[13.31543, 52.44931, 59.6], [8.34961, 47.24941, 58.9]]
        
        decoded = convert.decode_polyline(enc, is3D=True)
        self.assertEqual(truth, [list(x) for x in decoded.coords])
        
        
    def test_encode_polyline(self):
        coords_3d = [[13.31543, 52.449314, 59.6],[8.349609, 47.249407, 58.9]]
        truth = 'e_c_ImtgpAosJjrv^j{h]jC'
    
        enc = convert.encode_polyline(coords_3d, is3D=True)
        self.assertEqual(truth, enc)
