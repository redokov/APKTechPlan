#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кроп области PNG + апскейл + OCR (winsdk). Использование: crop_ocr.py <png> <x> <y> <w> <h> [scale]"""
import asyncio, os, sys

import winsdk.windows.globalization as glob
import winsdk.windows.graphics.imaging as imaging
import winsdk.windows.media.ocr as ocr
import winsdk.windows.storage as storage


async def main(path, x, y, w, h, scale=2):
    file = await storage.StorageFile.get_file_from_path_async(path)
    stream = await file.open_async(storage.FileAccessMode.READ)
    decoder = await imaging.BitmapDecoder.create_async(stream)
    bmp = await decoder.get_software_bitmap_async()
    from winsdk.windows.graphics.imaging import BitmapBounds, SoftwareBitmap
    # crop через BitmapTransform при повторном декоде
    transform = imaging.BitmapTransform()
    transform.bounds = BitmapBounds(x=int(x), y=int(y), width=int(w), height=int(h))
    stream2 = await file.open_async(storage.FileAccessMode.READ)
    decoder2 = await imaging.BitmapDecoder.create_async(stream2, transform)
    cropped = await decoder2.get_software_bitmap_async()
    if scale > 1:
        sw = cropped.pixel_width * scale
        sh = cropped.pixel_height * scale
        big = imaging.SoftwareBitmap.create_copy_from_buffer(
            cropped.copy_to_buffer(), cropped.bitmap_pixel_format, sw, sh)
        # create_copy_from_buffer не масштабирует; масштабируем через PrintWindow-free путь не выйдет.
    lang_obj = glob.Language("ru")
    engine = ocr.OcrEngine.try_create_from_language(lang_obj)
    if engine is None:
        engine = ocr.OcrEngine.try_create_from_user_profile_languages()
    res = await engine.recognize_async(cropped)
    out = []
    for line in res.lines:
        for word in line.words:
            r = word.bounding_rect
            out.append("%s|%d|%d|%d|%d" % (word.text, int(r.x), int(r.y), int(r.width), int(r.height)))
    sys.stdout.buffer.write(("\n".join(out)).encode("utf-8"))


if __name__ == "__main__":
    p = os.path.abspath(sys.argv[1])
    x, y, w, h = (int(v) for v in sys.argv[2:6])
    scale = int(sys.argv[6]) if len(sys.argv) > 6 else 2
    asyncio.run(main(p, x, y, w, h, scale))
