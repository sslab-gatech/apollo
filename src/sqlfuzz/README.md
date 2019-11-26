# Sqlite Fuzzing

### 0) Setup the DBMS

### 1) Do fuzzing

``` bash
./fuzz.py -db sqlite -o out --no-probability --no-initialize
```

* NOTE: we do not support `--probability` and `--initialize` options for Sqlite.

# PostgreSQL Fuzzing

### 0) Setup the DBMS

### 1) Do fuzzing

``` bash
./fuzz.py -db postgres -o out --no-probability --no-initialize
or 
./fuzz.py -db postgres -o out --probability --initialize

```
* `--no-probability` or `--probability`: whether use probability table

* `--no-initialize` or `--initialize`: initialize test database

### 2) Fuzzing parameters

`To be updated ...`