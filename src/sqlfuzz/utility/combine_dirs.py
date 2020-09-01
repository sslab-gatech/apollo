
"""
Combine sql files from multiple directory into one
"""

import os
import sys
import glob
import time

from tqdm import tqdm

def mkdirs(pn):
    try:
        os.makedirs(pn)
    except OSError as e:
        pass

class Collector(object):
    def __init__(self, dir_list, out_dir):
        self.dir_list = dir_list
        self.out_dir = out_dir
        self.count = 0

    def check(self):
        print (self.dir_list)
        print (self.out_dir)

    def collect(self):
        mkdirs(self.out_dir)
        os.system("rm -f %s/*" % self.out_dir)

        filelist = []
        for dirname in self.dir_list:
            filelist = filelist + glob.glob(dirname+"/*/*/*.sql")

        for filename in filelist:
            out_pn = os.path.join(self.out_dir, str(self.count)+".sql")
            os.system("cp %s %s" % (filename, out_pn))
            self.count += 1

def main(argv):
    num_args = len(argv)
    proc_dirs = argv[1:-1]
    out_dir = argv[-1]

    if len(proc_dirs) < 1:
        print ("You should specify dirs")
        print ("  e.g., python combine_dirs.py dir_a dir_b ... OUTDIR")
        sys.exit()
    
    cl = Collector(proc_dirs, out_dir)
    #cl.check()
    cl.collect()

if __name__ == "__main__":
    main(sys.argv)
