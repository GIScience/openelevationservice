# -*- coding: utf-8 -*-

from openelevationservice.server.utils.logger import get_logger
from openelevationservice.server.db_import.models import db, Cgiar

from shapely import wkb

from geoalchemy2.functions import ST_DumpPoints, ST_Value, ST_Intersects, ST_X, ST_Y, ST_AsText

from sqlalchemy import func

log = get_logger(__name__)

def request_elevation(geometry):
    
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
        
        query_final = db.session \
                          .query(func.ST_AsGeoJSON(func.ST_MakeLine(query_points3d.c.geom)))
        
#        Matching SQL:
#        WITH line AS
#                (SELECT 'SRID=4326;LINESTRING (8.677842999999999 49.406192,...)'::geometry AS geom),
#            cells AS
#                -- Get DEM elevation for each
#                (SELECT p.geom AS geom, ST_Value(r.rast, 1, p.geom) AS val
#                 FROM "50_tiles" r,
#                 (SELECT (ST_DumpPoints(geom)).geom AS geom FROM line) as p
#                 WHERE ST_Intersects(r.rast, p.geom)),
#                -- Instantiate 3D points
#            points3d AS
#                (SELECT ST_SetSRID(ST_MakePoint(ST_X(geom), ST_Y(geom), val), 4326) AS geom FROM cells)
#        -- Build 3D line from 3D points
#        SELECT ST_MakeLine(geom) FROM points3d;
        
        return query_final[0]