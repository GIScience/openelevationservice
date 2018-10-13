                                                                           QUERY PLAN                                                                            
-----------------------------------------------------------------------------------------------------------------------------------------------------------------
 Aggregate  (cost=320293.29..320293.30 rows=1 width=32) (actual time=951.354..951.354 rows=1 loops=1)
   CTE line
     ->  Result  (cost=0.00..0.01 rows=1 width=32) (actual time=0.001..0.001 rows=1 loops=1)
   CTE cells
     ->  Nested Loop  (cost=0.29..310213.27 rows=192000 width=40) (actual time=1.904..932.321 rows=8624 loops=1)
           ->  Result  (cost=0.00..265.27 rows=1000 width=32) (actual time=0.303..9.626 rows=8624 loops=1)
                 ->  ProjectSet  (cost=0.00..5.28 rows=1000 width=32) (actual time=0.299..7.465 rows=8624 loops=1)
                       ->  CTE Scan on line  (cost=0.00..0.02 rows=1 width=32) (actual time=0.197..0.197 rows=1 loops=1)
           ->  Index Scan using "50_tiles_st_convexhull_idx" on "50_tiles" r  (cost=0.29..261.75 rows=19 width=338) (actual time=0.060..0.061 rows=1 loops=8624)
                 Index Cond: ((rast)::geometry && (((st_dumppoints(line.geom))).geom))
                 Filter: _st_intersects((((st_dumppoints(line.geom))).geom), rast, NULL::integer)
   CTE points3d
     ->  CTE Scan on cells  (cost=0.00..5760.00 rows=192000 width=32) (actual time=1.909..943.524 rows=8624 loops=1)
   ->  CTE Scan on points3d  (cost=0.00..3840.00 rows=192000 width=32) (actual time=1.911..946.157 rows=8624 loops=1)
 Planning time: 0.713 ms
 Execution time: 988.803 ms
(16 rows)

