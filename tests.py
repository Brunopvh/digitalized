#!/usr/bin/env python3
import sys
import os

TEST_FILE = os.path.abspath(__file__)
ROOT_DIR = os.path.dirname(TEST_FILE)
MODULES_DIR = os.path.join(ROOT_DIR, 'sheet_stream')
#EXPORT_DIR = sp.UserFileSystem().userDownloads.concat('output', create=True)

sys.path.insert(0, MODULES_DIR)

f = '/home/brunoc/Documentos/LV10.xlsx'
ods = '/home/brunoc/Documentos/LV10.ods'


def test():
    from digitalized.documents.sheet.excel.load import ReadSheetExcel
    from digitalized.documents.sheet.ods import ReadSheetODS

    ld = ReadSheetODS.create_load_pandas(ods)
    print(ld.get_workbook_data().get_last())


def main():
    test()


if __name__ == '__main__':
    main()
