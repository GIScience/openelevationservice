# -*- coding: utf-8 -*-

from openelevationservice.server.utils import codec

from unittest import TestCase

valid_coords_3d = [
    (13.331302, 38.108433, 112.92),
    (13.331273, 38.10849, 1503.0932)
]


class TestCodec(TestCase):

    def test_encode_polyline5(self):
        """Tests polyline encoding with precision 5"""

        self.assertEqual(codec.encode(valid_coords_3d, precision=5, is3d=True), 'u`rgFswjpAw`UKDqonG')

    def test_encode_polyline6(self):
        """Tests polyline encoding with precision 6"""

        self.assertEqual(codec.encode(valid_coords_3d, precision=6, is3d=True), 'ap}tgAkutlXw`UqBx@qonG')

    def test_decode_polyline5_3d(self):
        """Tests polyline decoding with precision 5"""

        valid_coords_2d = [
            (13.3313, 38.10843),
            (13.33127, 38.10849)
        ]

        self.assertEqual(list(codec.decode('u`rgFswjpAKD').coords), valid_coords_2d)

    def test_decode_polyline6_3d(self):
        """Tests polyline decoding with precision 5"""

        valid_coords_2d = [
            (13.331302, 38.108433),
            (13.331273, 38.10849)
        ]

        self.assertEqual(list(codec.decode('ap}tgAkutlXqBx@', precision=6).coords), valid_coords_2d)
