#!/usr/bin/env python2
import os
import sys
import operator
import commands
import glob
import math

from tqdm import tqdm
from conf import *

def remove_zero(_dict):
    out = {}

    for k,v in _dict.iteritems():
        if v != 0:
            out[k] = v
    return out

def usage():
    print "python statdbg.py sqlite1"

def ret_result(line):
    temp_result = line.split(":")[1].strip()
    if temp_result == "true":
        result = 1
    elif temp_result == "false":
        result = 0
    else:
        raise Exception("should be either 1 or 0.")
    return result

def ret_count(line):
    return int(line.split(":")[1].strip())

def ret_addr(line):
    addr = line.split(":")[0].strip()
    addr = addr.replace("0000000000", "")
    addr = addr.replace("000000000", "")
    return addr

def ret_lines(filename):
    with open(filename, 'r') as f:
        return f.readlines()

class StatDbg(object):
    def __init__(self, query):
        self.tracedir = "trace"
        self.query = query

        self.num_fail = 0
        self.num_success = 0
        self.all_dict = {}
        self.failure = {}
        self.context = {}
        self.increase = {}
        self.importance = {}

        self.success_dict = {}
        self.success_true = {}
        self.success_observed = {}

        self.fail_dict = {}
        self.fail_true = {}
        self.fail_observed = {}

        self.read_trace()
        self.fill_missing_addr("success")
        self.fill_missing_addr("fail")

        self.calc_failure()
        print "\n[*] Failure"
        print self.failure

        self.calc_context()
        print "\n[*] Context"
        print self.context

        self.calc_increase()
        new_increase = remove_zero(self.increase)
        print "\n[*] Increase: %d" % len(new_increase)
        print new_increase

        #self.calc_importance()
        #print "\n[*] Importance: %d" % len(self.importance)
        #print self.importance

    def fill_missing_addr(self, case):
        if case == "success":
            target_dict = self.success_dict
            true_dict = self.success_true
            observe_dict = self.success_observed
        elif case == "fail":
            target_dict = self.fail_dict
            true_dict = self.fail_true
            observe_dict = self.fail_observed

        for addr in self.all_dict.keys():
            if addr not in observe_dict.keys():
                observe_dict[addr] = 0
            if addr not in true_dict.keys():
                true_dict[addr] = 0

    def read_trace(self):
        filelist_success = glob.glob(self.tracedir+"/success/%s/*" % self.query)
        filelist_fail = glob.glob(self.tracedir+"/fail/%s/*" % self.query)

        print filelist_success
        print filelist_fail
        self.num_success = len(filelist_success)
        self.num_fail = len(filelist_fail)

        print "[*] Reading all files to extract all predicate info"
        for filename in tqdm(filelist_success):
            self.read_allkey(ret_lines(filename))
        for filename in tqdm(filelist_fail):
            self.read_allkey(ret_lines(filename))

        print "[*] Building F(P) and S(P)"
        for filename in tqdm(filelist_success):
            self._read_trace(ret_lines(filename), case="success")
        for filename in tqdm(filelist_fail):
            self._read_trace(ret_lines(filename), case="fail")

        for addr in self.success_observed.keys():
            if addr not in self.fail_true.keys():
                pass

    def read_allkey(self, lines):
        for line in lines:
            addr = ret_addr(line)
            result = ret_result(line)

            if addr not in self.all_dict.keys():
                if result == True:
                    self.all_dict[addr] = 1

    def _read_trace(self, lines, case):
        """ calculate F_P,S_P """

        for line in lines:
            addr = ret_addr(line)
            result = ret_result(line)

            if case == "success":
                target_dict = self.success_dict
                true_dict = self.success_true
                observe_dict = self.success_observed
            elif case == "fail":
                target_dict = self.fail_dict
                true_dict = self.fail_true
                observe_dict = self.fail_observed

            # update all dict for success/fail
            if addr not in target_dict.keys():
                target_dict[addr] = result
            elif addr in target_dict.keys():
                if target_dict[addr] == 1:
                    continue
            else:
                self.success_dict[addr] = result

            # update F(P) and S(P) ==> success_true / fail_true
            if addr not in true_dict.keys() and result == True:
                true_dict[addr] = 1
            elif addr in true_dict.keys() and result == True:
                true_dict[addr] += 1

            # update F(P_obsserved) and S(P_observed) ==> success_observed / fail_observed
            if addr not in observe_dict.keys():
                observe_dict[addr] = 1
            else:
                observe_dict[addr] += 1

    def calc_failure(self):
        """ S(P): self.success_true
            F(P): self.fail_true
        """
        for predicate in self.all_dict.keys():
            self.failure[predicate] = self.fail_true[predicate] / \
                                    float(self.success_true[predicate] + self.fail_true[predicate])

    def calc_context(self):
        """ S(P_obs): self.success_observed
            F(P_obs): self.fail_observed
            Failure(P): self.failure
        """
        for predicate in self.all_dict.keys():
            self.context[predicate] = self.fail_observed[predicate] / \
                                    float(self.success_observed[predicate] + self.fail_observed[predicate])

    def calc_increase(self):
        for predicate in self.failure.keys():
            self.increase[predicate] = self.failure[predicate] - self.context[predicate]

    def calc_importance(self):
        for predicate in self.fail_true.keys():

            if self.fail_true[predicate] == 1 or self.fail_true[predicate] == 0:
                continue

            if self.increase[predicate] == 0:
                continue

            inverse_increase = 1/self.increase[predicate]
            inverse_log = 1/(math.log(self.fail_true[predicate]) / math.log(self.num_fail))
            self.importance[predicate] = 2 / (inverse_increase + inverse_log)

    def addr2line(self, addr, executable):
        output = commands.getoutput("/usr/bin/addr2line -s -f -a %s -e %s"\
            % (addr, executable)).split("\n")

        print("/usr/bin/addr2line -s -f -a %s -e %s" % (addr, executable))
        funcname = output[1]
        srcname = output[2].split(" ")[0].split(":")[0]
        srcline = output[2].split(" ")[0].split(":")[1].strip()

        return funcname, srcname, int(srcline)

    def rundbg(self):
        number = 5 
        sorted_dict = sorted(self.increase.items(), key=operator.itemgetter(1))
        print "\n[*] Result (TOP %d) from new binary" % number
        for i in xrange(min(number, len(sorted_dict))):
            if sorted_dict[i][1] < 0:
                print sorted_dict[i]
                #print self.addr2line(sorted_dict[i][0], BINNEW)

        print "\n\n[*] Result (TOP %d) from old binary" % number
        for i in xrange(min(number, len(sorted_dict))):
            if sorted_dict[i][1] < 0:
                print sorted_dict[i]
                #print self.addr2line(sorted_dict[i][0], BINOLD)

        if CONTEXT:
            for key in self.context.keys():
                if self.context[key] == 0.5:
                    print key
                    print self.addr2line(key, BINNEW)

def main():
    if len(sys.argv) < 2:
        usage()
    else:
        #tracedir = sys.argv[1]
        query = sys.argv[1]
        sd = StatDbg(query)
        sd.rundbg()

if __name__ == "__main__":
    main()
