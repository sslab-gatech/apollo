import os
import sys
import time
import sqlite3 as sqlite_old
import sqlite4 as sqlite_new


class Executor(object):
    def __init__(self, filename):
        self.filepath = filename
        self.timeout = 2
        self.old_db_pn = os.path.join("../../sqlite/sqlite323", "sqlite3")
        self.new_db_pn = os.path.join("../../sqlite/sqlite327", "sqlite3")
        self.tpcc_pn = os.path.join("../sqlfuzz/benchmark/tpcc_sqlite.db")

    def run_query(self, version):
        if version == "old":
            db_pn = self.old_db_pn
        else:
            db_pn = self.new_db_pn

        cmd = "timeout %ds %s %s < %s > /dev/null" \
            % (self.timeout, db_pn, self.tpcc_pn, self.filepath)

        start = time.time()
        os.system(cmd)
        elapsed_time = time.time() - start

        return elapsed_time


def main(argv):
    ext = Executor(argv[1])  # query_pn
    elapsed_time = ext.run_query(argv[2])  # either "old" or "new"
    print elapsed_time


if __name__ == "__main__":
    main(sys.argv)
