#!/usr/bin/env python3
import sys
import os

TEST_FILE = os.path.abspath(__file__)
ROOT_DIR = os.path.dirname(TEST_FILE)
MODULES_DIR = os.path.join(ROOT_DIR, 'sheet_stream')
#EXPORT_DIR = sp.UserFileSystem().userDownloads.concat('output', create=True)

sys.path.insert(0, MODULES_DIR)

ods = '/home/brunoc/Documentos/LV10.ods'
out = '/home/bruno/Documentos/teste.ods'
output_dir = '/home/brunoc/Downloads/output'

from digitalized.documents.sheet import ReadSheetExcel, ReadSheetODS
from digitalized.documents.sheet.parse import SplitDataFrame, ParserData


def test():

    ld = ReadSheetODS.create_load_pandas(ods)
    df = ld.get_workbook_data().get_sheet('Sheet1')
    parse = ParserData(df.to_data_frame())
    parse.concat_columns(['numliv', 'codlcd', 'numrota'])

    split_df = SplitDataFrame(parse.get_data(), col_split='concatenar')
    split_df.split_to_disk(output_dir, extension='ods')


def main():
    test()


if __name__ == '__main__':
    main()
