#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""bsl-ls diagnostics for ONE .bsl file (fast local gate, no tree copy).

Usage:
  python scripts/bsl_ls_file.py <file.bsl> [--rules R1,R2,...] [--json out.json]

Prints: per-rule counts (all rules), then a detail list for --rules (or all
if --rules is omitted and there are <=60 diagnostics).
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("--rules", default="")
    ap.add_argument("--json", default="")
    a = ap.parse_args()

    work = tempfile.mkdtemp(prefix="bsl_one_")
    shutil.copyfile(a.src, os.path.join(work, "mod.bsl"))
    rep = os.path.join(work, "rep")
    os.makedirs(rep)
    subprocess.run([JAVA, "-jar", JAR, "analyze", "-s", work, "-o", rep,
                    "-r", "json", "-q"], capture_output=True, text=True,
                   timeout=600)
    path = os.path.join(rep, "bsl-json.json")
    if not os.path.isfile(path):
        print("FATAL: no report")
        return 2
    data = json.load(open(path, encoding="utf-8"))
    if a.json:
        shutil.copyfile(path, a.json)
    diags = []
    for fi in data.get("fileinfos") or []:
        for d in fi.get("diagnostics") or []:
            diags.append(d)
    if not data.get("fileinfos"):
        print("FATAL: 0 files analyzed = check NOT performed")
        return 1
    counts = collections.Counter((d.get("code") or "").split(":")[-1] for d in diags)
    print("diags=%d" % len(diags))
    for rule, n in counts.most_common():
        print("  %-36s %d" % (rule, n))
    rules = set(x.strip() for x in a.rules.split(",") if x.strip())
    show = [d for d in diags if not rules or (d.get("code") or "").split(":")[-1] in rules]
    if show:
        print("--- details ---")
        for d in sorted(show, key=lambda x: x["range"]["start"]["line"]):
            print("L%-6d [%-34s] %s" % (
                d["range"]["start"]["line"] + 1,
                (d.get("code") or "").split(":")[-1],
                (d.get("message") or "").replace("\n", " ")[:150]))

    shutil.rmtree(work, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
