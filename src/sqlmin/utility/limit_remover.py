
import re
import os
import sys
import glob

def mkdirs(pn):
    try:
        os.makedirs(pn)
    except OSError as e:
        pass

def sanitize_line(line):
    """
    abstime =>: time
    reltime => time
    tinterval => interval
    """

    line = line.replace("abstime", "time")
    line = line.replace("reltime", "time")
    line = line.replace("tinterval", "interval")
    return line

in_pn = sys.argv[1]
out_pn = sys.argv[2]

if len(sys.argv) <2:
    print "This script removes limit statement."
    print "e.g., python limit_remover.py in_dir out_dir"

mkdirs(out_pn)
os.system("rm -f %s/*" % out_pn)

filelist = glob.glob(in_pn+"/*.sql")
for filename in filelist:
    basename = os.path.basename(filename)

    f = open(filename, 'r')
    #data = f.read()
    """ remove limit and offset
    with open(out_pn+"/"+basename, 'w') as f2:
        data = re.sub(r'limit \d+', '', data)
        data = re.sub(r'offset \d+', '', data)
        f2.write(data)
    """
    lines = f.readlines()
    with open(out_pn+"/"+basename, 'w') as f2:
        out = ""
        for line in lines:                           
            if "limit" in line and "offset" not in line: 
                line = re.sub(r'limit \d+', '', line)

            line= sanitize_line(line)
            out += line
        f2.write(out)

