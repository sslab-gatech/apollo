#!/bin/bash

echo "Oldest original"
PGPASSWORD=mysecretpassword psql -h 127.0.0.1 -p 5432 -U postgres -f ./$1.sql > /tmp/out ; cat /tmp/out |grep -A 1  Execution
echo "Oldest reduced"
PGPASSWORD=mysecretpassword psql -h 127.0.0.1 -p 5432 -U postgres -f ./$1.sql_reduced > /tmp/out ; cat /tmp/out |grep -A 1  Execution
echo 
echo "Latest original"
PGPASSWORD=mysecretpassword psql -h 127.0.0.1 -p 5435 -U postgres -f ./$1.sql > /tmp/out ; cat /tmp/out |grep -A 1  Execution
echo "Latest reduced"
PGPASSWORD=mysecretpassword psql -h 127.0.0.1 -p 5435 -U postgres -f ./$1.sql_reduced > /tmp/out ; cat /tmp/out |grep -A 1 Execution
