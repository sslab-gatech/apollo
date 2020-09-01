#!/usr/bin/env python2

"""
$ git clone https://github.com/postgres/postgres.git
$ git bisect start HEAD REL9_5_15 --
$ git bisect run /home/jjung/db-fuzz/db-fuzz/src/bisect/bisect.py
"""

import os
import commands

from conf import *


class Bisect (object):
    def __init__(self, commit):
        self.init_commit_good = commit
        self.gitlog = self.load_gitlog(commit)
        self.curr_index = len(self.gitlog) - 1
        self.diff = self.curr_index / 2
        self.good = True
        self.visited = {}

    def mov_commit(self, commit):
        os.system("cd %s; git reset --hard %s" % (SRC_DIR, commit))

    def run_bisect(self):
        while True:
            # read idx
            if self.good is True:
                next_idx = self.curr_index - self.diff
            else:
                next_idx = self.curr_index + self.diff
            self.curr_index = next_idx
            next_commit = self.gitlog[next_idx]
            print("Testing at %d (diff %d)" % (next_idx, self.diff))

            # hard reset to the commit
            self.mov_commit(next_commit)

            # run compile and measure time
            self.exec_inst_script()
            self.good = self.check_good_bad()
            self.diff = self.diff / 2

            if self.good is True:
                self.visited[next_commit] = "GOOD"
            else:
                self.visited[next_commit] = "BAD"

            if self.diff == 0:
                break

        # make sure we scanned everything
        next_commit = self.gitlog[next_idx + 1]
        if next_commit not in self.visited.keys():
            self.mov_commit(next_commit)
            self.exec_inst_script()
            self.good = self.check_good_bad()

        next_commit = self.gitlog[next_idx - 1]
        if next_commit not in self.visited.keys():
            self.mov_commit(next_commit)
            self.exec_inst_script()
            self.good = self.check_good_bad()

    def load_gitlog(self, init_commit_good):
        out = []
        with open(GITLOG, 'r') as f:
            lines = f.readlines()
            for line in lines:
                commit_hash = line.split("/")[0]
                if commit_hash != init_commit_good:
                    out.append(commit_hash)
                else:
                    out.append(commit_hash)
                    return out

    def exec_inst_script(self):
        print("[*] RUN SCRIPT")
        os.system(RUN_SCRIPT)

    def check_good_bad(self):
        exec_time = commands.getoutput(VAL_SCRIPT)
        ms_time = float(exec_time.split(":")[1].split("ms")[0].strip())
        print(" Timeout: %f / Execution time: %f" % (TOUT, ms_time))
        if ms_time > TOUT:
            print(" >> Eval: BAD")
            return False
        else:
            print(" >> Eval: GOOD")
            return True


def main():
    bi = Bisect(COMMIT)
    bi.run_bisect()


if __name__ == "__main__":
    main()
