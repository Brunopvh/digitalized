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
    from digitalized.documents.sheet import ReadSheetCsv


def main():
    test()


if __name__ == '__main__':
    main()
