# -*- coding: utf-8 -*-

from openelevationservice.server.api.api_exceptions import InvalidUsage
from openelevationservice.server.utils import logger

from shapely.geometry import shape, LineString, Point

log = logger.get_logger(__name__)

def geojson_to_geometry(geometry_str):
    """
    Converts GeoJSON to shapely geometries
    
    :param geometry_str: GeoJSON representation to be converted
    :type geometry_str: str
    
    :raises InvalidUsage: internal HTTP 500 error with more detailed description.
    
    :returns: Shapely geometry
    :rtype: Shapely geometry
    """
    
    try:
        geom = shape(geometry_str)
    except Exception as e:
        raise InvalidUsage(status_code=500,
                          error_code=4002,
                          message=str(e))
    return geom
    
    
def point_to_geometry(point):
    """
    Converts a point to shapely Point geometries
    
    :param point: coordinates of a point
    :type point: list/tuple
    
    :raises InvalidUsage: internal HTTP 500 error with more detailed description.
    
    :returns: Point
    :rtype: shapely.geometry.Point
    """
    
    try:
        geom = Point(point)
    except Exception as e:
        raise InvalidUsage(status_code=500,
                          error_code=4002,
                          message=str(e))
    return geom

def polyline_to_geometry(point_list):
    """
    Converts a list/tuple of coordinates lists/tuples to a shapely LineString.
    
    :param point_list: Coordinates of line to be converted.
    :type point_list: list/tuple of lists/tuples
    
    :raises InvalidUsage: internal HTTP 500 error with more detailed description.
    
    :returns: LineString
    :rtype: shapely.geometry.LineString
    """
    
    try:
        geom = LineString(point_list)
    except Exception as e:
        raise InvalidUsage(status_code=500,
                          error_code=4002,
                          message=str(e))
    return geom
    
    
def decode_polyline(polyline, is3D):
    """Decodes a Polyline string into a shapely.geometry.LineString.
    
    After GraphHopper's Java code:
    https://github.com/graphhopper/graphhopper/blob/13ed18d4cc22d9c4c61b5a1de59dd2ff2e1c105d/web/src/main/java/com/graphhopper/http/WebHelper.java#L49
        
    :param polyline: An encoded polyline, only the geometry.
    :type polyline: string
    
    :param is3D: switch for polylines with elevation data
    :type id3D: boolean
    
    :returns: LineString in 2D or 3D
    :rtype: shapely.geometry.LineString
    """
    points = []
    index = lat = lng = z= 0

    while index < len(polyline):
        result = 1
        shift = 0
        while True:
            b = ord(polyline[index]) - 63 - 1
            index += 1
            result += b << shift
            shift += 5
            if b < 0x1f:
                break
        lat += (~result >> 1) if (result & 1) != 0 else (result >> 1)

        result = 1
        shift = 0
        while True:
            b = ord(polyline[index]) - 63 - 1
            index += 1
            result += b << shift
            shift += 5
            if b < 0x1f:
                break
        lng += ~(result >> 1) if (result & 1) != 0 else (result >> 1)
        
        if is3D:
            result = 1
            shift = 0
            while True:
                b = ord(polyline[index]) - 63 - 1
                index += 1
                result += b << shift
                shift += 5
                if b < 0x1f:
                    break
            if (result & 1) != 0:
                z += ~(result >> 1)
            else:
                z += (result >> 1) 
                
            points.append([round(lng * 1e-5, 6), round(lat * 1e-5, 6), round(z*1e-2,1)])   
            
        else:
            points.append([round(lng * 1e-5, 6), round(lat * 1e-5, 6)])
        
    return polyline_to_geometry(points)


def encode_polyline(coords, is3D):
    """
    Encodes 2D or 3D coordinates to Google's encoded polyline format.
    
    After GraphHopper's Java code:
    https://github.com/graphhopper/graphhopper/blob/13ed18d4cc22d9c4c61b5a1de59dd2ff2e1c105d/web/src/main/java/com/graphhopper/http/WebHelper.java#L108
    
    :param coords: a list of of coordinates in [x, y(, z)]    
    :type coords: tuple/list of tuples/lists
    
    :param is3D: switch for polylines with elevation data
    :type id3D: boolean
    
    :returns: encoded polyline
    :rtype: string
    """
    result = []
    
    prev_lat = 0
    prev_lng = 0
    prev_z = 0
    
    for coord in coords:        
        lng = int(coord[0] * 1e5)
        lat = int(coord[1] * 1e5)
        
        d_lng = _encode_value(lng - prev_lng) 
        d_lat = _encode_value(lat - prev_lat)
        
        prev_lat, prev_lng = lat, lng
        
        result.append(d_lat)
        result.append(d_lng)
        if is3D:
            z = int(coord[2] * 100)
            d_z = _encode_value(z - prev_z)
            prev_z = z
            result.append(d_z)
    
    return ''.join(c for r in result for c in r)


def _split_into_chunks(value):
    while value >= 32: #2^5, while there are at least 5 bits
        
        # first & with 2^5-1, zeros out all the bits other than the first five
        # then OR with 0x20 if another bit chunk follows
        yield (value & 31) | 0x20 
        value >>= 5
    yield value
    

def _encode_value(value):
    # Step 2 & 4
    value = ~(value << 1) if value < 0 else (value << 1)
    
    # Step 5 - 8
    chunks = _split_into_chunks(value)
    
    # Step 9-10
    return (chr(chunk + 63) for chunk in chunks)