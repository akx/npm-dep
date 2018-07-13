import argparse
from collections import defaultdict

import tqdm

from dep_db_utils import get_pkgs_depending_on, print_adjacency


def get_dependent_graph(package, version, ignore_prerelease=False):
    nodes = {(package, version)}
    graph = defaultdict(set)

    with tqdm.tqdm(unit='pkg', unit_scale=1) as pbar:
        while nodes:
            pkg, ver = node = nodes.pop()
            if node in graph:
                continue
            dependents = get_pkgs_depending_on(pkg, ver)
            for dep in dependents:
                graph[node].add(dep)
                if not (ignore_prerelease and '-' in dep[1]):
                    nodes.add(dep)
            pbar.total = len(nodes) + len(graph)
            pbar.n = len(graph)
            pbar.set_description(f'{node[0]}@{node[1]}'.ljust(40)[:40])
    return graph


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('package')
    ap.add_argument('version')
    ap.add_argument('--ignore-prerelease', action='store_true')
    args = ap.parse_args()
    graph = get_dependent_graph(args.package, args.version, ignore_prerelease=args.ignore_prerelease)
    print_adjacency(graph)
