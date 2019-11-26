#!/bin/bash

(cd lib/sqlsmith; autoreconf -i; sed -i 's/char conninfo/char\* conninfo/g' configure; ./configure; make)
(cd lib/sqlsmith-prob; autoreconf -i; sed -i 's/char conninfo/char\* conninfo/g' configure;./configure; make)

ln -s -r lib/sqlsmith/sqlsmith src/sqlfuzz/sqlsmith
ln -s -r lib/sqlsmith-prob/sqlsmith src/sqlfuzz/sqlsmith-prob

ln -s -r lib/sqlparse/sqlparse src/sqlmin/sqlparse
ln -s -r lib/pgFormatter/pg_format src/sqlmin/pg_format
