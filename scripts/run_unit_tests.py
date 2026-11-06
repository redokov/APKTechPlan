#!/usr/bin/env python3
"""Запуск модульных тестов Тх_Тесты из расширения ПланированиеТехникиАПК."""
import sys
import time

def main(results):
    total = 0
    passed = 0
    skipped = 0
    failed = 0
    started = time.time()
    elapsed = 0.0
    print("\n%-58s %-8s %s" % ("TEST", "RESULT", "MS"))
    skipped = 0
    for item in results:
        total += 1
        name = item.Имя
        status = "PASS"
        if hasattr(item, "Статус") and item.Статус == "SKIP":
            skipped += 1
            status = "SKIP"
        elif item.Статус == "FAIL":
            failed += 1
        else:
            passed += 1
        ms = item.ДлительностьМс
        details = ""
        try:
            details = item.Детали
        except Exception:
            pass
        line = "%-58s %-8s %s" % (name, status, ms)
        print(line)
        if details:
            for dl in str(details).splitlines():
                print("    | " + dl)
    print("\n[summary] total=%d passed=%d skipped=%d failed=%d wall=%.1fs"
          % (total, passed, skipped, failed, elapsed))
    if total != 20:
        print("UNEXPECTED: expected 20 tests, got %d" % total)
        return 1
    if skipped > 0:
        print("[skip] %d test(s) skipped (exit code 2, not a failure)" % skipped)
        return 2
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

