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
    from digitalized.ocr.recognize import TesseractOcr, TextRecognized, create_document_from_image
    from digitalized.types.array import ArrayList

    image_file = File('/mnt/dados/ERO/2025-11-02 Cartas Toi WhatsApp/Output/GM E NM/OutputString/NOVA MAMORE 1060346 160154310 N6169165586.jpg')
    image_obj = ImageObject.create_from_file(image_file)

    _imp = TesseractOcr.builder_easyocr().set_langs(['por'])

    rec = TesseractOcr(_imp.build())
    txt = rec.get_recognized_text(image_obj)
    txt.to_file_pdf(output.join_file("final.pdf"))


def main():
    test()


if __name__ == '__main__':
    main()
