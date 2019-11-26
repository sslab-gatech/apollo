
select  
  subq_1.c0 as c0, 
  subq_1.c0 as c1
from 
  (select  
          26 as c0
        from 
          (select  
                ref_0.C_W_ID as c0, 
                ref_0.C_ZIP as c1, 
                81 as c2, 
                ref_0.C_CREDIT_LIM as c3, 
                77 as c4, 
                ref_0.C_MIDDLE as c5, 
                ref_0.C_ID as c6, 
                ref_0.C_ZIP as c7, 
                ref_0.C_CITY as c8, 
                ref_0.C_MIDDLE as c9, 
                ref_0.C_DISCOUNT as c10, 
                ref_0.C_DISCOUNT as c11, 
                ref_0.C_SINCE as c12, 
                ref_0.C_CREDIT as c13, 
                ref_0.C_W_ID as c14, 
                ref_0.C_DISCOUNT as c15, 
                ref_0.C_CITY as c16, 
                ref_0.C_PHONE as c17
              from 
                main.CUSTOMER as ref_0
              where ref_0.C_MIDDLE is not NULL
              limit 145) as subq_0
        where subq_0.c11 is not NULL) as subq_1
    left join (select  
          ref_1.C_STREET_2 as c0
        from 
          main.CUSTOMER as ref_1
        where ((((((((EXISTS (
                          select  
                              ref_1.C_YTD_PAYMENT as c0, 
                              ref_1.C_W_ID as c1, 
                              ref_2.S_DIST_01 as c2, 
                              ref_2.S_YTD as c3, 
                              ref_1.C_MIDDLE as c4, 
                              ref_1.C_D_ID as c5, 
                              ref_2.S_I_ID as c6, 
                              ref_1.C_CITY as c7, 
                              ref_1.C_STREET_2 as c8, 
                              98 as c9, 
                              ref_1.C_FIRST as c10, 
                              ref_2.S_DIST_07 as c11
                            from 
                              main.STOCK as ref_2
                            where 0
                            limit 35)) 
                        and ((ref_1.C_BALANCE is not NULL) 
                          or (1))) 
                      or (((1) 
                          and (ref_1.C_CITY is not NULL)) 
                        and ((0) 
                          and ((1) 
                            or ((ref_1.C_CREDIT_LIM is not NULL) 
                              or ((0) 
                                or (0))))))) 
                    and (((ref_1.C_MIDDLE is not NULL) 
                        and (0)) 
                      or (ref_1.C_DATA is not NULL))) 
                  and ((ref_1.C_DELIVERY_CNT is not NULL) 
                    and ((1) 
                      or (ref_1.C_D_ID is not NULL)))) 
                or ((0) 
                  or ((ref_1.C_SINCE is not NULL) 
                    or (ref_1.C_STATE is not NULL)))) 
              and (((((ref_1.C_ID is not NULL) 
                      and ((ref_1.C_FIRST is not NULL) 
                        or (0))) 
                    and ((0) 
                      and ((ref_1.C_CREDIT_LIM is not NULL) 
                        or (ref_1.C_CITY is not NULL)))) 
                  and (0)) 
                and (0))) 
            and (((((1) 
                    and ((1) 
                      and (((1) 
                          and (((((ref_1.C_MIDDLE is not NULL) 
                                  or (EXISTS (
                                    select  
                                        ref_3.NO_D_ID as c0, 
                                        ref_1.C_LAST as c1, 
                                        ref_1.C_PHONE as c2, 
                                        ref_3.NO_D_ID as c3, 
                                        ref_3.NO_W_ID as c4, 
                                        ref_3.NO_W_ID as c5, 
                                        ref_1.C_ID as c6, 
                                        ref_1.C_ID as c7, 
                                        ref_3.NO_D_ID as c8
                                      from 
                                        main.NEW_ORDER as ref_3
                                      where ref_3.NO_O_ID is not NULL))) 
                                and ((0) 
                                  or (1))) 
                              and (0)) 
                            and (1))) 
                        and ((EXISTS (
                            select  
                                ref_4.D_YTD as c0, 
                                ref_4.D_STREET_2 as c1, 
                                ref_4.D_STATE as c2, 
                                ref_4.D_STREET_2 as c3, 
                                ref_1.C_DATA as c4, 
                                ref_1.C_STATE as c5, 
                                ref_4.D_TAX as c6, 
                                ref_1.C_BALANCE as c7
                              from 
                                main.DISTRICT as ref_4
                              where (1) 
                                or (0))) 
                          and ((0) 
                            or ((0) 
                              and ((1) 
                                or (EXISTS (
                                  select  
                                      ref_1.C_CITY as c0
                                    from 
                                      main.HISTORY as ref_5
                                    where 0
                                    limit 134))))))))) 
                  or (EXISTS (
                    select  
                        ref_6.OL_O_ID as c0, 
                        ref_1.C_STATE as c1
                      from 
                        main.ORDER_LINE as ref_6
                      where 1
                      limit 123))) 
                and (ref_1.C_ZIP is not NULL)) 
              and ((0) 
                and ((0) 
                  and ((ref_1.C_W_ID is not NULL) 
                    and ((((EXISTS (
                            select  
                                ref_7.C_ZIP as c0, 
                                ref_7.C_DATA as c1, 
                                ref_1.C_LAST as c2, 
                                ref_7.C_LAST as c3, 
                                ref_1.C_CREDIT as c4, 
                                ref_1.C_PAYMENT_CNT as c5, 
                                ref_7.C_FIRST as c6
                              from 
                                main.CUSTOMER as ref_7
                              where (ref_1.C_FIRST is not NULL) 
                                and ((1) 
                                  and (((0) 
                                      and (1)) 
                                    and (1)))
                              limit 125)) 
                          or (((ref_1.C_DELIVERY_CNT is not NULL) 
                              and ((ref_1.C_MIDDLE is not NULL) 
                                or (0))) 
                            or ((ref_1.C_PHONE is not NULL) 
                              and (ref_1.C_SINCE is not NULL)))) 
                        and (ref_1.C_W_ID is not NULL)) 
                      and (((1) 
                          and (1)) 
                        or (EXISTS (
                          select  
                              ref_8.I_PRICE as c0
                            from 
                              main.ITEM as ref_8
                            where ref_1.C_PAYMENT_CNT is not NULL))))))))) 
          or (0)) as subq_2
    on (((((subq_2.c0 is not NULL) 
              or ((subq_1.c0 is not NULL) 
                and ((EXISTS (
                    select  
                        ref_9.H_DATA as c0, 
                        subq_2.c0 as c1, 
                        ref_9.H_DATE as c2, 
                        ref_9.H_C_D_ID as c3
                      from 
                        main.HISTORY as ref_9
                      where subq_2.c0 is not NULL
                      limit 77)) 
                  and (EXISTS (
                    select  
                        subq_2.c0 as c0, 
                        ref_10.C_YTD_PAYMENT as c1
                      from 
                        main.CUSTOMER as ref_10
                      where (((EXISTS (
                              select  
                                  ref_10.C_CREDIT as c0, 
                                  ref_10.C_SINCE as c1, 
                                  subq_1.c0 as c2, 
                                  subq_2.c0 as c3
                                from 
                                  main.STOCK as ref_11
                                where (ref_10.C_SINCE is not NULL) 
                                  or (ref_10.C_LAST is not NULL))) 
                            and (ref_10.C_PAYMENT_CNT is not NULL)) 
                          and ((0) 
                            and (1))) 
                        or (1)))))) 
            and ((1) 
              or (subq_2.c0 is not NULL))) 
          or (EXISTS (
            select  
                subq_2.c0 as c0, 
                ref_12.C_STATE as c1, 
                subq_1.c0 as c2, 
                subq_1.c0 as c3, 
                ref_12.C_PHONE as c4
              from 
                main.CUSTOMER as ref_12
              where 0
              limit 186))) 
        and (77 is not NULL))
where subq_2.c0 is not NULL
limit 130;

/* Elapsed old:0.128324 new:16.951913 ratio:132.102402 */
