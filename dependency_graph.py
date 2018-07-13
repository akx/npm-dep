from collections import defaultdict
import argparse

from dep_db_utils import print_adjacency, get_pkg_dependencies, get_best_pkg_version_matching


def get_dependency_graph(package, version):
    nodes = {(package, version)}
    graph = defaultdict(set)

    while nodes:
        pkg, ver = node = nodes.pop()
        if node in graph:
            continue
        deps = get_pkg_dependencies(pkg, ver)
        for dep in deps:
            dpkg, drange = dep
            resolved = get_best_pkg_version_matching(dpkg, drange)
            if resolved:
                dnode = (dpkg, resolved)
                graph[node].add(dnode)
                if dnode not in graph:  # Not seen yet?
                    nodes.add(dnode)
            else:
                print(node, dep, 'not resolved')
    return graph


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('package')
    ap.add_argument('version')
    args = ap.parse_args()
    graph = get_dependency_graph(args.package, args.version)
    print_adjacency(graph)
