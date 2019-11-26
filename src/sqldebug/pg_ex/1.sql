EXPLAIN ANALYZE

WITH 
jennifer_0 AS (select  
    subq_0.c3 as c0, 
    subq_0.c6 as c1, 
    subq_0.c0 as c2, 
    subq_0.c3 as c3, 
    (select pg_catalog.max(idx_scan) from pg_catalog.pg_stat_user_indexes)
       as c4, 
    case when subq_0.c6 is NULL then pg_catalog.timeofday() else pg_catalog.timeofday() end
       as c5
  from 
    (select  
          ref_0.typanalyze as c0, 
          ref_0.typispreferred as c1, 
          ref_0.typtypmod as c2, 
          ref_0.typrelid as c3, 
          ref_0.typcollation as c4, 
          ref_0.typdelim as c5, 
          ref_0.typnotnull as c6
        from 
          pg_catalog.pg_type as ref_0
        where case when ((cast(null as anyrange) <> cast(null as anyrange)) 
                and (((cast(null as path) @> cast(null as point)) 
                    or ((ref_0.typtypmod <= ref_0.typndims) 
                      and ((ref_0.typtype is not NULL) 
                        and (((false) 
                            and (cast(null as tsvector) @@@ cast(null as tsquery))) 
                          or (cast(null as record) *<> cast(null as record)))))) 
                  and (cast(null as box) ?# cast(null as box)))) 
              and (ref_0.typname >= ref_0.typname) then cast(null as polygon) else cast(null as polygon) end
             <@ pg_catalog.polygon(
            cast(ref_0.typndims as int4),
            cast(cast(null as circle) as circle))
        limit 45) as subq_0
  where (pg_catalog.tintervalin(
        cast(case when (true) 
            and ((cast(null as circle) |>> cast(null as circle)) 
              and (true)) then cast(null as cstring) else cast(null as cstring) end
           as cstring)) #> case when subq_0.c2 is not NULL then case when true then cast(null as reltime) else cast(null as reltime) end
           else case when true then cast(null as reltime) else cast(null as reltime) end
           end
        ) 
    or ((select agginitval from pg_catalog.pg_aggregate limit 1 offset 5)
         >= (select provider from pg_catalog.pg_shseclabel limit 1 offset 6)
        ))
select  
    subq_1.c0 as c0, 
    subq_1.c0 as c1, 
    subq_1.c0 as c2, 
    subq_1.c1 as c3, 
    subq_1.c1 as c4, 
    subq_1.c0 as c5
  from 
    (select  
          ref_1.relname as c0, 
          ref_1.relname as c1
        from 
          pg_catalog.pg_statio_sys_sequences as ref_1
              inner join information_schema.role_routine_grants as ref_2
              on (ref_1.blks_read >= ref_1.blks_hit)
            inner join pg_catalog.pg_type as ref_3
              right join information_schema.user_mapping_options as ref_4
              on ((select seq_scan from pg_catalog.pg_stat_xact_sys_tables limit 1 offset 2)
                     <= ref_3.typlen)
            on (ref_2.specific_name = ref_4.authorization_identifier )
        where ref_1.blks_hit is not NULL) as subq_1
  where true
  limit 107
;;