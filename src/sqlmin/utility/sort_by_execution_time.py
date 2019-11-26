import os
import glob
from operator import itemgetter

filelist = glob.glob("*.sql")
num_print = 100
result = []

def ret_time(lines):
    #/* Elapsed old:5.893000 new:14.025000 ratio:2.379942 */
    for line in lines:
        if "Elapsed" in line:
            old_time = float(line.split("old:")[1].split("new")[0].strip())
            new_time = float(line.split("new:")[1].split("ratio")[0].strip())
            ratio = float(line.split("ratio:")[1].split(" ")[0].strip())
            
    return old_time, new_time, ratio

def print_list(slist):
    for item in slist:
        print item

for filename in filelist:
    basename = os.path.basename(filename).split(".")[0]

    query = ""
    with open (filename, 'r') as f:
        query = f.readlines()

    old_time, new_time, ratio = ret_time(query)
    result.append([filename, old_time, new_time, ratio])

#print result
sort_by_oldtime = sorted(result, key=itemgetter(1), reverse=True)[:num_print]
sort_by_ratio = sorted(result, key=itemgetter(3), reverse=True)[:num_print]

print "SORT BY OLDTIME"
print_list(sort_by_oldtime)

print "\nSORT BY RATIO"
print_list(sort_by_ratio)
