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

from digitalized.documents.pdf import DocumentPdf, ConvertImageToPdf, ConvertPdfToImages
from digitalized.documents.image import ImageObject, ImageStream

def test():

    _input_dir = sp.Directory('/mnt/dados/ERO/2025-11-02 Cartas Toi WhatsApp/Output/GM E NM/OutputString')
    files = sp.InputFiles(_input_dir).images[0:10]
    img_stream = ImageStream()
    img_stream.add_files_image(files)

    images_zip = output_dir.join_file('images.zip')
    f = '/home/brunoc/Downloads/output/teste/imagem_para_pdf-1.pdf'

    conv = ConvertPdfToImages.create_from_document(DocumentPdf.create_from_file(sp.File(f)))
    final_zip = conv.to_zip_bytes()
    images_zip.path.write_bytes(final_zip.getvalue())


def main():
    test()


if __name__ == '__main__':
    main()
