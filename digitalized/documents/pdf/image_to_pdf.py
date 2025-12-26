#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Módulo para trabalhar com imagens
"""

from __future__ import annotations
from io import BytesIO
from soup_files import File, Directory, ProgressBarAdapter
from abc import ABC, abstractmethod
from typing import Union, Any, Literal

from digitalized.documents.pdf import PageDocumentPdf, LibPDF, DocumentPdf
from digitalized.documents.image import ImageObject, ImageExtension, LibImage, ImageStream
from digitalized.io import ZipOutputStream
from digitalized.types.core import ObjectAdapter

MOD_IMG_PIL: bool = False
MOD_IMG_OPENCV: bool = False
MOD_PYPDF: bool = False
MOD_CANVAS: bool = False

try:
    import pymupdf as fitz
    MODULE_FITZ = True
except ImportError:
    try:
        import fitz
        MODULE_FITZ = True
    except ImportError as e:
        raise ImportError(f'{e}')

try:
    from reportlab.pdfgen import canvas
    from reportlab.pdfgen.canvas import Canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.utils import ImageReader
    MOD_CANVAS = True
except ImportError:
    canvas = object
    Canvas = object
    letter = (612, 792)
    ImageReader = object
    MOD_CANVAS = False

try:
    from PIL import Image
    from PIL import ImageOps, ImageFilter
    MOD_IMG_PIL = True
except ImportError:
    Image = object
    Image.Image = object


LibImageToPdf = Literal["fitz", "canvas", "pil"]


class InterfaceConvertImagesToPdf(ABC):

    def __init__(self, *, a4: bool = False, landscape: bool = False, **kwargs) -> None:
        self._a4: bool = a4
        self._landscape: bool = landscape

    @abstractmethod
    def get_current_library(self) -> LibImageToPdf:
        pass

    def set_landscape(self, landscape: bool):
        self._landscape = landscape

    def set_a4(self, a4: bool):
        self._a4 = a4

    @abstractmethod
    def to_document(self, img_stream: ImageStream) -> DocumentPdf:
        pass

    def to_file_pdf(self, img_stream: ImageStream, *, output_file: File) -> None:
        self.to_document(img_stream).to_file(output_file)

    def to_zip_document(self, img_stream: ImageStream, *, prefix: str = 'imagem_para_pdf') -> BytesIO:
        zip_stream = ZipOutputStream('pdf')
        return zip_stream.save_zip(
            [self.to_document(img_stream).to_bytes()],
            prefix=prefix
        )


class ImplementImagesToPdfCanvas(InterfaceConvertImagesToPdf):

    def __init__(self, *, a4: bool = False, landscape: bool = False, **kwargs) -> None:
        super().__init__(a4=a4, landscape=landscape, **kwargs)

    def get_current_library(self) -> LibImageToPdf:
        return "canvas"

    def to_document(self, img_stream: ImageStream) -> DocumentPdf:
        if not MOD_CANVAS:
            raise RuntimeError("A biblioteca 'reportlab' não está disponível.")
        if img_stream.size() == 0:
            raise ValueError("A lista de imagens não pode estar vazia.")

        buffer = BytesIO()
        if self._landscape:
            img_stream.set_landscape()

        # Lógica para determinar o tamanho inicial da página
        first_img_obj: ImageObject = img_stream.get_first()
        first_img_width, first_img_height = first_img_obj.get_width(), first_img_obj.get_height()

        if self._a4:
            # Se for A4, o tamanho da página é fixo desde o início
            c = canvas.Canvas(buffer, pagesize=letter)
        else:
            # Se não for A4, o canvas é inicializado com as dimensões da primeira imagem
            c = canvas.Canvas(buffer, pagesize=(first_img_width, first_img_height))

        img_bytes: BytesIO = BytesIO(first_img_obj.to_bytes())
        img_bytes.seek(0)
        img_reader = ImageReader(img_bytes)

        if self._a4:
            # Lógica de redimensionamento e centralização para A4
            page_width, page_height = letter
            scale_factor = min(page_width / first_img_width, page_height / first_img_height)
            scaled_width = first_img_width * scale_factor
            scaled_height = first_img_height * scale_factor
            x_pos = (page_width - scaled_width) / 2
            y_pos = (page_height - scaled_height) / 2
            c.drawImage(img_reader, x_pos, y_pos, width=scaled_width, height=scaled_height)
        else:
            # Desenha a imagem preenchendo a página que já tem o tamanho correto
            c.drawImage(img_reader, 0, 0, width=first_img_width, height=first_img_height)

        # Processa as imagens restantes
        for num, img_obj in enumerate(img_stream[1:], 1):
            img_bytes = BytesIO(img_obj.to_bytes())
            img_bytes.seek(0)
            img_reader = ImageReader(img_bytes)
            img_width, img_height = img_obj.get_width(), img_obj.get_height()
            # Cria nova página
            c.showPage()

            if self._a4:
                # O tamanho da página é fixo, apenas desenha a imagem centralizada e redimensionada
                page_width, page_height = letter
                scale_factor = min(page_width / img_width, page_height / img_height)
                scaled_width = img_width * scale_factor
                scaled_height = img_height * scale_factor
                x_pos = (page_width - scaled_width) / 2
                y_pos = (page_height - scaled_height) / 2
                c.drawImage(img_reader, x_pos, y_pos, width=scaled_width, height=scaled_height)
            else:
                # Ajusta o tamanho da nova página para as dimensões da imagem atual
                c.setPageSize((img_width, img_height))
                c.drawImage(img_reader, 0, 0, width=img_width, height=img_height)

        c.save()
        buffer.seek(0)
        bt = buffer.getvalue()
        buffer.close()
        return DocumentPdf.create_from_bytes(bt)


class ImplementImagesToPdfPil(InterfaceConvertImagesToPdf):
    """
        Classe para converter uma lista de ImageObject em um DocumentPdf
        usando a biblioteca Pillow (PIL).
    """

    def __init__(self, *, a4: bool = False, landscape: bool = False, **kwargs) -> None:
        super().__init__(a4=a4, landscape=landscape, **kwargs)

    def get_current_library(self) -> LibImageToPdf:
        return "pil"

    def to_document(self, img_stream: ImageStream) -> DocumentPdf:
        if not MOD_IMG_PIL:
            raise RuntimeError("A biblioteca 'Pillow' não está disponível.")
        if img_stream.size() == 0:
            raise ValueError("A lista de imagens não pode estar vazia.")
        if self._landscape:
            img_stream.set_landscape()

        pil_images_to_save = []
        if self._a4:
            # Obtém as dimensões da página A4 em píxels
            # Usando uma resolução de 100 DPI para consistência
            page_width, page_height = letter  # Padrão do reportlab
            page_size = (int(page_width), int(page_height))

            max_num = img_stream.size()
            for num, img_obj in enumerate(img_stream):
                original_pil_image = img_obj.to_image_pil()
                img_width, img_height = original_pil_image.size

                # Calcula o fator de escala para ajustar a imagem à página, mantendo a proporção
                scale_factor = min(page_size[0] / img_width, page_size[1] / img_height)
                scaled_width = int(img_width * scale_factor)
                scaled_height = int(img_height * scale_factor)

                # Redimensiona a imagem
                resized_image = original_pil_image.resize(
                    (scaled_width, scaled_height), Image.Resampling.LANCZOS
                )

                # Criar imagem de fundo branca com o tamanho A4
                new_image = Image.new('RGB', page_size, 'white')

                # Centraliza a imagem redimensionada na nova imagem
                x_pos = (page_size[0] - scaled_width) // 2
                y_pos = (page_size[1] - scaled_height) // 2
                new_image.paste(resized_image, (x_pos, y_pos))

                pil_images_to_save.append(new_image)
        else:
            # Para a4 = False, não precisa redimensionar. Pillow ajusta o tamanho da página.
            pil_images_to_save = [img.to_image_pil() for img in img_stream]

        buffer = BytesIO()
        try:
            first_image_pil = pil_images_to_save[0]
            other_images_pil = pil_images_to_save[1:]

            first_image_pil.save(
                buffer,
                'PDF',
                resolution=140.0,
                save_all=True,
                append_images=other_images_pil
            )
        except Exception as e:
            raise RuntimeError(f"Erro ao criar o PDF com Pillow: {e}")

        buffer.seek(0)
        bt = buffer.getvalue()
        buffer.close()
        return DocumentPdf.create_from_bytes(bt)


class ImplementImagesToPdfFitz(InterfaceConvertImagesToPdf):
    """
        Classe para converter uma lista de ImageObject em um DocumentPdf
        usando a biblioteca PyMuPDF (fitz).
    """

    def __init__(self, *, a4: bool = False, landscape: bool = False, **kwargs) -> None:
        super().__init__(a4=a4, landscape=landscape, **kwargs)

    def get_current_library(self) -> LibImageToPdf:
        return "fitz"

    def to_document(self, img_stream: ImageStream) -> DocumentPdf:
        max_num: int = img_stream.size()
        if max_num == 0:
            raise ValueError('Adicione imagens para prosseguir')

        buffer = BytesIO()
        doc = fitz.open()  # Cria um novo documento PDF vazio

        for num, img_obj in enumerate(img_stream):
            if self._landscape:
                img_obj.set_landscape()

            # Converte a imagem para bytes
            img_bytes_obj = img_obj.to_bytes()
            # Obtém as dimensões da imagem e da página
            img_width, img_height = img_obj.get_width(), img_obj.get_height()

            # Adiciona uma nova página ao documento
            if self._a4:
                page = doc.new_page()
            else:
                page = doc.new_page(width=img_width, height=img_height)

            # Cria um retângulo que preenche a página
            rect = page.rect
            page_width, page_height = rect.width, rect.height

            # Calcula o fator de escala para ajustar a imagem à página
            scale_factor_w = page_width / img_width
            scale_factor_h = page_height / img_height
            scale_factor = min(scale_factor_w, scale_factor_h)

            # Ajusta o retângulo de inserção para centralizar a imagem
            scaled_width = img_width * scale_factor
            scaled_height = img_height * scale_factor
            x0 = (page_width - scaled_width) / 2
            y0 = (page_height - scaled_height) / 2

            # Insere a imagem no retângulo calculado
            page.insert_image(
                fitz.Rect(x0, y0, x0 + scaled_width, y0 + scaled_height),
                stream=img_bytes_obj
            )

        # Salva o documento no buffer de memória
        doc.save(buffer)
        doc.close()
        buffer.seek(0)
        bt = buffer.getvalue()
        buffer.close()
        return DocumentPdf.create_from_bytes(bt)


class ConvertImageToPdf(ObjectAdapter):
    """
        Classe com padrão ADAPTER para converter Imagens em documento(s) PDF.
    """

    def __init__(self, images_to_pdf: InterfaceConvertImagesToPdf) -> None:
        super().__init__()
        self._images_to_pdf = images_to_pdf

    def get_implementation(self) -> Any:
        return self._images_to_pdf

    def get_current_library(self) -> LibImageToPdf:
        return self._images_to_pdf.get_current_library()

    def to_document(self, img_stream: ImageStream) -> DocumentPdf:
        return self._images_to_pdf.to_document(img_stream)

    def to_zip_document(self, img_stream: ImageStream, *, prefix: str = 'imagem_para_pdf') -> BytesIO:
        return self._images_to_pdf.to_zip_document(img_stream, prefix=prefix)

    def to_file_pdf(self, img_stream: ImageStream, *, output_file: File) -> None:
        self._images_to_pdf.to_file_pdf(img_stream, output_file=output_file)

    @classmethod
    def create(
                cls,
                *,
                a4: bool = False,
                landscape: bool = False,
                lib_images_to_pdf: LibImageToPdf = "fitz"
            ) -> ConvertImageToPdf:
        if lib_images_to_pdf == "fitz":
            return cls(ImplementImagesToPdfFitz(a4=a4, landscape=landscape))
        elif lib_images_to_pdf == "canvas":
            return cls(ImplementImagesToPdfCanvas(a4=a4, landscape=landscape))
        elif lib_images_to_pdf == "pil":
            return cls(ImplementImagesToPdfPil(a4=a4, landscape=landscape))
        else:
            raise NotImplementedError()
