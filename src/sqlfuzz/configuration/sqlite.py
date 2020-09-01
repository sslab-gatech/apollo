import os
import yaml

class MyDumper(yaml.Dumper):

    def increase_indent(self, flow=False, indentless=False):
        return super(MyDumper, self).increase_indent(flow, False)


CONF = {}

# target DBMS
CONF["DBMS"] = "sqlite"
CONF["DB"] = "test_bd"

# username, password, dsn
CONF["USERNAME"] = None
CONF["PASSWD"] = None
CONF["FILEDB"] = os.path.abspath("./benchmark/tpcc_sqlite.db")
CONF["DSN"] = "file:%s?mode=ro" % CONF["FILEDB"]

# DB version: old, new | port
CONF["DB_VER"] = [318, 327]
CONF["SQLSMITH_PORT"] = None

# DB run cmd
CONF["RUN_OLD"] = None
CONF["RUN_NEW"] = None

# difference between new/old to become regression
# e.g., If 2, newer version should x2 slower
CONF["THRESHOLD"] = 2

# timeout for each query (second)
CONF["TIMEOUT"] = 10
CONF["SQLSMITH_TIMEOUT"] = 20

# query prefix
CONF["PREFIX"] = ""

# we discard very short execution time (second)
CONF["MINIMUM_QUERY_TIME"] = 0.00001

# using a probability table?
# how frequenty reset the prob-table (minutes)
CONF["USE_PROB"] = False
CONF["PROBRESET"] = 120

# settings for setup or restore DB
CONF["USE_TPCC"] = True

# DB initialization required?
CONF["INIT"] = False

# Minimization
CONF["USE_MINIMIZER"] = True
CONF["MINIMIZER_DIR"] = "/tmp/sqlmin"
CONF["MIN_THRESHOLD"] = 0.3

# output directory
CONF["OUTDIR"] = "/tmp/out"

with open("sqlite.yaml", "w") as f:
    dump_str = yaml.dump(CONF, Dumper=MyDumper, default_flow_style=False)
    f.write(dump_str)
