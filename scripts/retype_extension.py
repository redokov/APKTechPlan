# -*- coding: utf-8 -*-
"""T2/T3: ретайпинг реквизитов объектов расширения.

Name-scoped замена содержимого блока <Type>...</Type> у атрибута/измерения/ресурса
по имени. Ожидаемое число замен контролируется. utf-8-sig + CRLF сохраняются.
Usage: python scripts/retype_extension.py [--t2|--t3]
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1] / "src/cfe/ПланированиеТехникиАПК"

# (relpath, attr_name, [новые v8:Type-строки без префикса], expected_count)
T2 = [
    ("Documents/Тх_ПланТехническихРесурсов.xml", "Организация",
     ["cfg:CatalogRef.Организации"], 1),
    ("Documents/Тх_ПланТехническихРесурсов.xml", "Подразделение",
     ["cfg:CatalogRef.СтруктураПредприятия"], 1),
    ("Documents/Тх_ПланТехническихРесурсов.xml", "СценарийПланирования",
     ["cfg:CatalogRef.АпкСценарииПланирования"], 1),
    ("InformationRegisters/Тх_ДефицитТехники.xml", "Организация",
     ["cfg:CatalogRef.Организации"], 1),
    ("InformationRegisters/Тх_ДефицитТехники.xml", "Подразделение",
     ["cfg:CatalogRef.СтруктураПредприятия"], 1),
    ("InformationRegisters/Тх_ДефицитТехники.xml", "СценарийПланирования",
     ["cfg:CatalogRef.АпкСценарииПланирования"], 1),
    ("InformationRegisters/Тх_ДефицитТехники.xml", "ВидРаботы",
     ["cfg:CatalogRef.ВидыРаботСотрудников"], 1),
    ("InformationRegisters/Тх_ДефицитТехники.xml", "МодельТехники",
     ["cfg:CatalogRef.АпкМоделиСХТехники",
      "cfg:CatalogRef.АпкМоделиАвтотранспорта",
      "cfg:CatalogRef.АпкМоделиСХОборудования",
      "cfg:CatalogRef.АпкМоделиПрицепов"], 1),
]

# T3 наполняется отдельным шагом (ТЧ документа, 3 таблицы) — здесь каркас.
T3 = []


def retype(path, attr_name, new_types, expected):
    raw = path.read_text(encoding="utf-8-sig")
    trailing = "\r\n" if raw.endswith("\r\n") else ("\n" if raw.endswith("\n") else "")
    lines = raw.splitlines(keepends=False)
    hits = 0
    i = 0
    n = len(lines)
    while i < n:
        if f"<Name>{attr_name}</Name>" in lines[i]:
            # ищем следующий <Type> в пределах 6 строк (Properties-блок)
            j = i + 1
            while j < min(i + 20, n) and "<Type>" not in lines[j]:
                j += 1
            if j < min(i + 20, n) and "<Type>" in lines[j]:
                indent = lines[j][: len(lines[j]) - len(lines[j].lstrip("\t"))]
                k = j
                while k < n and "</Type>" not in lines[k]:
                    k += 1
                if k < n:
                    block = [indent + "<Type>"]
                    child = indent + "\t"
                    for t in new_types:
                        block.append(child + f"<v8:Type>{t}</v8:Type>")
                    block.append(indent + "</Type>")
                    lines[j:k + 1] = block
                    hits += 1
                    i = k + len(block)
                    continue
        i += 1
    if hits != expected:
        print(f"FAIL {path.name}::{attr_name}: retyped {hits}, expected {expected}")
        return False
    text = "\r\n".join(lines) + trailing
    path.write_bytes(text.encode("utf-8-sig"))
    print(f"OK {path.name}::{attr_name}: {hits}x -> {len(new_types)} type(s)")
    return True


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "--t2"
    plan = T2 if which in ("--t2", "both") else []
    if which in ("--t3", "both"):
        plan += T3
    if not plan:
        print("nothing to do (T3 plan empty)")
        return
    ok = True
    for rel, name, types, cnt in plan:
        ok = retype(ROOT / rel, name, types, cnt) and ok
    print("RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
