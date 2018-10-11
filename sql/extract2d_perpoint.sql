EXPLAIN (ANALYZE, TIMING OFF)
/*WITH point AS
    (SELECT 'SRID=4326;POINT(8.685477000000001 49.405781)'::geometry AS geom),*/
WITH  point2d AS
    (SELECT p.geom AS geom, ST_Value(oes_cgiar.rast, 1, p.geom) AS val
     FROM oes_cgiar,
	  (SELECT ST_GeomFromText('POINT(8.685477000000001 49.405781)', 4326) as geom) as p
     WHERE ST_Intersects(oes_cgiar.rast, p.geom)),
  points3d AS
    (SELECT ST_SetSRID(ST_MakePoint(ST_X(geom), ST_Y(geom), val), 4326) AS geom FROM point2d, oes_cgiar)
-- Build 3D line from 3D points
SELECT * FROM points3d;
/*CREATE TABLE temp AS SELECT ST_MakeLine(geom) FROM points3d;*/
