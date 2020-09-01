
select  
  cast(coalesce(ref_0.O_ALL_LOCAL,
    ref_0.O_OL_CNT) as INTEGER) as c0, 
  case when 1 then subq_0.c5 else subq_0.c5 end
     as c1, 
  ref_0.O_W_ID as c2, 
  cast(coalesce(ref_0.O_C_ID,
    ref_0.O_CARRIER_ID) as INTEGER) as c3, 
  (select O_ENTRY_D from main.OORDER limit 1 offset 4)
     as c4, 
  11 as c5
from 
  main.OORDER as ref_0
    left join (select  
          ref_1.S_DIST_01 as c0, 
          ref_1.S_YTD as c1, 
          79 as c2, 
          ref_1.S_DIST_05 as c3, 
          ref_1.S_DIST_06 as c4, 
          case when (1) 
              and (((0) 
                  and (75 is not NULL)) 
                and ((((0) 
                      and (((EXISTS (
                            select  
                                ref_2.OL_W_ID as c0
                              from 
                                main.ORDER_LINE as ref_2
                              where 1
                              limit 34)) 
                          or (0)) 
                        and (1))) 
                    or (ref_1.S_ORDER_CNT is not NULL)) 
                  and (ref_1.S_DIST_01 is not NULL))) then ref_1.S_DIST_04 else ref_1.S_DIST_04 end
             as c5, 
          ref_1.S_DIST_01 as c6, 
          ref_1.S_YTD as c7, 
          ref_1.S_DIST_04 as c8
        from 
          main.STOCK as ref_1
        where (ref_1.S_DIST_03 is not NULL) 
          or (0)) as subq_0
    on (ref_0.O_OL_CNT = subq_0.c1 )
where ((36 is not NULL) 
    and (subq_0.c1 is not NULL)) 
  and ((ref_0.O_W_ID is not NULL) 
    or ((((((((((0) 
                      or ((subq_0.c7 is not NULL) 
                        and (0))) 
                    or (0)) 
                  or (((ref_0.O_ALL_LOCAL is not NULL) 
                      or (((1) 
                          and ((0) 
                            and (0))) 
                        or (1))) 
                    or ((EXISTS (
                        select  
                            ref_0.O_CARRIER_ID as c0
                          from 
                            main.OORDER as ref_3
                          where 0
                          limit 108)) 
                      or (((((45 is not NULL) 
                              or (((((((subq_0.c0 is not NULL) 
                                          and (1)) 
                                        and ((ref_0.O_C_ID is not NULL) 
                                          and (subq_0.c1 is not NULL))) 
                                      or (subq_0.c7 is not NULL)) 
                                    and (1)) 
                                  and (0)) 
                                or ((0) 
                                  and ((0) 
                                    or (0))))) 
                            and ((1) 
                              and (EXISTS (
                                select  
                                    ref_4.W_YTD as c0, 
                                    ref_0.O_ID as c1
                                  from 
                                    main.WAREHOUSE as ref_4
                                  where 0)))) 
                          or ((1) 
                            and ((((EXISTS (
                                    select  
                                        (select W_ID from main.WAREHOUSE limit 1 offset 1)
                                           as c0, 
                                        ref_5.S_DIST_01 as c1, 
                                        (select NO_O_ID from main.NEW_ORDER limit 1 offset 33)
                                           as c2, 
                                        subq_0.c4 as c3, 
                                        subq_0.c0 as c4, 
                                        subq_0.c2 as c5, 
                                        ref_5.S_DIST_01 as c6, 
                                        ref_0.O_CARRIER_ID as c7, 
                                        subq_0.c2 as c8, 
                                        subq_0.c6 as c9, 
                                        ref_5.S_DIST_10 as c10, 
                                        subq_0.c3 as c11
                                      from 
                                        main.STOCK as ref_5
                                      where (1) 
                                        or (ref_0.O_ID is not NULL))) 
                                  and (subq_0.c2 is not NULL)) 
                                and (1)) 
                              and ((ref_0.O_D_ID is not NULL) 
                                and (0))))) 
                        or (ref_0.O_C_ID is not NULL))))) 
                or (ref_0.O_ID is not NULL)) 
              and (((EXISTS (
                    select  
                        subq_0.c6 as c0, 
                        ref_6.W_STREET_1 as c1, 
                        ref_6.W_YTD as c2, 
                        ref_6.W_STREET_1 as c3, 
                        ref_6.W_STATE as c4, 
                        ref_0.O_ALL_LOCAL as c5, 
                        subq_0.c0 as c6, 
                        ref_6.W_CITY as c7, 
                        74 as c8, 
                        subq_0.c1 as c9, 
                        ref_6.W_CITY as c10, 
                        ref_0.O_ENTRY_D as c11, 
                        39 as c12, 
                        ref_6.W_STREET_2 as c13
                      from 
                        main.WAREHOUSE as ref_6
                      where ref_0.O_C_ID is not NULL)) 
                  and (((1) 
                      and (ref_0.O_CARRIER_ID is not NULL)) 
                    or (1))) 
                or (subq_0.c4 is not NULL))) 
            and (((((ref_0.O_ALL_LOCAL is not NULL) 
                    and (0)) 
                  or ((EXISTS (
                      select  
                          ref_0.O_ID as c0, 
                          ref_0.O_W_ID as c1, 
                          ref_0.O_OL_CNT as c2, 
                          ref_0.O_C_ID as c3, 
                          ref_0.O_D_ID as c4, 
                          subq_0.c6 as c5, 
                          subq_0.c8 as c6, 
                          ref_0.O_W_ID as c7, 
                          ref_0.O_W_ID as c8, 
                          (select H_AMOUNT from main.HISTORY limit 1 offset 1)
                             as c9, 
                          9 as c10
                        from 
                          main.ORDER_LINE as ref_7
                        where (1) 
                          and (subq_0.c7 is not NULL)
                        limit 126)) 
                    and (0))) 
                or (subq_0.c0 is not NULL)) 
              and (0))) 
          or (((ref_0.O_ID is not NULL) 
              or (1)) 
            or ((1) 
              or (EXISTS (
                select  
                    subq_0.c8 as c0
                  from 
                    main.OORDER as ref_8
                  where 0
                  limit 97))))) 
        or (0)) 
      or ((65 is not NULL) 
        or (EXISTS (
          select  
              ref_9.D_ZIP as c0, 
              ref_0.O_CARRIER_ID as c1, 
              subq_0.c5 as c2, 
              70 as c3, 
              ref_0.O_CARRIER_ID as c4, 
              ref_9.D_W_ID as c5
            from 
              main.DISTRICT as ref_9
            where (((0) 
                  or ((((((subq_0.c3 is not NULL) 
                            and (1)) 
                          and (((1) 
                              and ((subq_0.c0 is not NULL) 
                                or (1))) 
                            and (ref_9.D_TAX is not NULL))) 
                        and (57 is not NULL)) 
                      or (1)) 
                    or (ref_0.O_ID is not NULL))) 
                or (((1) 
                    or ((0) 
                      or ((((((0) 
                                and (EXISTS (
                                  select  
                                      ref_10.W_CITY as c0, 
                                      ref_9.D_ID as c1, 
                                      36 as c2
                                    from 
                                      main.WAREHOUSE as ref_10
                                    where 1
                                    limit 149))) 
                              and (1)) 
                            and (ref_9.D_STREET_2 is not NULL)) 
                          and ((EXISTS (
                              select  
                                  ref_0.O_D_ID as c0, 
                                  ref_11.NO_D_ID as c1, 
                                  subq_0.c1 as c2, 
                                  subq_0.c4 as c3, 
                                  ref_9.D_ID as c4, 
                                  ref_11.NO_W_ID as c5
                                from 
                                  main.NEW_ORDER as ref_11
                                where (1) 
                                  and (0)
                                limit 19)) 
                            or (subq_0.c4 is not NULL))) 
                        and (1)))) 
                  and ((0) 
                    and (ref_0.O_C_ID is not NULL)))) 
              or ((0) 
                and ((ref_9.D_TAX is not NULL) 
                  or ((0) 
                    and (0))))
            limit 91)))))
limit 87;

/* Elapsed old:0.644195 new:13.626051 ratio:21.152057 */
