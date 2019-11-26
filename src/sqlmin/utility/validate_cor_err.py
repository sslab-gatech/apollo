#!/usr/bin/env python2

"""
1. find discovered queries (in multiple directories) and copy to one directory
2. run query (with Analyze) and save result
3. discard if:
    - result doesn't show regression
    - result has 0 size
    - result contain never executed
    - result contain 0 rows

"""

import os
import sys
import glob
import time

from tqdm import tqdm
from executor import execute
from conf import *

def mkdirs(pn):
    try:
        os.makedirs(pn)
    except OSError as e:
        pass

def retrieve_actual_time(query_out):
    # use small initial number to avoid div by zero
    p_time = 0.000001
    e_time = 0.000001
    for line in query_out.split("\n"):
        if "planning time" in line.lower():
            p_time = float(line.split(":")[1].split("ms")[0].strip())
        if "execution time" in line.lower():                        
            e_time = float(line.split(":")[1].split("ms")[0].strip())

    return float(p_time+e_time)

def run_queries (query_pn, port):
    #e.g., PGPASSWORD=mysecretpassword psql -h 127.0.0.1 -p 5433 -U postgres -d test_bd -c "select * from table1000_key_pk_parts_2_varchar_1024_not_null"
    
    basename = os.path.basename(query_pn).split(".")[0]
    dirname = os.path.dirname(query_pn)
    if port ==5432:
        with open(query_pn, 'r') as f:
            query = f.read()

        #query = query.replace("`", "")
        #query = "ANALYZE;" + query

        with open(query_pn, 'w') as f:
            f.write(query)

        output_pn = os.path.join(dirname, basename+".old")

    if port ==5435:
        output_pn = os.path.join(dirname, basename+".new")
    
    cmd = "psql -h 127.0.0.1 -p %d -U postgres -d test_bd -f %s 1> %s 2> /dev/null" % (port, query_pn, output_pn)    
    cmd = "PGPASSWORD=mysecretpassword  timeout --signal=SIGINT 100s %s" % (cmd)
    #cmd = "PGPASSWORD=mysecretpassword  %s" % (cmd)
    #print cmd
    os.system(cmd)

def run_queries_wo_analyze (query_pn, port):
    #e.g., PGPASSWORD=mysecretpassword psql -h 127.0.0.1 -p 5433 -U postgres -d test_bd -c "select * from table1000_key_pk_parts_2_varchar_1024_not_null"
    
    basename = os.path.basename(query_pn).split(".")[0]
    dirname = os.path.dirname(query_pn)
    if port ==5432:
        with open(query_pn, 'r') as f:
            query = f.read()

        query = query.replace("EXPLAIN ANALYZE", "--EXPLAIN ANALYZE")

        with open(query_pn, 'w') as f:
            f.write(query)

        output_pn = os.path.join(dirname, basename+".rold")
        err_out_pn = os.path.join(dirname, basename+".eold")

    if port ==5435:
        output_pn = os.path.join(dirname, basename+".rnew")
        err_out_pn = os.path.join(dirname, basename+".enew")
    
    cmd = "psql -h 127.0.0.1 -p %d -U postgres -d test_bd -f %s 1> %s 2> %s" % \
    (port, query_pn, output_pn, err_out_pn)    
    cmd = "PGPASSWORD=mysecretpassword  timeout --signal=SIGINT 100s %s" % (cmd)
    #cmd = "PGPASSWORD=mysecretpassword  %s" % (cmd)
    #print cmd
    os.system(cmd)


def postprocess(query_pn):
    basename = os.path.basename(query_pn).split(".")[0]
    dirname = os.path.dirname(query_pn)
    
    newresult = os.path.join(dirname, basename+".rnew")
    oldresult = os.path.join(dirname, basename+".rold")

    orgquery = os.path.join(dirname, basename+".sql")
    query_data = open(orgquery, 'r').read().lower()
    
    with open(newname, 'r') as f:
        newquery = f.read()

    with open(oldname, 'r') as f:
        oldquery = f.read()

    new_execution_time = retrieve_actual_time(newquery)
    old_execution_time = retrieve_actual_time(oldquery)

    remove_flag = False

    if "time" in query_data or "date" in query_data or "inet" in query_data:        
        remove_flag = True

    if not os.path.exists(newname) and not os.path.exists(oldname) :                
        remove_flag = True
        
    if os.path.getsize(newname) < 100 and os.path.getsize(oldname) < 100:        
        remove_flag = True

    # we want to keep correctness bug
    if os.path.getsize(newresult) != os.path.getsize(oldresult):
        remove_flag = False
        
    if remove_flag:
        os.system("rm -f %s/%s.*" % (dirname, basename))
    
def postprocess_target(query_pn):
    basename = os.path.basename(query_pn).split(".")[0]
    dirname = os.path.dirname(query_pn)
    
    newresult = os.path.join(dirname, basename+".rnew")
    oldresult = os.path.join(dirname, basename+".rold")

    orgquery = os.path.join(dirname, basename+".sql")
    query_data = open(orgquery, 'r').read().lower()
    
    with open(newname, 'r') as f:
        newquery = f.read()

    with open(oldname, 'r') as f:
        oldquery = f.read()

    new_execution_time = retrieve_actual_time(newquery)
    old_execution_time = retrieve_actual_time(oldquery)

    remove_flag = False

    # we want to keep correctness bug
    if os.path.getsize(newresult) != os.path.getsize(oldresult):
        print "[*] possible correctness bug, we will keep the file alive"
        remove_flag = False
        
    if remove_flag:
        os.system("rm -f %s/%s.*" % (dirname, basename))

    # TODO: consider row=0 and planning time condition
    # TODO: analyze (for each 1000 times)

class Validate(object):
    def __init__(self, in_pn, query_pn):
        self.in_pn = in_pn
        self.query_pn = os.path.abspath(query_pn)
        self.counter = 0        
        self.querylist = glob.glob(self.in_pn+"/*.sql")        
   
    def runall(self):
        #for filename in tqdm(self.querylist):
        for filename in self.querylist:
            print filename
            run_queries_wo_analyze(filename, 5432)
            run_queries_wo_analyze(filename, 5435)
            postprocess(filename)

            run_queries_wo_analyze(self.query_pn, 5432)
            run_queries_wo_analyze(self.query_pn, 5435)
            postprocess_target(self.query_pn)

def main(argv):
    in_pn = argv[1]
    query = argv[2]

    integ = Validate(in_pn, query)
    integ.runall()

if __name__ == "__main__":
    os.environ["PGPASSWORD"] = "mysecretpassword"
    def usage():                
        print "usage: python integrate_collection target_dir problem_query"
        print "    e.g., python integrate_collection.py /tmp/query/ 333.sql"

    main(sys.argv)
