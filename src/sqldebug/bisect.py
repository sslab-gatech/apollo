#!/usr/bin/env python2
import os
import sys
import glob
import time
import signal
import argparse
import tempfile
import commands

from tqdm import tqdm
from conf_sqlite import *
from conf_postgres import *

""" example
./bisect.py -db sqlite -i sq_ex -r sqlite_fossil -l bisect_log
"""

def exit_gracefully(original_sigint):    
    # code from: https://stackoverflow.com/questions/18114560/
    #  python-catch-ctrl-c-command-prompt-really-want-to-quit-y-n-resume-execution
    def _exit_gracefully(signum, frame):
        # restore the original signal handler as otherwise evil things will happen
        # in raw_input when CTRL+C is pressed, and our signal handler is not re-entrant
        signal.signal(signal.SIGINT, original_sigint)
        try:
            if raw_input("\nReally quit? (y/n)> ").lower().startswith('y'):
                sys.exit(1)
        except KeyboardInterrupt:
            print("Ok ok, quitting")
            sys.exit(1)

        # restore the exit gracefully handler here
        signal.signal(signal.SIGINT, _exit_gracefully)
    return _exit_gracefully

class Bisect (object):
    def __init__(self, dbname, insql, repodir):
        self.dbname = dbname
        self.insql = insql
        self.repodir = repodir
        self.timeout = 0.0
        self.good_to_go = False

        self.l = Logger()
        self.l.debug("[*] Start bisecting on %s" % self.insql)

    def bisect(self):
        self.regression_test()
        if self.good_to_go:
            # input current result
            self.bisect_init()            

            # bisect loop
            while True:
                current_commit = self.get_current_commit()
                self.l.debug("Testing commit: %s" % current_commit, _print=True)
                self.compile(current_commit)                

                elapsed, output = self.run_cmd(current_commit)

                #print output
                #print "bisect complete" in output
                #print "NEXT" not in self.get_status()

                if "bisect complete" in output or "NEXT" not in self.get_status():
                    for line in output.split("\n"):
                        if "CURRENT" in line:
                            self.l.debug("Bisect complete", _print=True)
                            self.l.debug(line, _print=True)
                    break

                if elapsed > self.timeout:
                    self.push_bisect_result(current_commit, "bad")
                else:
                    self.push_bisect_result(current_commit, "good")

        self.l.debug(self.sqlite_cmd("vlist"), _print=True)

    def sqlite_cmd(self, command):
        cmd = "cd %s;fossil bisect %s" % (self.repodir, command)
        output = commands.getoutput(cmd)
        return output

    def get_status(self):
        if self.dbname == "sqlite":
            return self.sqlite_cmd("status")            

        elif self.dbname == "postgres": 
            pass

        else:
            raise "Not supported DB"

        return None


    def get_current_commit(self):
        if self.dbname == "sqlite":
            cmd = "cd %s;fossil bisect log" % (self.repodir)
            output = commands.getoutput(cmd)

            for line in output.split("\n"):
                if "CURRENT" in line:
                    commit = line.split(":")[2].split(" ")[1]
                    return commit

        elif self.dbname == "postgres": 
            pass

        else:
            raise "Not supported DB"

        return None

    def run_cmd(self, commit):
        """ run and measure time """ 
        filenames = [os.path.basename(x) for x in glob.glob(CACHE_DIR+"/*")]

        if self.dbname == "sqlite": 
            

            if commit not in filenames:
                cmd = "%s/sqlite3 %s < %s" % (self.repodir, DBPATH, self.insql)
            else:
                cmd = "%s/%s %s < %s" % (CACHE_DIR, commit, DBPATH, self.insql)
            
            start = time.time()
            output = commands.getoutput(cmd)
            end = time.time()

            return end-start, output

        elif self.dbname == "postgres": 
            pass

        else:
            raise "Not supported DB"

    def push_bisect_result(self, commit, result):
        if self.dbname == "sqlite":
            cmd = "cd %s; fossil bisect %s %s" % (self.repodir, result, commit)
            commands.getoutput(cmd)
            self.l.debug("Pushed result \"%s\" for commit: %s" % \
                (result, commit), _print=True)  

            cmd = "cd %s; fossil bisect log" % (self.repodir)
            logoutput = commands.getoutput(cmd)

            self.l.debug("*"*20, _print=True)
            self.l.debug(logoutput, _print=True)
            self.l.debug("*"*20, _print=True)          

        elif self.dbname == "postgres": 
            pass

        else:
            raise "Not supported DB"

    def bisect_init(self):
        """ checkout repo and compile DB """

        if self.dbname == "sqlite":

            cmd = "cd %s; fossil reset" % (self.repodir)
            commands.getoutput(cmd)
            self.l.debug("Reset fossil", _print=True)

            cmd = "cd %s; fossil bisect good %s" % (self.repodir, OLD_DB_COMMIT)            
            commands.getoutput(cmd)
            self.l.debug("Mark first good commit: %s" % OLD_DB_COMMIT, _print=True)

            cmd = "cd %s; fossil bisect bad %s" % (self.repodir, NEW_DB_COMMIT)            
            commands.getoutput(cmd)
            self.l.debug("Mark first bad commit: %s" % NEW_DB_COMMIT, _print=True)

        elif self.dbname == "postgres": 
            pass

        else:
            raise "Not supported DB"

    def compile(self, commit):

        filenames = [os.path.basename(x) for x in glob.glob(CACHE_DIR+"/*")]

        if self.dbname == "sqlite":

            if commit not in filenames:
                self.l.debug("Compile commit \"%s\"" % commit, _print=True)
                cmd = "cd %s; ./configure --enable-unicode=ucs4; make -j 4" % (self.repodir)                
                commands.getoutput(cmd)

                # backup the file to cache
                if os.path.getsize("%s/sqlite3" % self.repodir) > 10000:
                    os.system("cp %s/sqlite3 %s/%s" % (self.repodir, CACHE_DIR, commit))
                    self.l.debug("  >> Compile (%s) and save cache" % commit, _print=True)

            else:
                self.l.debug("  >> Skip compile (%s)" % commit, _print=True)

        elif self.dbname == "postgres": 
            pass

        else:
            raise "Not supported DB"

    def checkout_and_compile(self, commit):
        """ checkout repo and compile DB """

        filenames = [os.path.basename(x) for x in glob.glob(CACHE_DIR+"/*")]                

        if self.dbname == "sqlite":

            if commit not in filenames:
                cmd = "cd %s; fossil checkout %s; ./configure --enable-unicode=ucs4; make -j 4" % (self.repodir, commit)
                commands.getoutput(cmd)

                # backup the file to cache
                os.system("cp %s/sqlite3 %s/%s" % (self.repodir, CACHE_DIR, commit))
                self.l.debug("  >> Compile (%s) and save cache" % commit, _print=True)

            else:
                self.l.debug("  >> Skip compile (%s)" % commit, _print=True)

        elif self.dbname == "postgres": 
            pass

        else:
            raise "Not supported DB"

    def regression_test(self):
        """ test whether the query actually shows regression """

        if self.dbname == "sqlite":
            self.l.debug("Initial regression test between %s and %s (takes minutes)" % \
                (OLD_DB_COMMIT, NEW_DB_COMMIT), _print=True)

            self.checkout_and_compile(OLD_DB_COMMIT)
            old_time, old_output = self.run_cmd (OLD_DB_COMMIT)
            self.l.debug(" >> completed old commit: %s, time:%f" % (OLD_DB_COMMIT, old_time), _print=True)
            
            self.checkout_and_compile(NEW_DB_COMMIT)
            new_time, new_output = self.run_cmd (NEW_DB_COMMIT)
            self.l.debug(" >> completed new commit: %s, time:%f" % (NEW_DB_COMMIT, new_time), _print=True)

            if old_time * REGRESSION_THRESHOLD < new_time:
                self.good_to_go = True
                self.timeout = old_time * REGRESSION_THRESHOLD

        elif self.dbname == "postgres": 
            pass

        else:
            raise "Not supported DB"

    def template(self):
        if self.dbname == "sqlite":
            pass

        elif self.dbname == "postgres": 
            pass

        else:
            raise "Not supported DB"

class Logger (object):
    def __init__(self):
        self.logfile = LOGFILE

    def debug(self, msg, _print=False):
        with open(self.logfile, 'a') as f:
            f.write(msg+"\n")

        if _print:
            print msg

if __name__ == "__main__":

    #### DEFINE PARSER
    main_parser = argparse.ArgumentParser()    
    main_parser.add_argument("-db", "--database", dest="dbname", type=str,
                    default=None, help="DBMS name", required=True)
    main_parser.add_argument("-i", "--indir", dest="indir", type=str,
                        default=None, help="path of input directory", required=True)
    main_parser.add_argument("-r", "--repodir", dest="repodir", type=str,
                        default=None, help="path of repository directory", required=True)    
    main_parser.add_argument("-l", "--logfile", dest="logfile", type=str,
                        default=None, help="bisect logfile", required=False)    
    main_parser.set_defaults(action='sqldebug')    
    args = main_parser.parse_args() 
    #### END PARSER    

    # Ctrl-c handler
    signal.signal(signal.SIGINT, exit_gracefully(signal.getsignal(signal.SIGINT))) 
    TEST_DB = 'test_bd'

    if args.dbname == 'postgres':
        os.environ['PGPASSWORD'] = "mysecretpassword"
        USER = "postgres"
        LATEST_VERSION_PORT = 5435
        OLDEST_VERSION_PORT = 5432
        DSN = "\"dbi:Pg:host=127.0.0.1;port={PORT};user=postgres;password=mysecretpassword;database=%s\"" % (TEST_DB)

    elif args.dbname == 'sqlite':
        DBPATH = "../sqlfuzz/benchmark/tpcc_sqlite.db"
        DSN = "file:%s?mode=ro" % DBPATH

        if args.logfile:
            LOGFILE = args.logfile
        else: 
            LOGFILE = "bisect_log"

    os.system("rm -f %s" % LOGFILE)
    target_dir = args.indir
    filelist = glob.glob(target_dir + "/*.sql")

    for filename in filelist:
        bi = Bisect(args.dbname, filename, "sqlite_fossil")
        bi.bisect()
