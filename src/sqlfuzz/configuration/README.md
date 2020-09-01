* Configuration attributes

| Config attribute | Description |
| --- | --- |
| DBMS  | target DBMS name (e.g., postgres)  |
| DB | create database name |
| DB_VER | array about DBMS versions (for displaying) |
| DSN | URI string for connecting DBMS |
| FILEDB | whether DBMS is running on file system (e.g., sqlite) |
| INIT | should Apollo initialize the DB? |
| MIN | minimum query execution time that we should consider |
| NEW_VER_PORT | port number of new version of DBMS |
| OLD_VER_PORT | port number of old version of DBMS |
| PASSWORD | DBMS password |
| PREFIX | prefix string which is added to query |
| PROBRESET | how frequently reset the probability table (unit: minutes) |
| RUN_NEW | external command to run query |
| RUN_OLD | external command to run query |
| SQLSMITH_PORT | specify sqlsmith port (useful when fuzzing cockroachDB) |
| SQLSMITH_TIMEOUT | maximum query generation time |
| THRESHOLD | we will consider query as regression if it is larget than this |
| TIMEOUT | timeout for one query execution |
| USERNAME | DBMS username |
| USE_MINIMIZER | true if user wants auto-minimization on-the-fly |
| USE_PROB | true if user wants feedback-driven fuzzing |
| USE_TPCC | true if user wants to use pre-defined DB |