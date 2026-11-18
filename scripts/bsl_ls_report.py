#!/usr/bin/env python3
"""Run bsl-language-server over the CFE tree and save the raw JSON report.

Same workaround as scripts/bsl_ls_fulltree.py (CommonModules metadata XML is
relocated into the module dir in a throwaway copy), but this script persists
the bsl-json.json report so it can be diffed later by scripts/sonar_ls_diff.py.

Usage:
    python scripts/bsl_ls_report.py <cfe-dir> <out-json> [--targets]

--targets prints a per-file count of the wave-5 WONTFIX rules with their
current line numbers (fresh positions after previous edits).
"""
import argparse
import collections
import json
import os
import shutil
import subprocess
import sys
import tempfile

JAVA = os.path.expanduser("~/.pi/vendor/jdk-21.0.12.1+1/bin/java.exe")
JAR = os.path.expanduser("~/.pi/vendor/jars/bsl-language-server-1.0.7-exec.jar")

TARGET_RULES = [
    "MagicNumber", "MissingParameterDescription",
    "MissingReturnedValueDescription", "NestedFunctionInParameters", "Typo",
    "YoLetterUsage", "DuplicateStringLiteral", "LineLength", "CodeOutOfRegion",
    "NonStandardRegion", "IfElseIfEndsWithElse",
    "NumberOfValuesInStructureConstructor", "IfConditionComplexity",
    "CognitiveComplexity", "CommentedCode", "UnusedLocalVariable",
    "ConsecutiveEmptyLines", "DuplicatedInsertionIntoCollection",
]


def prepare_tree(src_dir, work_dir):
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src_dir")
    ap.add_argument("out_json")
    ap.add_argument("--targets", action="store_true")
    args = ap.parse_args()

    work_dir = tempfile.mkdtemp(prefix="bsl_rep_")
    rep_dir = os.path.join(work_dir, "rep")
    os.makedirs(rep_dir)
    prepare_tree(args.src_dir, work_dir)
    proc = subprocess.run(
        [JAVA, "-jar", JAR, "analyze", "-s", work_dir, "-o", rep_dir,
         "-r", "json", "-q"],
        capture_output=True, text=True, timeout=1800)
    report = os.path.join(rep_dir, "bsl-json.json")
    if not os.path.isfile(report):
        print("FATAL: no report (exit %d)" % proc.returncode)
        print(proc.stdout[-2000:], proc.stderr[-2000:])
        return 2
    data = json.load(open(report, encoding="utf-8"))
    infos = data.get("fileinfos", [])
    if not infos:
        print("FATAL: 0 files analyzed = check NOT performed")
        return 1

    out_dir = os.path.dirname(os.path.abspath(args.out_json))
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(report, args.out_json)

    total = 0
    per_rule = collections.Counter()
    rows = []
    for fi in infos:
        p = (fi.get("path") or "").replace("file:///", "").replace("\\", "/")
        short = p.split("/Тх_")[-1]
        for d in fi.get("diagnostics") or []:
            code = (d.get("code") or "").split(":")[-1]
            per_rule[code] += 1
            total += 1
            if args.targets and code in TARGET_RULES:
                line = d["range"]["start"]["line"] + 1
                msg = (d.get("message") or "").replace("\n", " ")[:150]
                rows.append((short, line, code, d.get("severity", ""), msg))

    print("[bsl-ls] files analyzed: %d, diagnostics: %d" % (len(infos), total))
    print("[bsl-ls] report saved: %s" % args.out_json)
    if args.targets:
        rows.sort(key=lambda r: (r[0], r[1], r[2]))
        for r in rows:
            print("L%-6d %-32s %-8s %s | %s" % (r[1], r[2], r[3], r[0][:34], r[4]))
        print("[targets] total: %d" % len(rows))
        print("[targets] by rule: %s" % dict(
            collections.Counter(r[2] for r in rows).most_common()))
    else:
        print("[bsl-ls] by rule: %s" % dict(per_rule.most_common(15)))
    shutil.rmtree(work_dir, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
