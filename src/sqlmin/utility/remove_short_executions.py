
import os
import glob

filelist = glob.glob("*.sql")

def should_remove(lines):
    for line in lines:
        if "Elapsed" in line:
            old_time = float(line.split("old:")[1].split("new")[0].strip())
            new_time = float(line.split("new:")[1].split("ratio")[0].strip())

            if old_time < 2 and new_time < 0.5:
                return True
    return False

for filename in filelist:
    basename = os.path.basename(filename).split(".")[0]

    query = ""
    with open (filename, 'r') as f:
        query = f.readlines()

    if should_remove(query):
        print "removing %s" % basename
        os.system("rm -f %s.*" % (basename))


