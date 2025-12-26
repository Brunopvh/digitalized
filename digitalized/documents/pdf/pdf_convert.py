"""
Módulo para converter PDF em Imagens
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from io import BytesIO
from typing import Any, Literal
from soup_files import Directory, File
from digitalized.documents.image import ImageObject, ImageStream, LibImage, ImageExtension
from digitalized.documents.pdf import PageDocumentPdf, DocumentPdf
from digitalized.types.core import ObjectAdapter
from digitalized.io import ZipOutputStream

try:
    import pymupdf as fitz
    MODULE_FITZ = True
except ImportError:
    try:
        import fitz
        MODULE_FITZ = True
    except ImportError as e:
        raise ImportError(f'{e}')

LibPdfToImage = Literal["fitz"]


class InterfacePdfToImages(ABC):

    @abstractmethod
    def get_current_library(self) -> LibPdfToImage:
        pass

    @abstractmethod
    def get_document(self) -> DocumentPdf:
        pass

    @abstractmethod
    def to_images(
                self, *,
                dpi: int = 250,
                lib_image: LibImage = "opencv",
                image_extension: ImageExtension = "png",
            ) -> ImageStream:
        """
            Converte as páginas PDF do documento em lista de objetos imagem ImageObject

        :param dpi: DPI do documento, resolução da renderização.
        :param lib_image: Biblioteca para manipular imagens PIL/OpenCv
        :param image_extension: Extensão das imagens a serem salvas.
        """
        pass

    @abstractmethod
    def to_files_image(
            self,
            output_dir: Directory, *,
            replace: bool = False,
            dpi: int = 250,
            lib_image: LibImage = "opencv",
            prefix: str = None,
            image_extension: ImageExtension = "png",
            ) -> None:
        """
            Converte todas as páginas do documento em objeto de imagem e salva no disco
        em formato de imagem PNG.
        """
        pass

    @abstractmethod
    def to_zip_bytes(
                self, *,
                dpi: int = 250,
                lib_image: LibImage = "opencv",
                image_extension: ImageExtension = "png",
            ) -> BytesIO:
        pass


class ImplementConvertPdfToImagesFitz(InterfacePdfToImages):

    def __init__(self, document: DocumentPdf):
        super().__init__()
        if document.get_current_library() == "fitz":
            self._document: DocumentPdf = document
        else:
            _builder = DocumentPdf.build_interface().set_bytes(document.to_bytes())
            self._document = DocumentPdf(_builder.set_lib("fitz").create())

    def __hash__(self) -> int:
        raise NotImplementedError()

    def get_current_library(self) -> LibPdfToImage:
        return "fitz"

    def get_document(self) -> DocumentPdf:
        return self._document

    def to_zip_bytes(
                self, *,
                dpi: int = 250,
                lib_image: LibImage = "pil",
                image_extension: ImageExtension = "png",
            ) -> BytesIO:
        zip_stream = ZipOutputStream(image_extension)
        _image_obj: ImageObject
        images_list: ImageStream = self.to_images(
            dpi=dpi, lib_image=lib_image, image_extension=image_extension
        )

        return zip_stream.save_zip(
            images_list.apply(lambda _image_obj: _image_obj.to_bytes()),
            prefix='pdf_para_imagem'
        )

    def to_images(
                self, *,
                dpi: int = 200,
                lib_image: LibImage = "pil",
                image_extension: ImageExtension = "png",
            ) -> ImageStream:
        """
            Converte um Documento em lista de objetos ImageObject.
        """
        final_images = ImageStream()
        pages_fitz: list[PageDocumentPdf] = self._document.to_pages()
        _count = len(pages_fitz)
        pg: PageDocumentPdf
        for n, pg in enumerate(pages_fitz):
            pix: fitz.Pixmap = pg.get_real_module().get_pixmap(dpi=dpi)
            img = ImageObject.create_from_bytes(
                pix.tobytes('png', jpg_quality=100),
                library=lib_image,
            )
            final_images.add_image(img)
        return final_images

    def to_files_image(
                self,
                output_dir: Directory, *,
                replace: bool = False, dpi: int = 250,
                lib_image: LibImage = "opencv",
                prefix: str = None,
                image_extension: ImageExtension = "png",
            ) -> None:
        """
            Converter as páginas do documento em imagem e salvar no disco.
        """
        if prefix is None:
            prefix = "pdf_para_imagem"
        _pages: list[PageDocumentPdf] = self.get_document().to_pages()
        _count = len(_pages)
        for n, pg in enumerate(_pages):
            out_file: File = output_dir.join_file(f'{prefix}-{n+1}.{image_extension}')
            if not replace:
                if out_file.exists():
                    continue
            pix: fitz.Pixmap = pg.get_real_module().get_pixmap(dpi=dpi)
            img = ImageObject.create_from_bytes(
                pix.tobytes(image_extension, jpg_quality=100),
                library=lib_image,
            )
            img.set_output_extension(image_extension)
            img.to_file(out_file)


class ConvertPdfToImages(ObjectAdapter):

    def __init__(self, converter: InterfacePdfToImages):
        super().__init__()
        self.converter: InterfacePdfToImages = converter

    def get_real_module(self) -> Any:
        raise NotImplementedError()

    def get_implementation(self) -> InterfacePdfToImages:
        return self.converter

    def get_current_library(self) -> LibPdfToImage:
        return self.converter.get_current_library()

    def get_document(self) -> DocumentPdf:
        return self.converter.get_document()

    def to_images(
                self, *,
                dpi: int = 250,
                lib_image: LibImage = "opencv",
                image_extension: ImageExtension = "png"
            ) -> ImageStream:
        return self.converter.to_images(
            dpi=dpi, lib_image=lib_image, image_extension=image_extension
        )

    def to_files_image(
                self,
                output_dir: Directory, *,
                replace: bool = False,
                dpi: int = 250,
                lib_image: LibImage = "opencv",
                prefix: str = None,
                image_extension: ImageExtension = "png"
            ) -> None:
        return self.converter.to_files_image(
            output_dir=output_dir,
            replace=replace,
            dpi=dpi,
            lib_image=lib_image,
            prefix=prefix,
            image_extension=image_extension,
        )

    def to_zip_bytes(
                self, *,
                dpi: int = 250,
                lib_image: LibImage = "opencv",
                image_extension: ImageExtension = "png"
            ) -> BytesIO:
        return self.converter.to_zip_bytes(
            dpi=dpi, lib_image=lib_image, image_extension=image_extension
        )

    @classmethod
    def create_from_document(
                cls,
                document: DocumentPdf, *,
                lib_pdf_to_image: LibPdfToImage = "fitz",
            ) -> "ConvertPdfToImages":
        if lib_pdf_to_image == "fitz":
            return cls(ImplementConvertPdfToImagesFitz(document))
        else:
            raise NotImplementedError()


