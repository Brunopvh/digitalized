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

base = '/home/brunoc/Downloads/base.xlsx'
ods_file = '/home/brunoc/Documentos/EXCEL/LV10.ods'
file_csv = '/home/brunoc/Documentos/EXCEL/ANALITICO/2025-11 ANALITICO REG NORTE.csv'

output_dir = '/home/brunoc/Downloads/output'
img = '/mnt/dados/2025-11-02 Cartas Toi WhatsApp/OriginLocalidades/EXT/EXTREMA - JAN A JUN 2025/NOMEADOS/278970/EXTREMA_--107-- UC 278970 167393150 POSTAGEM nan..png'
img2 = '/mnt/dados/2025-11-02 Cartas Toi WhatsApp/OriginLocalidades/EXT/EXTREMA - JAN A JUN 2025/NOMEADOS/1030464/EXTREMA_--107-- UC 1030464 152298670 POSTAGEM -..png'

output = UserFileSystem().userDownloads


def test():
    from digitalized.ocr.tesseract import BinTesseract
    from digitalized.ocr.recognize import TesseractOcr
    from digitalized.types.array import ArrayList

    tess1 = TesseractOcr.crate("easyocr", kwargs={"gpu": False})
    tess2 = TesseractOcr.crate("easyocr", kwargs={"gpu": False})
    print(tess1.iqual(tess2))


def main():
    test()


if __name__ == '__main__':
    main()
