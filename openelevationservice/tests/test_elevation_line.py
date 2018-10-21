from openelevationservice.tests.base import BaseTestCase

import json

line_geometry = dict(format_in='geojson',
                     geometry=dict(geojson=dict(type="LineString",
                                                coordinates=[[8.807132326847508, 53.07574568891761], [8.807514373051843, 53.0756845615249],
                                                             [8.807865855559836, 53.07559287043586], [8.807926982952514, 53.07545533380228]])
                              )
                )

class LineTest(BaseTestCase):
    
    def test_valid_polyline(self):
        response = self.client.post('elevation/line',
                                    data=json.dumps(line_geometry))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['geometry']['type'], 'LineString')
        
    
    def test_empty_response(self):
        response = self.client.post('/elevation/line', data='')
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.get_json()['code'], 4000)
    
    