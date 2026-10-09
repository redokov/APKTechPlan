# -*- coding: utf-8 -*-
"""T3: ретайпинг ТЧ документа + новые колонки + колонки форм + тип-гард автозаполнения.

Part A: uuid-scoped retype ТЧ-колонок (6 замен).
Part B: +10 Attribute-блоков в ТЧ документа (5 в ОсновнаяТехника, 5 в Автотранспорт).
Part C: +10 InputField-колонок в Form.xml (таблицы id=25 и id=91).
Part D: тип-гард в Module.bsl (автозаполнение модели под узкий тип колонки).
utf-8-sig + CRLF сохраняются; каждый шаг проверяет счётчик.
"""
import pathlib
import re
import sys
import uuid

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "src/cfe/ПланированиеТехникиАПК/Documents/Тх_ПланТехническихРесурсов.xml"
FORM = ROOT / "src/cfe/ПланированиеТехникиАПК/Documents/Тх_ПланТехническихРесурсов/Forms/Тх_ФормаДокумента/Ext/Form.xml"
MODULE = ROOT / "src/cfe/ПланированиеТехникиАПК/Documents/Тх_ПланТехническихРесурсов/Forms/Тх_ФормаДокумента/Ext/Form/Module.bsl"

ok_all = True


def load(p):
    raw = p.read_text(encoding="utf-8-sig")
    trailing = "\r\n" if raw.endswith("\r\n") else ("\n" if raw.endswith("\n") else "")
    eol = "\r\n" if "\r\n" in raw else "\n"
    return raw, trailing, eol


def save(p, text, trailing):
    text = "\r\n".join(text.split("\r\n")) if "\r\n" in text else text
    p.write_bytes((text + trailing).encode("utf-8-sig"))


def check(cond, msg):
    global ok_all
    print(("OK " if cond else "FAIL ") + msg)
    if not cond:
        ok_all = False


# ---------- Part A: uuid-scoped retype ----------
RETYPE = [
    ("2ed6ae80-c9a0-414c-8938-2f96959124b7", ["cfg:CatalogRef.ТранспортныеСредства"]),   # Осн.Техника.ТС
    ("f70b882e-b2b9-4d72-addf-4526d63ffb96", ["cfg:CatalogRef.ТранспортныеСредства"]),   # Оборудование.ТС
    ("ca15284c-d83e-4caa-8e50-61896955135a", ["cfg:CatalogRef.ТранспортныеСредства"]),   # Автотранспорт.ТС
    ("c1f3b26a-74db-4bb1-9b73-e0e64a4d5d71", ["cfg:CatalogRef.АпкМоделиСХТехники"]),    # Осн.Техника.Модель
    ("a48dcac2-5d2b-40b6-a605-b39a8ef56e4f", ["cfg:CatalogRef.АпкМоделиСХОборудования"]),  # Оборудование.Модель
    ("db54f8c9-c097-4d27-b613-332d68172699", ["cfg:CatalogRef.АпкМоделиАвтотранспорта"]),  # Автотранспорт.Модель
]


def retype_by_uuid(text, attr_uuid, new_types, eol):
    pat = re.compile(r'(<Attribute uuid="' + attr_uuid + r'">.*?<Type>\s*)(.*?)(\s*</Type>)', re.S)
    n = 0

    def repl(m):
        nonlocal n
        n += 1
        inner = "\r\n".join("\t\t\t\t\t\t\t<v8:Type>%s</v8:Type>" % t for t in new_types)
        return m.group(1) + inner + m.group(3)

    out = pat.sub(repl, text, count=1)
    return out, n


# ---------- Part B: новые Attribute-блоки ТЧ ----------
TS_IND = "\t" * 5  # <Attribute внутри TabularSection
PR_IND = "\t" * 6
CH_IND = "\t" * 7


def attr_block(name, synonym, types, number=None, eol="\r\n"):
    lines = [
        TS_IND + '<Attribute uuid="%s">' % uuid.uuid4(),
        PR_IND + "<Properties>",
        PR_IND + "\t<Name>%s</Name>" % name,
        PR_IND + "\t<Synonym>",
        PR_IND + "\t\t<v8:item>",
        PR_IND + "\t\t\t<v8:lang>ru</v8:lang>",
        PR_IND + "\t\t\t<v8:content>%s</v8:content>" % synonym,
        PR_IND + "\t\t</v8:item>",
        PR_IND + "\t</Synonym>",
        PR_IND + "\t<Comment/>",
        PR_IND + "\t<Type>",
    ]
    for t in types:
        lines.append(CH_IND + "<v8:Type>%s</v8:Type>" % t)
    if number:
        digits, frac = number
        lines += [
            CH_IND + "<v8:NumberQualifiers>",
            CH_IND + "\t<v8:Digits>%d</v8:Digits>" % digits,
            CH_IND + "\t<v8:FractionDigits>%d</v8:FractionDigits>" % frac,
            CH_IND + "\t<v8:AllowedSign>Nonnegative</v8:AllowedSign>",
            CH_IND + "</v8:NumberQualifiers>",
        ]
    lines += [
        PR_IND + "\t</Type>",
        PR_IND + "\t<PasswordMode>false</PasswordMode>",
        PR_IND + "\t<Format/>",
        PR_IND + "\t<EditFormat/>",
        PR_IND + "\t<ToolTip/>",
        PR_IND + "\t<MarkNegatives>false</MarkNegatives>",
        PR_IND + "\t<Mask/>",
        PR_IND + "\t<MultiLine>false</MultiLine>",
        PR_IND + "\t<ExtendedEdit>false</ExtendedEdit>",
        PR_IND + "\t<MinValue xsi:nil=\"true\"/>",
        PR_IND + "\t<MaxValue xsi:nil=\"true\"/>",
        PR_IND + "\t<FillChecking>DontCheck</FillChecking>",
        PR_IND + "\t<ChoiceFoldersAndItems>Items</ChoiceFoldersAndItems>",
        PR_IND + "\t<ChoiceParameterLinks/>",
        PR_IND + "\t<ChoiceParameters/>",
        PR_IND + "\t<QuickChoice>Auto</QuickChoice>",
        PR_IND + "\t<CreateOnInput>Auto</CreateOnInput>",
        PR_IND + "\t<ChoiceForm/>",
        PR_IND + "\t<LinkByType/>",
        PR_IND + "\t<ChoiceHistoryOnInput>Auto</ChoiceHistoryOnInput>",
        PR_IND + "\t<Indexing>DontIndex</Indexing>",
        PR_IND + "\t<FullTextSearch>Use</FullTextSearch>",
        PR_IND + "\t<DataHistory>Use</DataHistory>",
        PR_IND + "</Properties>",
        TS_IND + "</Attribute>",
    ]
    return eol.join(lines)


DEC3 = (10, 3)
DEC0 = (5, 0)
NEW_COLS = {
    "ОсновнаяТехника": [
        ("Оборудование", "Оборудование", ["cfg:CatalogRef.АпкМоделиСХОборудования"], None),
        ("ВидРаботы", "Вид работы", ["cfg:CatalogRef.ВидыРаботСотрудников"], None),
        ("ПотребностьСмен", "Потребность, смен", ["xs:decimal"], DEC3),
        ("ПотребностьЧасов", "Потребность, часов", ["xs:decimal"], DEC3),
        ("ДоступноЕдиниц", "Доступно, единиц", ["xs:decimal"], DEC0),
    ],
    "Автотранспорт": [
        ("Оборудование", "Прицеп", ["cfg:CatalogRef.АпкМоделиПрицепов"], None),
        ("ВидРаботы", "Вид работы", ["cfg:CatalogRef.ВидыРаботСотрудников"], None),
        ("ПотребностьСмен", "Потребность, смен", ["xs:decimal"], DEC3),
        ("ПотребностьЧасов", "Потребность, часов", ["xs:decimal"], DEC3),
        ("ДоступноЕдиниц", "Доступно, единиц", ["xs:decimal"], DEC0),
    ],
}


TS_UUIDS = {"ОсновнаяТехника": "2491056f", "Автотранспорт": "8c97ed51"}


def insert_ts_attrs(text, ts_name, blocks, eol):
    m = re.search(r'<TabularSection uuid="' + TS_UUIDS[ts_name] + r'[^"]*">.*?</TabularSection>', text, re.S)
    if not m:
        return text, 0
    block = m.group(0)
    anchor = TS_IND + "</Attribute>\r\n" + "\t\t\t\t</TabularSection>"
    # последний атрибут ТЧ: </Properties>(6) </Attribute>(5) </ChildObjects>(4)
    tail_pat = re.compile(r"(\t{6}</Properties>\r?\n\t{5}</Attribute>)(\r?\n)(\t{4}</ChildObjects>)")
    n = 0
    newblock = block
    for name, syn, types, num in blocks:
        newblock = tail_pat.sub(lambda mm: mm.group(1) + eol + attr_block(name, syn, types, num, eol) + eol + mm.group(3), newblock, count=1)
        n += 1
    return text.replace(block, newblock, 1), n


# ---------- Part C: колонки форм ----------
F_IND = "\t" * 8   # InputField в ChildItems таблицы
FC_IND = "\t" * 9


def form_col(name, title, datapath, idmain, eol):
    ids = [idmain, idmain + 1, idmain + 2]
    return eol.join([
        F_IND + '<InputField name="%s" id="%d">' % (name, ids[0]),
        FC_IND + "<DataPath>%s</DataPath>" % datapath,
        FC_IND + "<Title>",
        FC_IND + "\t<v8:item>",
        FC_IND + "\t\t<v8:lang>ru</v8:lang>",
        FC_IND + "\t\t<v8:content>%s</v8:content>" % title,
        FC_IND + "\t</v8:item>",
        FC_IND + "</Title>",
        FC_IND + '<ContextMenu name="%sКонтекстноеМеню" id="%d"/>' % (name, ids[1]),
        FC_IND + '<ExtendedTooltip name="%sРасширеннаяПодсказка" id="%d"/>' % (name, ids[2]),
        F_IND + "</InputField>",
    ])


FORM_TABLES = [
    # (имя таблицы, id таблицы, префикс имени колонок, счётчик строк уже вставленных)
    ("ОсновнаяТехника", 25, "ОсновнаяТехника"),
    ("Автотранспорт", 91, "Автотранспорт"),
]

FORM_COL_DEFS = [
    ("Оборудование", "Оборудование"),
    ("ВидРаботы", "Вид работы"),
    ("ПотребностьСмен", "Потребность, смен"),
    ("ПотребностьЧасов", "Потребность, часов"),
    ("ДоступноЕдиниц", "Доступно, единиц"),
]

# для таблицы Автотранспорт заголовок Оборудование = «Прицеп»
FORM_COL_DEFS_AUTO = [
    ("Оборудование", "Прицеп"),
    ("ВидРаботы", "Вид работы"),
    ("ПотребностьСмен", "Потребность, смен"),
    ("ПотребностьЧасов", "Потребность, часов"),
    ("ДоступноЕдиниц", "Доступно, единиц"),
]


def insert_form_cols(text, ts_name, prefix, defs, start_id, eol):
    m = re.search(r'<Table name="' + ts_name + r'" id="\d+">.*?</Table>', text, re.S)
    if not m:
        return text, 0
    block = m.group(0)
    newblock = block
    cnt = 0
    cid = start_id
    for col, title in defs:
        el_name = prefix + col
        dp = "Объект.%s.%s" % (ts_name, col)
        colxml = form_col(el_name, title, dp, cid, eol)
        cid += 3
        # вставка перед закрывающим </ChildItems> таблицы (последний в блоке)
        k = newblock.rfind("\t\t\t\t\t\t\t</ChildItems>")
        if k < 0:
            return text, -1
        newblock = newblock[:k] + colxml + "\r\n" + newblock[k:]
        cnt += 1
    return text.replace(block, newblock, 1), cnt


def main():
    # Part A
    text, trailing, eol = load(DOC)
    for u, types in RETYPE:
        text, n = retype_by_uuid(text, u, types, eol)
        check(n == 1, f"A: retype {u[:8]} -> {types[0]} ({n})")
    # Part B
    for ts_name, defs in NEW_COLS.items():
        text, n = insert_ts_attrs(text, ts_name, defs, eol)
        check(n == len(defs), f"B: +{n} attrs into TS {ts_name} (expect {len(defs)})")
    save(DOC, text, trailing)

    # Part C
    ftext, ftrailing, feol = load(FORM)
    ftext, n1 = insert_form_cols(ftext, "ОсновнаяТехника", "ОсновнаяТехника", FORM_COL_DEFS, 202, feol)
    check(n1 == 5, f"C: +{n1} columns into form table 25 (expect 5)")
    ftext, n2 = insert_form_cols(ftext, "Автотранспорт", "Автотранспорт", FORM_COL_DEFS_AUTO, 217, feol)
    check(n2 == 5, f"C: +{n2} columns into form table 91 (expect 5)")
    save(FORM, ftext, ftrailing)

    print("RESULT:", "PASS" if ok_all else "FAIL")
    sys.exit(0 if ok_all else 1)


if __name__ == "__main__":
    main()
