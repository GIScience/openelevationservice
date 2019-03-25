# -*- coding: utf-8 -*-

from .convert import polyline_to_geometry

import itertools
import six
import math

"""
Copyright (c) 2014 Bruno M. Custódio
Copyright (c) 2016 Frederick Jansen

https://github.com/hicsail/polyline/commit/ddd12e85c53d394404952754e39c91f63a808656
"""


def _pcitr(iterable):
    return six.moves.zip(iterable, itertools.islice(iterable, 1, None))


def _py2_round(x):
    # The polyline algorithm uses Python 2's way of rounding
    return int(math.copysign(math.floor(math.fabs(x) + 0.5), x))


def _write(output, curr_value, prev_value, factor):
    curr_value = _py2_round(curr_value * factor)
    prev_value = _py2_round(prev_value * factor)
    coord = curr_value - prev_value
    coord <<= 1
    coord = coord if coord >= 0 else ~coord

    while coord >= 0x20:
        output.write(six.unichr((0x20 | (coord & 0x1f)) + 63))
        coord >>= 5

    output.write(six.unichr(coord + 63))
    

def _trans(value, index):
    byte, result, shift = None, 0, 0

    while byte is None or byte >= 0x20:
        byte = ord(value[index]) - 63
        index += 1
        result |= (byte & 0x1f) << shift
        shift += 5
        comp = result & 1

    return ~(result >> 1) if comp else (result >> 1), index


def decode(expression, precision=5, is3d=False):
    coordinates, index, lat, lng, z, length, factor = [], 0, 0, 0, 0, len(expression), float(10 ** precision)

    while index < length:
        lat_change, index = _trans(expression, index)
        lng_change, index = _trans(expression, index)
        lat += lat_change
        lng += lng_change
        # Careful, Lng/Lat are interchanged here, so that shapely converts correctly
        if not is3d:
            coordinates.append((lng / factor, lat / factor))
        else:
            z_change, index = _trans(expression, index)
            z += z_change
            coordinates.append((lng / factor, lat / factor, z / 100))

    return polyline_to_geometry(coordinates)


def encode(coordinates, precision=5, is3d=False):
    output, factor = six.StringIO(), int(10 ** precision)

    # Careful, Lnt/Lat are interchanged here, bcs PostGIS query outputs x, y, but encodedpolyline has the convention of
    # lat, lon
    _write(output, coordinates[0][1], 0, factor)
    _write(output, coordinates[0][0], 0, factor)
    if is3d:
        _write(output, coordinates[0][2], 0, 100)

    for prev, curr in _pcitr(coordinates):
        _write(output, curr[1], prev[1], factor)
        _write(output, curr[0], prev[0], factor)
        if is3d==True:
            _write(output, curr[2], prev[2], 100)

    return output.getvalue()
