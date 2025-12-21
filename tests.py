#!/usr/bin/env python3
import sys
import os

TEST_FILE = os.path.abspath(__file__)
ROOT_DIR = os.path.dirname(TEST_FILE)
MODULES_DIR = os.path.join(ROOT_DIR, 'sheet_stream')
#EXPORT_DIR = sp.UserFileSystem().userDownloads.concat('output', create=True)

sys.path.insert(0, MODULES_DIR)

from digitalized.documents.sheet import ReadSheetExcel, ReadSheetODS, ReadSheetCsv
from digitalized.documents.sheet.parse import SplitDataFrame, ParserData, FilterData, SearchInData
from digitalized.documents.image.image import LibImage, ImageObject
import pandas as pd
from soup_files import File, UserFileSystem, Directory, InputFiles

output = UserFileSystem().userDownloads


def test():
    from digitalized.documents.image.image import ImageObject
    from digitalized.ocr.tesseract import BinTesseract
    from digitalized.ocr.recognize import TesseractOcr, TextRecognized
    from digitalized.types.array import ArrayList

    image_file = File('/mnt/dados/ERO/2025-11-02 Cartas Toi WhatsApp/Output/GM E NM/OutputString/NOVA MAMORE 1060346 160154310 N6169165586.jpg')
    rec = TesseractOcr.crate()

    img = ImageObject.create_from_file(image_file)
    img.set_background("gray")
    t = rec.get_recognized_text(img)
    print(t.get_text())


def main():
    test()


if __name__ == '__main__':
    main()
