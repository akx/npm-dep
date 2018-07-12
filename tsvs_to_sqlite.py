import sqlite3
import csv
import tqdm


class TsvDialect(csv.Dialect):
    delimiter = '\t'
    quotechar = None
    lineterminator = '\n'
    quoting = csv.QUOTE_NONE


db = sqlite3.connect('dependencies.db')
db.executescript('''
create table if not exists deps (srcpkg text, srcver text, type text, dstpkg text, dstver text);
create table if not exists pkgs (pkg text, ver text);
''')

with open('versions.tsv') as infp:
    db.executemany(
        'insert into pkgs (pkg, ver) values (?, ?)',
        tqdm.tqdm(csv.reader(infp, dialect=TsvDialect), desc='package versions'),
    )
db.commit()

with open('dependencies.tsv') as infp:
    db.executemany(
        'insert into deps (srcpkg, srcver, type, dstpkg, dstver) values (?, ?, ?, ?, ?)',
        tqdm.tqdm((l for l in csv.reader(infp, dialect=TsvDialect) if len(l) == 5), desc='package dependencies'),
    )
db.commit()
print('creating indexes...')
db.executescript('''
create index pkgs_pkg_ix on pkgs (pkg);
create index deps_srcpkg_ix on deps (srcpkg);
create index deps_dstpkg_ix on deps (dstpkg);
''')
print('done!')
