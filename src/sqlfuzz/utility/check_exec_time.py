import os
import glob

filelist = glob.glob("*.sql")

def ret_time(lines):
    #/* Elapsed old:5.893000 new:14.025000 ratio:2.379942 */
    exectime = 0.0000001
    count = 0
    for line in lines:
        if "Execution" in line:
            exectime = float(line.split("me:")[1].split("ms")[0].strip())

        if "never" in line:
            count +=1

    if len(lines) > 3:
        firstplan = lines[2].split("  ")[0].strip()
    else:
        firstplan = ""
                      
    return exectime, count, firstplan

def print_list(slist):
    for item in slist:
        print item

for filename in filelist:
    basename = os.path.basename(filename).split(".")[0]

    oldlines = open(basename+".old", 'r').readlines()
    newlines = open(basename+".new", 'r').readlines()
    
    oldtime, oldcount, oldplan = ret_time(oldlines)
    newtime, newcount, newplan = ret_time(newlines)

    if oldtime < 0.00001 or newtime < 0.00001:
        continue

    if oldtime > (newtime / 1.3):
        continue
    
    print basename, oldtime, newtime, newtime/oldtime, oldcount, newcount, oldplan==newplan, oldplan, newplan
    if oldplan!=newplan:
        print "FOUND"