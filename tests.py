#!/usr/bin/env python3
import sys
import os

import fitz
import soup_files as sp

TEST_FILE = os.path.abspath(__file__)
ROOT_DIR = os.path.dirname(TEST_FILE)
MODULES_DIR = os.path.join(ROOT_DIR, 'sheet_stream')

output_dir = sp.UserFileSystem().userDownloads.concat('output', create=True)

sys.path.insert(0, MODULES_DIR)

from digitalized.documents.pdf.pdf_document import DocumentPdf, merge_pdf_bytes
from digitalized.ocr.recognize import RecognizePdf
import pandas as pd


def test():

    _input_dir = sp.Directory('/mnt/dados/BACKUPS-PC/2025-09-23 MEU DRIVE/Documentos/60_DOCS DIVERSOS E COMPROVANTES/LAGOA AZUL/Lagoa azul contrato')
    files = sp.InputFiles(_input_dir).pdfs

    rec = RecognizePdf.crate()
    f = files[1]
    print(f.basename())
    doc = rec.recognize_pdf(DocumentPdf.create_from_file(f))
    doc.to_file(output_dir.join_file("ocr.pdf"))


def main():
    test()


if __name__ == '__main__':
    main()
