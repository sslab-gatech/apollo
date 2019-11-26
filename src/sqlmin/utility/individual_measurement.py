#!/usr/bin/env python2

"""
1. run target queries on three different DBs (scalefactor 1/10/50)
2. we are running on same version

"""

import os
import sys
import glob
import time
import csv

from tqdm import tqdm
from executor import execute
from prettytable import PrettyTable

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

def run_queries (query_pn, dbname, port):
    #e.g., PGPASSWORD=mysecretpassword psql -h 127.0.0.1 -p 5433 -U postgres -d test_bd -c "select * from table1000_key_pk_parts_2_varchar_1024_not_null"
    
    basename = os.path.basename(query_pn).split(".")[0]
    dirname = os.path.dirname(query_pn)
    
    with open(query_pn, 'r') as f:
        query = f.read()

    #query = query.replace("`", "")
    #query = "ANALYZE;" + query

    with open(query_pn, 'w') as f:
        f.write(query)

    output_pn = os.path.join(dirname, basename+".out")
    
    cmd = "psql -h 127.0.0.1 -p %d -U postgres -d %s -f %s 1> %s 2> /dev/null" % (port, dbname, query_pn, output_pn)    
    cmd = "PGPASSWORD=mysecretpassword  timeout --signal=SIGINT 60s %s" % (cmd)
    #cmd = "PGPASSWORD=mysecretpassword  %s" % (cmd)
    #print cmd
    os.system(cmd)


def postprocess(query_pn):
    basename = os.path.basename(query_pn).split(".")[0]
    dirname = os.path.dirname(query_pn)

    outname = os.path.join(dirname, basename+".out")        
    orgquery = os.path.join(dirname, basename+".sql")
    query_data = open(orgquery, 'r').read().lower()
    
    with open(outname, 'r') as f:
        outquery = f.read()
    
    execution_time = retrieve_actual_time(outquery)    
    return execution_time
    
class Integrate(object):
    def __init__(self, in_pn, out_pn, version):
        self.in_pn = in_pn
        self.out_pn = out_pn
        self.counter = 0
        self.collect()
        self.querylist = sorted(glob.glob(out_pn+"/*.sql"))
        self.t = PrettyTable(['filename', 'scale1', 'scale10', 'scale50'])
        self.result = []

        if version == 11:
            self.port = 5435
            self.csv_pn = "11.csv"
        elif version == 9:
            self.port = 5432            
            self.csv_pn = "9.csv"
        
    def ret_next_file(self):
        self.counter +=1
        filename = str(self.counter)+".sql"
        return os.path.join(self.out_pn, filename)

    def collect(self):
        print "[*] Copying file to target directory"
        os.system("rm -rf %s" % self.out_pn)
        mkdirs(self.out_pn)
        filelist = sorted(glob.glob(self.in_pn+"/*.sql"))
        for filename in tqdm(filelist):
            #os.system("cp %s %s" % (filename, self.ret_next_file()))
            os.system("cp %s %s" % (filename, self.out_pn))
    
    def runall(self):
        #for filename in tqdm(self.querylist):
        for filename in self.querylist:
            print filename            
            run_queries(filename, "test_bd", self.port)
            scale1 = postprocess(filename)
            run_queries(filename, "test_bd10", self.port)
            scale10 = postprocess(filename)
            run_queries(filename, "test_bd50", self.port)
            scale50 = postprocess(filename)

            self.t.add_row([os.path.basename(filename), scale1, scale10, scale50])
            self.result.append([os.path.basename(filename), scale1, scale10, scale50])
          
    def printtable(self):
        print self.t
        with open(self.csv_pn, 'wb') as myfile:
            wr = csv.writer(myfile)
            wr.writerows(self.result)

def main(argv):    
    in_pn = argv[1]
    out_pn = argv[2]
    version = int( argv[3])

    integ = Integrate(in_pn, out_pn, version)
    integ.runall()
    integ.printtable()

if __name__ == "__main__":
    os.environ["PGPASSWORD"] = "mysecretpassword"
    def usage():                
        print "usage: python integrate_collection target_dir output_dir version"
        print "    e.g., python integrate_collection.py /tmp/query/ /tmp/result/  11"

    main(sys.argv)
