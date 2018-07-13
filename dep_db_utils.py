import sqlite3
from functools import lru_cache
import nsemver

BOUNDED_CACHE_SIZE = 2048

db = sqlite3.connect('dependencies.db')


def get_cursor():
    return db.cursor()


@lru_cache(maxsize=BOUNDED_CACHE_SIZE)
def get_pkg_versions(pkg):
    c = db.cursor()
    c.execute("select ver from pkgs where pkg = ?", [pkg])
    return frozenset(r[0] for r in c)


@lru_cache(maxsize=BOUNDED_CACHE_SIZE)
def get_pkgs_depending_on_any_version_of(pkg, type='dep'):
    c = db.cursor()
    c.execute("select srcpkg, srcver, dstver from deps where dstpkg = ? AND type = ?", [pkg, type])
    return frozenset(c)


_semver_satisfy_cache = {}


@lru_cache(maxsize=None)
def semver_satisfies(version, range):
    cache_key = (version, range)

    if not range:  # Any version?
        return True

    if range.startswith('git'):
        return False

    if range.startswith('file:'):
        return False

    if version == range:
        return True

    if '-' in version and '-' not in range:  # Prereleases can't be satisfied by non-prerelease ranges
        return False

    if range[0].isdigit() and version[0] != range[0] and '|' not in range:  # Quick numeric comparison
        return False

    ret = slow_semver_satisfies(version, range)
    #ci = semver_satisfies.cache_info()
    #hit_ratio = ((ci.hits / (ci.hits + ci.misses) if ci.hits else 0))
    #print('Slow:', version, range, '->', ret, '%.2f%%' % (hit_ratio * 100))
    return ret


def slow_semver_satisfies(version, range):
    try:
        return nsemver.satisfies(version, range)
    except Exception as exc:
        print(range, ':', exc)
        return False


def get_pkgs_depending_on(pkg, ver, type='dep'):
    out = []
    for srcpkg, srcver, dst_range in get_pkgs_depending_on_any_version_of(pkg, type):
        if semver_satisfies(ver, dst_range):
            out.append((srcpkg, srcver))
    return out


@lru_cache(maxsize=BOUNDED_CACHE_SIZE)
def get_pkg_dependencies(pkg, ver, type='dep'):
    c = db.cursor()
    c.execute("select dstpkg, dstver from deps where srcpkg = ? AND srcver = ? AND type = ?", [pkg, ver, type])
    return frozenset(c)


@lru_cache()
def get_best_pkg_version_matching(pkg, range):
    versions = get_pkg_versions(pkg)
    if range == 'latest':
        range = '*'
    return nsemver.max_satisfying(versions, range, loose=True)
    # matching_versions = [version for version in versions if semver_satisfies(version, range)]
    # return (max(matching_versions, key=nsemver.comparator()Version) if matching_versions else None)


def print_adjacency(graph):
    for (srcpkg, srcver), destnodes in sorted(graph.items()):
        for (destpkg, destver) in destnodes:
            print(f'{srcpkg}@{srcver};{destpkg}@{destver}')
