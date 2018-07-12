try:
    import ujson as json
except:
    import json
import tqdm
import os

input_filename = 'all_docs.jsonl'
versions_filename = 'versions.tsv'
deps_filename = 'dependencies.tsv'

key_to_kind_map = {
    'dependencies': 'dep',
    'devDependencies': 'dev',
    'peerDependencies': 'peer',
    'optionalDependencies': 'optional',
}

size = os.stat(input_filename).st_size
bytes_read = 0
pkgs_seen = set()
with tqdm.tqdm(total=size, unit='Byte', unit_scale=True) as prog:
    with \
        open(input_filename) as jsonl_fp, \
        open(deps_filename, 'a') as deps_fp, \
        open(versions_filename, 'a') as versions_fp:
        for doc_line in jsonl_fp:
            bytes_read += len(doc_line)
            doc = json.loads(doc_line)['doc']
            pkg_name = doc.get('name')
            if not pkg_name:
                continue
            if pkg_name in pkgs_seen:
                continue
            pkgs_seen.add(pkg_name)
            for version in doc['versions'].values():
                vname = version.get('name')
                vver = version.get('version')
                versions_fp.write(f'{vname}\t{vver}\n')
                for key, kind in key_to_kind_map.items():
                    src = version.get(key)
                    if isinstance(src, dict):
                        for dep_package, dep_ver in sorted(src.items()):
                            deps_fp.write(f'{vname}\t{vver}\t{kind}\t{dep_package}\t{dep_ver}\n')

            if len(pkgs_seen) % 100 == 0:
                prog.update(bytes_read - prog.n)
