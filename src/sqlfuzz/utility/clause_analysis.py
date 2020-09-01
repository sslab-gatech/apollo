import re
import os
import sys
import time
import operator

blacklist = ["ref_", "subq_", "c_", "d_", "h_", "public.", "s_", \
    "ol_", "o_", "---", "w_", "--ex", "i_", "no_", "(", ")", "--where", "pg_catalog",\
    "analyze", ",", "main.", "--", "actual"]
opr = [">", "<", "=", "#", "|", "?", "*", "&", "!", "~", "@"]
total_count = 0

def is_opr(word):
    for item in opr:
        if item in word:
            return True
    return False

def is_blacklist(word):
    num_pattern = re.compile("c[0-9]+")
    for item in blacklist:
        if word.startswith(item):
            return True

        if re.match("c[0-9]+", word):
            return True

        if re.match("[0-9]+", word):
            return True

    return False

def word_count(str, size):
    global total_count
    counts = dict()
    words = str.split()

    for word in words: 
        if is_blacklist(word):
            continue

        if is_opr(word):
            word = "OPERATOR"

        if word in counts:
            counts[word] += 1
            total_count +=1
        else:
            counts[word] = 1
            total_count +=1

        if (word.lower() == "left" or word.lower() == "right") and "join" in counts:
            counts["join"] -= 1

    for k in counts.keys():
        counts[k] = "%3.6f" % (counts[k] / float(size))

    sorted_dict = sorted(counts.items(), key=operator.itemgetter(1), reverse=True)
    
    return sorted_dict

def sanitize(_str):
    slow_str = _str.lower()
    slow_str = slow_str.replace("\"", "")
    slow_str = slow_str.replace("(", "\n(\n")
    slow_str = slow_str.replace(",", "\n,\n")
    slow_str = slow_str.replace(")", "\n)\n)")
    slow_str = slow_str.replace(";", "\n;\n)")
    slow_str = slow_str.replace(";", "")

    return slow_str

class Analyze(object):
    def __init__(self, db):
        self.db = db
        self.slow_pn = os.path.join("goodbad_queries", self.db+"_slow")
        self.normal_pn = os.path.join("goodbad_queries", self.db+"_normal")
        self.slow_size = os.path.getsize(self.slow_pn)
        self.normal_size = os.path.getsize(self.normal_pn)

    def analyze(self):
        slow_str = open(self.slow_pn, 'r').read()
        normal_str = open(self.normal_pn, 'r').read()
        
        """
        slow_str = sanitize(slow_str)
        slow_count = word_count(slow_str, self.slow_size)
        for k,v in slow_count:
            print k,v
        """
       
        normal_str = sanitize(normal_str)
        normal_count = word_count(normal_str, self.normal_size)
        for k,v in normal_count:
            print k,v

        print total_count
        

def main(argv):    
    db = argv[1]
    az = Analyze(db)
    az.analyze()

if __name__ == "__main__":
    def usage():                
        print "usage: python clause_analysis.py DBNAME"
        print "    e.g., usage: python clause_analysis.py postgres"

    main(sys.argv)


"""
pattern = re.compile("c[0-9]+")
re.match("c[0-9]+", "c")
"""
