#!/bin/bash
PGPASSWORD=mysecretpassword psql -h 127.0.0.1 -p 5432 -U postgres -c "drop database test_bd;"
PGPASSWORD=mysecretpassword psql -h 127.0.0.1 -p 5435 -U postgres -c "drop database test_bd;"

PGPASSWORD=mysecretpassword psql -h 127.0.0.1 -p 5432 -U postgres -c "create database test_bd;"
PGPASSWORD=mysecretpassword psql -h 127.0.0.1 -p 5435 -U postgres -c "create database test_bd;"