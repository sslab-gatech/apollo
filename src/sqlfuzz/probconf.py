#!/usr/bin/env python2

""" Probability table related variables
[OR<=>AND, NOT<=>nothing, TRUE<=>FALSE, distinct,       limit
case,     nullif,        coalesce,     atomic_seclect, subquery
join,     inner join,    left join,    right join,     N/A]
"""
INIT_PROB = [ 500.0, 500.0, 500.0, 11.0 , 668.0, \
              110.0, 24.0 , 24.0 , 84.0 , 500.0, \
              500.0, 500.0, 500.0, 500.0, 0.0 ]

MIN_PROB  = [ 300.0, 300.0, 300.0, 0.0,   300.0, \
              10.0,  0.0,   0.0,   0.0,   300.0, \
              300.0, 300.0, 300.0, 300.0, 0.0 ]

MAX_PROB  = [ 800.0, 800.0, 800.0, 150.0, 850.0, \
              400.0, 200.0, 200.0, 300.0, 800.0, \
              800.0, 800.0, 800.0, 800.0, 0.0 ]

KEYWORD_IDX = {}
KEYWORD_IDX["or"]        = 0
KEYWORD_IDX["not"]       = 1
KEYWORD_IDX["true"]      = 2
KEYWORD_IDX["distinct"]  = 3
KEYWORD_IDX["limit"]     = 4
KEYWORD_IDX["case"]      = 5
KEYWORD_IDX["nullif"]    = 6
KEYWORD_IDX["coalesce"]  = 7
KEYWORD_IDX["join"]      = 10
KEYWORD_IDX["inner"]     = 11
KEYWORD_IDX["left"]      = 12
KEYWORD_IDX["right"]     = 13


# blacklist names
BLACKLIST = ["tablesample", "inet_client", "plpgsql_call_handler"]
STR_BLACKLIST = ["ref_", "subq_", "c_", "d_", "h_", "public.", "s_", \
    "ol_", "o_", "---", "w_", "--ex", "i_", "no_", "(", ")", "--where", "pg_catalog",\
    "analyze", ",", "main.", "--", "actual"]
OPR = [">", "<", "=", "#", "|", "?", "*", "&", "!", "~", "@"]
