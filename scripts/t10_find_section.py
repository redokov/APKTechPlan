#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Найти раздел «Планирование техники» в OCR-боксах (слова text|x|y|w|h) и вывести
клик-цель в координатах битмапа. Использование: t10_find_section.py <ocr_boxes.txt>
Вывод: FOUND x y  |  NOTFOUND [причина]"""
import sys
from pathlib import Path

lines = Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()
words = []
for ln in lines:
    parts = ln.strip().split("|")
    if len(parts) != 5:
        continue
    try:
        words.append((parts[0], int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4])))
    except ValueError:
        continue

# ищем слово «техники» рядом (по вертикали ИЛИ на той же строке) со словом «Планирование»
for text, x, y, w, h in words:
    if text.lower() != "техники":
        continue
    for t2, x2, y2, w2, h2 in words:
        if t2 != "Планирование":
            continue
        same_line = abs(y - y2) <= 5 and -10 <= (x - (x2 + w2)) <= 20
        stacked = abs(x2 - x) <= 15 and 0 < (y - y2) <= 30
        if same_line or stacked:
            cx = x + w // 2
            cy = (y + y2 + h + h2) // 2
            print("FOUND %d %d" % (cx, cy))
            sys.exit(0)
print("NOTFOUND no Планирование+техники pair; words total=%d" % len(words))
