# -*- coding: utf-8 -*-

from openelevationservice import SETTINGS
from openelevationservice.server.utils.logger import get_logger
from openelevationservice.server.db_import.models import db, Cgiar
# from openelevationservice.server.utils.custom_func import ST_SnapToGrid
from openelevationservice.server.api.api_exceptions import InvalidUsage

from geoalchemy2.functions import ST_Value, ST_Intersects, ST_X, ST_Y # ST_DumpPoints, ST_Dump, 
from sqlalchemy import func, literal_column
import json

log = get_logger(__name__)

coord_precision = SETTINGS['coord_precision']
if "/" in coord_precision:
    coord_precision = float(coord_precision.split("/")[0]) / float(coord_precision.split("/")[1])
else:
    coord_precision = float(coord_precision)

division_limit = 1 / float(SETTINGS['maximum_nodes'])

def _getModel(dataset):
    """
    Choose model based on dataset parameter
    
    :param dataset: elevation dataset to use for querying
    :type dataset: string
    
    :returns: database model
    :rtype: SQLAlchemy model
    """
    if dataset == 'srtm':
        model = Cgiar
    
    return model


def format_PixelAsPoints(result_pixels):
    # format: [ ('(0101000020E61000000000000000C05240D169039D36003D40,202,1,2)',) , ...
    points = []
    heights = []
    for pixel in result_pixels:
        subcolumns = pixel[0].split(",")
        point = subcolumns[0][1: ]
        if point not in points:
            points.append(point)
            heights.append(int(subcolumns[1]))
    
    return func.unnest(literal_column("ARRAY{}".format(points))), \
           func.unnest(literal_column("ARRAY{}".format(heights)))


def polygon_elevation(geometry, format_out, dataset):
    """
    Performs PostGIS query to enrich a polygon geometry.
    
    :param geometry: Input 2D polygon to be enriched with elevation
    :type geometry: Shapely geometry
    
    :param format_out: Specifies output format. One of ['geojson', 'polygon']
    :type format_out: string
    
    :param dataset: Elevation dataset to use for querying
    :type dataset: string
    
    :raises InvalidUsage: internal HTTP 500 error with more detailed description. 
        
    :returns: 3D polygon as GeoJSON or WKT
    :rtype: string
    """
    
    Model = _getModel(dataset)
    
    if geometry.geom_type == 'Polygon':
        query_geom = db.session \
                            .query(func.ST_SetSRID(func.ST_PolygonFromText(geometry.wkt), 4326) \
                            .label('geom')) \
                            .subquery().alias('pGeom')

        result_pixels = db.session \
                            .query(func.ST_PixelAsPoints(
                                func.ST_Clip(Model.rast, 1, query_geom.c.geom, coord_precision), #.geom
                                1)) \
                            .select_from(query_geom.join(Model, ST_Intersects(Model.rast, query_geom.c.geom))) \
                            .all() #.subquery().alias('getsubrast')
        
        point_col, height_col = format_PixelAsPoints(result_pixels)
        
        #
        #query_getelev = db.session \
        #                    .query(query_subrast.c.geom,
        #                           query_subrast.c.val) \
        #                    .subquery().alias('getelev')

        query_points3d = db.session \
                            .query(func.ST_SetSRID(func.ST_MakePoint(ST_X(point_col),
                                                                     ST_Y(point_col),
                                                                     height_col),
                                              4326).label('geom')) \
                            .order_by(ST_X(point_col), ST_Y(point_col)) \
                            .subquery().alias('points3d')

        if format_out == 'geojson':
            # Return GeoJSON directly in PostGIS
            query_final = db.session \
                              .query(func.ST_AsGeoJson(func.ST_MakeLine(query_points3d.c.geom)))
            
        else:
            # Else return the WKT of the geometry
            query_final = db.session \
                              .query(func.ST_AsText(func.ST_MakeLine(query_points3d.c.geom)))
    else:
        raise InvalidUsage(400, 4002, "Needs to be a Polygon, not a {}!".format(geometry.geom_type))

    # Behaviour when all vertices are out of bounds
    if query_final[0][0] == None:
        raise InvalidUsage(404, 4002,
                           'The requested geometry is outside the bounds of {}'.format(dataset))
        
    return query_final[0][0]


def line_elevation(geometry, format_out, dataset):
    """
    Performs PostGIS query to enrich a line geometry.
    
    :param geometry: Input 2D line to be enriched with elevation
    :type geometry: Shapely geometry
    
    :param format_out: Specifies output format. One of ['geojson', 'polyline',
        'encodedpolyline']
    :type format_out: string
    
    :param dataset: Elevation dataset to use for querying
    :type dataset: string
    
    :raises InvalidUsage: internal HTTP 500 error with more detailed description. 
        
    :returns: 3D line as GeoJSON or WKT
    :rtype: string
    """
    
    Model = _getModel(dataset)
    
    if geometry.geom_type == 'LineString':
        num_points = db.session \
                        .query(func.ST_NPoints(geometry.wkt)) \
                        .scalar()
        
        if int(num_points) != 2:
            raise InvalidUsage(400, 4002, "Actually, only LineString with exactly 2 points are supported!")
        
        lineLen = max(geometry.bounds[2] - geometry.bounds[0], geometry.bounds[3] - geometry.bounds[1])

        query_points2d = db.session \
                            .query(func.ST_SetSRID(func.ST_DumpPoints(func.ST_Union(
                                func.ST_PointN(geometry.wkt, 1),
                                func.ST_LineInterpolatePoints(
                                    geometry.wkt,
                                    max(min(1, coord_precision / lineLen), division_limit)
                                )
                            )).geom, 4326).label('geom')).subquery().alias('points2d')
        
        #query_points2d = db.session\
        #                    .query(func.ST_SetSRID(ST_DumpPoints(geometry.wkt, coord_precision).geom, 4326) \
        #                    .label('geom')) \
        #                    .subquery().alias('points2d')

        query_getelev = db.session \
                            .query(func.DISTINCT(query_points2d.c.geom).label('geom'),
                                   ST_Value(Model.rast, query_points2d.c.geom).label('z')) \
                            .select_from(query_points2d) \
                            .join(Model, ST_Intersects(Model.rast, query_points2d.c.geom)) \
                            .subquery().alias('getelevation')

        query_points3d = db.session \
                            .query(func.ST_SetSRID(func.ST_MakePoint(ST_X(query_getelev.c.geom),
                                                                     ST_Y(query_getelev.c.geom),
                                                                     query_getelev.c.z),
                                              4326).label('geom')) \
                            .order_by(ST_X(query_getelev.c.geom)) \
                            .subquery().alias('points3d')

        if format_out == 'geojson':
            # Return GeoJSON directly in PostGIS
            query_final = db.session \
                              .query(func.ST_AsGeoJson(func.ST_MakeLine(query_points3d.c.geom))) #ST_SnapToGrid(, coord_precision)
            
        else:
            # Else return the WKT of the geometry
            query_final = db.session \
                              .query(func.ST_AsText(func.ST_MakeLine(query_points3d.c.geom))) #ST_SnapToGrid(, coord_precision)
    else:
        raise InvalidUsage(400, 4002, "Needs to be a LineString, not a {}!".format(geometry.geom_type))

    # Behaviour when all vertices are out of bounds
    if query_final[0][0] == None:
        raise InvalidUsage(404, 4002,
                           'The requested geometry is outside the bounds of {}'.format(dataset))
        
    return query_final[0][0]


def point_elevation(geometry, format_out, dataset):
    """
    Performs PostGIS query to enrich a point geometry.
    
    :param geometry: Input point to be enriched with elevation
    :type geometry: shapely.geometry.Point
    
    :param format_out: Specifies output format. One of ['geojson', 'point']
    :type format_out: string
    
    :param dataset: Elevation dataset to use for querying
    :type dataset: string
    
    :raises InvalidUsage: internal HTTP 500 error with more detailed description.
    
    :returns: 3D Point as GeoJSON or WKT
    :rtype: string
    """
    
    Model = _getModel(dataset)
    
    if geometry.geom_type == "Point":
        query_point2d = db.session \
                            .query(func.ST_SetSRID(func.St_PointFromText(geometry.wkt), 4326).label('geom')) \
                            .subquery() \
                            .alias('points2d')
        
        query_getelev = db.session \
                            .query(query_point2d.c.geom,
                                   ST_Value(Model.rast, query_point2d.c.geom).label('z')) \
                            .filter(ST_Intersects(Model.rast, query_point2d.c.geom)) \
                            .subquery().alias('getelevation')
        
        if format_out == 'geojson': 
            query_final = db.session \
                                .query(func.ST_AsGeoJSON(func.ST_MakePoint(ST_X(query_getelev.c.geom),
                                                                                         ST_Y(query_getelev.c.geom),
                                                                                         query_getelev.c.z)
                                                                        ))
        else:
            query_final = db.session \
                                .query(func.ST_AsText(func.ST_MakePoint(ST_X(query_getelev.c.geom),
                                                                        ST_Y(query_getelev.c.geom),
                                                                        query_getelev.c.z)
                                                                    ))
    else:
        raise InvalidUsage(400, 4002, "Needs to be a Point, not {}!".format(geometry.geom_type))
    
    try:
        return query_final[0][0]
    except:
        raise InvalidUsage(404, 4002,
                           'The requested geometry is outside the bounds of {}'.format(dataset))
