#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B6: run one Vanessa Automation feature file via TestManager + TestClient.

Pattern from the vanessa-automation skill:
  - 1cv8c (thin client) ENTERPRISE /TESTMANAGER
  - /S localhost\\dev_erpapk_demo, user with empty password (/P "")
  - /Execute vanessa-automation-single.epf
  - /CStartFeaturePlayer;VAParams=<json>   (VAParams generated per run)
  - verdict is read from TWO artifacts, machine-readable first:
      1) va_status_<stem>.log -- Vanessa "ВыгружатьСтатусВыполненияСценариев"
         artifact: BOM + error count as plain digits ("0" = no errors).
      2) va_1c_<stem>.log -- 1C /Out log line
         "Выполнение сценариев закончено. Ошибок не было." / "... БЫЛИ ОШИБКИ."
  - parsing is STRICT (line-scoped, fail-closed): inconclusive or
    contradictory artifacts yield UNKNOWN, never a guessed PASS.
  - process exit code is NOT a verdict (always 0)

Offline self-test (no COM/Vanessa/IB is launched):
  python scripts/run_va_feature.py --selftest

Usage: python scripts/run_va_feature.py <feature-file> [timeout_sec]
"""
import io
import json
import os
import re
import subprocess
import sys
import time

V8C = r"C:\Program Files\1cv8\8.5.4.2028\bin\1cv8c.exe"
EPF = os.environ.get(
    "VA_EPF",
    r"C:\Program Files\OneScript\lib\vanessa-automation-single\vanessa-automation-single.epf",
)
USER = "Администратор (ОрловАВ)"
BASE = r"localhost\dev_erpapk_demo"
LOGDIR = r"C:\MyProjects\APKTechPlan\heartbeat"

# Verdict vocabulary. SKIP is deliberately NOT produced by this runner:
# the SKIP terminal policy is unresolved (spec-003 Q-007) and VA features
# carry no machine-readable SKIP artifact. Anything not provably PASS or
# FAIL is reported as UNKNOWN (fail-closed, exit 1).
VERDICTS = ("PASS", "FAIL", "UNKNOWN")

# Line-scoped, strict sentence forms (must sit inside ONE log line;
# trailing period optional, no timestamp anchor assumed).
_VERDICT_RE = re.compile(
    u"Выполнение сценариев закончено\\.\\s+(Ошибок не было|БЫЛИ ОШИБКИ)\\s*\\.?\\s*$")

ROLES_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "va_assign_roles_direct.py")


def ensure_roles():
    """BSP access-management periodically rewrites IB-user roles from access
    groups and wipes manually assigned Tх_ roles (B6 finding: profile roles
    reference the extension-identifiers catalog which is never populated in
    this demo base). Restore the roles right before each run (idempotent)."""
    print("[va] ensuring Tх_ roles on IB user")
    p = subprocess.run(
        [sys.executable, ROLES_SCRIPT, USER, "add"],
        capture_output=True, timeout=300)
    tail = (p.stdout or b"")[-200:].decode("utf-8", errors="replace")
    print("[va] ensure_roles rc=%s %s" % (p.returncode, tail.strip()))
    return p.returncode == 0


# ---------------------------------------------------------------------------
# Strict verdict parsing (shared by run_all_va.py; unit-tested offline).
# ---------------------------------------------------------------------------

def decode_artifact(raw):
    """Decode artifact bytes: utf-8-sig -> utf-8 -> cp1251 -> utf-8/replace."""
    for enc in ("utf-8-sig", "utf-8", "cp1251"):
        try:
            return raw.decode(enc), enc
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace"), "utf-8/replace"


def status_verdict(raw):
    """Parse the machine-readable VA status artifact (error count).

    Observed on-disk format (2026-11-07 artifacts): UTF-8 BOM + ASCII digits.
    "0" -> PASS (paired with 'Ошибок не было' in every existing artifact);
    any other non-negative integer -> FAIL (fail-closed);
    anything else (empty, non-numeric) -> None (not parseable).
    """
    if raw is None:
        return None
    txt = raw
    if isinstance(txt, bytes):
        if txt.startswith(b"\xef\xbb\xbf"):
            txt = txt[3:]
        txt = txt.decode("ascii", errors="replace")
    txt = txt.strip()
    if not txt:
        return None
    if not txt.isdigit():
        return None
    return "PASS" if txt == "0" else "FAIL"


def log_verdict(text):
    """Strict line-scoped verdict from the 1C /Out log text.

    Returns "PASS"/"FAIL" only when exactly one verdict sentence matches;
    no match, truncated fragments, or both sentences -> None (unresolved).
    Loose substrings ('Ошибок не было' anywhere) are intentionally rejected.
    """
    if not text:
        return None
    seen = set()
    for line in text.splitlines():
        m = _VERDICT_RE.search(line.strip())
        if m:
            seen.add("PASS" if m.group(1) == u"Ошибок не было" else "FAIL")
    if len(seen) == 1:
        return seen.pop()
    return None  # empty, ambiguous, or fragment-only


def verdict_from_files(onec_log, status_log):
    """Combine both artifacts into a strict verdict.

    Precedence: the machine-readable status artifact is authoritative unless
    the 1C log explicitly contradicts it (then UNKNOWN, fail-closed).
    If the status artifact is missing/unparseable, the log verdict is used.

    Returns (verdict, source, note); verdict in VERDICTS.
    """
    st_raw = None
    if status_log and os.path.exists(status_log):
        with io.open(status_log, "rb") as f:
            st_raw = f.read()
    st = status_verdict(st_raw)

    log_txt = None
    if onec_log and os.path.exists(onec_log):
        raw = open(onec_log, "rb").read()
        log_txt, _enc = decode_artifact(raw)
    lv = log_verdict(log_txt)

    if st is not None and lv is not None and st != lv:
        return "UNKNOWN", "conflict", (
            "status artifact says %s but 1C log says %s" % (st, lv))
    if st is not None:
        return st, "status-artifact", ""
    if lv is not None:
        return lv, "1c-log", ""
    if log_txt is not None and log_txt.strip():
        first = log_txt.strip().splitlines()[0][:180]
        return "UNKNOWN", "none", first
    return "UNKNOWN", "none", "no conclusive verdict artifact"


# ---------------------------------------------------------------------------
# Offline fixtures / self-test (strict machine-readable artifact handling).
# ---------------------------------------------------------------------------

_PASS_LINE = u"07.11.2026 16:27:32 Выполнение сценариев закончено. Ошибок не было."
_FAIL_LINE = u"07.11.2026 16:27:32 Выполнение сценариев закончено. БЫЛИ ОШИБКИ."


def _selftest():
    import shutil
    import tempfile

    tmp = tempfile.mkdtemp(prefix="va_verdict_")
    cases = []  # (name, status_bytes|None, log_bytes|None, enc, expected, exp_source)

    def add(name, st, log, expected, source):
        cases.append((name, st, log, expected, source))

    add("status0+log_pass", b"\xef\xbb\xbf0", _PASS_LINE.encode("utf-8-sig"),
        "PASS", "status-artifact")
    add("status2+log_fail", b"\xef\xbb\xbf2", _FAIL_LINE.encode("utf-8-sig"),
        "FAIL", "status-artifact")
    add("status_pass_vs_log_fail_conflict", b"\xef\xbb\xbf0",
        _FAIL_LINE.encode("utf-8-sig"), "UNKNOWN", "conflict")
    add("status_fail_vs_log_pass_conflict", b"\xef\xbb\xbf7",
        _PASS_LINE.encode("utf-8-sig"), "UNKNOWN", "conflict")
    add("status_garbage_log_pass", b"\xef\xbb\xbf???", _PASS_LINE.encode("utf-8-sig"),
        "PASS", "1c-log")
    add("no_status_cp1251_log_fail", None, _FAIL_LINE.encode("cp1251"),
        "FAIL", "1c-log")
    add("truncated_fragment_is_unknown", None,
        u"07.11.2026 16:27:32 ... Ошибок не было".encode("utf-8-sig"),
        "UNKNOWN", "none")
    add("log_both_sentences_unknown", None,
        (_PASS_LINE + u"\r\n" + _FAIL_LINE).encode("utf-8-sig"),
        "UNKNOWN", "none")
    add("no_artifacts", None, None, "UNKNOWN", "none")
    add("status0_only_empty_log", b"\xef\xbb\xbf0", b"", "PASS", "status-artifact")
    add("empty_status_no_sentence", b"", _PASS_LINE.encode("utf-8-sig"),
        "PASS", "1c-log")
    add("no_period_log_pass", None,
        u"07.11.2026 16:27:32 Выполнение сценариев закончено. Ошибок не было".encode("utf-8-sig"),
        "PASS", "1c-log")

    failures = []
    try:
        for i, (name, st_bytes, log_bytes, expected, exp_source) in enumerate(cases):
            st_path = os.path.join(tmp, "st_%02d.log" % i)
            log_path = os.path.join(tmp, "log_%02d.log" % i)
            if st_bytes is not None:
                with io.open(st_path, "wb") as f:
                    f.write(st_bytes)
            if log_bytes is not None:
                with io.open(log_path, "wb") as f:
                    f.write(log_bytes)
            verdict, source, note = verdict_from_files(log_path, st_path)
            ok = verdict == expected and source == exp_source
            print("  [%s] %-34s -> %s/%s (want %s/%s)%s"
                  % ("ok" if ok else "FAIL", name, verdict, source,
                     expected, exp_source, "" if ok else " note=" + note))
            if not ok:
                failures.append(name)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    total = len(cases)
    print("[selftest] run_va_feature verdict parsing: %d/%d ok" % (total - len(failures), total))
    if failures:
        print("[selftest] FAILURES: %s" % ", ".join(failures))
        return 1
    print("[selftest] PASS (offline fixtures only; no COM/Vanessa/IB launched)")
    return 0


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
        return _selftest()
    feature = os.path.abspath(sys.argv[1])
    timeout = int(sys.argv[2]) if len(sys.argv) > 2 else 600
    # argv[3] (optional): test-client user override. TestManager stays under
    # USER (admin); only КлиентыТестирования connects as the override user.
    # Role ensure (admin's Tх_ roles) is skipped for override runs: the
    # override user's roles are managed by the caller (T12 stages).
    tc_user = sys.argv[3] if len(sys.argv) > 3 else None
    if tc_user is None:
        if not ensure_roles():
            print("[va] ABORT: could not ensure roles")
            return 2
    else:
        print("[va] test-client user override: " + tc_user)
    stem = os.path.splitext(os.path.basename(feature))[0]
    vap_path = os.path.join(LOGDIR, "vap_%s.json" % stem)
    onec_log = os.path.join(LOGDIR, "va_1c_%s.log" % stem)
    run_log = os.path.join(LOGDIR, "va_run_%s.log" % stem)
    status_log = os.path.join(LOGDIR, "va_status_%s.log" % stem)
    # Remove ALL verdict artifacts before the run: a stale va_status file
    # from a previous run must never fabricate a verdict (strictness rule).
    for p in (onec_log, run_log, status_log):
        if os.path.exists(p):
            os.remove(p)

    vap = {
        "ИмяСборки": "B6 " + stem,
        "ВерсияПлатформы": "8.5.4",
        "КаталогПоискаВерсииПлатформы": r"C:\Program Files\1cv8",
        # 1C's parser rejects the spaced form  /N "user"  ("Ошибка в параметрах
        # командной строки") - keys and values must be glued: /N"user".
        "СтрокаПодключенияКБазе": (
            'ENTERPRISE /S"%s" /N"%s" /P""' % (BASE, USER)
        ),
        "ПутьКVanessaAutomation": EPF,
        "КаталогФич": feature.replace("\\", "/"),
        "КаталогиБиблиотек": [],
        "КлиентыТестирования": [
            {
                "Имя": "Основной",
                "ПутьКИнфобазе": '/S"%s" /N"%s" /P""' % (
                    BASE, tc_user if tc_user is not None else USER),
                "ДопПараметры": (
                    "/DisableStartupMessages /DisableStartupDialogs"
                ),
                "ТипКлиента": "Тонкий",
                "ИмяКомпьютера": "localhost",
                "ПортЗапускаТестКлиента": "1538",
            }
        ],
        "ВыполнитьСценарии": "Истина",
        "ЗавершитьРаботуСистемы": "Истина",
        "ЗакрытьTestClientПослеЗапускаСценариев": "Истина",
        "ДелатьЛогВыполненияСценариевВТекстовыйФайл": "Истина",
        "ИмяФайлаЛогВыполненияСценариев": run_log.replace("\\", "/"),
        "ВыгружатьСтатусВыполненияСценариевВФайл": "Истина",
        "ПутьКФайлуДляВыгрузкиСтатусаВыполненияСценариев": (
            status_log.replace("\\", "/")
        ),
        "ТаймаутЗапуска1С": "600",
    }
    with io.open(vap_path, "w", encoding="utf-8") as f:
        json.dump(vap, f, ensure_ascii=False)

    cmd = [
        V8C, "ENTERPRISE", "/TESTMANAGER",
        "/S", BASE,
        "/N", USER, "/P", "",
        "/Execute", EPF,
        "/CStartFeaturePlayer;VAParams=" + vap_path.replace("\\", "/"),
        "/DisableStartupDialogs", "/DisableStartupMessages",
        "/Out", onec_log,
    ]
    print("[va] launching TestManager for %s" % os.path.basename(feature))
    proc = subprocess.Popen(cmd)
    rc = None
    try:
        rc = proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                       capture_output=True)
        print("[va] TIMEOUT after %ds, killed" % timeout)
        return 124

    time.sleep(2)
    verdict, source, note = verdict_from_files(onec_log, status_log)
    print("[va] %s: %s (source=%s, rc=%s)" % (os.path.basename(feature), verdict, source, rc))
    if note:
        print("[va] note: %s" % note)
    if verdict == "UNKNOWN":
        print("[va] UNRESOLVED verdict: artifacts inconclusive; not counted as PASS")
    print("[va] 1C log: %s" % onec_log)
    print("[va] run log: %s" % run_log)
    print("[va] status artifact: %s" % status_log)
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
