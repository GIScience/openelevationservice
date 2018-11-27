# -*- coding: utf-8 -*-

from openelevationservice.tests.base import BaseTestCase
from openelevationservice import SETTINGS
from openelevationservice.server.api import api_exceptions

from copy import deepcopy
import json

valid_coords = [[13.331302, 38.108433],
                [13.331273, 38.10849]]

invalid_coords = [[8.807132326847508, 53.07574568891761], 
                  [8.807514373051843, 53.0756845615249]]

valid_line_geojson = dict(format_in='geojson',
                          geometry=dict(type="LineString",
                                        coordinates=valid_coords))

valid_line_polyline = dict(format_in='polyline',
                           geometry=valid_coords)


valid_line_encoded = dict(format_in='encodedpolyline',
                          geometry='u`rgFswjpAKD')


class LineTest(BaseTestCase):
        
    def test_input_geojson_output_geojson(self):
        geom = deepcopy(valid_line_geojson)
        geom.update({'format_out': 'geojson'})
        response = self.client.post('elevation/line',
                                    json=geom,
                                    )
        
        j = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertIn(('type', 'LineString'), list(j['geometry'].items()))
        self.assertEqual(len(j['geometry']['coordinates']), 2)

    def test_input_geojson_output_encodedpolyline(self):
        geom = deepcopy(valid_line_geojson)
        geom.update({'format_out': 'encodedpolyline'})
        response = self.client.post('elevation/line',
                                    json=geom,
                                    )

        j = response.get_json()
        print(j)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(j['geometry'], 'u`rgFswjpA_aMKD?')
    
    def test_output_polyline(self):
        geom = deepcopy(valid_line_polyline)
        geom.update({'format_out': 'polyline'})
        response = self.client.post('elevation/line',
                                    json=geom)
        
        j = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(j['geometry'], list)
        self.assertEqual(len(j['geometry']), 2)
    
    def test_output_encodedpolyline(self):
        geom = deepcopy(valid_line_encoded)
        geom.update({'format_out': 'encodedpolyline'})
        response = self.client.post('elevation/line',
                                    json=geom)
        
        j = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(j['geometry'], 'u`rgFswjpA_aMKD?')
    
    def test_exceed_maximum_nodes(self):
        dummy_list = [[x, x] for x in range(SETTINGS['maximum_nodes'] + 1)]
        response = self.client.post('elevation/line',
                                    json={'format_in': 'polyline',
                                          'geometry': dummy_list})
        
        self.assertRaises(api_exceptions.InvalidUsage)
        self.assertEqual(response.get_json()['code'], 4003)
    
    def test_schema_wrong_format_in(self):
        response = self.client.post('elevation/line',
                                    json={'format_in': 'geoJSON',
                                          'format_out': 'geoJson',
                                          'dataset': 'SRTM'})
    
        self.assertRaises(api_exceptions.InvalidUsage)
        self.assertEqual(response.get_json()['code'], 4000)
    
    def test_schema_no_header(self):
        response = self.client.post('elevation/line',
                                    data=json.dumps(valid_line_geojson)
                                    )
        
        self.assertRaises(api_exceptions.InvalidUsage)
        self.assertEquals(response.get_json()['code'], 4001)
        
    def test_invalid_coords(self):
        geom = deepcopy(valid_line_polyline)
        geom.update(geometry=invalid_coords)
        response = self.client.post('elevation/line',
                                    json=geom,
                                    )
        
        self.assertRaises(api_exceptions.InvalidUsage)
        self.assertEqual(response.get_json()['code'], 4002)
        self.assertIn(b'The requested geometry is outside the bounds of', response.data)
    
    def test_point_geojson_error(self):
        geom = deepcopy(valid_line_geojson)
        geom.update(geometry={'coordinates': valid_coords[0], 'type': 'Point'})
        response = self.client.post('elevation/line',
                                    json=geom,
                                    )
        
        self.assertRaises(api_exceptions.InvalidUsage)
        self.assertEqual(response.get_json()['code'], 4002)
        self.assertIn(b'not a Point', response.data)
    
    def test_one_invalid_vertex(self):
        mixed_coords = [valid_coords[0], invalid_coords[0]]
        geom = deepcopy(valid_line_geojson)
        geom.update(geometry={'coordinates': mixed_coords, 'type': 'LineString'})
        response = self.client.post('elevation/line',
                                    json=geom,
                                    )
        
        self.assertRaises(api_exceptions.InvalidUsage)
        self.assertEqual(response.get_json()['code'], 4002)