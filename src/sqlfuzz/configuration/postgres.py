import yaml

class MyDumper(yaml.Dumper):

    def increase_indent(self, flow=False, indentless=False):
        return super(MyDumper, self).increase_indent(flow, False)


CONF = {}

# target DBMS
CONF["DBMS"] = "postgres"
CONF["DB"] = "test_bd"

# using a probability table?
CONF["USE_PROB"] = False

# username, password, dsn
CONF["USERNAME"] = "postgres"
CONF["PASSWD"] = "mysecretpassword"
CONF["FILEDB"] = None
CONF["DSN"] = "\"dbi:Pg:host=127.0.0.1;port={PORT} \
;user=%s;password=%s;database=%s\"" \
% (CONF["USERNAME"], CONF["PASSWD"], CONF["DB"])

# DB version: old, new | port
CONF["DB_VER"] = [96, 111]
CONF["NEW_VER_PORT"] = 5435
CONF["OLD_VER_PORT"] = 5432
CONF["SQLSMITH_PORT"] = None

# DB run cmd
CONF["RUN_OLD"] = "psql -h 127.0.0.1 -p {PORT} -U %s -d %s -f " \
    % (CONF["USERNAME"], CONF["DB"])
CONF["RUN_NEW"] = "psql -h 127.0.0.1 -p {PORT} -U %s -d %s -f " \
    % (CONF["USERNAME"], CONF["DB"])

# difference between new/old to become regression
# e.g., If 2, newer version should x2 slower
CONF["THRESHOLD"] = 2

# timeout for each query (second)
CONF["TIMEOUT"] = 10
CONF["SQLSMITH_TIMEOUT"] = 20

# query prefix
CONF["PREFIX"] = "EXPLAIN ANALYZE"

# we discard very short execution time (second)
CONF["MINIMUM_QUERY_TIME"] = 0.00001

# how frequenty reset the prob-table (minutes)
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

with open("postgres.yaml", "w") as f:
    dump_str = yaml.dump(CONF, Dumper=MyDumper, default_flow_style=False)
    f.write(dump_str)
