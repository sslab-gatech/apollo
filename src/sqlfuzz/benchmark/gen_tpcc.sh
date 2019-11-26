#!/bin/bash
sudo pg_ctlcluster 9.6 main stop
sudo pg_ctlcluster 11 main stop
sudo pg_ctlcluster 9.6 main start
sudo pg_ctlcluster 11 main start

PGPASSWORD=mysecretpassword psql -h 127.0.0.1 -p 5432 -U postgres -c "drop database test_bd;"
PGPASSWORD=mysecretpassword psql -h 127.0.0.1 -p 5435 -U postgres -c "drop database test_bd;"

PGPASSWORD=mysecretpassword psql -h 127.0.0.1 -p 5432 -U postgres -c "create database test_bd;"
PGPASSWORD=mysecretpassword psql -h 127.0.0.1 -p 5435 -U postgres -c "create database test_bd;"

PGPASSWORD=mysecretpassword psql -h 127.0.0.1 -p 5432 -U postgres -d test_bd -f ./tpcc_postgres.sql
PGPASSWORD=mysecretpassword psql -h 127.0.0.1 -p 5435 -U postgres -d test_bd -f ./tpcc_postgres.sql
