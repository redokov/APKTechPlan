#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OCR PNG через Windows.Media.Ocr (winsdk). Использование: ocr_py.py <png> [lang]"""
import asyncio, sys

import winsdk.windows.globalization as glob
import winsdk.windows.graphics.imaging as imaging
import winsdk.windows.media.ocr as ocr
import winsdk.windows.storage as storage

async def main(path, lang="ru"):
    file = await storage.StorageFile.get_file_from_path_async(path)
    stream = await file.open_async(storage.FileAccessMode.READ)
    decoder = await imaging.BitmapDecoder.create_async(stream)
    bmp = await decoder.get_software_bitmap_async()
    lang_obj = glob.Language(lang)
    engine = ocr.OcrEngine.try_create_from_language(lang_obj)
    if engine is None:
        engine = ocr.OcrEngine.try_create_from_user_profile_languages()
    assert engine is not None, "no OCR engine for %r" % lang
    res = await engine.recognize_async(bmp)
    out = "\n".join(line.text for line in res.lines)
    sys.stdout.buffer.write(out.encode("utf-8"))

if __name__ == "__main__":
    import os
    p = os.path.abspath(sys.argv[1])
    lang = sys.argv[2] if len(sys.argv) > 2 else "ru"
    asyncio.run(main(p, lang))
