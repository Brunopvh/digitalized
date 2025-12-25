#!/usr/bin/env python3
import sys
import os

import fitz
import soup_files as sp

from digitalized.documents.pdf.pdf_page import PageDocumentPdf

TEST_FILE = os.path.abspath(__file__)
ROOT_DIR = os.path.dirname(TEST_FILE)
MODULES_DIR = os.path.join(ROOT_DIR, 'sheet_stream')

output_dir = sp.UserFileSystem().userDownloads.concat('output', create=True)

sys.path.insert(0, MODULES_DIR)

from digitalized.documents.pdf.pdf_document import DocumentPdf, merge_pdf_bytes
from digitalized.ocr.recognize import RecognizePdf
from digitalized.documents.image import ImageObject, ImageStream
import pandas as pd


def test():

    _input_dir = sp.Directory('/mnt/dados/ERO/2025-11-02 Cartas Toi WhatsApp/Output/GM E NM/OutputString')
    files = sp.InputFiles(_input_dir).images[0:10]

    stream = ImageStream()
    stream.add_files_image(files)
    stream.set_landscape()
    bt = stream.to_zip()
    out = output_dir.join_file('commp.zip')
    out.path.write_bytes(bt.getvalue())


def main():
    test()


if __name__ == '__main__':
    main()
