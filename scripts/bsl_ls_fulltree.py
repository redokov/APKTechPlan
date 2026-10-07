#!/usr/bin/env python3
"""Full-tree bsl-ls gate for a 1C CFE/XML source tree (Designer dump layout).

Why this exists: bsl-language-server 1.0.7 (MDClasses) locates common-module
metadata XML as CommonModules/<Name>/<Name>.xml, while the Designer 8.5 dump
layout (authoritative for LoadConfigFromFiles) is CommonModules/<Name>.xml
beside the <Name>/Ext/Module.bsl directory. When Configuration.xml is present,
the flags of such modules read as "all false" and the diagnostic
CommonModuleInvalidType fires as a false positive (2 errors per extension).

Workaround (no source changes): copy the tree to an ASCII temp dir, move
CommonModules/<Name>.xml into CommonModules/<Name>/, then run the analyzer.
The copy is throwaway; sources stay in the canonical Designer layout.

Usage:
    python scripts/bsl_ls_fulltree.py <path-to-cfe-dir> [--keep]

Exit code 0 iff: file count > 0 AND severity Error count == 0.
Prints every Error/Warning with full path (no lost attribution).
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

JAVA = os.path.expanduser("~/.pi/vendor/jdk-21.0.12.1+1/bin/java.exe")
JAR = os.path.expanduser("~/.pi/vendor/jars/bsl-language-server-1.0.7-exec.jar")

SEVERITY_RANK = {"Error": 0, "Warning": 1, "Information": 2, "Hint": 3}


def prepare_tree(src_dir: str, work_dir: str) -> int:
    """Copy tree; relocate CommonModules metadata XML into module dirs."""
    shutil.copytree(src_dir, work_dir, dirs_exist_ok=True)
    moved = 0
    cm_dir = os.path.join(work_dir, "CommonModules")
    if os.path.isdir(cm_dir):
        for entry in os.listdir(cm_dir):
            if not entry.endswith(".xml"):
                continue
            name = entry[:-4]
            target_dir = os.path.join(cm_dir, name)
            if os.path.isdir(target_dir):
                shutil.move(os.path.join(cm_dir, entry),
                            os.path.join(target_dir, entry))
                moved += 1
    return moved


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("src_dir")
    parser.add_argument("--keep", action="store_true",
                        help="keep the temp analysis copy for inspection")
    args = parser.parse_args()

    if not (os.path.isfile(JAVA) and os.path.isfile(JAR)):
        print("FATAL: bsl-ls jar or JDK not found under ~/.pi/vendor")
        return 2
    if not os.path.isdir(args.src_dir):
        print("FATAL: source dir not found: %s" % args.src_dir)
        return 2

    work_dir = tempfile.mkdtemp(prefix="bsl_fulltree_")
    rep_dir = os.path.join(work_dir, "rep")
    os.makedirs(rep_dir)
    moved = prepare_tree(args.src_dir, work_dir)
    if moved:
        print("[prep] moved %d CommonModules metadata XML(s) into module dirs"
              % moved)

    proc = subprocess.run(
        [JAVA, "-jar", JAR, "analyze", "-s", work_dir, "-o", rep_dir,
         "-r", "json", "-q"],
        capture_output=True, text=True, timeout=900)
    report = os.path.join(rep_dir, "bsl-json.json")
    if not os.path.isfile(report):
        print("FATAL: no report produced (jar exit %d)" % proc.returncode)
        print(proc.stdout[-2000:])
        print(proc.stderr[-2000:])
        return 2

    data = json.load(open(report, encoding="utf-8"))
    total_files = 0
    errors, warnings = [], []
    for fileinfo in data.get("fileinfos", []):
        diags = fileinfo.get("diagnostics", [])
        if diags:
            total_files += 1
        path = fileinfo.get("path", "").replace("file:///", "")
        for d in diags:
            line = d["range"]["start"]["line"] + 1
            item = (path, line, d.get("code"), d.get("message", ""))
            sev = d.get("severity", "Hint")
            if sev == "Error":
                errors.append(item)
            elif sev == "Warning":
                warnings.append(item)

    analyzed = len(data.get("fileinfos", []))
    print("[bsl-ls] analyzed files: %d (with diagnostics: %d)"
          % (analyzed, total_files))
    if analyzed == 0:
        print("GATE FAILED: 0 files analyzed = check NOT performed")
        return 1
    for path, line, code, message in errors:
        print("  Error %s:%d [%s] %s" % (path, line, code, message))
    for path, line, code, message in warnings:
        print("  Warning %s:%d [%s] %s" % (path, line, code, message))
    print("[bsl-ls] Errors: %d, Warnings: %d" % (len(errors), len(warnings)))
    if errors:
        print("GATE FAILED: %d Error(s)" % len(errors))
        rc = 1
    else:
        print("GATE PASSED: 0 Error")
        rc = 0

    if args.keep:
        print("[keep] analysis copy: %s" % work_dir)
    else:
        shutil.rmtree(work_dir, ignore_errors=True)
    return rc


if __name__ == "__main__":
    sys.exit(main())
