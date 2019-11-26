EXPLAIN ANALYZE

WITH 
jennifer_0 AS (select  
    case when case when cast(null as text) < (select definition from pg_catalog.pg_rules limit 1 offset 6)
               then pg_catalog.cashlarger(
            cast(cast(null as money) as money),
            cast(cast(null as money) as money)) else pg_catalog.cashlarger(
            cast(cast(null as money) as money),
            cast(cast(null as money) as money)) end
           > case when cast(null as tsvector) <> cast(null as tsvector) then cast(null as money) else cast(null as money) end
           then subq_0.c3 else subq_0.c3 end
       as c0, 
    subq_0.c2 as c1, 
    subq_0.c2 as c2, 
    case when (select pg_catalog.max(valuntil) from pg_catalog.pg_shadow)
           >= pg_catalog.timenow() then pg_catalog.pg_stat_get_function_self_time(
        cast(subq_0.c0 as oid)) else pg_catalog.pg_stat_get_function_self_time(
        cast(subq_0.c0 as oid)) end
       as c3, 
    subq_0.c3 as c4, 
    11 as c5
  from 
    (select  
          ref_1.conrelid as c0, 
          68 as c1, 
          (select tmplnamespace from pg_catalog.pg_ts_template limit 1 offset 5)
             as c2, 
          ref_1.conindid as c3, 
          ref_1.connoinherit as c4
        from 
          information_schema.foreign_data_wrappers as ref_0
            inner join pg_catalog.pg_constraint as ref_1
            on (ref_1.coninhcount < (select attlen from pg_catalog.pg_attribute limit 1 offset 3)
                  )
        where ref_1.coninhcount <> cast(null as int8)) as subq_0
  where pg_catalog.date_trunc(
      cast((select objtype from pg_catalog.pg_seclabels limit 1 offset 5)
         as text),
      cast(cast(null as "timestamp") as "timestamp")) = cast(null as date)), 

jennifer_1 AS (select  
    ref_4.amopopr as c0, 
    pg_catalog.ltrim(
      cast(case when case when true then cast(null as "timestamp") else cast(null as "timestamp") end
             = cast(null as "timestamp") then (select rolpassword from pg_catalog.pg_roles limit 1 offset 4)
           else (select rolpassword from pg_catalog.pg_roles limit 1 offset 4)
           end
         as text),
      cast(cast(nullif((select application_name from pg_catalog.pg_stat_activity limit 1 offset 6)
          ,
        cast(coalesce(cast(null as text),
          cast(null as text)) as text)) as text) as text)) as c1, 
    ref_4.amoppurpose as c2, 
    pg_catalog.pg_stop_backup() as c3, 
    ref_4.amopmethod as c4, 
    ref_4.amoplefttype as c5, 
    
      pg_catalog.var_samp(
        cast((select checkpoint_write_time from pg_catalog.pg_stat_bgwriter limit 1 offset 10)
           as float8)) over (partition by ref_4.amoprighttype order by subq_2.c1,subq_2.c0,subq_2.c0) as c6
  from 
    (select  
            ref_2.analyze_count as c0, 
            ref_2.autoanalyze_count as c1, 
            subq_1.c4 as c2
          from 
            pg_catalog.pg_stat_all_tables as ref_2,
            lateral (select  
                  ref_3.tidx_blks_hit as c0, 
                  ref_2.n_dead_tup as c1, 
                  ref_3.relid as c2, 
                  ref_2.n_tup_upd as c3, 
                  ref_3.heap_blks_read as c4
                from 
                  pg_catalog.pg_statio_sys_tables as ref_3
                where ref_2.last_analyze > cast(null as "timestamp")) as subq_1
          where cast(null as tid) = cast(null as tid)
          limit 121) as subq_2
      left join pg_catalog.pg_amop as ref_4
      on (cast(null as point) @ pg_catalog.lseg(
            cast(cast(null as box) as box)))
  where ((select client_addr from pg_catalog.pg_stat_activity limit 1 offset 80)
         < (select client_addr from pg_catalog.pg_stat_replication limit 1 offset 3)
        ) 
    or (ref_4.amopfamily is not NULL)
  limit 156)
select  
    subq_3.c0 as c0, 
    (select pad_attribute from information_schema.collations limit 1 offset 31)
       as c1
  from 
    (select  
          (select srvoptions from information_schema._pg_foreign_servers limit 1 offset 2)
             as c0, 
          ref_6.grantor as c1
        from 
          information_schema.udt_privileges as ref_5
            inner join information_schema.role_usage_grants as ref_6
            on (ref_5.is_grantable = ref_6.is_grantable )
        where (cast(null as point) @ cast(null as box)) 
          or (EXISTS (
            select  
                ref_6.object_catalog as c0, 
                ref_6.grantee as c1, 
                ref_7.table_name as c2, 
                ref_8.n_tup_upd as c3, 
                ref_7.constraint_name as c4, 
                ref_5.grantor as c5, 
                ref_8.schemaname as c6, 
                ref_5.privilege_type as c7, 
                ref_5.privilege_type as c8, 
                93 as c9, 
                ref_7.constraint_name as c10, 
                ref_6.object_catalog as c11, 
                ref_5.grantee as c12, 
                ref_7.constraint_catalog as c13, 
                ref_8.n_tup_hot_upd as c14, 
                ref_7.table_schema as c15
              from 
                information_schema.constraint_table_usage as ref_7
                  left join pg_catalog.pg_stat_xact_all_tables as ref_8
                  on ((ref_6.grantor is NULL) 
                      or (cast(null as aclitem) = cast(null as aclitem)))
              where cast(null as bpchar) !~~ (select pg_catalog.min(description) from pg_catalog.pg_description)
                  
              limit 174))) as subq_3
  where true
  limit 157
;;