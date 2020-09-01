
select  
  subq_1.c8 as c0, 
  97 as c1, 
  subq_1.c4 as c2, 
  subq_1.c0 as c3, 
  subq_1.c1 as c4, 
  subq_1.c0 as c5
from 
  (select  
        subq_0.c2 as c0, 
        subq_0.c0 as c1, 
        29 as c2, 
        subq_0.c2 as c3, 
        subq_0.c2 as c4, 
        subq_0.c2 as c5, 
        subq_0.c2 as c6, 
        subq_0.c1 as c7, 
        subq_0.c0 as c8
      from 
        (select  
              ref_0.D_CITY as c0, 
              ref_0.D_CITY as c1, 
              ref_1.I_DATA as c2
            from 
              main.DISTRICT as ref_0
                left join main.ITEM as ref_1
                on (ref_0.D_CITY = ref_1.I_NAME )
            where ((1) 
                and (((0) 
                    or (ref_1.I_ID is not NULL)) 
                  or ((0) 
                    and (0)))) 
              or ((ref_0.D_NEXT_O_ID is not NULL) 
                or ((EXISTS (
                    select  
                        ref_0.D_W_ID as c0, 
                        ref_1.I_PRICE as c1, 
                        87 as c2, 
                        ref_2.W_STREET_2 as c3, 
                        ref_1.I_IM_ID as c4, 
                        ref_0.D_ZIP as c5, 
                        ref_0.D_ZIP as c6, 
                        (select NO_W_ID from main.NEW_ORDER limit 1 offset 5)
                           as c7, 
                        ref_0.D_ZIP as c8, 
                        ref_2.W_TAX as c9, 
                        ref_1.I_ID as c10, 
                        ref_0.D_STREET_1 as c11, 
                        ref_1.I_PRICE as c12, 
                        ref_1.I_PRICE as c13, 
                        ref_2.W_ID as c14, 
                        ref_0.D_NEXT_O_ID as c15
                      from 
                        main.WAREHOUSE as ref_2
                      where ((0) 
                          or (ref_2.W_TAX is not NULL)) 
                        or (0)
                      limit 93)) 
                  and (ref_1.I_PRICE is not NULL)))) as subq_0
      where (subq_0.c2 is not NULL) 
        and (subq_0.c2 is not NULL)) as subq_1
where (subq_1.c8 is not NULL) 
  or ((1) 
    or ((subq_1.c6 is not NULL) 
      or ((subq_1.c5 is not NULL) 
        and (subq_1.c2 is not NULL))))
limit 163;

/* Elapsed old:0.414178 new:4.084102 ratio:9.860743 */
