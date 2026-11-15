#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Собирает ПОСТАВОЧНЫЙ профиль расширения: рабочее расширение без проверочных
объектов (решение владельца 15.11.2026 по задаче TEST-03).

Зачем так, а не отдельным расширением: проверено прогоном 15.11.2026 -
внешнее соединение (COM) видит объекты ТОЛЬКО одного расширения, поэтому при
выносе проверочных объектов во второе расширение перестают работать
автоматические проверки (запускатор тестов, маркер тестовой базы, уборка
остатков). Подробности: docs/review/test04-design-2026-11-15.md §10.

Что делает: копирует src/cfe/ПланированиеТехникиАПК в dist/ПланированиеТехникиАПК,
убирая проверочные объекты из состава и с диска. Всё остальное копируется байт
в байт, поэтому профиль не может разойтись с рабочим деревом по содержанию -
расходится только состав.

Использование:
    python scripts/make_prod_cfe.py [--check]

--check ничего не пишет: только проверяет, что профиль в dist/ совпадает
с текущим рабочим деревом минус проверочные объекты (exit 1 при расхождении).
"""
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'src', 'cfe', 'ПланированиеТехникиАПК')
DST = os.path.join(ROOT, 'dist', 'ПланированиеТехникиАПК')

# Проверочные объекты: не входят в поставку (TEST-02, TEST-03, TEST-04).
TEST_OBJECTS = [
    ('CommonModules', 'Тх_Тесты', 'CommonModule'),
    ('Constants', 'Тх_ТестоваяБаза', 'Constant'),
    ('InformationRegisters', 'Тх_РеестрТестовыхОбъектов', 'InformationRegister'),
    ('DataProcessors', 'Тх_РаннерТестов', 'DataProcessor'),
    ('DataProcessors', 'Тх_ПодготовкаТестовыхДанных', 'DataProcessor'),
    ('DataProcessors', 'Тх_ЗапускVanessa', 'DataProcessor'),
]


def build_config_xml(text):
    for folder, name, tag in TEST_OBJECTS:
        line = '\t\t\t<%s>%s</%s>' % (tag, name, tag)
        for candidate in (line + '\r\n', line + '\n', line, line.replace('\t\t\t', '\t\t')):
            if candidate in text:
                text = text.replace(candidate, '', 1)
                break
        else:
            raise SystemExit('в Configuration.xml не найден объект: ' + name)
    return text


def build(dst):
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    shutil.copytree(SRC, dst)
    for folder, name, _tag in TEST_OBJECTS:
        xml = os.path.join(dst, folder, name + '.xml')
        obj_dir = os.path.join(dst, folder, name)
        if os.path.isfile(xml):
            os.remove(xml)
        if os.path.isdir(obj_dir):
            shutil.rmtree(obj_dir)
    cfg = os.path.join(dst, 'Configuration.xml')
    with open(cfg, 'rb') as f:
        raw = f.read()
    bom = raw.startswith(b'\xef\xbb\xbf')
    text = raw[3:].decode('utf-8') if bom else raw.decode('utf-8')
    text = build_config_xml(text)
    data = text.encode('utf-8')
    with open(cfg, 'wb') as f:
        f.write((b'\xef\xbb\xbf' if bom else b'') + data)
    return dst


def check(dst):
    if not os.path.isdir(dst):
        print('ПРОФИЛЬ ОТСУТСТВУЕТ: %s' % dst)
        return 1
    for folder, name, _tag in TEST_OBJECTS:
        if os.path.exists(os.path.join(dst, folder, name + '.xml')):
            print('В ПРОФИЛЕ ЛИШНИЙ ПРОВЕРОЧНЫЙ ОБЪЕКТ: %s' % name)
            return 1
    problems = []
    for root, _dirs, files in os.walk(dst):
        for f in files:
            p = os.path.join(root, f)
            rel = os.path.relpath(p, dst)
            src_p = os.path.join(SRC, rel)
            if not os.path.isfile(src_p):
                problems.append('лишний файл: ' + rel)
                continue
            with open(p, 'rb') as a, open(src_p, 'rb') as b:
                if a.read() != b.read():
                    if rel == 'Configuration.xml':
                        continue
                    problems.append('содержимое отличается: ' + rel)
    if problems:
        for p in problems[:20]:
            print(p)
        return 1
    print('профиль соответствует рабочему дереву (без проверочных объектов)')
    return 0


def main():
    if '--check' in sys.argv[1:]:
        return check(DST)
    build(DST)
    print('собран поставочный профиль: %s' % DST)
    print('исключено проверочных объектов: %d' % len(TEST_OBJECTS))
    for folder, name, _tag in TEST_OBJECTS:
        print('   - %s/%s' % (folder, name))
    return 0


if __name__ == '__main__':
    sys.exit(main())
