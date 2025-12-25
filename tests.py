#!/usr/bin/env python3
import sys
import os

TEST_FILE = os.path.abspath(__file__)
ROOT_DIR = os.path.dirname(TEST_FILE)
MODULES_DIR = os.path.join(ROOT_DIR, 'sheet_stream')
#EXPORT_DIR = sp.UserFileSystem().userDownloads.concat('output', create=True)

sys.path.insert(0, MODULES_DIR)

from digitalized.documents.pdf.pdf_document import DocumentPdf
import pandas as pd
from soup_files import File, UserFileSystem, Directory, InputFiles

output = UserFileSystem().userDownloads

f = '/home/bruno/Documentos/OUTRO/2025-08 ORGANIZAÇÃO DE DOCUMENTOS DIGITALIZADOS COM O USO DA TECNOLOGIA OCR(1).pdf'


def test():

    _imp = DocumentPdf.build_interface().set_lib("fitz").set_bytes(File(f).path.read_bytes()).create()
    doc = DocumentPdf(_imp)
    doc.set_land_scape()
    doc.to_file(output.join_file('test.pdf'))


def main():
    test()


if __name__ == '__main__':
    main()
