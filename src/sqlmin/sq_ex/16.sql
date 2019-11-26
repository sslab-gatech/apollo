
select  
  ref_0.OL_O_ID as c0, 
  ref_0.OL_NUMBER as c1
from 
  main.ORDER_LINE as ref_0
    left join (select  
          ref_1.H_D_ID as c0, 
          ref_1.H_D_ID as c1, 
          ref_1.H_AMOUNT as c2, 
          ref_1.H_AMOUNT as c3, 
          ref_1.H_C_ID as c4, 
          ref_1.H_C_W_ID as c5
        from 
          main.HISTORY as ref_1
        where EXISTS (
          select  
              ref_1.H_C_ID as c0, 
              ref_1.H_AMOUNT as c1, 
              ref_1.H_W_ID as c2, 
              ref_1.H_C_D_ID as c3, 
              ref_1.H_W_ID as c4
            from 
              main.WAREHOUSE as ref_2
            where ((EXISTS (
                  select  
                      ref_1.H_D_ID as c0, 
                      ref_1.H_D_ID as c1, 
                      ref_2.W_STREET_1 as c2, 
                      ref_2.W_CITY as c3, 
                      ref_3.I_DATA as c4, 
                      ref_2.W_YTD as c5, 
                      ref_3.I_DATA as c6, 
                      ref_3.I_DATA as c7, 
                      ref_1.H_D_ID as c8, 
                      ref_3.I_ID as c9, 
                      ref_2.W_STREET_2 as c10, 
                      ref_2.W_YTD as c11, 
                      ref_2.W_STREET_1 as c12, 
                      ref_2.W_ID as c13, 
                      ref_1.H_C_ID as c14
                    from 
                      main.ITEM as ref_3
                    where (1) 
                      or (EXISTS (
                        select  
                            ref_2.W_STREET_1 as c0, 
                            ref_2.W_STREET_2 as c1
                          from 
                            main.STOCK as ref_4
                          where ref_3.I_IM_ID is not NULL))
                    limit 128)) 
                and ((0) 
                  and ((EXISTS (
                      select  
                          ref_5.S_DIST_04 as c0, 
                          ref_1.H_DATE as c1, 
                          ref_2.W_ZIP as c2, 
                          ref_2.W_STATE as c3, 
                          ref_1.H_D_ID as c4, 
                          (select I_PRICE from main.ITEM limit 1 offset 6)
                             as c5, 
                          ref_1.H_DATA as c6, 
                          ref_5.S_I_ID as c7, 
                          ref_2.W_ZIP as c8, 
                          ref_5.S_DIST_03 as c9, 
                          ref_2.W_NAME as c10, 
                          ref_2.W_STREET_2 as c11, 
                          ref_2.W_CITY as c12, 
                          ref_1.H_C_ID as c13, 
                          31 as c14, 
                          ref_5.S_REMOTE_CNT as c15, 
                          ref_1.H_AMOUNT as c16, 
                          ref_5.S_DIST_07 as c17, 
                          ref_1.H_C_ID as c18, 
                          ref_1.H_DATA as c19
                        from 
                          main.STOCK as ref_5
                        where 0
                        limit 47)) 
                    or ((0) 
                      or (ref_2.W_TAX is NULL))))) 
              and (ref_2.W_ID is NULL))) as subq_0
    on (ref_0.OL_I_ID = subq_0.c4 )
where subq_0.c5 is not NULL
limit 28;

/* Elapsed old:0.190720 new:3.006070 ratio:15.761685 */
