#!/usr/bin/env python2
import os
import sys
import argparse

# TODO: remove this (stupid) duplicated parsing
dbfuzz_parser = argparse.ArgumentParser()    
dbfuzz_parser.add_argument("-db", "--database", dest="dbname", type=str,
                    default=None, help="DBMS name", required=True)
dbfuzz_parser.add_argument("-o", "--outdir", dest="outdir", type=str,
                    default=None, help="path of output directory", required=True)
dbfuzz_parser.add_argument("--probability", default=False, action='store_true')
dbfuzz_parser.add_argument("--no-probability", default=False, action='store_false')
dbfuzz_parser.add_argument("--initialize", default=False, action='store_true')
dbfuzz_parser.add_argument("--no-initialize", default=False, action='store_false')
args = dbfuzz_parser.parse_args()

if args.dbname == "postgres":
    TARGET_DB = "postgres" 
elif args.dbname == "sqlite":
    TARGET_DB = "sqlite" 
else:
    raise "Please specify either postgres or sqlite"

if args.probability:
    SQLSMITH = "./sqlsmith-prob"
else:
    SQLSMITH = "./sqlsmith"

if TARGET_DB == "postgres":    
    PASSWD = "mysecretpassword"
    os.environ['PGPASSWORD'] = PASSWD
    USER = "postgres"    
    SERVERS = {"5432":96, "5435":111}   # postgres 2 versions 

    LATEST_VERSION_PORT = 5435
    OLDEST_VERSION_PORT = 5432

# file path related
TMP_ERR_PN    = os.path.join(args.outdir,  ".sqlsmith_err")
TMP_QUERY_PN  = os.path.join(args.outdir,  ".sqlsmith_query")
TMP_QUERY_OUT = os.path.join(args.outdir,  "queue")
TMP_QUERY_ERR = os.path.join(args.outdir,  "error")
CURR_QUERY    = os.path.join(args.outdir,  ".curr_query")

PROB_PN       = "%s/probability" % (args.outdir) 
TMP_ERR       = "%s/.stderr" % (args.outdir) 
TMP_ERR2      = "%s/.stderr2" % (args.outdir)
TPCC_DIR      = "benchmark/tpcc_postgres.sql"
TMP_OUTPUT    = os.path.join(args.outdir, ".tmpout")
TMP_CMD       = os.path.join(args.outdir, ".curcmd")

# values 
TEST_DB            = "test_bd" # db name for fuzzing
THRESHOLD          = 2  # we only consider as regression if ... (2 means two times of difference)
MIN                = 0.000001 
TIMEOUT            = 10  # timeout for each query (second)
MINIMUM_QUERY_TIME = 0.01 # we discard very short execution time (second)
PROBRESET          = 120 # how frequenty reset the prob-table (minutes)

# settings for setup or restore DB
USE_TPCC = True 
RELAUNCH_SCRIPT_DIR  = "benchmark"
RELAUNCH_SCRIPT_TPCC = "gen_tpcc.sh"
RELAUNCH_SCRIPT_NOR  = "gen_nor.sh"

class Logger (object):
    def __init__(self, target_db):
        if target_db == "postgres":
            self.logfile = "fuzz_log_pg"
        elif target_db == "sqlite":
            self.logfile = "fuzz_log_sq"  

    def debug(self, msg, _print=False):
        with open(self.logfile, 'a') as f:
            f.write(msg+"\n")

        if _print:
            print msg
