**SQLMIN** will automatically distill the regression-activating SQL statements discovered by SQLFUZZ to their essence for filing regression reports. The user will send the regression report to the developers containing the query reduced by SQLMIN.

# Minimizer command

``` bash
./sql_minimizer.py -db postgres -i pg_ex -o out 
./sql_minimizer.py -db sqlite -i sq_ex -o out 
```

* NOTE: we use same command for Sqlite and Postgres

* `-db`: postgres or sqlite

* `-i` or `--indir`: input directory which contains a number of SQL queries to be minimized

* `-o` or `--outdir`: output directory which will store minimized queries

# Utility commands

`To be updated...`
