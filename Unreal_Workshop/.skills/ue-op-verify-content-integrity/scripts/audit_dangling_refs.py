#!/usr/bin/env python3
"""Classify every dangling /Game/ path in a project's content.

Unreal never prunes stale name-table entries, so a .uasset keeps the old path string
long after the reference it belonged to was correctly rewritten. Grepping binaries for
old paths therefore produces false positives, and "fix every hit" corrupts healthy files.

This script splits the hits into the two kinds that matter:

  name-table leftover  the corrected path is ALSO present in the same file, so the
                       reference was rewritten and the old string is inert. Harmless.
  live broken          no corrected path exists. This one needs a decision.
  unmapped             dangling, and no prefix mapping covers it -- typically content
                       from another Epic template that this project never had.

Usage:
    python audit_dangling_refs.py <ContentRoot> [mappingFile]

mappingFile holds one "oldprefix=newprefix" pair per line, e.g.
    /Game/Characters=/Game/ContentPack/Characters

Exit code 0 always; the report is the output.
"""

import os
import re
import sys
import collections

PATH_RE = re.compile(rb'/Game/(?:[A-Za-z0-9_]+/)+[A-Za-z0-9_]+(?:\.[A-Za-z0-9_]+)*')


def package_of(path_string):
    """'/Game/A/B.Obj' -> '/Game/A/B'.  A UE package name never contains a dot."""
    tail = path_string.rsplit('/', 1)[-1]
    if '.' in tail:
        return path_string[:-(len(tail) - tail.index('.'))]
    return path_string


def load_mapping(path):
    pairs = []
    if not path:
        return pairs
    with open(path, 'r', encoding='utf-8') as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            old, new = line.split('=', 1)
            pairs.append((old.strip(), new.strip()))
    return pairs


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    root = os.path.abspath(sys.argv[1])
    mapping = load_mapping(sys.argv[2] if len(sys.argv) > 2 else None)
    sep = os.sep

    existing = set()
    for dp, _dn, fn in os.walk(root):
        for f in fn:
            if f.endswith(('.uasset', '.umap')):
                rel = os.path.relpath(os.path.join(dp, f), root).replace(sep, '/')
                existing.add('/Game/' + rel.rsplit('.', 1)[0])

    leftovers = collections.defaultdict(set)
    live = collections.defaultdict(set)
    unmapped = collections.defaultdict(set)

    for dp, _dn, fn in os.walk(root):
        for f in fn:
            if not f.endswith(('.uasset', '.umap')):
                continue
            path = os.path.join(dp, f)
            with open(path, 'rb') as fh:
                data = fh.read()
            rel = os.path.relpath(path, root).replace(sep, '/')

            for match in set(PATH_RE.findall(data)):
                pkg = package_of(match.decode('ascii', 'ignore'))
                if pkg in existing or pkg.startswith('/Game/__External'):
                    continue

                corrected = None
                for old, new in mapping:
                    if pkg.startswith(old):
                        corrected = new + pkg[len(old):]
                        break

                if corrected and corrected in existing and corrected.encode('ascii') in data:
                    leftovers[pkg].add(rel)
                elif corrected:
                    live[pkg].add(rel)
                else:
                    unmapped[pkg].add(rel)

    def dump(title, table):
        print("\n=== %s (%d) ===" % (title, len(table)))
        for pkg in sorted(table):
            print("  " + pkg)
            for holder in sorted(table[pkg]):
                print("       <- " + holder)

    dump("LIVE BROKEN  (dangling, no valid target)", live)
    dump("UNMAPPED    (dangling, no prefix mapping -- usually another Epic template)", unmapped)
    dump("NAME-TABLE LEFTOVERS  (harmless -- the reference was rewritten)", leftovers)

    print("\nSUMMARY  live_broken=%d  unmapped=%d  name_table_leftovers=%d"
          % (len(live), len(unmapped), len(leftovers)))
    print("Only the LIVE BROKEN list is work. The others are inert strings.")


if __name__ == '__main__':
    main()
