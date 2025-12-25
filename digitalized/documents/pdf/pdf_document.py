#!/usr/bin/env python3
#
"""
    Módulo para trabalhar com imagens
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from io import BytesIO
from typing import Union, Any
import pandas as pd
from soup_files import File, Directory, LibraryDocs, InputFiles, ProgressBarAdapter, JsonConvert
from digitalized.types.core import ObjectAdapter, BuilderInterface
from digitalized.types.array import ArrayList, ArrayString
from digitalized.documents.erros import NotImplementedModulePdfError
from digitalized.documents.pdf.pdf_page import (
    PageDocumentPdf, InterfacePagePdf, LibPDF, MODULE_FITZ, MODULE_PYPDF, BuilderInterfacePagePdf
)

if MODULE_PYPDF:
    from pypdf import PdfWriter, PdfReader, PageObject

if MODULE_FITZ:
    try:
        import fitz
        MODULE_FITZ = True
    except ImportError:
        try:
            import pymupdf as fitz
            MODULE_FITZ = True
        except ImportError:
            pass


#======================================================================#
# Funções para juntar/dividir documentos
#======================================================================#
def merge_pdf_bytes(
            pdf_bytes_list: list[bytes], *,
            lib_pdf: LibPDF = "fitz"
        ) -> Union[fitz.Document, PdfReader]:
    """
    Mescla uma lista de bytes de PDFs
    """
    if len(pdf_bytes_list) == 0:
        raise ValueError()

    if lib_pdf == "fitz":
        # Cria um documento novo e vazio
        final_doc = fitz.open()
        for pdf_bytes in pdf_bytes_list:
            # Abre o PDF individual a partir dos bytes
            current_doc: fitz.Document = fitz.open(stream=pdf_bytes, filetype="pdf")
            # Insere todas as páginas do documento atual no documento final
            #final_doc.insert_pdf(current_doc)
            page: fitz.Page
            for page in current_doc:
                final_doc.insert_pdf(page.parent, from_page=page.number, to_page=page.number)
            # Fecha o documento temporário para liberar memória
            current_doc.close()
        return final_doc
    elif lib_pdf == "pypdf":
        raise NotImplementedError()
    else:
        raise NotImplementedModulePdfError()


def merge_documents(
            pdf_documents: list[fitz.Document | PdfReader], *, lib_pdf: LibPDF = "fitz",
        ) -> Union[fitz.Document | PdfReader]:
    """
    Mescla uma lista de documentos PDFs.
    """
    if len(pdf_documents) == 0:
        raise ValueError()

    if lib_pdf == "fitz":
        # Cria um documento novo e vazio
        final_doc = fitz.open()
        pdf_doc: fitz.Document
        for pdf_doc in pdf_documents:
            # Insere todas as páginas do documento atual no documento final
            _page: fitz.Page
            for _page in pdf_doc:
                final_doc.insert_pdf(_page.parent, from_page=_page.number, to_page=_page.number)
            pdf_doc.close()
        return final_doc
    elif lib_pdf == "pypdf":
        raise NotImplementedError()
    else:
        raise NotImplementedModulePdfError()


def merge_pages_documents(
            pages_pdf: list[fitz.Page | PageObject], *, lib_pdf: LibPDF = "fitz",
        ) -> Union[fitz.Document | PdfReader]:
    """
    Mescla uma lista de documentos PDFs.
    """
    if len(pages_pdf) == 0:
        raise ValueError()

    if lib_pdf == "fitz":
        # Cria um documento novo e vazio
        final_doc = fitz.open()

        # Insere todas as páginas do documento atual no documento final
        _page: fitz.Page
        for _page in pages_pdf:
            final_doc.insert_pdf(_page.parent, from_page=_page.number, to_page=_page.number)
        return final_doc
    elif lib_pdf == "pypdf":
        raise NotImplementedError()
    else:
        raise NotImplementedModulePdfError()


class InterfaceDocumentPdf(ABC):
    """
        Classe molde para gerir os documentos, para operações como:
    - leitura e escrita de arquivos pdf
    - exportar páginas ou arquivos pdf
    - permitir a leitura de arquivos ou bytes de pdf.
    """
    def __init__(self):
        pass

    @abstractmethod
    def __hash__(self) -> int:
        pass

    @abstractmethod
    def get_real_module(self) -> Union[fitz.Document | PdfReader]:
        pass

    def set_real_module(self, module: Union[fitz.Document, PdfReader]):
        pass

    @abstractmethod
    def size(self) -> int:
        """Retorna o número total de páginas do documento"""
        pass

    @abstractmethod
    def get_current_library(self) -> LibPDF:
        pass

    @abstractmethod
    def get_first_page(self) -> PageDocumentPdf:
        pass

    @abstractmethod
    def get_last_page(self) -> PageDocumentPdf:
        pass

    @abstractmethod
    def get_page(self, idx: int) -> PageDocumentPdf | Exception:
        pass

    @abstractmethod
    def add_page(self, page: PageDocumentPdf):
        pass

    def add_pages(self, pages: list[PageDocumentPdf]):
        for pg in pages:
            self.add_page(pg)

    def merge_document(self, document: InterfaceDocumentPdf):
        final_doc = merge_documents(
            [self.get_real_module(), document.get_real_module()],
            lib_pdf=self.get_current_library()
        )
        self.set_real_module(final_doc)

    @abstractmethod
    def to_file(self, file: File):
        pass

    @abstractmethod
    def to_bytes(self) -> bytes:
        pass

    @abstractmethod
    def to_pages(self) -> list[PageDocumentPdf]:
        pass

    @classmethod
    def create_from_file(cls, file: File) -> InterfaceDocumentPdf:
        pass

    @classmethod
    def create_from_bytes(cls, bt: BytesIO) -> InterfaceDocumentPdf:
        pass

    @classmethod
    def builder(cls) -> BuilderInterfaceDocumentPdf:
        return BuilderInterfaceDocumentPdf()


class ImplementDocumentPdfFitz(InterfaceDocumentPdf):
    """
        Implementação usando a biblioteca fitz.
    """
    def __init__(self, document: fitz.Document):
        super().__init__()
        self.pdf_doc: fitz.Document = document

    def __hash__(self) -> int:
        return hash(self.pdf_doc)

    def set_real_module(self, module: fitz.Document):
        self.pdf_doc = module

    def get_real_module(self) -> fitz.Document:
        return self.pdf_doc

    def get_current_library(self) -> LibPDF:
        return "fitz"

    def merge_document(self, document: InterfaceDocumentPdf):
        final_doc: fitz.Document = merge_documents(
            [self.get_real_module(), document.get_real_module()],
            lib_pdf="fitz"
        )
        self.set_real_module(final_doc)

    def size(self) -> int:
        return self.pdf_doc.page_count

    def get_first_page(self) -> PageDocumentPdf:
        return self.get_page(0)

    def get_last_page(self) -> PageDocumentPdf:
        last_idx = self.pdf_doc.page_count - 1
        return self.get_page(last_idx)

    def get_page(self, idx: int) -> PageDocumentPdf | Exception:
        try:
            pg: fitz.Page = self.pdf_doc.load_page(idx)  # retorna fitz.Page
            _page_pdf = PageDocumentPdf.create_from_page_fitz(pg, pg.number + 1)
        except Exception as e:
            return Exception(f"{__class__.__name__} {e}")
        else:
            return _page_pdf

    def add_page(self, page: PageDocumentPdf):
        # Assume que page.get_implementation().get_real_module() é fitz.Page
        self.pdf_doc.insert_pdf(
            page.get_implementation().get_real_module().parent,
            from_page=page.get_implementation().get_real_module().number,
            to_page=page.get_implementation().get_real_module().number
        )

    def add_pages(self, pages: list[PageDocumentPdf]):
        for page in pages:
            self.add_page(page)

    def to_file(self, file: File):
        try:
            self.pdf_doc.save(file.path)
        except Exception as e:
            print(f'{__class__.__name__}: {e}')

    def to_bytes(self) -> bytes:
        buf = BytesIO()
        self.pdf_doc.save(buf)
        buf.seek(0)
        bt = buf.getvalue()
        buf.close()
        return bt

    def to_pages(self) -> list[PageDocumentPdf]:
        pages: list[PageDocumentPdf] = []
        _builder = PageDocumentPdf.build_interface().set_lib_pdf(self.get_current_library())
        for num, pg in enumerate(self.pdf_doc):
            #page_pdf = PageDocumentPdf.create_from_page_fitz(pg, num + 1)
            page_pdf = _builder.set_num_page(num+1).set_page(pg).create()
            pages.append(PageDocumentPdf(page_pdf))
        return pages

    @classmethod
    def create_from_bytes(cls, bt: bytes) -> ImplementDocumentPdfFitz:
        # Cria documento a partir de BytesIO
        if not MODULE_FITZ:
            raise ImportError("Módulo fitz|pymupdf não instalado! - Use pip install fitz.")
        doc: fitz.Document = fitz.Document(stream=bt, filetype="pdf")
        return cls(doc)

    @classmethod
    def create_from_file(cls, file: File) -> ImplementDocumentPdfFitz:
        # Cria documento a partir de caminho no disco
        if not MODULE_FITZ:
            raise ImportError("Módulo fitz|pymupdf não instalado!\nUse pip install fitz.")
        doc = fitz.open(file.path)
        return cls(doc)

    @classmethod
    def create_from_pages(cls, pages: list[PageDocumentPdf]) -> ImplementDocumentPdfFitz:
        if len(pages) == 0:
            raise ValueError(f'{__class__.__name__} lista de páginas vazias!')
        # Criar documento PDF.
        pdf_document = fitz.Document()
        for page in pages:
            # Verifica se a página é do tipo fitz.Page
            if not isinstance(page.get_implementation().get_real_module(), fitz.Page):
                raise TypeError(f"Todas as páginas devem ser do tipo [fitz.Page]")
            # Insere as páginas no novo documento
            pdf_document.insert_pdf(
                page.get_implementation().get_real_module().parent,
                from_page=page.get_num_page(),
                to_page=page.get_num_page()
            )
        bt = pdf_document.write()
        return cls.create_from_bytes(bt)


class ImplementDocumentPdfPyPdf(InterfaceDocumentPdf):
    """
        Implementação usando a biblioteca pypdf
    """

    def __init__(self, doc_pdf: PdfReader):
        super().__init__()
        self.doc_pdf: PdfReader = doc_pdf  # ou PdfReader

    def __hash__(self) -> int:
        return hash(self.doc_pdf)

    def set_real_module(self, module: PdfReader):
        self.doc_pdf = module

    def get_real_module(self) -> PdfReader:
        return self.doc_pdf

    def merge_document(self, document: InterfaceDocumentPdf):
        raise NotImplementedError()

    def get_current_library(self) -> LibPDF:
        return "pypdf"

    def size(self) -> int:
        return len(self.doc_pdf.pages)

    def get_first_page(self) -> PageDocumentPdf:
        """
        Retorna a primeira página do documento.
        """
        # O índice da primeira página em PyPDF2 é 0.
        return self.get_page(0)

    def get_last_page(self) -> PageDocumentPdf:
        """
        Retorna a última página do documento.
        """
        # O índice da última página é o número total de páginas menos um.
        last_page_idx = len(self.doc_pdf.pages) - 1
        return self.get_page(last_page_idx)

    def get_page(self, idx: int) -> PageDocumentPdf | Exception:
        """
        Retorna uma página específica pelo seu índice.
        Se o índice for inválido, retorna None.
        """
        try:
            pg = self.doc_pdf.pages[idx]
            # O número da página é idx + 1
            page_pdf_doc = PageDocumentPdf.create_from_page_pypdf(pg, idx + 1)
        except Exception as err:
            return Exception(err)
        return page_pdf_doc

    def add_page(self, page: PageDocumentPdf):
        self.doc_pdf.add_page(page.get_implementation().get_real_page())

    def add_pages(self, pages: list[PageDocumentPdf]):
        for page in pages:
            self.add_page(page)

    def to_file(self, file: File):
        with open(file.path, 'wb') as f:
            self.doc_pdf.write(f)

    def to_bytes(self) -> BytesIO:
        buf = BytesIO()
        self.doc_pdf.write(buf)
        buf.seek(0)
        return buf

    def to_pages(self) -> list[PageDocumentPdf]:
        pages_pdf: list[PageDocumentPdf] = []
        for num, page in enumerate(self.doc_pdf.pages):
            pg = PageDocumentPdf.create_from_page_pypdf(page, num + 1)
            pages_pdf.append(pg)
        return pages_pdf

    @classmethod
    def create_from_bytes(cls, bt: bytes) -> ImplementDocumentPdfPyPdf:
        # Usa PdfReader diretamente de BytesIO
        if not MODULE_PYPDF:
            raise ImportError("Módulo pypdf não instalado!\nUse pip install pypdf.")
        reader = PdfReader(BytesIO(bt))
        pdf_writer = PdfWriter()
        for page in reader.pages:
            pdf_writer.add_page(page)
        return cls(pdf_writer)

    @classmethod
    def create_from_file(cls, file: File) -> ImplementDocumentPdfPyPdf:
        # Usa PdfReader diretamente de arquivo
        if not MODULE_PYPDF:
            raise ImportError("Módulo pypdf não instalado!\nUse pip install pypdf.")
        reader = PdfReader(file.absolute())
        pdf_writer = PdfWriter()
        for p in reader.pages:
            pdf_writer.add_page(p)
        _obj_doc = cls(pdf_writer)
        reader.close()
        return _obj_doc

    @classmethod
    def create_from_pages(cls, pages: list[PageDocumentPdf]) -> ImplementDocumentPdfPyPdf:
        if len(pages) == 0:
            raise ValueError(f'{__class__.__name__} lista de páginas vazias!')

        pdf_writer = PdfWriter()
        for page_obj in pages:
            # Obtém o objeto de página da implementação da lib
            pdf_writer.add_page(page_obj.get_implementation().get_real_page())
        output_bytes = BytesIO()
        pdf_writer.write(output_bytes)
        output_bytes.seek(0)
        pdf_bytes = output_bytes.getvalue()
        output_bytes.close()
        return cls.create_from_bytes(pdf_bytes)


class DocumentPdf(ObjectAdapter):
    """
        Gerir um documento PDF com uma implementação de fitz ou pypdf.
    As operações são feitas pela classe encapsulada aqui.
    """
    def __init__(self, implement_interface_pdf: InterfaceDocumentPdf):
        super().__init__()
        self._implement_interface_pdf: InterfaceDocumentPdf = implement_interface_pdf

    def set_land_scape(self) -> None:
        pages = self.to_pages()
        for n, p in enumerate(pages):
            pages[n].set_land_scape()

        if self.get_current_library() == "fitz":
            self.set_implementation(ImplementDocumentPdfFitz.create_from_pages(pages))
        elif self.get_current_library() == "pypdf":
            self.set_implementation(ImplementDocumentPdfPyPdf.create_from_pages(pages))

    def get_implementation(self) -> InterfaceDocumentPdf:
        return self._implement_interface_pdf

    def set_implementation(self, implementation: InterfaceDocumentPdf):
        self._implement_interface_pdf = implementation

    def size(self) -> int:
        return self._implement_interface_pdf.size()

    def merge_document(self, document: DocumentPdf):
        return self._implement_interface_pdf.merge_document(document.get_implementation())

    def get_current_library(self) -> LibPDF:
        return self._implement_interface_pdf.get_current_library()

    def get_first_page(self) -> PageDocumentPdf:
        """
        Retorna a primeira página do documento.
        """
        return self._implement_interface_pdf.get_first_page()

    def get_last_page(self) -> PageDocumentPdf:
        """
        Retorna a última página do documento.
        """
        return self._implement_interface_pdf.get_last_page()

    def get_page(self, idx: int) -> PageDocumentPdf | Exception:
        """
        Retorna uma página específica pelo seu índice.
        Se o índice for inválido, retorna None.
        """
        return self._implement_interface_pdf.get_page(idx)

    def add_page(self, page: PageDocumentPdf):
        self._implement_interface_pdf.add_page(page)

    def add_pages(self, pages: list[PageDocumentPdf]):
        self._implement_interface_pdf.add_pages(pages)

    def to_file(self, file: File):
        self._implement_interface_pdf.to_file(file)

    def to_bytes(self) -> bytes:
        return self._implement_interface_pdf.to_bytes()

    def to_pages(self) -> list[PageDocumentPdf]:
        return self._implement_interface_pdf.to_pages()

    def to_list(self, separator: str = '\n') -> list[str]:
        _pages = self.to_pages()
        _values = []
        for page in _pages:
            txt = page.get_text()
            if (txt is not None) and (txt != ""):
                try:
                    _values.extend(txt.split(separator))
                except Exception as err:
                    print(f'{__class__.__name__} Error: {err}')
        return _values

    def to_dict(self, separator: str = '\n') -> dict[str, list[str]]:
        raise NotImplementedError()

    def to_data(self, separator: str = '\n') -> pd.DataFrame:
        return pd.DataFrame.from_dict(self.to_dict(separator=separator))

    @classmethod
    def create_from_bytes(cls, bt: bytes, *, lib_pdf: LibPDF = "fitz") -> DocumentPdf:
        if lib_pdf == "fitz":
            return cls(ImplementDocumentPdfFitz.create_from_bytes(bt))
        elif lib_pdf == "pypdf":
            return cls(ImplementDocumentPdfPyPdf.create_from_bytes(bt))
        else:
            raise NotImplementedModulePdfError()

    @classmethod
    def create_from_file(cls, file: File, *, lib_pdf: LibPDF = "fitz") -> DocumentPdf:
        if lib_pdf == "fitz":
            return cls(ImplementDocumentPdfFitz.create_from_file(file))
        elif lib_pdf == "pypdf":
            return cls(ImplementDocumentPdfPyPdf.create_from_file(file))
        else:
            raise NotImplementedModulePdfError()

    @classmethod
    def create_from_pages(cls, pgs: list[PageDocumentPdf], *, lib_pdf: LibPDF = "fitz") -> DocumentPdf:
        if lib_pdf == "fitz":
            return cls(ImplementDocumentPdfFitz.create_from_pages(pgs))
        elif lib_pdf == "pypdf":
            return cls(ImplementDocumentPdfPyPdf.create_from_pages(pgs))
        else:
            raise NotImplementedModulePdfError()

    @classmethod
    def build_interface(cls) -> BuilderInterfaceDocumentPdf:
        return BuilderInterfaceDocumentPdf().set_lib("fitz")


class BuilderInterfaceDocumentPdf(BuilderInterface):

    def __init__(self) -> None:
        self.__lib = "fitz"
        self.__doc_bytes: bytes = None

    def set_lib(self, lib_pdf: LibPDF) -> BuilderInterfaceDocumentPdf:
        self.__lib = lib_pdf
        return self

    def set_bytes(self, document_bytes: bytes) -> BuilderInterfaceDocumentPdf:
        self.__doc_bytes = document_bytes
        return self

    def create(self) -> InterfaceDocumentPdf:
        if self.__doc_bytes is None:
            raise ValueError(f"{__class__.__name__} Necessário setar os bytes pdf para prosseguir!")

        if self.__lib == "fitz":
            return ImplementDocumentPdfFitz.create_from_bytes(self.__doc_bytes)
        elif self.__lib == "pypdf":
            return ImplementDocumentPdfPyPdf.create_from_bytes(self.__doc_bytes)
        else:
            raise NotImplementedModulePdfError()

