#!/usr/bin/env python3
import sys
import os

TEST_FILE = os.path.abspath(__file__)
ROOT_DIR = os.path.dirname(TEST_FILE)
MODULES_DIR = os.path.join(ROOT_DIR, 'sheet_stream')
#EXPORT_DIR = sp.UserFileSystem().userDownloads.concat('output', create=True)

sys.path.insert(0, MODULES_DIR)

from digitalized.documents.sheet import ReadSheetExcel, ReadSheetODS
from digitalized.documents.sheet.parse import SplitDataFrame, ParserData
from digitalized.documents.image.image import LibImage, ImageObject
import pandas as pd
from soup_files import File, UserFileSystem

base = '/home/brunoc/Documentos/EXCEL/LV10.xlsx'
ods_file = '/home/brunoc/Documentos/EXCEL/LV10.ods'
output_dir = '/home/brunoc/Downloads/output'
img = '/mnt/dados/2025-11-02 Cartas Toi WhatsApp/OriginLocalidades/EXT/EXTREMA - JAN A JUN 2025/NOMEADOS/278970/EXTREMA_--107-- UC 278970 167393150 POSTAGEM nan..png'
img2 = '/mnt/dados/2025-11-02 Cartas Toi WhatsApp/OriginLocalidades/EXT/EXTREMA - JAN A JUN 2025/NOMEADOS/1030464/EXTREMA_--107-- UC 1030464 152298670 POSTAGEM -..png'

output = UserFileSystem().userDownloads


def test():

    img_obj = ImageObject.create_from_file(File(img))
    img_obj.set_background("gray")
    img_obj.to_file(output.join_file('teste.png'))


def main():
    test()


if __name__ == '__main__':
    main()
