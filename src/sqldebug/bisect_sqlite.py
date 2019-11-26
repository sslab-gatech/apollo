#!/usr/bin/env python2

"""
$ git clone https://github.com/postgres/postgres.git
$ git bisect start HEAD REL9_5_15 --
$ git bisect run /home/jjung/db-fuzz/db-fuzz/src/bisect/bisect.py

sed -i 's/--EXP/EXP/g'  *.sql

HOW_TO_GITLOG DUMP
git clone --recursive https://github.com/mackyle/sqlite.git
git log --pretty='format:%h/%cd/' --abbrev-commit --date=format:'%Y-%m-%d %H:%M:%S' > sqlite_gitlog
"""

import os
import sys
import time
import glob
import commands

from tqdm import tqdm
from conf_sqlite import *

def is_commit_blacklist(commit):
    if commit in BLACKLIST:
        return True
    return False

def ret_tout(filename):
    #97.sql:-- New elapsed old:0.352000 new:4.630000 ratio:13.153409
    time = 0.0
    with open (filename, 'r') as f:
        lines = f.readlines()
        for line in lines:
            if "--" in line and "New" in line:
                time = float(line.split("new:")[1].split("ratio")[0].strip())
    return time * 0.6

def ret_tout_sqlite(filename, num_test):
    #97.sql:-- New elapsed old:0.352000 new:4.630000 ratio:13.153409
    cmd = "%s %s < %s" % (SQLITE_NEW, TESTDB, filename)

    ms_time = 0.0    
    for x in tqdm(xrange(num_test)):
        start_time = time.time()        
        commands.getoutput(cmd)
        ms_time += time.time() - start_time

    ms_time = ms_time / num_test

    """
    time = 0.0
    with open (filename, 'r') as f:
        lines = f.readlines()
        for line in lines:
            if "--" in line and "New" in line:
                time = float(line.split("new:")[1].split("ratio")[0].strip())
    return time * 0.6
    """
    return ms_time * 0.7


class Bisect (object):
    def __init__(self, commit, dirname):
        self.filelist = glob.glob(dirname+"/*.sql")
        self.init_commit_good = commit
        self.gitlog = self.load_gitlog(commit)
        self.curr_index = len(self.gitlog) -1

        self.diff = self.curr_index / 2
        self.good = True
        self.tout = 0.0
        self.num_test = 3
        self.current_file = None

        self.visited = {}
        self.val_script = ""
        self.use_precompiled = False
        #print len(self.gitlog)     

    def log(self, msg, out=False):
        with open("./sqlite_bisect_log", "a+") as f:
            f.write(msg+"\n")

        if out == True:
            print msg

    def mov_commit (self, commit):
        self.log(" >> now we are at commit %s" % commit)

        # sorry about the abs path...
        #os.system("rm -rf %s" % SRC_DIR)
        #os.system("cp -r /mnt/sdb/jinho/db-fuzz/sqlite_git %s" % SRC_DIR)
        #os.system("cd %s; git reset --hard %s" % (SRC_DIR, commit))
        if os.path.exists(OUT_DIR+"/"+commit) == True:
            self.use_precompiled = True
            return 
        else:
            self.use_precompiled = False
            os.system("cd %s; make clean" % (SRC_DIR))
            os.system("cd %s; fossil checkout %s --force > /dev/null" % (SRC_DIR, commit))
        

    def run_bisect(self):
        # start with recent one
        for filename in self.filelist:
            self.current_file = filename
            self.curr_index = len(self.gitlog) -1
            self.diff = self.curr_index / 2
            self.visited = {}
            self.good = True

            self.log("[*] Start: %s" % filename, out=True)

            self.tout = ret_tout_sqlite (filename, self.num_test)
            self.log(" >> use %f as timeout" % self.tout, out=True)            
            #self.val_script = "PGPASSWORD=mysecretpassword psql -h 127.0.0.1 -p 5432 -U postgres -d test_bd -f %s |grep Exec" % filename
            self.val_script = "%s/sqlite3 %s < %s" % (SRC_DIR, TESTDB, filename)            

            # last validation about the regression
            # if no regression? skip this file
            "[*] Initial compilation on latest commit"
            self.mov_commit (RECENT_COMMIT)            
            self.exec_inst_script(RECENT_COMMIT) # just run script
            
            first_check = self.check_good_bad(RECENT_COMMIT)
            if first_check == True:  # GOOD
                print "NO REGRESSION!!!!"
                self.log("NO REGRESSION!!!!, next filess")
                continue

            while True:
                #print self.curr_index
                #print self.diff
                # read idx            
                if self.good == True:
                    next_idx = self.curr_index - self.diff
                else:
                    next_idx = self.curr_index + self.diff
                self.curr_index = next_idx

                #print next_idx
                next_commit = self.gitlog[next_idx]
                print "Testing at %d (diff %d)" % (next_idx, self.diff)
                self.log(" >> Testing at %d (diff %d)" % (next_idx, self.diff))

                # hard reset to the commit
                print "[*] Moving around the existing commit"
                self.mov_commit(next_commit)                
                self.exec_inst_script(next_commit)

                # run compile and measure time                
                self.good = self.check_good_bad(next_commit)
                self.diff = self.diff / 2

                if self.good == True:
                    self.visited[next_commit] = "GOOD"
                else:
                    self.visited[next_commit] = "BAD"

                if self.diff == 0:
                    break

            # make sure we scanned everything
            next_commit = self.gitlog[next_idx+1]
            if next_commit not in self.visited.keys():
                print "[*] Finally checking"
                self.mov_commit(next_commit)
                self.exec_inst_script(next_commit)
                self.good = self.check_good_bad(next_commit)        

            next_commit = self.gitlog[next_idx-1]
            if next_commit not in self.visited.keys():
                print "[*] Finally checking"
                self.mov_commit(next_commit)
                self.exec_inst_script(next_commit)
                self.good = self.check_good_bad(next_commit) 

    def load_gitlog(self, init_commit_good):        
        out = []
        with open(GITLOG, 'r') as f:
            lines = f.readlines()
            for line in lines:
                commit_hash = line.split("[")[1].split("]")[0].strip()
                if commit_hash != init_commit_good:
                    out.append(commit_hash)
                else:
                    out.append(commit_hash)
                    return out

    def exec_inst_script(self, commit):
        print "[*] RUN SCRIPT, Commit %s" % commit
        if self.use_precompiled == False:
            os.system(RUN_SCRIPT)
            os.system("cp %s/sqlite3 %s/%s" % (SRC_DIR, OUT_DIR, commit))
        else:
            print " >> we found already built file. Skip the compilation!"

    def check_good_bad(self, commit):
        #print "Evaluating"

        ms_time = 0.0        
        for x in tqdm(xrange(self.num_test)):
            start_time = time.time()
            if self.use_precompiled == False:
                commands.getoutput(self.val_script)
            else:
                commit_script = "%s/%s %s < %s" % (OUT_DIR, commit, TESTDB, self.current_file)
                commands.getoutput(commit_script)

            ms_time += time.time() - start_time

        ms_time = ms_time / self.num_test
        
        """
        if ":" not in exec_time and "ms" not in exec_time:
            print " >> SOMETHING WRONG!"
            self.log(" >> SOMETHING WRONG!")
            return False

        ms_time = float(exec_time.split(":")[1].split("ms")[0].strip())
        """

        print " Timeout: %f / Execution time: %f" % (self.tout, ms_time)        
        self.log(" >> Timeout: %f / Execution time: %f" % (self.tout, ms_time)        )
        if ms_time > self.tout:
            #exit(1)   # bad            
            print " >> Eval: BAD"            
            self.log(" >> Eval: BAD" )
            return False
        else:
            #exit(0)   # good
            print " >> Eval: GOOD"            
            self.log(" >> Eval: GOOD")
            return True

def main(argv):
    dirname = argv[1]
    bi = Bisect(COMMIT, dirname)
    bi.run_bisect()

if __name__ == "__main__":
    main(sys.argv)
