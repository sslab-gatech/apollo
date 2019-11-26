/*
index, default value, affected keyword,  
 0, 500, "or" / "and"
 1, 500, "not" / ""
 2, 500, "true" / "false"
 3, 11, "distinct" / ""
 4, 668, "limit" / ""
 5, 110, "case"
 6, 24, "nullif"
 7, 24, "coalesce"
 8, 84, atomic_subselect (i.e., one line select statement with one row)
 9, 500, subquery
10, 500, join
11, 500, join - inner
12, 500, join - left
13, 500, join - right
14, 0,   reserved  - reserved
*/

int probability[15] = {500, 500, 500,  11, 668, 
					   110,  24,  24,  84, 500, 
					   500, 500, 500, 500,   0};