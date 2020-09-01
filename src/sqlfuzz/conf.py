#!/usr/bin/env python2
import os
import yaml
import argparse

yaml_parser = argparse.ArgumentParser()
yaml_parser.add_argument(
    "-c", "--config", dest="conf", type=str,
    default=None, help="Configuration YAML", required=True)
yaml_parser.add_argument(
    "-d", "--indir", dest="indir", type=str,
    default=None, help="path of input directory", required=False)
yaml_parser.add_argument(
    "-f", "--infile", dest="infile", type=str,
    default=None, help="path of input file", required=False)
args = yaml_parser.parse_args()

with open(args.conf, "r") as f:
    CONF = yaml.load(f, Loader=yaml.FullLoader)

TARGET_DB = CONF["DBMS"]

if CONF["USE_PROB"]:
    SQLSMITH = "./sqlsmith-prob"
else:
    SQLSMITH = "./sqlsmith"

if TARGET_DB == "postgres":
    PASSWD = CONF["PASSWD"]
    os.environ['PGPASSWORD'] = PASSWD
    USER = CONF["USERNAME"]
    LATEST_VERSION_PORT = CONF["NEW_VER_PORT"]
    OLDEST_VERSION_PORT = CONF["OLD_VER_PORT"]

elif TARGET_DB == "cockroach":
    LATEST_VERSION_PORT = CONF["NEW_VER_PORT"]
    OLDEST_VERSION_PORT = CONF["OLD_VER_PORT"]

elif TARGET_DB == "sqlite":
    LATEST_VERSION_PORT = None
    OLDEST_VERSION_PORT = None

if CONF["SQLSMITH_PORT"] is None:
    SQLSMITH_PORT = OLDEST_VERSION_PORT
else:
    SQLSMITH_PORT = CONF["SQLSMITH_PORT"]

SERVERS = {
    str(OLDEST_VERSION_PORT): CONF["DB_VER"][0],
    str(LATEST_VERSION_PORT): CONF["DB_VER"][1]
}

# db name for fuzzing
TEST_DB = CONF["DB"]

# difference between new/old to become regression
# e.g., If 2, newer version should x2 slower
THRESHOLD = CONF["THRESHOLD"]

# timeout for each query (second)
TIMEOUT = CONF["TIMEOUT"]

# we discard very short execution time (second)
MIN = MINIMUM_QUERY_TIME = CONF["MINIMUM_QUERY_TIME"]

# how frequenty reset the prob-table (minutes)
PROBRESET = CONF["PROBRESET"]

# settings for setup or restore DB
USE_TPCC = CONF["USE_TPCC"]

# output directory
OUT_DIR = CONF["OUTDIR"]

# file paths
PROB_PN = "%s/probability" % (OUT_DIR)
TMP_ERR = "%s/.stderr" % (OUT_DIR)
TMP_ERR2 = "%s/.stderr2" % (OUT_DIR)
TPCC_DIR = "benchmark/tpcc_postgres.sql"
TMP_OUTPUT = os.path.join(OUT_DIR, ".tmpout")
TMP_CMD = os.path.join(OUT_DIR, ".curcmd")
TMP_ERR_PN = os.path.join(OUT_DIR, ".sqlsmith_err")
TMP_QUERY_PN = os.path.join(OUT_DIR, ".sqlsmith_query")
TMP_QUERY_OUT = os.path.join(OUT_DIR, "queue")
TMP_QUERY_ERR = os.path.join(OUT_DIR, "error")
CURR_QUERY = os.path.join(OUT_DIR, ".curr_query")

# script for re-running the DB
RELAUNCH_SCRIPT_DIR = "benchmark"
RELAUNCH_SCRIPT_TPCC = "gen_tpcc.sh"
RELAUNCH_SCRIPT_NOR = "reset.sh"

# blacklist for cockroachdb
COCK_BLACKLIST = [
    'tablesample', 'as point', '*<', 'tsvector', 'tsquery', 'cstring']

# for minimizer
MIN_INFILE = args.infile
MIN_INDIR = args.indir

# etc.
CONFIG_PN = args.conf


class Logger (object):
    def __init__(self, target_db):
        if target_db == "postgres":
            self.logfile = "fuzz_log_pg"
        elif target_db == "sqlite":
            self.logfile = "fuzz_log_sq"
        elif target_db == "cockroach":
            self.logfile = "fuzz_log_cr"

    def debug(self, msg, _print=False):
        with open(self.logfile, 'a') as f:
            f.write(msg + "\n")

        if _print:
            print msg
