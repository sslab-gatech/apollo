#!/usr/bin/env python2
import os
import re
import sys
import time
import glob
import signal
import tempfile
import commands
import sqlparse

from conf import *
from tqdm import tqdm

"""
Standalone commands:
./sql_minimizer.py -c configuration/postgres.yaml -f pg_ex/1.sql
"""

# TODO: support both library and process mode for sqlite
# TODO: remove many duplicated code
# TODO:  add explanation for utility scripts


def exit_gracefully(original_sigint):
    # code from: https://stackoverflow.com/questions/18114560/
    def _exit_gracefully(signum, frame):
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


def print_title(title):
    print("\n")
    print("*" * len(title))
    print(title)
    print("*" * len(title))


def _run_cmd(cmd):
    """ run command and return execution time """
    start = time.time()
    os.system(cmd)

    end = time.time()
    return end - start


def run_cmd(cmd, port, no_stdout=True, timeout=None):
    """ run command for all servers """
    out = ""
    err = ""

    errfile = "/tmp/.err_min"
    outfile = "/tmp/.result_min"

    if os.path.exists(TMP_ERR):
        os.remove(TMP_ERR)

    # if we don't want stdout
    if no_stdout and "/dev/null" not in cmd:
        cmd += " > /dev/null 2> %s" % TMP_ERR
    else:
        if os.path.exists(errfile):
            os.remove(errfile)
        if os.path.exists(outfile):
            os.remove(outfile)

    if timeout is not None:
        cmd = "timeout --signal=SIGINT %s %s" % (timeout, cmd)

    cmd = cmd + "> %s 2> %s" % (outfile, errfile)

    newcmd = cmd.replace("{PORT}", port)
    newcmd = newcmd.replace("\n", "")
    newcmd = newcmd.replace("\r", "")

    elapsed = _run_cmd(newcmd)

    # collect output
    if os.path.exists(errfile):
        with open(errfile, 'r') as f:
            err = f.read()

    if os.path.exists(outfile):
        with open(outfile, 'r') as f:
            out = f.read()

    return elapsed, err, out


def print_log(args):
    print("*" * 40)
    for item in args:
        print(item)
        print("-" * 40)
    print("=" * 40)


def is_select_statement(token):
    if token.startswith("select") or \
            token.startswith("(select") or \
            token.startswith("( select"):
        return True
    return False


def is_case_statement(token):
    if token.startswith("case"):
        return True
    return False


def retrieve_actual_time(query_out):
    # use small initial number to avoid div by zero
    p_time = 0.000001
    e_time = 0.000001
    for line in query_out.split("\n"):
        if "planning time" in line.lower():
            p_time = float(line.split(":")[1].split("ms")[0].strip())
        if "execution time" in line.lower():
            e_time = float(line.split(":")[1].split("ms")[0].strip())

    return float(p_time + e_time)


def mkdirs(pn):
    try:
        os.makedirs(pn)
    except OSError:
        pass


def join(*args):
    return os.path.abspath(os.path.join(*args))


def load_filelist_from_dir(dirname, onlyfile=True):
    extension_path = []

    for root, dirs, files in os.walk(dirname):
        for filename in files:
            if onlyfile:
                extension_path.append(filename)
            else:
                extension_path.append(root + "/" + filename)

    return extension_path


def fix_as_statement(query):
    query_lines = query.split("\n")
    query_out = ""

    for index, line in enumerate(query_lines):
        # how to find problematic line
        if index == len(query_lines) - 1:
            break

        if query_lines[index + 1].lstrip().lower().startswith("as") and \
            len(query_lines[index + 1].strip().lower().split(' ')) == 2:
            line = line + " " + query_lines[index + 1].strip().lower()
            query_lines[index + 1] = ""

        if line != "":
            query_out += line + "\n"
    return query_out


def contain_limit(line):
    if 'limit' in line.lower() and any(i.isdigit() for i in line) \
        and ' ' in line:
        return True
    return False


def elements_between_select_from(query):
    """ return items between SELECT and FROM
        - should handle case of last element's comma  """

    query_lines = query.split("\n")
    result = []

    select_line = None
    from_line = None

    for index, line in enumerate(query_lines):
        if 'select' in line.lower() and 'from' in line.lower():
            continue

        if 'select' in line.lower():
            select_line = index

        if 'from' in line.lower():
            from_line = index
            result.append([select_line, from_line])
    return result

def replace_candidate_between_select_from(query, identified):

    query_lines = query.split("\n")
    result = []  # store [current, replace] e.g., ["ele,", ""]

    for sidx, eidx in identified:
        if isinstance(sidx, int) and isinstance(eidx, int):
            for idx in xrange(sidx + 1, eidx - 1):
                result.append([query_lines[idx].strip(), ""])
            result.append([query_lines[eidx - 1].strip(), "1"])

    return result


def parenthetic_contents(string):
    """Generate parenthesized contents in string as pairs (level, contents)."""
    stack = []
    for i, c in enumerate(string):
        if c == '(':
            stack.append(i)
        elif c == ')' and stack:
            start = stack.pop()
            yield (len(stack), string[start + 1: i])


def flatten_token(token):
    if not hasattr(token, 'tokens'):
        return token

    if hasattr(token.tokens[0], 'tokens'):
        return flatten_token(token.tokens[0]) + flatten_token(token.tokens[1:])
    return token.tokens[:1] + flatten_token(token.tokens[1:])


def flatten_ex(_list):
    if _list == []:
        return _list
    if isinstance(_list[0], list):
        return flatten_ex(_list[0]) + flatten_ex(_list[1:])
    return _list[:1] + flatten_ex(_list[1:])


def reindent_pg_formatter(query):
    _, pn = tempfile.mkstemp()
    with open(pn, 'w') as f:
        f.write(query)

    cmd = "cat %s | ./pg_format --keyword-case 0 --spaces 2 - " % pn
    output = commands.getoutput(cmd)
    os.system("rm -f %s" % pn)

    return output


def ret_leading_space(line):
    return len(line) - len(line.lstrip())


def pre_process_query(query):
    output = ""
    for line in query.split("\n"):
        if line == "":
            continue
        if line.lstrip() == ")":
            line = "    " + line
        output += line + "\n"
    return output.strip()


def split_block_by_indent(query):
    num_kinds = []
    result = []

    query = pre_process_query(query)

    for line in query.split("\n"):
        if int(ret_leading_space(line)) not in num_kinds:
            num_kinds.append(int(ret_leading_space(line)))

    num_kinds.sort()
    len_lines = len(query.split("\n"))

    for process_indent in num_kinds:
        start = None
        end = None
        open_flag = False
        for index, line in enumerate(query.split("\n")):
            current_indent = int(ret_leading_space(line))

            # print current_indent, process_indent, start, end, open_flag
            # when first scanned (open_flag is not set up)
            if current_indent == process_indent and open_flag is False:
                start = index
                open_flag = True
                continue

            # after the flag set up, we meet another same indent
            if current_indent == process_indent and open_flag:
                end = index - 1

                result.append([start, end])
                open_flag = False

                if index + 1 < len_lines:
                    start = index
                    open_flag = True

            if index == len_lines - 1 and open_flag:
                result.append([start, len_lines])
    return result


def calc_timeout(latest_time, old_time):
    # calculate possible timeout: assuming the latest_time is already slow
    candidate = [0.6, 0.7, 0.8]

    for idx in xrange(len(candidate)):
        if candidate[idx] * latest_time > old_time:
            return candidate[idx] * latest_time

    return latest_time


class Minimizer(object):
    """
    this class process one query
    """

    def __init__(self, filename, dbname, outdir, cleanlog=True):
        self.filepath = filename
        self.outdir = outdir
        self.dbname = dbname
        self.outfile = self.filepath + OUT_SUFFIX
        self.dsn = DSN
        self.log = Logger()

        with open(self.filepath) as f:
            self.org_query = f.read()
            self.org_size = len(self.org_query)

        mkdirs(outdir)
        self.current_query = ""
        self.difference = self.extract_comment()
        self.good_to_go = True

        # dry-run to decide whether start the minimizing process
        if dbname == 'sqlite':

            import sqlite3 as sqlite_old
            import sqlite4 as sqlite_new

            self.conn_old = sqlite_old.connect(DBPATH, timeout=10)
            self.conn_new = sqlite_new.connect(DBPATH, timeout=10)
            self.cur_old = self.conn_old.cursor()
            self.cur_new = self.conn_new.cursor()

            # run-original and get the timeout baseline
            self.ori_query_time_old, self.ori_query_time_new =\
                self.run_queries_sqlite(self.org_query)
            print(
                "Old_time:", self.ori_query_time_old, "New_time",
                self.ori_query_time_new, "Ratio",
                self.ori_query_time_new / self.ori_query_time_old)

            # discard if there is no regression
            if self.ori_query_time_new < self.ori_query_time_old:
                print(self.ori_query_time_old, self.ori_query_time_new)
                print(
                    "[!] Old version takes loger time, this is not regression")
                self.good_to_go = False

            # discard too short execution
            if self.ori_query_time_old < 0.001:
                self.good_to_go = False
            self.timeout = calc_timeout(
                self.ori_query_time_new, self.ori_query_time_old)
            mkdirs(TMP_QUERY_STORE)

        elif dbname == 'postgres':
            self.ori_query_time_new, self.ori_query_time_old \
                = self.run_original()
            print(
                "Old_time:", self.ori_query_time_old,
                "New_time", self.ori_query_time_new)

            # discard if there is no regression
            if self.ori_query_time_new < self.ori_query_time_old:
                print(self.ori_query_time_old, self.ori_query_time_new)
                print(
                    "[!] Old version takes loger time, this is not regression")
                self.good_to_go = False
            self.timeout = calc_timeout(
                self.ori_query_time_new, self.ori_query_time_old)
            mkdirs(TMP_QUERY_STORE)

        if cleanlog:
            self.clean_log()

    def run_queries_sqlite(self, query, tout=None):
        elapsed_old = elapsed_new = 0.1

        with open("/tmp/.query", 'w') as f:
            f.write(query)

        cmd_old = "python sqlite_executor.py /tmp/.query old"
        cmd_new = "python sqlite_executor.py /tmp/.query new"

        try:
            elapsed_new = float(commands.getoutput(cmd_new).strip())
        except:
            elapsed_new = 0.00001

        try:
            elapsed_old = float(commands.getoutput(cmd_old).strip())
        except:
            elapsed_old = 0.00001

        if elapsed_new > 4.5:
            elapsed_new = 0.00001

        if elapsed_old > 4.5:
            elapsed_old = 0.00001

        return elapsed_old, elapsed_new

    def run_query_latest(self, query):

        if self.dbname == 'sqlite':

            query = query.replace(";;", ";")
            elapsed_new = 0.1

            with open("/tmp/.query", 'w') as f:
                f.write(query)

            cmd_new = "python sqlite_executor.py /tmp/.query new"

            try:
                elapsed_new = float(commands.getoutput(cmd_new).strip())
            except:
                elapsed_new = 0.00001

            if elapsed_new > 4.5:
                elapsed_new = 0.00001

        elif self.dbname == 'postgres':
            elapsed, err, out = self.run_query(
                query, LATEST_VERSION_PORT, timeout=str(2))
            elapsed_new = retrieve_actual_time(out)

        return elapsed_new

    def extract_comment(self):
        out = ""
        with open(self.filepath, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if "--" in line:
                    out += line + "\n"
        return out

    def clean_log(self):
        if os.path.exists(LOGFILE):
            os.remove(LOGFILE)

    def run_query(self, query, port, timeout=None):

        with open(TMP_QUERY_PN, 'w') as f:
            f.write(query + "\n")

        cmd = "psql -h 127.0.0.1 \
            -p {PORT} -U postgres \
            -d %s -f %s" \
                % (TEST_DB, TMP_QUERY_PN)

        elapsed, err, out = run_cmd(
            cmd, str(port), no_stdout=False, timeout=timeout)
        return elapsed, err, out

    def test_sqlparse(self):
        query_parsed = sqlparse.parse(self.org_query)[0]

        tokens = query_parsed.tokens
        sub_query = tokens[30]
        sub_tokens = sub_query.tokens
        for i, item in enumerate(sub_tokens):
            print(i, item)

    def run_original(self):
        query = "analyze;" + self.org_query
        elapsed, err, out = self.run_query(
            query, LATEST_VERSION_PORT, timeout="7")
        elapsed2, err2, out2 = self.run_query(
            query, OLDEST_VERSION_PORT, timeout="7")

        actual_latest = retrieve_actual_time(out)  # latest
        actual_old = retrieve_actual_time(out2)  # old

        return actual_latest, actual_old

    def init_test(self, remove_intermediate=False):
        print("[*] Initializing directory")

        if remove_intermediate:
            os.system("rm -f %s/query*" % TMP_QUERY_STORE)
        else:
            os.system("rm -f %s/*" % TMP_QUERY_STORE)

    def clean_tmp_dir(self):
        os.system("rm -f %s/query*" % TMP_QUERY_STORE)

    # wrapper
    def topdown(self, threshold):
        # print("Start Top-down approach")
        self.extraction_subquery(threshold)

    # wrapper
    def bottomup(self, threshold):
        # print("Start Bottom-up approach")
        self.reduction_subquery(threshold)
        self.reduction_select_from_element()
        self.reduction_using_parenthesis()
        self.reduction_by_indent()

    # 1st strategy (top-down)
    def reduction_subquery(self, threshold):
        print("[*] Reduction by extracting valid and minimal subquery")

        # clean previous history
        self.clean_tmp_dir()

        reduction_param = {}
        start_query = ""

        if self.current_query == "":
            start_query = self.org_query
        else:
            start_query = self.current_query

        reduction_param['org_query'] = start_query
        reduction_param['token_threshold'] = threshold
        reduction_param['work_dir'] = TMP_QUERY_STORE

        # 1. generate testcases of subquery removed (one by one)
        with open("%s/%s" % (TMP_QUERY_STORE, TMP_REDUCTION_FILE), 'w') as f:
            f.write(start_query)

        # 2. whether each test case actually maintain the long execution time
        filelist = load_filelist_from_dir(TMP_QUERY_STORE, onlyfile=False)
        minsize = 100000
        effect = []

        for filename in tqdm(filelist):
            if "_token" in filename:
                continue

            with open(filename, 'r') as f:
                temp_query = f.read()
                temp_query = temp_query + ";"
                actual_time = self.run_query_latest(temp_query)

                if actual_time > self.timeout:
                    if os.path.exists(filename + "_token"):
                        with open(filename + "_token", 'r') as f:
                            effect_str = f.read()
                            effect.append(effect_str)

                        if len(temp_query) < minsize:
                            minsize = len(temp_query)

        effect.sort(lambda y, x: cmp(len(x), len(y)))

        print(" > Now generating final query")
        query = start_query

        # TODO: apply run_query and rollback
        for _str in effect:
            _str2 = " ".join(_str.split())
            if is_select_statement(_str2):
                query = query.replace(_str, "(select 1)")
            elif is_case_statement(_str):
                query = query.replace(_str, "")

            if "DEBUG" in os.environ:
                print_log([str, query])

        with open("%s/%s" % (TMP_QUERY_STORE, TMP_REDUCTION_FILE), 'w') as f:
            f.write(query)

        self.current_query = query

        if len(query) < 5:
            self.current_query = start_query

        pn = os.path.join(TMP_QUERY_STORE, TMP_REDUCTION_FILE)
        print(
            " > Query size is reduced %d ===> %d" %
            (len(start_query), os.path.getsize(pn)))

        actual_time = self.run_query_latest(temp_query)

        if actual_time > self.timeout:
            print(" > Elapsed time %6.3f (longer than TIMEOUT)" % actual_time)
        else:
            print(" > [WARNING] This strategy failed to reduce query size!!!")

    # 2nd strategy (SELECT~FROM and LIMIT)  (top-down)
    def reduction_select_from_element(self):
        print("\n[*] Try to remove elements between SELECT and FROM")

        # try to remove elements between SELECT and FROM
        start_query = ""

        if self.current_query == "":
            fixed_query = fix_as_statement(self.org_query)
            start_query = self.org_query
        else:
            fixed_query = fix_as_statement(self.current_query)
            start_query = self.current_query

        elements = elements_between_select_from(fixed_query)
        replace_candidate = replace_candidate_between_select_from(
            fixed_query, elements)

        intermediate_query = ""
        replace_candidates = []

        # identify replace candidate (SELECT~FROM)
        for candidate, replaced_str in tqdm(replace_candidate):
            temp_query = fixed_query
            temp_query = temp_query.replace(candidate, replaced_str)

            if "DEBUG" in os.environ:
                print_log([fixed_query, candidate, temp_query])

            actual_time = self.run_query_latest(temp_query)

            if actual_time > self.timeout:
                replace_candidates.append([candidate, replaced_str])

        # apply replacement
        intermediate_query = fixed_query
        for candidate, replaced_str in replace_candidates:
            intermediate_query = intermediate_query.replace(
                candidate, replaced_str)

        final_before_limit = ""
        for line in intermediate_query.split("\n"):
            if line.strip() == "":
                continue
            final_before_limit += line + "\n"

        # try to remove LIMIT
        matched_str = []
        replace_candidates = []
        for line in final_before_limit.split("\n"):
            if contain_limit(line):
                line = line.lower().strip()
                regex = re.search('limit.[0-9]+', line)
                if regex:
                    matched_str.append(regex.group(0))

        for limit in matched_str:
            temp_query = final_before_limit
            temp_query = temp_query.replace(limit, "")

            actual_time = self.run_query_latest(temp_query)

            if actual_time > self.timeout:
                replace_candidates.append(limit)

        final_query = final_before_limit
        for candidate in replace_candidates:
            final_query = final_query.replace(candidate, "")

        # check final query
        actual_time = self.run_query_latest(final_query)
        if actual_time > self.timeout:
            with open(
                "%s/%s" % (TMP_QUERY_STORE, TMP_REDUCTION_FILE), 'w') as f:
                f.write(final_query)
                self.current_query = final_query
        else:
            with open(
                "%s/%s" % (TMP_QUERY_STORE, TMP_REDUCTION_FILE), 'w') as f:
                f.write(self.current_query)

        if len(self.current_query) < 5:
            self.current_query = start_query

        pn = os.path.join(TMP_QUERY_STORE, TMP_REDUCTION_FILE)
        print(" > Query is stored at %s" % pn)
        print(
            " > Query size is reduced %d ===> %d"
            % (len(start_query), os.path.getsize(pn)))

        actual_time = self.run_query_latest(self.current_query)
        if actual_time > self.timeout:
            print(" > Elapsed time %6.3f (longer than TIMEOUT)" % actual_time)
        else:
            print(" > [WARNING] This strategy failed to reduce query size!!!")

    # 3rd strategy  (top-down)
    def reduction_using_parenthesis(self):
        print("\n[*] Try to remove any element in parenthesis.")

        matched_str = []
        if self.current_query == "":
            start_query = self.org_query
        else:
            start_query = self.current_query

        for stack, item in tqdm(list(parenthetic_contents(start_query))):
            temp_query = start_query
            temp_query = temp_query.replace(item, "(null)")

            actual_time = self.run_query_latest(temp_query)

            if "DEBUG" in os.environ:
                print_log([actual_time, temp_query])

            if actual_time > self.timeout:
                matched_str.append(item)

        print(" > Applying actual change to original query")

        final_query = start_query
        for candidate in matched_str:
            rollback = final_query
            final_query = final_query.replace(candidate, "(null)")

            if "DEBUG" in os.environ:
                print_log([actual_time, final_query])

            actual_time = self.run_query_latest(temp_query)

            if actual_time > self.timeout:
                final_query = rollback

        with open("%s/%s" % (TMP_QUERY_STORE, TMP_REDUCTION_FILE), 'w') as f:
            f.write(final_query)

        self.current_query = final_query
        if len(self.current_query) < 5:
            self.current_query = start_query

        pn = os.path.join(TMP_QUERY_STORE, TMP_REDUCTION_FILE)
        print(" > Query is stored at %s" % pn)
        print(
            " > Query size is reduced %d ===> %d"
            % (len(start_query), os.path.getsize(pn)))

        actual_time = self.run_query_latest(self.current_query)

        if actual_time > self.timeout:
            print(
                " > Elapsed time %6.3f (longer than TIMEOUT)\n" % actual_time)
        else:
            print(" > [WARNING] This strategy failed to reduce query size!!!")

    # 4th strategy (top-down)
    def reduction_by_indent(self):
        print("[*] Reduction by removing any group with same indent")
        """ since sqlparse library cannot parse subquery/terms correctly
            this script manually handle problem by using indent  """

        if self.current_query == "":
            start_query = self.org_query
        else:
            start_query = self.current_query

        reindent_query = reindent_pg_formatter(start_query)
        indent_block_list = split_block_by_indent(reindent_query)
        reindent_query = pre_process_query(reindent_query)

        matched_list = []
        for block_list in indent_block_list:
            temp_query_list = reindent_query.split("\n")
            temp_str = \
                "\n".join(temp_query_list[block_list[0]:block_list[1] + 1])
            del temp_query_list[block_list[0]:block_list[1] + 1]

            temp_query = "\n".join(temp_query_list)

            actual_time = self.run_query_latest(temp_query)

            if actual_time > self.timeout:
                matched_list.append(temp_str)

            if "DEBUG" in os.environ:
                print_log([actual_time, temp_query])

        # need to nicely apply all cases into one query
        print(" > Applying actual change to original query")
        for _str in tqdm(matched_list):
            rollback = reindent_query
            reindent_query = reindent_query.replace(_str, "")

            actual_time = self.run_query_latest(reindent_query)

            if actual_time < self.timeout:
                reindent_query = rollback

        if len(matched_list) < 1:
            reindent_query = start_query

        final_query = reindent_query
        if "DEBUG" in os.environ:
            print_log([actual_time, final_query])

        with open("%s/%s" % (TMP_QUERY_STORE, TMP_REDUCTION_FILE), 'w') as f:
            f.write(final_query)

        self.current_query = final_query
        if len(self.current_query) < 5:
            self.current_query = start_query

        pn = os.path.join(TMP_QUERY_STORE, TMP_REDUCTION_FILE)
        print(" > Query is stored at %s" % pn)
        print(
            " > Query size is reduced %d ===> %d"
            % (len(start_query), os.path.getsize(pn)))

        actual_time = self.run_query_latest(self.current_query)

        print(actual_time, self.timeout)
        if actual_time > self.timeout:
            print(" > Elapsed time %6.3f (longer than TIMEOUT)" % actual_time)
        else:
            print(" > [WARNING] This strategy failed to reduce query size!!!")

    # 5th strategy (bottom-up)
    def extraction_subquery(self, threshold):
        print("[*] Bottom-up by extracting valid and minimal subquery")

        # clean previous history
        self.clean_tmp_dir()

        reduction_param = {}
        start_query = ""

        if self.current_query == "":
            start_query = self.org_query
        else:
            start_query = self.current_query

        reduction_param['org_query'] = start_query
        reduction_param['token_threshold'] = threshold
        reduction_param['work_dir'] = TMP_QUERY_STORE

        # 1. generate testcases of subquery removed (one by one)
        # NOTHING

        # 2. whether each test case actually maintain the long execution time
        filelist = load_filelist_from_dir(TMP_QUERY_STORE, onlyfile=False)

        minsize = 100000
        minquery = start_query
        for filename in tqdm(filelist):
            if "_token" in filename:
                with open(filename, 'r') as f:
                    temp_query = f.read()
                    temp_query = temp_query + ";"  # just in case

                    actual_time = self.run_query_latest(temp_query)

                    if actual_time > self.timeout:
                        if len(temp_query) < minsize:
                            minsize = len(temp_query)
                            minquery = temp_query

        # finish
        query = minquery
        with open("%s/%s" % (TMP_QUERY_STORE, TMP_REDUCTION_FILE), 'w') as f:
            f.write(query)

        self.current_query = minquery
        if len(self.current_query) < 5:
            self.current_query = start_query

        pn = os.path.join(TMP_QUERY_STORE, TMP_REDUCTION_FILE)
        print(" > Query is stored at %s" % pn)
        print(
            " > Query size is reduced %d ===> %d"
            % (len(start_query), os.path.getsize(pn)))

        actual_time = self.run_query_latest(self.current_query)

        if actual_time > self.timeout:
            self.current_query = query
            print(
                " > Elapsed time %6.3f (longer than TIMEOUT)\n" % actual_time)
        else:
            print(" > [WARNING] This strategy failed to reduce query size!!!")

    def storefile(self, target_dir, filename):
        actual_time = self.run_query_latest(self.current_query)

        print(
            "[*] Final result: actual_time = %f, timeout = %f" %
            (actual_time, self.timeout))
        result = "--reduced actual_latest = %f\n" % actual_time

        if "--" not in self.current_query:
            self.current_query = self.current_query + "\n" + self.difference

        pn = os.path.basename(filename) + "_reduced"

        if len(self.current_query) > 150:
            with open(os.path.join(target_dir, pn), 'w') as f:
                f.write(self.current_query + "\n" + result)


class Report(object):
    def __init__(self):
        self.storage = {}
        self.sum_reduced_size = 0
        self.sum_ori_size = 0

    def add_entry(
        self, filename, org_size, reduced_size, elapsed_time,
        org_time=None, reduced_time=None):

        reduced_ratio = str("%.4f" % float(float(reduced_size) / org_size))
        self.storage[filename] = \
            [filename, org_size, reduced_size, reduced_ratio, elapsed_time]

        self.sum_reduced_size += reduced_size
        self.sum_ori_size += org_size

    def print_report(self):
        for key in self.storage.keys():
            print(self.storage[key])

        print("%d  ====>  %d" % (self.sum_ori_size, self.sum_reduced_size))


class Logger (object):
    def __init__(self):
        self.logfile = LOGFILE

    def debug(self, msg, _print=False):
        with open(self.logfile, 'a') as f:
            f.write(msg + "\n")

        if _print:
            print(msg)


if __name__ == "__main__":

    signal.signal(
        signal.SIGINT, exit_gracefully(signal.getsignal(signal.SIGINT)))

    if TARGET_DB == 'postgres':
        DSN = "\"dbi:Pg:host=127.0.0.1;port={PORT}\
         ;user=postgres;password=mysecretpassword;database=%s\"" % (TEST_DB)

    elif TARGET_DB == 'sqlite':
        DBPATH = "benchmark/tpcc_sqlite.db"
        DSN = "file:%s?mode=ro" % DBPATH

    outdir = CONF["MINIMIZER_DIR"]
    TMP_ERR = os.path.join(outdir, ".stderr")
    TMP_ERR_PN = os.path.join(outdir, ".minimizer_err")
    TMP_QUERY_PN = os.path.join(outdir, ".minimizer_query")
    LOGFILE = os.path.join(outdir, "qmin_log")
    TMP_QUERY_STORE = os.path.join(outdir, "queries")
    TMP_REDUCTION_FILE = "reduction"
    DIFF_THRESHOLD = CONF["MIN_THRESHOLD"]
    OUT_SUFFIX = "_out"

    mkdirs(TMP_QUERY_STORE)

    if MIN_INFILE is not None:
        filelist = [MIN_INFILE]
    else:
        filelist = glob.glob(MIN_INDIR + "/*.sql")

    for filename in filelist:

        output_directory = os.path.dirname(filename)

        # skip if it already minimized
        if os.path.exists(filename + "_reduced"):
            continue

        report = Report()
        start = time.time()
        mini = Minimizer(filename, CONF["DBMS"], output_directory)
        mini.init_test()

        # check the dry-run result
        if mini.good_to_go is False:
            continue

        print_title("Minimizer Processing %s" % filename)

        mini.bottomup(15)
        mini.topdown(15)

        mini.storefile(output_directory, filename)
        elapsed_time = time.time() - start
        report.add_entry(
            filename, mini.org_size, len(mini.current_query), elapsed_time)
        report.print_report()

        del mini, report
