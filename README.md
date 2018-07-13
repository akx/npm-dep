setup
=====

```
# get all the documents in npm's skim db (about 11 gigs)
python get_all_docs.py
# convert them to tsv
python jsonl_to_tsvs.py
# convert the tsvs to a sqlite database (takes a while, no progress bar)
cat sqlite.txt | sqlite3 dependencies.sqlite3
```

usage
=====

dependency graph (forward)
--------------------------

```
python3 dependency_graph.py vue-cli 2.9.6 > vue.csv
```

the output is an adjacency matrix readable by Gephi, etc
