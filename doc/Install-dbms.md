
`Apollo` requires two version of DBMSs (e.g., old and latest version of sqlite).
In this document, we will guide how to install two version of them using
`sqlite` and `postgres`. 

# 1. SQLITE (as a python module)

In this example, we will make two sqlite module for python.
* Test environment
  * Ubuntu 18.04.3 64bit
  * python 2.7.16

At the end, we will install two modules 
```
1) sqlite3 (old version: 3.18.0, 2017)
2) sqlite4 (new version: 3.27.0, 2019)
```

So if you will see this result:
``` python
Python 2.7.15+ (default, Oct  7 2019, 17:39:04)
[GCC 7.4.0] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import sqlite3
>>> import sqlite4
>>>
>>> print sqlite3.sqlite_version_info
(3, 18, 0)
>>> print sqlite4.sqlite_version_info
(3, 27, 2)
```

First you should install:
``` bash
$ sudo apt-get build-dep python2.7 hexedit
```

### 1) back up the original file (if you have)
``` bash
$ sudo cp /usr/lib/python2.7/lib-dynload/_sqlite3.x86_64-linux-gnu.so /usr/lib/python2.7/lib-dynload/_sqlite3.x86_64-linux-gnu.so.bak

$ sudo mv /usr/lib/x86_64-linux-gnu/libsqlite3.so.0.8.6 /usr/lib/x86_64-linux-gnu/libsqlite3.so.0.8.6.bak
```

### 2) Build two library (.so file)

* You can choose any timeline: https://www.sqlite.org/src/timeline?t=release
* Build 3.27.0 (Feb, 2019)
``` bash
$ wget https://www.sqlite.org/2019/sqlite-src-3270200.zip
$ unzip sqlite-src-3270200.zip
$ mv sqlite-src-3270200 sqlite327
$ cd sqlite327
$ ./configure --enable-unicode=ucs4
$ make -j 4

$ cp .libs/libsqlite3.so.0.8.6 ./libsqlite3.so.3.27
$ sudo cp libsqlite3.so.3.27 /usr/lib/x86_64-linux-gnu/
```

* Build 3.18.0 (Mar, 2017)
``` bash
$ wget https://www.sqlite.org/2017/sqlite-src-3180000.zip
$ unzip sqlite-src-3180000.zip
$ mv sqlite-src-3180000 sqlite318
$ cd sqlite318
$ ./configure --enable-unicode=ucs4
$ make -j 4

$ cp .libs/libsqlite3.so.0.8.6 ./libsqlite3.so.3.18
$ sudo cp libsqlite3.so.3.18 /usr/lib/x86_64-linux-gnu/libsqlite3.so.0.8.6
```

### 3) Build python module

* Build Python for `_sqlite4.so` module and copy to `dynload` directory
``` bash
$ wget https://www.python.org/ftp/python/2.7.16/Python-2.7.16.tgz
$ tar xzvf Python-2.7.16.tgz
$ cd Python-2.7.16
$ vim Modules/_sqlite/module.c  
  => modify 
    PyMODINIT_FUNC init_sqlite3(void)
    Py_InitModule("_sqlite3", module_methods)
     to
    PyMODINIT_FUNC init_sqlite4(void)
    Py_InitModule("_sqlite4", module_methods)

$ ./configure --enable-unicode=ucs4
$ make -j 4
$ sudo cp ./build/lib.linux-x86_64-2.7/_sqlite3_failed.so /usr/lib/python2.7/lib-dynload/_sqlite4.x86_64-linux-gnu.so
$ sudo hexedit /usr/lib/python2.7/lib-dynload/_sqlite4.x86_64-linux-gnu.so
 => modify "libsqlite3.so.0" to "libsqlite3.so.1"
 => how to use hexedit? https://linux.die.net/man/1/hexedit

#make libsqlite3.so.1 link to /usr/lib/x86_64-linux-gnu/libsqlite3.so.3.27
$ cd /usr/lib/x86_64-linux-gnu/
$ sudo ln -s libsqlite3.so.3.27 libsqlite3.so.1
```

### 4) Adjust symlink and test

* Modify currently installed python
``` bash
$ cd /usr/lib/python2.7
$ sudo cp -r sqlite3 sqlite4
$ cd sqlite4
$ sudo vim dbapi2.py
 => "from _sqlite3" to "from _sqlite4"
```

* Check the correct installation
``` bash
import sqlite3
import sqlite4

print sqlite3.sqlite_version_info
print sqlite4.sqlite_version_info
```

***

# 2. Two versions of PostgreSQL

In this example, we will show how to set up two version 
of PostgreSQL in one machine. 

At the end of the example, you will install latest version 
of `PostgreSQL 11` (port 5435) and `PostgreSQL 9.6` (port 5432).


### 1) Install Postgres using APT 

* PostgreSQL 11 and 9.6

```bash
# Enable PostgreSQL Apt Repository
$ sudo apt-get install wget ca-certificates
$ wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
$ sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main" >> /etc/apt/sources.list.d/pgdg.list'

$ sudo apt-get update
$ sudo apt-get install postgresql-11 postgresql-9.6 postgresql-contrib
```

### 2) Change listening port
``` bash
# stop services
$ sudo pg_ctlcluster 9.6 main stop
$ sudo pg_ctlcluster 11 main stop

# modify port numbers
$ sudo vim /etc/postgresql/11/main/postgresql.conf 
  => modify port number to 5435

$ sudo vim /etc/postgresql/9.6/main/postgresql.conf 
  => modify port number to 5432

# start services
$ sudo pg_ctlcluster 9.6 main start
$ sudo pg_ctlcluster 11 main start

# check ports
$ netstat -napt |grep "5435\|5432"
```

### 3) Modify USER setting and assign password

``` bash
# Grant access to the current user
$ sudo -u postgres createuser -p 5432 -s $(whoami); createdb -p 5432 $(whoami)
$ sudo -u postgres createuser -p 5435 -s $(whoami); createdb -p 5435 $(whoami)

# Set password
$ sudo -i -u postgres
$ psql -p 5432
=# ALTER USER postgres PASSWORD 'mysecretpassword';

$ psql -p 5435
=# ALTER USER postgres PASSWORD 'mysecretpassword';
```

***

# 3. Build SqlSmith and SqlSmith-prob

``` bash
$ ./compile-libs.sh
```
