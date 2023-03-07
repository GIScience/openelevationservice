# -*- coding: utf-8 -*-

from openelevationservice.server.api.api_exceptions import InvalidUsage
from openelevationservice.server.utils import logger

from shapely.geometry import shape, LineString, Point, Polygon

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
        raise InvalidUsage(status_code=400,
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
        raise InvalidUsage(status_code=400,
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
        raise InvalidUsage(status_code=400,
                          error_code=4002,
                          message=str(e))
    return geom

def polygon_to_geometry(point_list):
    try:
        geom = Polygon(point_list)
    except Exception as e:
        raise InvalidUsage(status_code=400,
                          error_code=4002,
                          message=str(e))
    return geom
