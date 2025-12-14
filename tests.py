#!/usr/bin/env python3
import sys
import os
import pandas as pd
import soup_files as sp
from sheet_stream import *

TEST_FILE = os.path.abspath(__file__)
ROOT_DIR = os.path.dirname(TEST_FILE)
MODULES_DIR = os.path.join(ROOT_DIR, 'sheet_stream')
EXPORT_DIR = sp.UserFileSystem().userDownloads.concat('output', create=True)

sys.path.insert(0, MODULES_DIR)

f = '/home/brunoc/Documentos/LV10.xlsx'


def test():
    from documents.sheet.excel.load import ReadSheetExcel, SheetData, RowIterator
    from pathlib import Path
    from io import BytesIO

    ld = ReadSheetExcel.create_load_open_pyxl(f)
    s: SheetData = ld.get_sheet('Sheet1')
    print(s.to_data_frame())


def main():
    test()


if __name__ == '__main__':
    main()
