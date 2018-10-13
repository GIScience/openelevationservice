                                                                       QUERY PLAN                                                                       
--------------------------------------------------------------------------------------------------------------------------------------------------------
 Aggregate  (cost=2949.72..2949.73 rows=1 width=32) (actual time=15064.299..15064.299 rows=1 loops=1)
   CTE line
     ->  Result  (cost=0.00..0.01 rows=1 width=32) (actual time=0.001..0.001 rows=1 loops=1)
   CTE cells
     ->  Nested Loop  (cost=0.14..2949.03 rows=13 width=40) (actual time=41.342..15058.789 rows=394 loops=1)
           ->  Result  (cost=0.00..265.27 rows=1000 width=32) (actual time=0.025..1.819 rows=394 loops=1)
                 ->  ProjectSet  (cost=0.00..5.28 rows=1000 width=32) (actual time=0.024..1.399 rows=394 loops=1)
                       ->  CTE Scan on line  (cost=0.00..0.02 rows=1 width=32) (actual time=0.011..0.011 rows=1 loops=1)
           ->  Index Scan using no_tiles_st_convexhull_idx on no_tiles r  (cost=0.14..2.66 rows=1 width=18) (actual time=0.049..0.051 rows=1 loops=394)
                 Index Cond: ((rast)::geometry && (((st_dumppoints(line.geom))).geom))
                 Filter: _st_intersects((((st_dumppoints(line.geom))).geom), rast, NULL::integer)
   CTE points3d
     ->  CTE Scan on cells  (cost=0.00..0.39 rows=13 width=32) (actual time=41.353..15062.736 rows=394 loops=1)
   ->  CTE Scan on points3d  (cost=0.00..0.26 rows=13 width=32) (actual time=41.354..15063.175 rows=394 loops=1)
 Planning time: 2.005 ms
 Execution time: 15096.652 ms
(16 rows)

