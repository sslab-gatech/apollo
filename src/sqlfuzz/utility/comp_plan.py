#!/usr/bin/env python2

import glob
import sys
import os
import re
import commands
import operator

NEW_RESULT = "new_result"
OLD_RESULT = "old_result"
FILES = [NEW_RESULT, OLD_RESULT]

TMP_SED = "/tmp/sed"
NUM_HIGHEST = 3

def load_files(filedir):
    filelist = glob.glob(filedir+"/*/???_result")
    outlist = []

    for filename in filelist:
        dirname = os.path.dirname(filename)
        if dirname not in outlist:
            outlist.append(dirname)

    return outlist

def run_sed_remove_parenthesis(pn):
    cmd = "cat %s | sed 's/(.*)//g' |grep -v \"Planning\\|Execution\\|QUERY\\|------\"" \
        % (pn)
    return commands.getoutput(cmd)

def ret_actual(line):
    startup = float(line.split('actual time=')[1].split(' ')[0].split('..')[0])
    execution = float(line.split('actual time=')[1].split(' ')[0].split('..')[1])

    return startup + execution

def extract_actual_time(contents):
    outdict = {}
    lines = contents.split("\n")
    for index, line in enumerate(lines):
        if "actual time" in line:
            elapsed = ret_actual(line)
            outdict [index] = elapsed

    sorted_dic = sorted(outdict.items(), key=operator.itemgetter(0))
    sorted_dic = sorted_dic [0:NUM_HIGHEST]
    return sorted_dic

class Result(object):
    def __init__ (self, dirname):
        self.cur_dir = dirname
        with open(os.path.join(self.cur_dir, NEW_RESULT), 'r') as f:
            self.new_org = f.read()
        with open(os.path.join(self.cur_dir, OLD_RESULT), 'r') as f:
            self.old_org = f.read()

        self.new_org_lines = self.new_org.split("\n")
        self.old_org_lines = self.old_org.split("\n")

        self.new_removed_paren = run_sed_remove_parenthesis(os.path.join(self.cur_dir, NEW_RESULT))
        self.old_removed_paren = run_sed_remove_parenthesis(os.path.join(self.cur_dir, OLD_RESULT))

        self.old_actual_time = extract_actual_time(self.old_org)
        self.new_actual_time = extract_actual_time(self.new_org)

        #print self.old_actual_time[0][0]

    def comp_max_actual_loc(self):
        different = False
        for idx in xrange(NUM_HIGHEST):

            if self.old_actual_time[idx][0] != self.new_actual_time[idx][0]:
                print "%dth highest actual time different:" % idx
                print "old_result line: %d" % self.old_actual_time[idx][0] 
                print "new_result line: %d" % self.new_actual_time[idx][0] 
                different = True
        return different

def process_directory(dirlist):
    for dirname in dirlist:
        print "\n[*] Processing directory: %s" % dirname
        rst = Result(dirname)        
        if not rst.comp_max_actual_loc():
            print "Maximum actual time loc are same"

def main(filedir):
    dirlist = load_files(filedir)
    process_directory(dirlist)
        

if __name__ == "__main__":

    filedir = "parse_candidate/181018"
    main(filedir)