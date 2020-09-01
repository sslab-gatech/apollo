
select  
  ref_1.I_ID as c0, 
  ref_1.I_ID as c1, 
  (select H_AMOUNT from main.HISTORY limit 1 offset 1)
     as c2, 
  subq_0.c0 as c3, 
  ref_1.I_DATA as c4, 
  subq_0.c0 as c5, 
  ref_1.I_ID as c6, 
  ref_1.I_IM_ID as c7, 
  subq_0.c0 as c8
from 
  (select  
          ref_0.S_DIST_06 as c0
        from 
          main.STOCK as ref_0
        where ref_0.S_DIST_10 is not NULL
        limit 87) as subq_0
    left join main.ITEM as ref_1
    on (subq_0.c0 = ref_1.I_NAME )
where ref_1.I_DATA is not NULL
limit 160;

/* Elapsed old:0.730127 new:5.885671 ratio:8.061159 */
