#!/usr/bin/env python3
from __future__ import annotations
from io import BytesIO
from abc import abstractmethod, ABC
from typing import Literal, Any, Callable
from dataclasses import dataclass
from soup_files import File, Directory
from pytesseract import pytesseract
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import cv2

from digitalized.types.array import ArrayList
from digitalized.types.core import ObjectAdapter
from digitalized.ocr.tesseract import BinTesseract, CheckTesseractSystem
from digitalized.documents.image.image import ImageObject, LibImage
from digitalized.documents.erros import NotImplementedModuleImageError
from digitalized.ocr.error import (
    NotImplementedModuleTesseractError
)

try:
    import fitz
except ImportError:
    import pymupdf as fitz

try:
    import keras_ocr
    import numpy as np
except Exception as e:
    print(f"Alerta: {e}")

try:
    import easyocr
except Exception as err:
    print(f'Alerta: {err}')


LibOcr = Literal['pytesseract', 'easyocr', 'kerasocr']


def create_document_from_image(img: ImageObject) -> fitz.Document:
    # Converter o objeto de entrada para imagem OpenCV
    img_h, img_w = img.get_height(), img.get_width()

    # Converter a imagem para PDF (imagem de fundo)
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=(img_w, img_h))

    # Desenha a imagem original como fundo
    success, encoded_image = cv2.imencode('.png', img.to_image_opencv())
    img_stream = BytesIO(encoded_image.tobytes())
    pdf.drawImage(ImageReader(img_stream), 0, 0, width=img_w, height=img_h)

    # Adiciona o texto OCR como camada "invisível" sobre a imagem
    pdf.setFont("Helvetica", 8)
    pdf.setFillColorRGB(1, 1, 1, alpha=0)  # texto invisível
    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    final_bytes: bytes = buffer.read()
    buffer.close()
    return fitz.Document(stream=final_bytes, filetype="pdf")


def create_images_from_pdf(
            pdf_bytes: bytes, *,
            dpi=300,
            lib_image: LibImage = "pil",
        ) -> ArrayList[ImageObject]:
    _document = fitz.Document(stream=pdf_bytes, filetype="pdf")
    images = ArrayList()
    page: fitz.Page
    for page in _document:
        pix: fitz.Pixmap = page.get_pixmap(dpi=dpi)
        img_obj = ImageObject.create_from_bytes(
            pix.tobytes('png', jpg_quality=100), library=lib_image
        )
        images.append(img_obj)
    return images


def merge_pdf_bytes(pdf_bytes_list: ArrayList[bytes]) -> fitz.Document:
    """
    Mescla uma lista de bytes de PDFs em um único objeto fitz.Document.
    """
    if pdf_bytes_list.size() == 0:
        raise ValueError()

    # Cria um documento novo e vazio
    final_doc = fitz.open()
    for pdf_bytes in pdf_bytes_list:
        # Abre o PDF individual a partir dos bytes
        # O parâmetro 'stream' recebe os bytes, e 'filetype' ajuda a identificar o formato
        current_doc: fitz.Document = fitz.open(stream=pdf_bytes, filetype="pdf")
        # Insere todas as páginas do documento atual no documento final
        final_doc.insert_pdf(current_doc)
        # Fecha o documento temporário para liberar memória
        current_doc.close()
    return final_doc


def merge_pdf_fitz(pdf_documents: ArrayList[fitz.Document]) -> fitz.Document:
    """
    Mescla uma lista de bytes de PDFs em um único objeto fitz.Document.
    """
    if pdf_documents.size() == 0:
        raise ValueError()

    # Cria um documento novo e vazio
    final_doc = fitz.open()
    pdf_doc: fitz.Document
    for pdf_doc in pdf_documents:
        # Insere todas as páginas do documento atual no documento final
        final_doc.insert_pdf(pdf_doc)
        pdf_doc.close()
    return final_doc


# ======================================================================#
# Tipo para Easy Ocr
# ======================================================================#

@dataclass
class OCRResult:
    text: str
    confidence: float
    bbox: list[list[int]]  # [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]

    @property
    def x_min(self) -> int: return self.bbox[0][0]

    @property
    def y_min(self) -> int: return self.bbox[0][1]

    @property
    def width(self) -> int: return abs(self.bbox[1][0] - self.bbox[0][0])

    @property
    def y_avg(self) -> float:
        return sum(p[1] for p in self.bbox) / 4


def include_text_on_image_as_pdf(image: ImageObject, raw_results: list) -> TextRecognized:
    """
    Recebe um fitz.Document (com a imagem) e os resultados do OCR,
    retornando um PDF pesquisável (imagem + texto sobreposto).
    """
    # Converter o objeto de entrada para imagem OpenCV
    img_w, img_h = image.get_width(), image.get_height()

    # Converter a imagem para PDF (imagem de fundo)
    buffer = BytesIO()
    _pdf_canvas = canvas.Canvas(buffer, pagesize=(img_w, img_h))

    # Desenha a imagem original como fundo
    success, encoded_image = cv2.imencode('.png', image.to_image_opencv())
    img_stream = BytesIO(encoded_image.tobytes())
    _pdf_canvas.drawImage(ImageReader(img_stream), 0, 0, width=img_w, height=img_h)

    # Adiciona o texto OCR como camada "invisível" sobre a imagem
    _pdf_canvas.setFont("Helvetica", 8)
    _pdf_canvas.setFillColorRGB(1, 1, 1, alpha=0)  # texto invisível

    # Converter os resultados do EasyOCR para classe tipada
    results: list[OCRResult] = [
        OCRResult(text=res[1], confidence=res[2], bbox=res[0]) for res in raw_results
    ]
    item: OCRResult
    for item in results:
        if not item.text.strip():
            continue
        # No PDF (ReportLab), a origem (0,0) é no canto INFERIOR esquerdo.
        # No OCR/OpenCV, a origem é no canto SUPERIOR esquerdo.
        y_pdf = img_h - item.y_avg
        _pdf_canvas.drawString(item.x_min, y_pdf, item.text)

    _pdf_canvas.showPage()
    _pdf_canvas.save()
    buffer.seek(0)
    output_bytes = buffer.read()
    buffer.close()
    return TextRecognized(output_bytes)


class TextRecognized(object):
    """
        Recebe os bytes de uma imagem reconhecida com o OCR no formato PDF.
    """

    def __init__(self, bytes_recognized: bytes):
        self.__bytes_recognized: bytes = bytes_recognized
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

    def get_bytes(self) -> bytes:
        return self.__bytes_recognized

    def get_document(self) -> fitz.Document:
        _doc = fitz.Document(stream=self.__bytes_recognized, filetype="pdf")
        return _doc

    def to_file_pdf(self, file_path: File) -> None:
        self.get_document().save(file_path.absolute())

    def get_text(self) -> str | None:
        return self.get_document()[0].get_text()


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
        """
        :pararam kwargs['gpu']:
            bool usar CPU ou GPU
            
        :pararam kwargs['langs']:
            list[str] lista de linguagens, por, eng etc...
            
        :paraam kwargs['model_storage_directory']:
            diretório de dados para lang tesseract.
        """
        _gpu = False
        model_storage_directory = None
        _langs = []

        if kwargs:
            if 'gpu' in kwargs:
                _gpu = kwargs['gpu']
            if 'langs' in kwargs:
                _langs = kwargs['langs']
            if 'model_storage_directory' in kwargs:
                model_storage_directory = kwargs['model_storage_directory']

        self.reader: easyocr.Reader = easyocr.Reader(
            _langs,
            gpu=_gpu,
            model_storage_directory=model_storage_directory
        )

        self.func_txt: Callable[[ImageObject, list], TextRecognized] = include_text_on_image_as_pdf

    def __hash__(self) -> int:
        return hash(f'{self.get_bin_tess().__hash__()}easyocr')

    def get_current_library(self) -> str:
        return 'easyocr'

    def get_image_text(self, img: ImageObject) -> str:
        result: list[str] | list[dict] | list[Any] = self.reader.readtext(img.to_image_opencv())
        text = '\n'.join([res[1] for res in result])
        return text

    def get_recognized_text(self, img: ImageObject) -> TextRecognized:
        results: list = self.reader.readtext(img.to_image_opencv())
        return self.func_txt(img, results)

    @classmethod
    def builder(cls) -> BuildEasyOcr:
        return BuildEasyOcr()


class BuildEasyOcr(object):

    def __init__(self):
        self.kwargs = dict()
        self.check: CheckTesseractSystem = CheckTesseractSystem.build()
        self.kwargs['langs'] = self.check.get_langs()
        self.kwargs['gpu'] = False
        if self.check.get_tess_data_dir() is not None:
            self.kwargs['model_storage_directory'] = self.check.get_tess_data_dir().absolute()

    def set_gpu(self, gpu: bool) -> BuildEasyOcr:
        self.kwargs['gpu'] = gpu
        return self

    def set_file_tesseract(self, file: File) -> BuildEasyOcr:
        self.check.set_file_tesseract(file)
        self.kwargs['path_tesseract'] = file.absolute()
        return self

    def set_tess_data_dir(self, d: Directory) -> BuildEasyOcr:
        self.check.set_tess_data_dir(d)
        self.kwargs['model_storage_directory'] = d.absolute()
        return self

    def set_langs(self, langs: list[str]) -> BuildEasyOcr:
        self.kwargs['langs'] = langs
        return self

    def build(self) -> ImplementEasyOcr:
        return ImplementEasyOcr(kwargs=self.kwargs)


# ======================================================================#
# Implementação com keras-ocr
# ======================================================================#


class ImplementKerasOcr(InterfaceTesseractOcr):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        """
        :param kwargs['scale']: float para redimensionar imagem se necessário.
        """
        # O keras-ocr baixa os pesos automaticamente na primeira execução
        self.pipeline = keras_ocr.pipeline.Pipeline()
        self.func_txt: Callable[[ImageObject, list], TextRecognized] = include_text_on_image_as_pdf

    def __hash__(self) -> int:
        return hash(f'{self.get_bin_tess().__hash__()}kerasocr')

    def get_current_library(self) -> str:
        return 'kerasocr'

    def get_image_text(self, img: ImageObject) -> str:
        # keras-ocr espera uma lista de imagens ou uma imagem (numpy array)
        # O método read trabalha com RGB
        _im = img.to_image_opencv()
        _im_rgb = cv2.cvtColor(_im, cv2.COLOR_BGR2RGB)

        # predictions é uma lista de listas (uma para cada imagem enviada)
        predictions: list[tuple[str, Any]] = self.pipeline.recognize([_im_rgb])[0]
        # predictions[i] = (texto, box)
        text = '\n'.join([res[0] for res in predictions])
        return text

    def get_recognized_text(self, img: ImageObject) -> TextRecognized:
        _im = img.to_image_opencv()
        _im_rgb = cv2.cvtColor(_im, cv2.COLOR_BGR2RGB)
        predictions: list[tuple[str, Any]] = self.pipeline.recognize([_im_rgb])[0]

        # Adaptar o formato do keras-ocr para o formato esperado pelo include_text_on_image_as_pdf
        # Keras-ocr retorna: (text, box_array)
        # O formato esperado na sua função é: [res[0]=bbox, res[1]=text, res[2]=confidence]
        raw_results = []
        for text, box in predictions:
            # Keras-ocr não retorna confiança por padrão na tupla básica,
            # setamos 1.0 ou extraímos se disponível.
            raw_results.append([box.tolist(), text, 1.0])
        return self.func_txt(img, raw_results)

    @classmethod
    def builder(cls) -> BuildKerasOcr:
        return BuildKerasOcr()


class BuildKerasOcr(object):
    def __init__(self):
        self.kwargs = dict()
        # Você pode adicionar configurações de detector/reconhecedor aqui se desejar

    def build(self) -> ImplementKerasOcr:
        return ImplementKerasOcr(**self.kwargs)


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
    def builder_easyocr(cls) -> BuildEasyOcr:
        return BuildEasyOcr()

    @classmethod
    def crate(cls, lib_ocr: LibOcr = "pytesseract", **kwargs) -> TesseractOcr:
        if lib_ocr == "pytesseract":
            return cls(ImplementPyTesseract(**kwargs))
        elif lib_ocr == "easyocr":
            if kwargs:
                return cls(ImplementEasyOcr(**kwargs))
            else:
                return cls(ImplementEasyOcr.builder().build())
        elif lib_ocr == "kerasocr":
            if kwargs:
                return cls(ImplementKerasOcr(**kwargs))
            else:
                return cls(ImplementKerasOcr.builder().build())
        else:
            raise NotImplementedModuleTesseractError()


class RecognizePdf(object):

    def __init__(self, tess: TesseractOcr):
        self.tess: TesseractOcr = tess

    def recognize_pdf(self, pdf_bytes: bytes, *, dpi: int = 300) -> fitz.Document:
        doc_images: ArrayList[ImageObject] = create_images_from_pdf(pdf_bytes, dpi=dpi)
        recognized_docs: ArrayList[fitz.Document] = ArrayList()
        for im in doc_images:
            txt = self.tess.get_recognized_text(im)
            recognized_docs.append(txt.get_document())
        return merge_pdf_fitz(recognized_docs)

    @classmethod
    def crate(cls, lib_ocr: LibOcr = "pytesseract", **kwargs) -> RecognizePdf:
        _tess = TesseractOcr.crate(lib_ocr, **kwargs)
        return cls(_tess)


__all__ = [
    'TesseractOcr',
    'TextRecognized',
    'RecognizePdf',
]
