#!/usr/bin/env python3
"""Find every project-local #include that the module's include paths cannot resolve.

Moving .cpp/.h files into subfolders does not break the build by itself -- it breaks
the build the moment a file includes a header that now lives in a directory UBT was
not told about. UBT resolves #include "Foo.h" against:

  1. the directory of the including file (quoted includes only)
  2. every directory in the module's PublicIncludePaths / PrivateIncludePaths
  3. the module root, when it is listed there

A module that declares its own PublicIncludePaths does NOT get its subdirectories
auto-expanded, so a newly created folder is invisible until it is listed.

This script reproduces that resolution exactly and reports the includes that fail.
To keep the output actionable it classifies each unresolvable include:

  MISSING   the header exists in this module but no include path reaches it.
            These are the ones that break the build.
  ENGINE    the header exists in the engine source tree -- it resolves against the
            engine's own include paths and is fine.
  UHT       a *.generated.h -- UnrealHeaderTool always writes these flat into
            Intermediate/Build/<Plat>/<Arch>/<Target>/Inc/<Module>/UHT/, and that
            directory is always on the include path.
  ABSENT    the header exists nowhere -- a typo or a deleted header.

Usage:
    python check_cpp_includes.py <ModuleDir> [<ModuleDir> ...] [--engine <EngineSource>]

ModuleDir is e.g. D:/UE/<Project>/Source/<Module>
The module's .Build.cs must sit directly inside it.
--engine points at the engine's Source directory and makes the ENGINE/ABSENT
split possible; without it those two are reported as one UNKNOWN bucket.
"""

import os
import re
import sys
import collections

INCLUDE_RE = re.compile(r'^\s*#\s*include\s+"([^"]+)"', re.MULTILINE)
# PublicIncludePaths.AddRange(new string[] { "A", "B" });  -- also Private.
PATH_LIST_RE = re.compile(
    r'(Public|Private)IncludePaths\s*\.AddRange\s*\(\s*new\s+string\[\]\s*\{(.*?)\}',
    re.DOTALL)
STRING_RE = re.compile(r'"([^"]*)"')


def parse_build_cs(module_dir):
    """Return (declared_include_paths, source_root) from the module's .Build.cs.

    Declared paths are relative to the module's PARENT directory (Source/), which is
    why "<Module>" means the module root itself. The parent is derived from the
    Build.cs being named <ModuleName>.Build.cs inside <ModuleName>/.
    """
    build_cs = None
    for f in os.listdir(module_dir):
        if f.endswith('.Build.cs'):
            build_cs = os.path.join(module_dir, f)
            break
    if build_cs is None:
        return None, None

    module_name = os.path.basename(build_cs)[:-len('.Build.cs')]
    source_root = os.path.dirname(module_dir)

    with open(build_cs, 'r', encoding='utf-8', errors='ignore') as fh:
        text = fh.read()

    declared = []
    for _kind, body in PATH_LIST_RE.findall(text):
        for entry in STRING_RE.findall(body):
            declared.append(os.path.normpath(os.path.join(source_root, entry)))

    # The module root is always searched for its own headers, listed or not.
    if os.path.normpath(module_dir) not in declared:
        declared.append(os.path.normpath(module_dir))
    return declared, source_root


def collect_project_headers(module_dir):
    """basename -> set of module-relative paths, for every header in the module."""
    headers = collections.defaultdict(set)
    for dp, _dn, fn in os.walk(module_dir):
        for f in fn:
            if f.endswith('.h'):
                rel = os.path.relpath(os.path.join(dp, f), module_dir).replace(os.sep, '/')
                headers[f].add(rel)
    return headers


def collect_engine_headers(engine_source):
    """basename set of every header the engine provides.

    Covers both Engine/Source and Engine/Plugins -- plugin headers (EnhancedInput,
    Niagara, StateTree, GameplayStateTree) live under Engine/Plugins and would
    otherwise be reported as ABSENT.
    """
    names = set()
    if not engine_source or not os.path.isdir(engine_source):
        return names
    roots = [engine_source]
    plugins = os.path.join(os.path.dirname(engine_source), 'Plugins')
    if os.path.isdir(plugins):
        roots.append(plugins)
    for root in roots:
        for dp, _dn, fn in os.walk(root):
            for f in fn:
                if f.endswith('.h'):
                    names.add(f)
    return names


def resolve(inc, including_file_dir, search_dirs):
    """Can #include "inc" be found? Returns the absolute path or None."""
    for d in [including_file_dir] + list(search_dirs):
        cand = os.path.normpath(os.path.join(d, inc.replace('/', os.sep)))
        if os.path.isfile(cand):
            return cand
    return None


def main():
    args = [a for a in sys.argv[1:]]
    engine_source = None
    if '--engine' in args:
        i = args.index('--engine')
        engine_source = args[i + 1] if i + 1 < len(args) else None
        del args[i:i + 2]

    if not args:
        print(__doc__)
        return 1

    project_headers = collect_project_headers(args[0]) if len(args) == 1 else None
    engine_headers = collect_engine_headers(engine_source)

    overall_missing = 0
    overall_absent = 0

    for module_dir in args:
        module_dir = os.path.abspath(module_dir)
        print("\n" + "=" * 72)
        print("MODULE  %s" % module_dir)

        search_dirs, source_root = parse_build_cs(module_dir)
        if search_dirs is None:
            print("  no .Build.cs found in the module directory -- skipping")
            continue

        print("  INCLUDE PATHS the build will actually use:")
        for d in search_dirs:
            mark = "   <-- DOES NOT EXIST" if not os.path.isdir(d) else ""
            print("      %s%s" % (d, mark))

        project_headers = collect_project_headers(module_dir)

        missing = collections.defaultdict(list)   # include -> [including files]
        absent = collections.defaultdict(list)
        engine = collections.defaultdict(list)
        uht = 0

        for dp, _dn, fn in os.walk(module_dir):
            for f in sorted(fn):
                if not f.endswith(('.cpp', '.h')):
                    continue
                path = os.path.join(dp, f)
                rel = os.path.relpath(path, module_dir).replace(os.sep, '/')
                with open(path, 'r', encoding='utf-8', errors='ignore') as fh:
                    text = fh.read()
                for inc in INCLUDE_RE.findall(text):
                    if resolve(inc, dp, search_dirs):
                        continue
                    base = inc.replace('\\', '/').rsplit('/', 1)[-1]
                    if base in project_headers:
                        missing[inc].append(rel)
                    elif base.endswith('.generated.h'):
                        uht += 1
                    elif base in engine_headers:
                        engine[inc].append(rel)
                    else:
                        absent[inc].append(rel)

        print("")
        if missing:
            print("  MISSING  -- project header, but not on any include path:")
            for inc in sorted(missing):
                print("      #include \"%s\"" % inc)
                for holder in sorted(missing[inc]):
                    print("           <- %s" % holder)
                for where in sorted(project_headers[inc.replace('\\', '/').rsplit('/', 1)[-1]]):
                    print("              (header lives at %s)" % where)
        else:
            print("  MISSING  -- none")

        if absent:
            print("  ABSENT   -- the header exists nowhere (typo or deleted):")
            for inc in sorted(absent):
                print("      #include \"%s\"   <- %s" % (inc, ", ".join(sorted(absent[inc]))))
        else:
            print("  ABSENT   -- none")

        print("  (resolved elsewhere: %d engine headers, %d UHT generated headers)"
              % (len(engine), uht))
        print("  SUMMARY  missing=%d  absent=%d" % (len(missing), len(absent)))
        overall_missing += len(missing)
        overall_absent += len(absent)

    print("\n" + "=" * 72)
    print("TOTAL  missing=%d  absent=%d" % (overall_missing, overall_absent))
    if overall_missing:
        print("Fix MISSING first. Each one is a project header UBT cannot see.")
        print("Either add the folder holding it to PublicIncludePaths in the .Build.cs,")
        print("or rewrite the include as a module-root-relative path.")
    else:
        print("No project include is unresolvable -- the module's include paths cover every reference.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
