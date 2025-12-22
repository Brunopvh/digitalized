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
    from digitalized.ocr.tesseract import BinTesseract, CheckTesseractSystem
    from digitalized.ocr.recognize import TesseractOcr, RecognizePdf, create_images_from_pdf
    from digitalized.types.array import ArrayList

    file_pdf = File('/home/brunoc/Downloads/Thiago  Coturno 42 NOV 2023.pdf')
    final_pdf = output.join_file('final.pdf')

    images = create_images_from_pdf(file_pdf.path.read_bytes())
    rec = TesseractOcr.crate()
    for x in images:
        print(rec.get_recognized_text(x).get_text())


def main():
    test()


if __name__ == '__main__':
    main()
