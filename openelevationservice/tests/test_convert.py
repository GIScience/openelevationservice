# -*- coding: utf-8 -*-

from openelevationservice.tests.base import BaseTestCase
from openelevationservice.server.utils import convert

class TestConvert(BaseTestCase):
    
    def test_valid_encoding(self):
        coords = [[13.31543, 52.449314, 59.6],[8.349609, 47.249407, 58.9]]
        truth = 'e_c_ImtgpAosJlrv^l{h]jC'
        
        enc = convert.encode_polyline(coords)
        self.assertEqual(truth, enc)
    
    