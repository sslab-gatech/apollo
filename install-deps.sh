#!/bin/bash
sudo apt-get update
sudo apt-get install build-essential autoconf autoconf-archive libpqxx-dev libboost-regex-dev sqlite3 libsqlite3-dev fossil
pip install executor --user
pip install psycopg2 --user

