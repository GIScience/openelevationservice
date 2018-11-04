# -*- coding: utf-8 -*-

from openelevationservice.tests.base import BaseTestCase
from openelevationservice.server.api import api_exceptions

valid_coord = [13.331302, 38.108433]

invalid_coord = [8.807514373051843, 53.0756845615249]

valid_point_geojson = dict(format_in='geojson',
                           geometry=dict(coordinates=valid_coord,
                                         type='Point'))

valid_point_point = dict(format_in='point',
                         geometry=valid_coord)


class PointTest(BaseTestCase):
        
    def test_post_geojson(self):
        valid_point_geojson.update({'format_out': 'geojson'})
        response = self.client.post('elevation/point',
                                    json=valid_point_geojson,
                                    )
        
        j = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertIn(('type', 'Point'), list(j['geometry'].items()))
        self.assertEqual(len(j['geometry']['coordinates']), 3)
    
    def test_post_point(self):
        valid_point_point.update({'format_out': 'point'})
        response = self.client.post('elevation/point',
                                    json=valid_point_point)
        
        j = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(j['geometry'], list)
        self.assertEqual(len(j['geometry']), 3)
    
    def test_get_point(self):
        response = self.client.get('elevation/point',
                                   query_string=dict(geometry=','.join([str(x) for x in valid_coord]),
                                                     format_out='point')
                                   )
        
        j = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(j['geometry'], list)
        self.assertEqual(len(j['geometry']), 3)
    
    def test_get_geojson(self):
        response = self.client.get('elevation/point',
                                   query_string=dict(geometry=','.join([str(x) for x in valid_coord]),
                                                     format_out='geojson')
                                   )
        
        j = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertIn(('type', 'Point'), list(j['geometry'].items()))
        self.assertEqual(len(j['geometry']['coordinates']), 3)
        
    def test_semicolon_separated_geometry_string(self):
        response = self.client.get('elevation/point',
                                   query_string=dict(geometry=';'.join([str(x) for x in valid_coord]),
                                                     format_out='geojson'))
        
        j = response.get_json()
        
        self.assertRaises(api_exceptions.InvalidUsage)
        self.assertEqual(j['code'], 4000)
        self.assertIn(b'is not a comma separated list of long, lat', response.data)
        
    def test_schema_get_wrong(self):
        response = self.client.get('elevation/point',
                                    query_string={'format_out': 'geoJson',
                                                  'dataset': 'SRTM',
                                                  'api_key': 540032})
    
        self.assertRaises(api_exceptions.InvalidUsage)
        self.assertEqual(response.get_json()['code'], 4000)
#        
    def test_invalid_coord_point(self):
        invalid_point = valid_point_point
        invalid_point.update(geometry=invalid_coord)
        response = self.client.post('elevation/point',
                                    json=invalid_point,
                                    )
        
        self.assertRaises(api_exceptions.InvalidUsage)
        self.assertEqual(response.get_json()['code'], 4002)
        self.assertIn(b'The requested geometry is outside the bounds of', response.data)
    
    def test_point_geojson_error(self):
        line_geojson = valid_point_geojson
        line_geojson.update(geometry={'coordinates': [valid_coord, valid_coord],
                                      'type': 'Point'})
        response = self.client.post('elevation/point',
                                    json=line_geojson,
                                    )
        
        self.assertRaises(api_exceptions.InvalidUsage)
        self.assertEqual(response.get_json()['code'], 4001)
        self.assertIn(b'must be a real number', response.data)
