#!/usr/bin/env python3
from __future__ import annotations
from io import BytesIO
from abc import abstractmethod, ABC
from typing import Union, Literal, Any
from pandas import DataFrame
from soup_files import File
from pytesseract import pytesseract
import easyocr
import os.path
from reportlab.pdfgen import canvas
#from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from PIL import Image
import cv2
from digitalized.types.core import ObjectAdapter
from digitalized.ocr.tesseract import BinTesseract, CheckTesseractSystem
from digitalized.documents.image.image import ImageObject
from digitalized.documents.erros import NotImplementedModuleImageError
from digitalized.ocr.error import (
    NotImplementedModuleTesseractError
)

LibOcr = Literal['pytesseract', 'easyocr']


class TextRecognized(object):
    """
        Recebe os bytes de uma imagem reconhecida com o OCR no formato PDF.
    """

    def __init__(self, bytes_recognized: bytes):
        self.bytes_recognized: bytes = bytes_recognized
        self.__text_document: str | None = None

        self.list_bad_char: list[str] = [
            ':', ',', ';', '$', '=',
            '!', '}', '{', '(', ')',
            '|', '\\', '‘', '*'
                            '¢', '“', '\'', '¢', '"',
            '#', '.', '<', '?', '>',
            '»', '@', '+', '[', ']',
            '%', '~', '¥', '♀',
        ]

    @property
    def is_empty(self) -> bool:
        txt = self.to_string()
        if (txt is None) or (txt == '') or (txt == 'nas'):
            return True
        return False

    def to_string(self) -> str | None:
        pass


class InterfaceTesseractOcr(ABC):

    def __init__(self, **kwargs):
        self._bin_tess: BinTesseract = BinTesseract.builder().build()

    @abstractmethod
    def get_current_library(self) -> LibOcr:
        pass

    @abstractmethod
    def get_image_text(self, img: ImageObject) -> str:
        pass

    @abstractmethod
    def get_recognized_text(self, img: ImageObject) -> TextRecognized:
        pass

    def get_bin_tess(self) -> BinTesseract:
        return self._bin_tess

    @abstractmethod
    def __hash__(self) -> int:
        pass


# ======================================================================#
# Implementação com pytesseract
# ======================================================================#
class ImplementPyTesseract(InterfaceTesseractOcr):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._mod_py_tesseract = pytesseract
        self._mod_py_tesseract.tesseract_cmd = self.get_bin_tess().get_path_tesseract().absolute()

    def __hash__(self) -> int:
        return hash(f'{self.get_bin_tess().__hash__()}pytesseract')

    def get_current_library(self) -> LibOcr:
        return "pytesseract"

    def __get_tess_dir_config(self) -> str | None:
        """
        https://github.com/h/pytesseract

        Example config: r'--tessdata-dir "C:\Program Files (x86)\Tesseract-OCR\tessdata"'
        tessdata_dir_config = r'--tessdata-dir <replace_with_your_tessdata_dir_path>'
        It's important to add double quotes around the dir path.
        """
        # Caminho para os dados de idioma, por, eng etc...
        # os.environ["TESSDATA_PREFIX"] = self.tess_data_dir.absolute()
        if self.get_bin_tess().get_tessdata_dir() is None:
            return ''
        if not self.get_bin_tess().get_tessdata_dir().path.exists():
            return ''
        return r'--tessdata-dir "{}"'.format(self.get_bin_tess().get_tessdata_dir().absolute())

    def get_image_text(self, img: ImageObject) -> str:
        if img.get_current_library() == "opencv":
            _im = img.to_image_opencv()
        elif img.get_current_library() == "pil":
            _im = img.to_image_pil()
        else:
            raise NotImplementedModuleImageError(
                f'{__class__.__name__} módulo imagem não implementado {img.get_current_library()}'
            )

        if self.get_bin_tess().get_lang() is None:
            return self._mod_py_tesseract.image_to_string(_im, config=self.__get_tess_dir_config())
        else:
            return self._mod_py_tesseract.image_to_string(
                _im,
                lang=self.get_bin_tess().get_lang(),
                config=self.__get_tess_dir_config()
            )

    def get_recognized_text(self, img: ImageObject) -> TextRecognized:
        if img.get_current_library() == "opencv":
            _im = img.to_image_opencv()
        elif img.get_current_library() == "pil":
            _im = img.to_image_pil()
        else:
            raise NotImplementedModuleImageError(
                f'{__class__.__name__} módulo imagem não implementado {img.get_current_library()}'
            )

        bt: bytes = self._mod_py_tesseract.image_to_pdf_or_hocr(
            _im,
            lang=self.get_bin_tess().get_lang(),
            config=self.__get_tess_dir_config(),
            extension='pdf',
        )
        return TextRecognized(bt)


# ======================================================================#
# Implementação com easyocr
# ======================================================================#
class ImplementEasyOcr(InterfaceTesseractOcr):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if kwargs:
            if 'gpu' in kwargs:
                self.reader: easyocr.Reader = easyocr.Reader(
                    [self.get_bin_tess().get_lang()], gpu=kwargs['gpu']
                )
        else:
            self.reader: easyocr.Reader = easyocr.Reader(
                [self.get_bin_tess().get_lang()], gpu=False
            )

    def __hash__(self) -> int:
        return hash(f'{self.get_bin_tess().__hash__()}easyocr')

    def get_current_library(self) -> str:
        return 'easyocr'

    def get_image_text(self, img: ImageObject) -> str:
        result: list[str] | list[dict] | list[Any] = self.reader.readtext(img.to_image_opencv())
        text = '\n'.join([res[1] for res in result])
        return text

    def get_recognized_text(self, img: ImageObject) -> TextRecognized:
        # Converter o objeto de entrada para imagem OpenCV
        img_cv = img.to_image_opencv()
        img_h, img_w = img_cv.shape[:2]

        # Reconhecer o texto com EasyOCR
        results: list = self.reader.readtext(img_cv)

        # Converter a imagem para PDF (imagem de fundo)
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=(img_w, img_h))

        # Desenha a imagem original como fundo
        img_pil = Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))
        pdf.drawImage(ImageReader(img_pil), 0, 0, width=img_w, height=img_h)

        # Adiciona o texto OCR como camada "invisível" sobre a imagem
        pdf.setFont("Helvetica", 8)
        pdf.setFillColorRGB(1, 1, 1, alpha=0)  # texto invisível

        for (bbox, text, conf) in results:
            if not text.strip():
                continue
            # Coordenadas do bounding box (EasyOCR retorna 4 pontos)
            (x1, y1), (x2, y2), (x3, y3), (x4, y4) = bbox

            # Média da posição vertical
            avg_y = (y1 + y2 + y3 + y4) / 4

            # Posição invertida (PDF tem origem no canto inferior esquerdo)
            y_pdf = img_h - avg_y

            # Largura estimada
            text_width = abs(x2 - x1)
            pdf.drawString(x1, y_pdf, text)

        pdf.showPage()
        pdf.save()
        buffer.seek(0)
        # Retorna como TextRecognized (bytes do PDF com texto embutido)
        text_rec = TextRecognized(buffer.read())
        return text_rec


class TesseractOcr(ObjectAdapter):

    def __init__(self, interface_ocr: InterfaceTesseractOcr):
        super().__init__()

        self.__implement_ocr: InterfaceTesseractOcr = interface_ocr

    def __hash__(self):
        return self.get_implementation().__hash__()

    def hash(self) -> int:
        return self.__hash__()

    def get_implementation(self) -> InterfaceTesseractOcr:
        return self.__implement_ocr

    def get_bin_tess(self) -> BinTesseract:
        return self.__implement_ocr.get_bin_tess()

    def get_current_library(self) -> str:
        return self.__implement_ocr.get_current_library()

    def get_image_text(self, img: ImageObject) -> str:
        return self.__implement_ocr.get_image_text(img)

    def get_recognized_text(self, img: ImageObject) -> TextRecognized:
        return self.__implement_ocr.get_recognized_text(img)

    @classmethod
    def crate(cls, lib_ocr: LibOcr = "pytesseract", **kwargs) -> TesseractOcr:
        if lib_ocr == "pytesseract":
            return cls(ImplementPyTesseract(**kwargs))
        elif lib_ocr == "easyocr":
            return cls(ImplementEasyOcr(**kwargs))
        else:
            raise NotImplementedModuleTesseractError()


__all__ = ['TesseractOcr', 'TextRecognized']
