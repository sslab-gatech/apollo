#!/usr/bin/env python
import os
import re
import sys
import time
import signal
import tempfile
import commands

from tqdm import tqdm
from random import randint

from conf import *
from probconf import *

"""
command:
    ./fuzz.py -c configuration/postgres.yaml
"""


def exit_gracefully(original_sigint):
    # code from: https://stackoverflow.com/questions/18114560/

    def _exit_gracefully(signum, frame):
        # restore the original signal handler
        # in raw_input when CTRL+C is pressed,
        # and our signal handler is not re-entrant
        signal.signal(signal.SIGINT, original_sigint)
        try:
            if raw_input("\nReally quit? (y/n)> ").lower().startswith('y'):
                sys.exit(1)
        except KeyboardInterrupt:
            print("Ok ok, quitting")
            sys.exit(1)
        # restore the exit gracefully handler here
        signal.signal(signal.SIGINT, _exit_gracefully)
    return _exit_gracefully


def is_blacklist(word):
    for item in STR_BLACKLIST:
        if word.startswith(item):
            return True

        if re.match("c[0-9]+", word):
            return True

        if re.match("[0-9]+", word):
            return True

    return False


def retrieve_actual_time(query_out):
    # use small initial number to avoid div by zero
    p_time = MIN
    e_time = MIN
    for line in query_out.split("\n"):
        if "planning time" in line.lower():
            p_time = float(line.split(":")[1].split("ms")[0].strip())
        if "execution time" in line.lower():
            e_time = float(line.split(":")[1].split("ms")[0].strip())

    return float(p_time + e_time)


def _run_cmd(cmd, ret_elapsed=False):
    """ run command and return execution time """
    if ret_elapsed:
        start = time.time()
        os.system(cmd)
        end = time.time()
        return end - start
    else:
        os.system(cmd)


def remove_stdout():
    if os.path.exists(TMP_OUTPUT):
        os.system("rm -f %s" % TMP_OUTPUT)


def run_cmd(cmd, no_stdout=True, exclude_port=0, timeout=None):
    """ run command for all servers """
    out = {}
    out_list = []
    stdout = {}
    stderr = {}

    if os.path.exists(TMP_ERR):
        os.remove(TMP_ERR)

    if "DEBUG" in os.environ:
        no_stdout = False

    # handle output to screen and file
    if no_stdout and "/dev/null" not in cmd:
        cmd += " > /dev/null 2> %s" % TMP_ERR2
    else:
        cmd += " > %s 2> %s" % (TMP_OUTPUT, TMP_ERR2)

    if timeout is not None:
        cmd = "timeout %ds %s" % (TIMEOUT, cmd)

    for port in SERVERS.keys():
        current_stdout = ""

        if exclude_port == int(port):
            continue

        newcmd = cmd.replace("{PORT}", port)
        newcmd = newcmd.replace("\n", "")
        newcmd = newcmd.replace("\r", "")

        with open(TMP_CMD, 'w') as f:
            f.write(newcmd)

        # remove temp_stdout file and run cmd
        remove_stdout()
        _run_cmd(newcmd)

        # correct stdout
        if os.path.exists(TMP_OUTPUT):
            with open(TMP_OUTPUT, 'r') as f:
                current_stdout = f.read()
        else:
            current_stdout = "NONE"

        elapsed = retrieve_actual_time(current_stdout)

        out[port] = elapsed
        out_list.append(elapsed)
        stdout[port] = current_stdout

        with open(TMP_ERR2, 'r') as f:
            stderr[port] = f.read()

        with open(TMP_ERR, 'a') as f:
            f.write(stderr[port])
            f.write("\n")

    return out, out_list, stdout, stderr


def run_one_cmd(cmd, portnum, no_stdout=True):
    """ run command for one server (desinated port) """

    if os.path.exists(TMP_ERR):
        os.remove(TMP_ERR)

    if no_stdout and "/dev/null" not in cmd:
        cmd += " > /dev/null 2>> %s" % TMP_ERR

    port = str(portnum)
    newcmd = cmd.replace("{PORT}", port)
    elapsed = _run_cmd(newcmd, ret_elapsed=True)

    return elapsed


def sanitize_table(_list):
    # MIN_PROB, MAX_PROB
    # return value within MIN_PROB / MAX_PROB
    return_list = _list

    for x in range(len(_list)):
        if return_list[x] > MAX_PROB[x]:
            return_list[x] = MAX_PROB[x]
        if return_list[x] < MIN_PROB[x]:
            return_list[x] = MIN_PROB[x]

    return return_list


def mkdirs(pn):
    try:
        os.makedirs(pn)
    except OSError:
        pass


def does_contain_many_join(query, count):
    if query.lower().count("join") > count:
        return True
    return False


def does_query_modify_table(query):
    keywords = ['insert', 'update', 'alter', "delete"]
    for keyword in keywords:
        if keyword in query.lower():
            return True
    return False


def check_daemon():
    check_cmd = "netstat -napt 2>/dev/null |grep LIST |grep \"0.0\" \
        |grep \"%d\\|%d\"|wc -l" \
        % (LATEST_VERSION_PORT, OLDEST_VERSION_PORT)
    output = commands.getoutput(check_cmd)
    output = output.strip()

    if output < "%d" % (len(SERVERS)):
        return True

    return False


def check_daemon_port(port):
    check_cmd = "netstat -napt 2>/dev/null |grep LIST |grep \"0.0\" \
        |grep %d |wc -l" % (port)
    output = commands.getoutput(check_cmd)
    output = output.strip()

    if int(output) < 1:
        return True

    return False


def relaunch_daemon():
    if USE_TPCC:
        cmd = "cd %s; ./%s" % (RELAUNCH_SCRIPT_DIR, RELAUNCH_SCRIPT_TPCC)
    else:
        cmd = "cd %s; ./%s" % (RELAUNCH_SCRIPT_DIR, RELAUNCH_SCRIPT_NOR)
    os.system(cmd)


def join(*args):
    return os.path.abspath(os.path.join(*args))


# check blacklist for cockroachdb
def no_blacklist(query):
    for item in COCK_BLACKLIST:
        if item in query:
            return False
    return True


def extract_valid_query(outdir, targetdb):
    query_result = []
    extract_queries = []
    with open(TMP_ERR_PN, 'r') as f:
        data = f.read()
        results = ""
        if "Generating" in data and "quer" in data:
            results = data.split(
                "Generating indexes...done.")[1].split("queries:")[0]
            results = results.replace("\n", "").strip()

        for x in xrange(len(results)):
            if results[x] == "e":
                query_result.append("fail")
            elif results[x] == ".":
                query_result.append("success")
            elif results[x] == "S":
                query_result.append("syntax error")
            elif results[x] == "C":
                query_result.append("crash server!!!")
                os.system("cat %s >> %s/crashed" % (outdir, TMP_QUERY_PN))
            elif results[x] == "t":
                query_result.append("timeout")
            else:
                raise Exception('Not possible!')

    with open(TMP_QUERY_PN, 'r') as f:
        data = f.read()
        results = data.split(";")[:-1]

        for x in xrange(len(results)):
            if query_result[x] == "success":
                if targetdb == 'cockroach' and no_blacklist(results[x]):
                    extract_queries.append(results[x] + ";")
                elif targetdb == 'postgres':
                    extract_queries.append(results[x] + ";")
    return extract_queries


class RegressionFuzzer(object):
    def __init__(
        self, targetdb, outdir, useprob, initdb, minimize, cleanlog=True):

        self.targetdb = targetdb
        self.tests = None
        self.outdir = outdir
        self.sql_filename = {}
        self.minimize = minimize
        self.found_count = 0
        self.current_true = 0
        self.total_true = 0
        self.round = 0
        self.probtable = INIT_PROB
        self.use_probtable = useprob
        self.initialize_db = initdb

        self.found_keyword = False
        self.total_executed = 0
        self.avg_regression = 0.0
        self.total_regression = 0.0
        self.count_regression = 0
        self.starttime = time.time()

        self.TMP_DIR = "%s" % (outdir)

        if self.targetdb == 'postgres':
            self.dsn = CONF["DSN"]

        elif self.targetdb == 'sqlite':
            import sqlite3 as sqlite_old
            import sqlite4 as sqlite_new

            # TODO: fix this
            self.DBPATH = CONF["FILEDB"]
            self.dsn = CONF["DSN"]
            self.conn_old = sqlite_old.connect(self.DBPATH, timeout=5)
            self.conn_new = sqlite_new.connect(self.DBPATH, timeout=5)
            self.cur_old = self.conn_old.cursor()
            self.cur_new = self.conn_new.cursor()

        self.log = Logger(self.targetdb)

        if cleanlog:
            self.clean_log(self.log.logfile)

        # cleanup
        os.system("rm -rf %s/* " % self.TMP_DIR)

        # make necessary dirs
        mkdirs(self.TMP_DIR)
        mkdirs(TMP_QUERY_OUT)
        mkdirs(TMP_QUERY_ERR)

    def update_prob_table(self):
        # dump current probtable to desinated directory (PROB_PN)
        sanitized_table = sanitize_table(self.probtable)
        with open(PROB_PN, 'w') as f:
            for x in range(len(sanitized_table)):
                f.write(str(sanitized_table[x]) + " ")

    def clean_log(self, LOGFILE):
        if os.path.exists(LOGFILE):
            os.remove(LOGFILE)

    def check_limit(self, _list, threshold):
        # any_value_above_threshold
        for item in _list:
            if float(item) < threshold:
                return False
        return True

    def analyze_output(self, qr_time):
        len_list = len(qr_time)
        for x in range(len_list):
            for y in range(len_list - x - 1):
                div = float(qr_time[x + y + 1]) / float(qr_time[x])
                if div > THRESHOLD and \
                    self.check_limit(qr_time, MINIMUM_QUERY_TIME):
                    return True, div
        return False, 0

    def check_latest_max(self, qr_time):
        """ check whether mysql 8.0 has lognest execution time """

        max_exec = max(qr_time)
        if max_exec == qr_time[1]:
            return True

        return False

    def run_fuzz(self):
        """ Enable for debugging
        if self.targetdb == 'postgres':
            self.run_fuzz_postgres()

        elif self.targetdb == 'sqlite':
            self.run_fuzz_sqlite()
        """

        self._run_fuzz()

    def dryrun_sqlsmith(self):
        """ run simple sqlsmith command to OLDEST_PORT """
        self._gen_sqlsmith_queries(1, 20)

    def store_current_query(self, query, stdout, elapsed_list):

        pn = os.path.join(TMP_QUERY_OUT, "%d.sql" % self.found_count)
        stdout_pn = os.path.join(TMP_QUERY_OUT, "%d.out" % self.found_count)
        self.found_count += 1

        elapsed = "/* Elapsed old:%f new:%f ratio:%f */\n" % \
            (elapsed_list[0], elapsed_list[1],
                elapsed_list[1] / elapsed_list[0])

        with open(pn, 'w') as f:
            f.write(query + "\n")
            f.write(elapsed)

        with open(stdout_pn, 'w') as f:
            f.write(stdout[str(OLDEST_VERSION_PORT)] + "\n")

        return pn

    def check_testdb(self, dbname):
        pass

    def increase_prob(self, keyword, val):
        self.found_keyword = True
        self.probtable[KEYWORD_IDX[keyword]] += val
        self.log.debug(" >> increase distinct", _print=False)

    def decrease_prob(self, keyword, val):
        self.found_keyword = True
        self.probtable[KEYWORD_IDX[keyword]] -= val
        self.log.debug(" >> increase distinct", _print=False)

    def check_clauses(self, query):
        self.found_keyword = False
        # and or condition
        if "or " in query.lower():
            self.increase_prob("or", 2)
        if "and " in query.lower():
            self.decrease_prob("or", 2)

        # true or false
        if "true" in query.lower():
            self.increase_prob("true", 1)
        if "false" in query.lower():
            self.decrease_prob("true", 1)

        if "not" in query.lower():
            self.increase_prob("not", 1)
        if "limit" in query.lower():
            self.increase_prob("limit", 1)
        if "case" in query.lower():
            self.increase_prob("case", 1)
        if "nullif" in query.lower():
            self.increase_prob("nullif", 1)
        if "coalesce" in query.lower():
            self.increase_prob("coalesce", 1)
        if "distinct" in query.lower():
            self.increase_prob("distinct", 2)
        if "right" in query.lower():
            self.increase_prob("right", 2)
        if "left" in query.lower():
            self.increase_prob("left", 2)
        if "inner" in query.lower():
            self.increase_prob("inner", 2)

    def run_minimizer(self, stored_pn):
        cmd = "python sql_minimizer.py -c %s -f %s" % (CONFIG_PN, stored_pn)
        os.system(cmd)

    def _run_fuzz(self):

        self.log.debug("[*] start fuzzing", _print=True)

        # 1) initialize DB
        self.log.debug("[*] Initialize DB", _print=True)

        # if test_db not exist, create/import the db
        # now we are only supporting postgres
        if self.initialize_db:
            self.init_db(TEST_DB)
            self.sync_dbs(TEST_DB, "", pn=TPCC_DIR, toAll=True)

        # create probability table with initial value
        if self.use_probtable:
            self.update_prob_table()

        count = 0
        crash_count = 0
        fp_count = 0

        try:
            while True:

                print("[*] Running %dth Round" % self.round)
                self.round += 1
                count += 1
                if count % 100 == 0:
                    print(" >> Processing %dth query" % count)

                # 3.1) generate N queries (store query and error files)
                while True:
                    self.log.debug(" >> gen_queries", _print=False)

                    # cockroachdb uses sqlsmith from postgresql
                    elapsed = self._gen_sqlsmith_queries(150, 20)
                    if elapsed < 9.7:
                        self.log.debug(
                            " >> gen_query success within timeout",
                            _print=False)
                        break

                # 3.2) parse query/error files and extract valid queries
                queries = extract_valid_query(self.TMP_DIR, self.targetdb)
                self.log.debug(
                    " >> succeed generating %d queries" % len(queries),
                    _print=True)

                # 3.3) run queries (only valid)
                self.current_true = 0
                for query in tqdm(queries):

                    # 3.4) query complexity check
                    if self.targetdb == 'postgres':
                        query = "%s\n%s" % (CONF["PREFIX"], query)
                    elif self.targetdb == 'sqlite':
                        query = query + "\n"
                        if randint(0, 100) > 80:
                            query = query.replace("is NULL", "is not NULL")
                    elif self.targetdb == 'cockroach':
                        # do nothing
                        pass

                    if does_query_modify_table(query):
                        continue

                    if does_contain_many_join(query, 6):
                        continue

                    with open(CURR_QUERY, 'w') as f:
                        f.write(query)

                    querying_time_org = [0.0, 0.0, 0.0, 0.0]
                    elapsed, elapsed_list, stdout, stderr = \
                        self.run_queries(TEST_DB, query, False, tout=TIMEOUT)
                    querying_time = [x + y for x, y in zip(
                        querying_time_org, elapsed_list)]

                    # 4) analyze output (elapsed time)
                    div = elapsed_list[1] / elapsed_list[0]
                    result = div > THRESHOLD

                    if "error" in stdout[str(OLDEST_VERSION_PORT)].lower():
                        continue

                    # result, div = self.analyze_output(querying_time)
                    if "DEBUG" in os.environ:
                        print(div, elapsed_list[0], elapsed_list[1])

                    # we found regression but we need to remove FPs
                    if result:

                        # elapsed time should be longer than 0.1 ms
                        if elapsed_list[0] < 0.01 or elapsed_list[1] < 0.01:
                            result = False
                            continue

                        # discard never executed condition
                        if self.targetdb == 'postgres':
                            if "never" in stdout[
                                str(OLDEST_VERSION_PORT)].lower():
                                result = False
                                continue

                        # we validate again and store only if
                        # the regression works
                        elapsed_val, elapsed_list_val, stdout_val, stderr_val \
                            = self.run_queries(
                                TEST_DB, query, False, tout=(TIMEOUT * 3))

                        # querying_time_val = [
                        #    x + y for x, y in zip(
                        #        querying_time_org, elapsed_list_val)]

                        div_val = elapsed_list_val[1] / elapsed_list_val[0]
                        result_val = div_val > THRESHOLD

                        if not result_val:
                            fp_count += 1
                            continue

                        # OK! we found regression
                        # 3.5) Update statistics

                        self.count_regression += 1
                        self.total_regression += div_val
                        self.avg_regression = \
                            self.total_regression / self.count_regression

                        # 3.6) Update probability table
                        if self.use_probtable:
                            self.check_clauses(query)
                            if self.found_keyword is True:
                                self.log.debug(
                                    " >>>>> update probability table ",
                                    _print=False)
                                self.log.debug(','.join(
                                    [str(elem) for elem in self.probtable]),
                                    _print=False)
                                self.update_prob_table()

                        # 3.7) Store the query
                        self.current_true += 1
                        stored_pn = self.store_current_query(
                            query, stdout, elapsed_list)
                        current_test = self.targetdb
                        current_query = query

                        # 3.8) Minimize
                        if self.minimize:
                            # TODO: process everything in python
                            self.run_minimizer(stored_pn)

                        # print out the result
                        self.log.debug(
                            "[!] Found interesting case in %s" % current_test,
                            _print=True)
                        self.log.debug("QUERY", _print=False)
                        self.log.debug("====START====", _print=False)
                        self.log.debug(current_query, _print=False)
                        self.log.debug("====END====", _print=False)
                        self.log.debug(
                            " ".join(map(str, querying_time)), _print=False)
                        self.log.debug(
                            "[!] %f times longer execution time" % div,
                            _print=True)

                        # if latest version shows maximum process time...
                        # if self.check_latest_max(querying_time):
                        #    self.log.debug(
                        #    "[!] postgres 11 showed longest time")

                        # backup err msg if any
                        if os.path.exists(TMP_ERR):
                            os.system(
                                "cp %s %s/%s" %
                                (TMP_ERR, TMP_QUERY_ERR, str(count) + ".err"))

                            self.log.debug(
                                "Copied stderr to %s/%s" %
                                (self.TMP_DIR, str(count) + ".err"))

                self.total_true += self.current_true
                self.log.debug(
                    " >> total number of true %d/%d/%d" %
                    (self.current_true, len(queries), self.total_true),
                    _print=True)
                self.log.debug(
                    " >> total number of fp queries %d" %
                    fp_count, _print=True)
                self.log.debug(
                    "[!] Total regression (count): %d, \
                    average regression: %f, executed (total): %d" %
                    (self.count_regression, self.avg_regression,
                        self.total_executed), _print=True)

                end = time.time()
                hours, rem = divmod(end - self.starttime, 3600)
                minutes, seconds = divmod(rem, 60)
                self.log.debug(
                    " >> Elapsed minutes: %d" % int(minutes), _print=True)

                # we occasionally reset the probability table
                # to prevent overfit
                if int(minutes) % PROBRESET == 0 and int(minutes) != 0:
                    self.log.debug("[*] reset probability table", _print=True)
                    os.system("cp probability %s" % PROB_PN)

                # Restore servers from crash (postgres DB)
                # we don't consider any memory curruption bug now
                if self.targetdb == "postgres":
                    crashed = check_daemon()
                    if crashed:
                        self.log.debug("Daemon Break!", _print=True)
                        with open(
                            "%s/crash%d" %
                                (self.TMP_DIR, crash_count), 'w') as f:
                            f.write("\n".join(queries))
                            crash_count += 1

                        relaunch_daemon()

                if self.targetdb == "cockroach":
                    crashed = check_daemon_port(SQLSMITH_PORT)
                    if crashed:
                        self.log.debug("Daemon Break!", _print=True)
                        with open(
                            "%s/crash%d" %
                                (self.TMP_DIR, crash_count), 'w') as f:
                            f.write("\n".join(queries))
                            crash_count += 1

                        relaunch_daemon()

        except KeyboardInterrupt:
            print('interrupted CTRL-C!')

    def dump_db(self, dbname):
        _, pn = tempfile.mkstemp()

        if self.targetdb == 'postgres':
            # PGPASSWORD=mysecretpassword pg_dump -h 127.0.0.1 -p 5432 -U
            # postgres test_bd > /tmp/export.pgsql
            cmd = "pg_dump -h 127.0.0.1 -p %d -U postgres %s > %s" \
                % (LATEST_VERSION_PORT, dbname, pn)

        _run_cmd(cmd)

        if os.path.getsize(pn) > 0:
            return pn

        else:
            raise Exception('Exception')

    def import_db(self, pn, dbname, toAll=False):

        if self.targetdb == 'postgres':
            """
            e.g., PGPASSWORD=mysecretpassword psql -h 127.0.0.1 -p 5433 -U
            postgres -d test_bd -f /tmp/export.pgsql
            """
            cmd = "psql -h 127.0.0.1 \
                -p {PORT} -U postgres \
                -d %s -f %s" \
                % (dbname, pn)

        if toAll:
            run_cmd(cmd, exclude_port=0, no_stdout=False)
        else:
            run_cmd(cmd, exclude_port=LATEST_VERSION_PORT, no_stdout=False)

    def sync_dbs(self, dbname, test, pn=None, toAll=False):
        """ export data from one DB and import to other DBs """

        if pn is None:
            pn = self.dump_db(dbname)
            self.import_db(pn, dbname, toAll)
        else:
            self.import_db(pn, dbname, toAll)

        return pn

    def retrieve_cockroach_time(stdout):

        if "Time:" in stdout:
            return float(stdout.split("Time:")[1].split(".")[0])
        return 0.0

    def run_queries(self, dbname, query, no_stdout, tout=None):
        """ -t : tuple only """

        if self.targetdb == 'postgres':
            """
            e.g., PGPASSWORD=mysecretpassword psql -h 127.0.0.1 -p 5433 -U
            postgres -d test_bd -c "select * from
            table1000_key_pk_parts_2_varchar_1024_not_null"
            """

            # TODO: remove backtick?
            query = query.replace("`", "")

            # cmd = "psql -h 127.0.0.1 -p {PORT} \
            #    -U postgres -d %s -c '%s'" % (dbname, query)
            cmd = "%s %s" % (CONF["RUN_OLD"], CURR_QUERY)

            elapsed, elapsed_list, stdout, stderr = run_cmd(
                cmd, no_stdout=no_stdout, timeout=tout)

        elif self.targetdb == 'sqlite':
            elapsed_old = elapsed_new = 0.01
            elapsed_list = []
            try:
                new_start = time.time()
                self.cur_new.execute(query)
                # new_out = len(self.cur_new.fetchmany(30000))
                elapsed_new = time.time() - new_start

                old_start = time.time()
                self.cur_old.execute(query)
                # old_out = len(self.cur_old.fetchmany(30000))
                elapsed_old = time.time() - old_start

            except:
                pass

            elapsed = stdout = stderr = ""
            elapsed_list.append(elapsed_old)
            elapsed_list.append(elapsed_new)

        elif self.targetdb == 'cockroach':
            elapsed_old = elapsed_new = 0.1
            elapsed_list = []

            cmd_old = "cockroach2 sql --insecure --host=localhost \
                --port=%d --database=test_bd < %s" \
                % (OLDEST_VERSION_PORT, CURR_QUERY)
            cmd_new = "cockroach19 sql --insecure --host=localhost \
                --port=%d --database=test_bd < %s" \
                % (LATEST_VERSION_PORT, CURR_QUERY)

            if tout is not None:
                cmd_old = "timeout %ds %s" % (tout, cmd_old)
                cmd_new = "timeout %ds %s" % (tout, cmd_new)

            old_start = time.time()
            stdout_old = commands.getoutput(cmd_old)
            elapsed_old = time.time() - old_start

            new_start = time.time()
            stdout_new = commands.getoutput(cmd_new)
            elapsed_new = time.time() - new_start

            elapsed = stderr = ""
            elapsed_list.append(elapsed_old)
            elapsed_list.append(elapsed_new)

            stdout = {}
            stdout[str(OLDEST_VERSION_PORT)] = stdout_old
            stdout[str(LATEST_VERSION_PORT)] = stdout_new

        return elapsed, elapsed_list, stdout, stderr

    def drop_db(self, dbname):

        if self.targetdb == 'postgres':
            """
            e.g., PGPASSWORD=mysecretpassword psql -h 127.0.0.1 -p 5432 -U
            postgres -c "drop database test_bd;"
            """
            cmd = "psql -h 127.0.0.1 \
                -p {PORT} -U postgres \
                -c 'drop database %s;'" % (dbname)

        run_cmd(cmd)

    def create_db(self, dbname):

        if self.targetdb == 'postgres':
            """
            e.g., PGPASSWORD=mysecretpassword psql -h 127.0.0.1 -p 5433 -U
            postgres -c "create database test_bd"
            """
            cmd = "psql -h 127.0.0.1 \
                -p {PORT} -U postgres \
                -c 'create database %s;'" % (dbname)

        run_cmd(cmd)

    def init_db(self, dbname):
        """ originally drop and create DB """
        self.drop_db(TEST_DB)
        self.create_db(TEST_DB)

    def _gen_sqlsmith_queries(self, query_num, timeout):
        """ generate sqlsmith queries on postgres DB using OLDEST version """

        if self.use_probtable:
            PROBTABLE = "--prob-table=\"%s\"" % PROB_PN
        else:
            PROBTABLE = ""

        if self.targetdb == 'postgres' or self.targetdb == 'cockroach':
            if USE_TPCC:
                cmd = "timeout %ds %s --verbose --exclude-catalog\
                --dump-all-queries --seed=%d --max-queries=%d %s \
                --target=\"host=127.0.0.1 port=%d  \
                user=postgres password=mysecretpassword \
                dbname=%s\" 1> %s  2> %s" \
                % (timeout, SQLSMITH, randint(1, 1000000),
                    query_num, PROBTABLE, SQLSMITH_PORT, TEST_DB,
                    TMP_QUERY_PN, TMP_ERR_PN)
            else:
                cmd = "timeout %ds %s --verbose \
                --dump-all-queries --seed=%d --max-queries=%d \
                --prob-table=\"%s\" \
                --target=\"host=127.0.0.1 port={PORT}  \
                user=postgres password=mysecretpassword \
                dbname=%s\" 1> %s  2> %s" \
                % (timeout, SQLSMITH, randint(1, 1000000),
                    query_num, PROBTABLE, TEST_DB, TMP_QUERY_PN, TMP_ERR_PN)

            elapsed = run_one_cmd(cmd, OLDEST_VERSION_PORT, no_stdout=False)

        elif self.targetdb == 'sqlite':
            cmd = "timeout %ds ./sqlsmith --verbose  \
            --exclude-catalog --dump-all-queries \
            --seed=%d --max-queries=%d --sqlite=\"%s\" \
            1> %s 2> %s" \
            % (timeout, randint(1, 1000000),
                query_num, self.dsn, TMP_QUERY_PN, TMP_ERR_PN)

            elapsed = run_one_cmd(cmd, 0, no_stdout=False)

        return elapsed

def main():

    # Ctrl-c handler
    signal.signal(
        signal.SIGINT, exit_gracefully(signal.getsignal(signal.SIGINT)))

    useprob = CONF["USE_PROB"]
    initialize = CONF["INIT"]
    minimize = CONF["USE_MINIMIZER"]
    dbname = CONF["DBMS"]
    outdir = CONF["OUTDIR"]

    if initialize and \
        (dbname == "sqlite" or dbname == "cockroach"):
        print("Sqlite/Cock does not need initialization")
        sys.exit(1)

    if useprob and \
        (dbname == "sqlite" or dbname == "cockroach"):
        print("We don't support feedback-driven fuzzing for Sqlite now")
        sys.exit(1)

    rf = RegressionFuzzer(
        dbname, outdir, useprob, initialize, minimize, cleanlog=True)
    rf.run_fuzz()


if __name__ == "__main__":
    main()
