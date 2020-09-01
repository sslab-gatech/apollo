- [ ] Replay previous work
  - [X] Run fuzzing on Postgres (12: 5436, 11:5435, 9.6:5432)
  - [X] Install DB to Postgres
  - [ ] Run fuzzing on SQLite3
  - [ ] Does fuzzing with prob work?

- [X] Introduce YAML
  - [X] Identify which field is necessary
  - [X] Sample Postgres
  - [X] Sample SQLite

- [ ] Integrate sqlmin
  - [X] just turn on/off the option in yaml (on: store after the minimization)
  - [X] make symbolic link
  - [ ] accept configuration from yaml
  - [ ] Unit-test in the sqlfuzz

- [ ] Update the document

``` bash
# PostgreSQL command
./fuzz.py -db postgres -o /tmp/out --no-probability --no-initialize
```