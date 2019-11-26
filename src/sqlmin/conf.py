#!/usr/bin/env python2
import os

DB = "sqlite"
#DB = "postgres"

os.environ['PGPASSWORD'] = "mysecretpassword"
USER = "postgres"
LATEST_VERSION_PORT = 5435
OLDEST_VERSION_PORT = 5432

TMP_ERR_PN   = os.path.join("/", "tmp", "minimizer_err")
TMP_QUERY_PN = os.path.join("/", "tmp", "minimizer_query")
LOGFILE  = "qmin_log"

TEST_DB  = "test_bd"
TMP_DIR  = "/tmp"
TMP_ERR  = "/tmp/stderr"
DSN      = "\"dbi:Pg:host=127.0.0.1;port={PORT};user=postgres;password=mysecretpassword;database=%s\"" % (TEST_DB)
OUT_SUFFIX = "_out"
TMP_QUERY_STORE = "/tmp/queries/"
TMP_REDUCTION_FILE = "reduction"

DIFF_THRESHOLD = 0.3

class Logger (object):
    def __init__(self):
        self.logfile = LOGFILE

    def debug(self, msg, _print=False):
        with open(self.logfile, 'a') as f:
            f.write(msg+"\n")

        if _print:
            print msg
