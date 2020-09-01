#!/usr/bin/env python2
import time
import os
import sys
import glob

def mkdirs(pn):
    try:
        os.makedirs(pn)
    except OSError as e:
        pass

def contain_never_executed(pn):
    with open(pn, 'r') as f:
        if "never executed" in f.read().lower():
            return True
    return False

class Runner(object):
    def __init__ (self, target_dir):
        self.target_dir = target_dir
        self.tmpdir = "/tmp/tmpquery"
        self.outdir = "/tmp/minimized"
        mkdirs(self.tmpdir)
        mkdirs(self.outdir)
        self.cleanup_tmp()
        self.processed_query = []
        self.sleep = 60
        self.count = 0

    def cleanup_tmp(self):
        os.system("rm -f %s/*" % self.tmpdir)
        os.system("rm -f %s/*" % self.outdir)

    def check_new_queries(self):
        out = []
        sql_list = glob.glob(self.target_dir+"/*/queue/*.sql")
        reduce_list = glob.glob(self.target_dir+"/*.sql_reduced")

        candidate_sql = []
        for item in sql_list:
            name = os.path.basename(item).split(".")[0]

            #old_pn = os.path.join(self.target_dir, name+".out")
            item_dir = os.path.dirname(item)
            item_basename = os.path.basename(item).split(".")[0]
            old_pn = os.path.join(item_dir, item_basename+".out")
            #new_pn = os.path.join(self.target_dir, name+".latest")

            # not in processed_query (assume possible failure)
            if name not in self.processed_query:
                if contain_never_executed(old_pn):
                    print "skipping %s due to never executed" % old_pn
                    continue
                if os.path.getsize(old_pn) < 1:
                    print "no executed result: %s" % old_pn
                    continue

                candidate_sql.append(name)

        return candidate_sql

    def backup_candidates(self, candidate):
        for item in candidate:
            #os.system("cp %s/%s.sql %s/" % (self.target_dir, item, self.tmpdir))
            os.system("cp %s/%s.sql %s/%d.sql" % (self.target_dir, item, self.tmpdir, self.count))
            os.system("cp %s/%s.sql %s/%d.out" % (self.target_dir, item, self.tmpdir, self.count))
            self.count += 1

    def copyback(self, candidate):
        for item in candidate:
            item_dir = os.path.dirname(item)
            os.system("cp %s/*.sql_reduced %s" % (self.tmpdir, self.outdir))  

    def update_status(self, candidate):
        for item in candidate:
            self.processed_query.append(item)

    def execute(self):
        while True:
            candidate = self.check_new_queries()
            
            if len(candidate) > 0:
                print "[*] Run query minimizer for %d queries" % (len(candidate))
                # prepare
                self.cleanup_tmp()
                self.backup_candidates(candidate)
                
                # run minimizer
                cmd = "python sql_minimizer.py %s > /dev/null" % (self.tmpdir)
                os.system(cmd)
                self.copyback(candidate)

                # update the status
                self.update_status(candidate)
                self.cleanup_tmp()

            else:
                print "[*] Sleep for %d seconds" % (self.sleep)
                time.sleep(self.sleep)

if __name__ == "__main__":
    def usage():        
        print "usage: python run_minimizer.py target_dir"

    if len(sys.argv) < 2:
        usage()
        exit()

    run = Runner(sys.argv[1])
    run.execute()
