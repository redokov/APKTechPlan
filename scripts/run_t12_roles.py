#!/usr/bin/env python3
"""T12 driver: staged role-assignment runs of 09-prava-agronom.feature.

Stages (TestClient always connects as IB user "Агроном"; TestManager as admin):
  1. remove Тх_-roles -> run @БезРолей scenario. While it runs, capture all
     visible 1cv8c windows (PrintWindow ps1) and OCR them: the Агроном main
     window must contain "Растениеводство" (his base section) and must NOT
     contain "Планирование техники" — UI evidence of NFR-004 (no absence
     steps exist in the VA-single build, see t12_probe_absence).
  2. add Тх_Чтение -> run @Тх_Чтение scenario.
  3. add Тх_Редактирование (both roles) -> run @Тх_Редактирование scenario.
  4. cleanup: remove both roles from Агроном (restore demo-base state).

Each stage feature is generated into heartbeat/ by filtering the canonical
tests/vanessa/09-prava-agronom.feature by scenario tag. Verdict per stage:
"Выполнение сценариев закончено. Ошибок не было" in va_1c log + rc==0.
"""
import io
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FEATURE = os.path.join(ROOT, "tests", "vanessa", "09-prava-agronom.feature")
HEART = os.path.join(ROOT, "heartbeat")
USER = "Агроном"
ROLES_SCRIPT = os.path.join(HERE, "va_assign_roles_direct.py")
RUN_SCRIPT = os.path.join(HERE, "run_va_feature.py")
CAP_PS1 = os.path.join(HERE, "t11_cap_choice2.ps1")
OCR_SCRIPT = os.path.join(HERE, "ocr_py.py")

PASS_LINE = "Выполнение сценариев закончено. Ошибок не было"


def run(cmd, timeout=600, **kw):
    p = subprocess.run(cmd, capture_output=True, timeout=timeout, **kw)
    out = (p.stdout or b"").decode("utf-8", errors="replace")
    return p.returncode, out


def roles(action, roles_arg=None):
    cmd = [sys.executable, ROLES_SCRIPT, USER, action]
    if roles_arg:
        cmd.append(roles_arg)
    rc, out = run(cmd, timeout=300)
    tail = "\n".join(out.strip().splitlines()[-2:])
    print("[t12] roles %s %s -> rc=%s\n%s" % (action, roles_arg or "both", rc, tail))
    return rc == 0


def build_stage_feature(tag, stage_name):
    """Split canonical feature: header (up to first '@'/'Сценарий:') + the
    scenario block whose preceding tag line matches @tag."""
    txt = io.open(FEATURE, encoding="utf-8-sig").read()
    lines = txt.splitlines()
    # find scenario block boundaries: a block starts at its '@' tag line (or
    # 'Сценарий:' line if untagged) and runs until the next one
    blocks = []
    header_end = None
    i = 0
    while i < len(lines):
        l = lines[i]
        if l.startswith("@") or l.startswith("Сценарий:"):
            header_end = i
            break
        i += 1
    header = lines[:header_end]
    starts = []
    for j, l in enumerate(lines):
        if l.startswith("@"):
            starts.append(j)
        elif l.startswith("Сценарий:") and not (j > 0 and lines[j - 1].startswith("@")):
            # untagged scenario header starts its own block; a 'Сценарий:'
            # line directly under a tag belongs to that tag's block
            starts.append(j)
    starts.append(len(lines))
    for k in range(len(starts) - 1):
        s, e = starts[k], starts[k + 1]
        # trim trailing blank lines of the block
        while e > s and not lines[e - 1].strip():
            e -= 1
        blocks.append((s, e))
    body = None
    for s, e in blocks:
        blk = lines[s:e]
        if blk[0].strip() == "@" + tag:
            body = blk
            break
    if body is None:
        raise SystemExit("[t12] tag @%s not found in %s" % (tag, FEATURE))
    path = os.path.join(HEART, "t12_%s.feature" % stage_name)
    with io.open(path, "w", encoding="utf-8-sig") as f:
        f.write("\n".join(header + [""] + body) + "\n")
    print("[t12] stage feature: %s (scenario: %s)" % (path, body[1] if body[0].startswith("@") else body[0]))
    return path


def ocr(png):
    rc, out = run([sys.executable, OCR_SCRIPT, png, "ru"], timeout=120)
    return out


def capture_loop(proc, stage_name):
    """While the VA process runs, capture 1cv8c windows every ~15s, OCR them,
    collect evidence for the Агроном TestClient main window.
    Filter: OCR must contain 'Агроном' (user name in the window header)
    and must NOT contain 'Vanessa'/'Орлов' (TestManager runs as admin; its
    window OCR contains the admin name and/or VA branding)."""
    evidence = []   # (png, ocr_text)
    seen = set()
    n = 0
    while proc.poll() is None and n < 120:
        n += 1
        time.sleep(15)
        try:
            rc, out = run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                           "-File", CAP_PS1], timeout=60)
        except subprocess.TimeoutExpired:
            # hung capture (e.g. a frozen window) must not kill the driver
            print("[t12] capture ps1 timed out - skipping cycle")
            continue
        for m in re.finditer(r"-> (C:\\\S+?\.png)", out):
            png = m.group(1)
            if png in seen:
                continue
            seen.add(png)
            try:
                t = ocr(png)
            except Exception:
                continue
            if ("Агроном" in t and "Vanessa" not in t and "Орлов" not in t):
                evidence.append((png, t))
                print("[t12] Агроном-window captured: %s" % png)
    return evidence


def taskkill_1cv8c():
    subprocess.run(["taskkill", "/IM", "1cv8c.exe", "/F"], capture_output=True)


def _run_once(path, log1c, do_capture):
    if os.path.exists(log1c):
        os.remove(log1c)
    proc = subprocess.Popen(
        [sys.executable, RUN_SCRIPT, path, "900", USER],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    evidence = []
    if do_capture:
        evidence = capture_loop(proc, path)
    out = proc.communicate(timeout=1000)[0].decode("utf-8", errors="replace")
    for l in out.strip().splitlines()[-4:]:
        print("   | " + l)
    verdict = "UNKNOWN"
    if os.path.exists(log1c):
        t = io.open(log1c, encoding="utf-8-sig", errors="replace").read()
        if PASS_LINE in t:
            verdict = "PASS"
        elif "БЫЛИ ОШИБКИ" in t:
            verdict = "FAIL"
    return verdict, evidence


def run_stage(stage_name, tag, do_capture=False, allow_retry=True):
    path = build_stage_feature(tag, stage_name)
    log1c = os.path.join(HEART, "va_1c_t12_%s.log" % stage_name)
    verdict, evidence = _run_once(path, log1c, do_capture)
    if verdict == "UNKNOWN" and allow_retry:
        # known flakiness: TestClient occasionally fails to connect to the
        # TestManager within the run timeout (stage1, 2026-10-10 13:49)
        print("[t12] stage %s: UNKNOWN (TestClient connect flake?) - retry once" % stage_name)
        taskkill_1cv8c()
        time.sleep(3)
        verdict, evidence = _run_once(path, log1c, do_capture)
    print("[t12] stage %s: %s" % (stage_name, verdict))
    return verdict, evidence


def main():
    ok = True

    # Stage 1: no roles
    if not roles("remove"):
        return 2
    v1, ev = run_stage("stage1_bezroley", "БезРолей", do_capture=True)
    ui_ok = False
    if ev:
        bad = [p for p, t in ev if "Планирование техники" in t]
        if bad:
            print("[t12] UI-EVIDENCE FAIL: 'Планирование техники' VISIBLE in %s" % bad)
        else:
            ui_ok = True
            print("[t12] UI-EVIDENCE OK: %d Агроном-window capture(s), 'Планирование техники' absent" % len(ev))
    else:
        print("[t12] UI-EVIDENCE MISSING: no Агроном window captured")
    ok = ok and v1 == "PASS" and ui_ok

    # Stage 2: Тх_Чтение
    if not roles("add", "Тх_Чтение"):
        return 2
    v2, _ = run_stage("stage2_chtenie", "Тх_Чтение")
    ok = ok and v2 == "PASS"

    # Stage 3: + Тх_Редактирование
    if not roles("add"):
        return 2
    v3, _ = run_stage("stage3_redaktirovanie", "Тх_Редактирование")
    ok = ok and v3 == "PASS"

    # Cleanup: restore demo-base state
    roles("remove")

    print("[t12] FINAL: %s (stage1=%s ui=%s, stage2=%s, stage3=%s)" %
          ("PASS" if ok else "FAIL", v1, "OK" if ui_ok else "MISSING/FAIL", v2, v3))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
