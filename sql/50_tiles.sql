                                                                           QUERY PLAN                                                                           
----------------------------------------------------------------------------------------------------------------------------------------------------------------
 Aggregate  (cost=320293.29..320293.30 rows=1 width=32) (actual time=34.049..34.049 rows=1 loops=1)
   CTE line
     ->  Result  (cost=0.00..0.01 rows=1 width=32) (actual time=0.001..0.001 rows=1 loops=1)
   CTE cells
     ->  Nested Loop  (cost=0.29..310213.27 rows=192000 width=40) (actual time=1.129..33.281 rows=394 loops=1)
           ->  Result  (cost=0.00..265.27 rows=1000 width=32) (actual time=0.027..0.365 rows=394 loops=1)
                 ->  ProjectSet  (cost=0.00..5.28 rows=1000 width=32) (actual time=0.026..0.279 rows=394 loops=1)
                       ->  CTE Scan on line  (cost=0.00..0.02 rows=1 width=32) (actual time=0.012..0.012 rows=1 loops=1)
           ->  Index Scan using "50_tiles_st_convexhull_idx" on "50_tiles" r  (cost=0.29..261.75 rows=19 width=338) (actual time=0.040..0.040 rows=1 loops=394)
                 Index Cond: ((rast)::geometry && (((st_dumppoints(line.geom))).geom))
                 Filter: _st_intersects((((st_dumppoints(line.geom))).geom), rast, NULL::integer)
   CTE points3d
     ->  CTE Scan on cells  (cost=0.00..5760.00 rows=192000 width=32) (actual time=1.132..33.737 rows=394 loops=1)
   ->  CTE Scan on points3d  (cost=0.00..3840.00 rows=192000 width=32) (actual time=1.133..33.860 rows=394 loops=1)
 Planning time: 1.989 ms
 Execution time: 70.122 ms
(16 rows)

