# -*- coding: utf-8 -*-

from openelevationservice import SETTINGS
from openelevationservice.server.utils.logger import get_logger
from openelevationservice.server.db_import.models import db, Cgiar
from openelevationservice.server.utils.custom_func import ST_SnapToGrid
from openelevationservice.server.api.api_exceptions import InvalidUsage

from geoalchemy2.functions import ST_DumpPoints, ST_Value, ST_Intersects, ST_X, ST_Y
from sqlalchemy import func

log = get_logger(__name__)

coord_precision = SETTINGS['coord_precision']

def line_elevation(geometry, format_out):
    
    if geometry.geom_type == 'LineString':
        query_points2d = db.session.query(func.ST_SetSRID((ST_DumpPoints(geometry.wkt).geom), 4326).label('geom')).subquery().alias('points2d')
    
        query_getelev = db.session \
                            .query(query_points2d.c.geom,
                                   Cgiar.rast.ST_Value(query_points2d.c.geom).label('z')) \
                            .filter(ST_Intersects(Cgiar.rast, query_points2d.c.geom)) \
                            .subquery().alias('getelevation')
        
        query_points3d = db.session \
                            .query(func.ST_SetSRID(func.ST_MakePoint(ST_X(query_getelev.c.geom),
                                                                     ST_Y(query_getelev.c.geom),
                                                                     query_getelev.c.z),
                                              4326).label('geom')) \
                            .subquery().alias('points3d')
        
        if format_out == 'geojson':
            # Return GeoJSON when requested directly in PostGIS
            query_final = db.session \
                              .query(func.ST_AsGeoJSON(ST_SnapToGrid(func.ST_MakeLine(query_points3d.c.geom), coord_precision)))
        else:
            # Else return the WKT of the geometry
            query_final = db.session \
                              .query(func.ST_AsText(ST_SnapToGrid(func.ST_MakeLine(query_points3d.c.geom), coord_precision)))
    else:
        raise InvalidUsage(500, 4002, "Needs to be a LineString, not {}!".format(geometry.geom_type))
        
    
    return query_final[0][0]

def point_elevation(geometry, format_out):
    
    if geometry.geom_type == "Point":
        query_point2d = db.session \
                            .query(func.ST_SetSRID(func.St_PointFromText(geometry.wkt), 4326).label('geom')) \
                            .subquery() \
                            .alias('points2d')
        
        query_getelev = db.session \
                            .query(query_point2d.c.geom,
                                   ST_Value(Cgiar.rast, query_point2d.c.geom).label('z')) \
                            .filter(ST_Intersects(Cgiar.rast, query_point2d.c.geom)) \
                            .subquery().alias('getelevation')
        
        if format_out == 'geojson': 
            query_final = db.session \
                                .query(func.ST_AsGeoJSON(ST_SnapToGrid(func.ST_MakePoint(ST_X(query_getelev.c.geom),
                                                                                           ST_Y(query_getelev.c.geom),
                                                                                           query_getelev.c.z),
                                                                        coord_precision)))
        else:
            query_final = db.session \
                                .query(func.ST_AsText(ST_SnapToGrid(func.ST_MakePoint(ST_X(query_getelev.c.geom),
                                                                                       ST_Y(query_getelev.c.geom),
                                                                                       query_getelev.c.z),
                                                                    coord_precision)))
    else:
        raise InvalidUsage(500, 4002, "Needs to be a Point, not {}!".format(geometry.geom_type))
    
        
    return query_final[0][0]
                                   