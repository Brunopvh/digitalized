#!/usr/bin/env python3
import sys
import os
import soup_files as sp
from digitalized.documents.pdf.pdf_page import PageDocumentPdf

TEST_FILE = os.path.abspath(__file__)
ROOT_DIR = os.path.dirname(TEST_FILE)
MODULES_DIR = os.path.join(ROOT_DIR, 'sheet_stream')

output_dir = sp.UserFileSystem().userDownloads.concat('output', create=True)
sys.path.insert(0, MODULES_DIR)


def test():
    import sys, os

    print(os.system(f'{sys.executable} -V'))


def main():
    test()


if __name__ == '__main__':
    main()
