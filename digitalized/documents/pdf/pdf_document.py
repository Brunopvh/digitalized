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
from digitalized.types.core import ObjectAdapter
from digitalized.types.array import ArrayList, ArrayString
from digitalized.documents.pdf.pdf_page import (
    PageDocumentPdf, InterfacePagePdf, LibPDF, MODULE_FITZ, MODULE_PYPDF
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
    def get_page(self, idx: int) -> PageDocumentPdf | None:
        pass

    @abstractmethod
    def add_page(self, page: PageDocumentPdf):
        pass

    @abstractmethod
    def add_pages(self, pages: list[PageDocumentPdf]):
        pass

    @abstractmethod
    def merge_document(self, document: InterfaceDocumentPdf):
        pass

    @abstractmethod
    def to_file(self, file: File):
        pass

    @abstractmethod
    def to_bytes(self) -> BytesIO:
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


class ImplementDocumentPdfFitz(InterfaceDocumentPdf):
    """
        Implementação usando a biblioteca fitz.
    """
    def __init__(self, document: fitz.Document):
        super().__init__()
        self.pdf_doc: fitz.Document = document

    def get_current_library(self) -> LibPDF:
        return "fitz"

    def merge_document(self, document: InterfaceDocumentPdf):
        pass

    def size(self) -> int:
        return self.pdf_doc.page_count

    def get_first_page(self) -> PageDocumentPdf:
        return self.get_page(0)

    def get_last_page(self) -> PageDocumentPdf:
        last_idx = self.pdf_doc.page_count - 1
        return self.get_page(last_idx)

    def get_page(self, idx: int) -> PageDocumentPdf | None:
        _page_pdf = None
        if 0 <= idx < self.pdf_doc.page_count:
            pg: fitz.Page = self.pdf_doc.load_page(idx)  # retorna fitz.Page
            if pg is not None:
                _page_pdf = PageDocumentPdf.create_from_page_fitz(pg, pg.number + 1)
        return _page_pdf

    def add_page(self, page: PageDocumentPdf):
        # Assume que page.get_implementation().get_real_page() é fitz.Page
        self.pdf_doc.insert_pdf(
            page.get_implementation().get_real_page().parent,
            from_page=page.get_implementation().get_real_page().number,
            to_page=page.get_implementation().get_real_page().number
        )

    def add_pages(self, pages: list[PageDocumentPdf]):
        for page in pages:
            self.add_page(page)

    def to_file(self, file: File):
        try:
            self.pdf_doc.save(file.path)
        except Exception as e:
            print(f'{__class__.__name__}: {e}')

    def to_bytes(self) -> BytesIO:
        buf = BytesIO()
        self.pdf_doc.save(buf)
        buf.seek(0)
        return buf

    def to_pages(self) -> list[PageDocumentPdf]:
        pages = []
        for num, pg in enumerate(self.pdf_doc):
            page_pdf = PageDocumentPdf.create_from_page_fitz(pg, num + 1)
            page_pdf.metadata = self.metadata
            page_pdf.metadata.md5 = MetaDataItem('nan')
            pages.append(page_pdf)
        return pages

    @classmethod
    def create_from_bytes(cls, bt: BytesIO) -> ImplementDocumentPdfFitz:
        # Cria documento a partir de BytesIO
        if not MOD_FITZ:
            raise ImportError("Módulo fitz|pymupdf não instalado!\nUse pip install fitz.")
        doc: ModDocPdf = fitz.Document(stream=bt.getvalue(), filetype="pdf")
        name = get_hash_from_bytes(bt)
        _obj_doc = cls(doc)
        _obj_doc.metadata.name = MetaDataItem(name)
        _obj_doc.metadata.md5 = MetaDataItem(name)
        return _obj_doc

    @classmethod
    def create_from_file(cls, file: File) -> ImplementDocumentPdfFitz:
        # Cria documento a partir de caminho no disco
        if not MOD_FITZ:
            raise ImportError("Módulo fitz|pymupdf não instalado!\nUse pip install fitz.")
        doc = fitz.open(file.path)
        _obj_doc = cls(doc)
        _obj_doc.metadata = MetaDataFile.create_metadata(file)
        return _obj_doc

    @classmethod
    def create_from_pages(cls, pages: list[PageDocumentPdf]) -> ImplementDocumentPdfFitz:
        # Criar documento PDF.
        pdf_document = fitz.Document()
        for page in pages:
            # Verifica se a página é do tipo fitz.Page
            if not isinstance(page.implement_page_pdf.mod_page, fitz.Page):
                raise TypeError(f"Todas as páginas devem ser do tipo [fitz.Page]")
            # Insere as páginas no novo documento
            pdf_document.insert_pdf(
                page.implement_page_pdf.mod_page.parent,
                from_page=page.implement_page_pdf.mod_page.number,
                to_page=page.implement_page_pdf.mod_page.number
            )
        bt = BytesIO(pdf_document.write())
        return cls.create_from_bytes(bt)


class ImplementDocumentPdfPyPdf(InterfaceDocumentPdf):
    """
        Implementação usando a biblioteca pypdf
    """

    def __init__(self, mod_doc_pdf: PdfWriter):
        super().__init__(mod_doc_pdf)
        self.mod_doc_pdf: PdfWriter = mod_doc_pdf  # ou PdfReader
        self.lib_pdf: LibPDF = LibPDF.PYPDF

    def lenght(self) -> int:
        return len(self.mod_doc_pdf.pages)

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
        last_page_idx = len(self.mod_doc_pdf.pages) - 1
        return self.get_page(last_page_idx)

    def get_page(self, idx: int) -> PageDocumentPdf | None:
        """
        Retorna uma página específica pelo seu índice.
        Se o índice for inválido, retorna None.
        """
        if 0 <= idx < len(self.mod_doc_pdf.pages):
            # Acessa a página pela lista self.mod_doc_pdf.pages
            pg = self.mod_doc_pdf.pages[idx]
            # O número da página é idx + 1
            page_pdf_doc = PageDocumentPdf.create_from_page_pypdf(pg, idx + 1)
            page_pdf_doc.metadata = self.metadata
            page_pdf_doc.metadata.md5 = MetaDataItem('nan')
            return page_pdf_doc
        return None

    def add_page(self, page: PageDocumentPdf):
        self.mod_doc_pdf.add_page(page.implement_page_pdf.mod_page)

    def add_pages(self, pages: list[PageDocumentPdf]):
        for page in pages:
            self.add_page(page)

    def to_file(self, file: File):
        with open(file.path, 'wb') as f:
            self.mod_doc_pdf.write(f)

    def to_bytes(self) -> BytesIO:
        buf = BytesIO()
        self.mod_doc_pdf.write(buf)
        buf.seek(0)
        return buf

    def to_pages(self) -> list[PageDocumentPdf]:
        pages_pdf: list[PageDocumentPdf] = []
        for num, page in enumerate(self.mod_doc_pdf.pages):
            pg = PageDocumentPdf.create_from_page_pypdf(page, num + 1)
            pg.metadata = self.metadata
            pg.metadata.md5 = MetaDataItem('nan')
            pages_pdf.append(pg)
        return pages_pdf

    @classmethod
    def create_from_bytes(cls, bt: BytesIO) -> ImplementDocumentPdfPyPdf:
        # Usa PdfReader diretamente de BytesIO
        if not MOD_PYPDF:
            raise ImportError("Módulo pypdf não instalado!\nUse pip install pypdf.")
        bt.seek(0)
        reader = PdfReader(bt)
        bt.seek(0)
        name = get_hash_from_bytes(bt)
        pdf_writer = PdfWriter()
        for page in reader.pages:
            pdf_writer.add_page(page)
        bt.close()
        del bt
        del reader
        _obj_doc = cls(pdf_writer)
        _obj_doc.metadata.name = MetaDataItem(name)
        _obj_doc.metadata.md5 = MetaDataItem(name)
        return _obj_doc

    @classmethod
    def create_from_file(cls, file: File) -> ImplementDocumentPdfPyPdf:
        # Usa PdfReader diretamente de arquivo
        if not MOD_PYPDF:
            raise ImportError("Módulo pypdf não instalado!\nUse pip install pypdf.")
        reader = PdfReader(file.absolute())
        pdf_writer = PdfWriter()
        for p in reader.pages:
            pdf_writer.add_page(p)
        del reader
        _obj_doc = cls(pdf_writer)
        _obj_doc.metadata = MetaDataFile.create_metadata(file)
        return _obj_doc

    @classmethod
    def create_from_pages(cls, pages: list[PageDocumentPdf]) -> ImplementDocumentPdfPyPdf:
        pdf_writer = PdfWriter()
        for page_obj in pages:
            # Obtém o objeto de página da implementação da lib
            pdf_writer.add_page(page_obj.implement_page_pdf.mod_page)
        output_bytes = BytesIO()
        pdf_writer.write(output_bytes)
        pdf_bytes = output_bytes
        return cls.create_from_bytes(pdf_bytes)


class DocumentPdf(object):
    """
        Gerir um documento PDF com uma implementação de fitz ou pypdf.
    As operações são feitas pela classe encapsulada aqui.
    """
    def __init__(
                self,
                document: Union[
                    str, File, PdfWriter, fitz.Document, BytesIO,
                    ImplementDocumentPdfFitz, ImplementDocumentPdfPyPdf,
                ],
                *,
                lib_pdf: LibPDF = LibPDF.FITZ
            ):
        self.doc_pdf: InterfaceDocumentPdf = None
        self.lib_pdf: LibPDF = lib_pdf
        if isinstance(document, str):
            if lib_pdf == LibPDF.PYPDF:
                self.doc_pdf = ImplementDocumentPdfPyPdf.create_from_file(File(document))
            elif lib_pdf == LibPDF.FITZ:
                self.doc_pdf = ImplementDocumentPdfFitz.create_from_file(File(document))
        elif isinstance(document, File):
            if lib_pdf == LibPDF.PYPDF:
                self.doc_pdf = ImplementDocumentPdfPyPdf.create_from_file(document)
            elif lib_pdf == LibPDF.FITZ:
                self.doc_pdf = ImplementDocumentPdfFitz.create_from_file(document)
        elif isinstance(document, PdfWriter):
            _tmp_bytes = BytesIO()
            document.write(_tmp_bytes)
            _tmp_bytes.seek(0)
            if lib_pdf == LibPDF.PYPDF:
                name = get_hash_from_bytes(_tmp_bytes)
                self.doc_pdf = ImplementDocumentPdfPyPdf(document)
                self.doc_pdf.metadata.name = MetaDataItem(name)
                self.doc_pdf.metadata.md5 = MetaDataItem(name)
                del _tmp_bytes
            elif lib_pdf == LibPDF.FITZ:
                self.doc_pdf = ImplementDocumentPdfFitz.create_from_bytes(_tmp_bytes)
        elif isinstance(document, fitz.Document):
            _tmp_bytes = BytesIO(document.tobytes())
            _tmp_bytes.seek(0)
            if lib_pdf == LibPDF.PYPDF:
                self.doc_pdf = ImplementDocumentPdfPyPdf.create_from_bytes(_tmp_bytes)
            elif lib_pdf == LibPDF.FITZ:
                name = get_hash_from_bytes(_tmp_bytes)
                self.doc_pdf = ImplementDocumentPdfFitz(document)
                self.doc_pdf.metadata.name = MetaDataItem(name)
                self.doc_pdf.metadata.md5 = MetaDataItem(name)
                del _tmp_bytes
        elif isinstance(document, BytesIO):
            if lib_pdf == LibPDF.PYPDF:
                self.doc_pdf = ImplementDocumentPdfPyPdf.create_from_bytes(document)
            elif lib_pdf == LibPDF.FITZ:
                self.doc_pdf = ImplementDocumentPdfFitz.create_from_bytes(document)
        elif isinstance(document, ImplementDocumentPdfFitz):
            self.doc_pdf = document
        elif isinstance(document, ImplementDocumentPdfPyPdf):
            self.doc_pdf = document

        if self.doc_pdf is None:
            raise ValueError(
                f'Use: str, File, PdfWriter, fitz.Document ou BytesIO não => {type(document)}'
            )

    @property
    def name(self) -> str | None:
        return self.doc_pdf.name

    @property
    def metadata(self) -> MetaDataFile:
        return self.doc_pdf.metadata

    @metadata.setter
    def metadata(self, metadata: MetaDataFile) -> None:
        self.doc_pdf.metadata = metadata

    @property
    def lenght(self) -> int:
        return self.doc_pdf.lenght()

    def get_real_document(self) -> fitz.Document | PdfWriter:
        return self.doc_pdf.mod_doc_pdf

    def get_first_page(self) -> PageDocumentPdf:
        """
        Retorna a primeira página do documento.
        """
        return self.doc_pdf.get_first_page()

    def get_last_page(self) -> PageDocumentPdf:
        """
        Retorna a última página do documento.
        """
        return self.doc_pdf.get_last_page()

    def get_page(self, idx: int) -> PageDocumentPdf | None:
        """
        Retorna uma página específica pelo seu índice.
        Se o índice for inválido, retorna None.
        """
        return self.doc_pdf.get_page(idx)

    def add_page(self, page: PageDocumentPdf):
        self.doc_pdf.add_page(page)

    def add_pages(self, pages: list[PageDocumentPdf]):
        self.doc_pdf.add_pages(pages)

    def to_file(self, file: File):
        self.doc_pdf.to_file(file)

    def to_bytes(self) -> BytesIO:
        return self.doc_pdf.to_bytes()

    def to_pages(self) -> list[PageDocumentPdf]:
        return self.doc_pdf.to_pages()

    def to_list(self, separator: str = '\n') -> list[str]:
        _pages = self.to_pages()
        _values = []
        for page in _pages:
            try:
                _values.extend(page.to_string().split(separator))
            except Exception as e:
                show_warning(f'{e}')
        return _values

    def _create_map(self, page: PageDocumentPdf, *, separator: str = '\n') -> DictTextTable:
        """
        @rtype: pd.DataFrame
        """
        txt_page = page.to_string()
        if (txt_page is None) or (txt_page == '') or (txt_page == 'nas'):
            _values = ['nan']
        else:
            _values = txt_page.split(separator)

        if not self.metadata.file_path.is_empty:
            return DictTextTable.create_from_values(
                _values,
                page_num=f'{page.number_page}',
                file_type='.pdf',
                file_path=self.metadata.file_path,
                dir_path=self.metadata.dir_path,
            )
        else:
            return DictTextTable.create_from_values(
                _values,
                page_num=f'{page.number_page}',
                file_type='.pdf',
                file_path=self.metadata.file_path,
                dir_path=self.metadata.dir_path,
            )

    def to_dict(self, separator: str = '\n') -> TableDocuments:
        list_data: list[DictTextTable] = []
        pages: list[PageDocumentPdf] = self.to_pages()

        for page_pdf in pages:
            _mp: DictTextTable = self._create_map(page_pdf, separator=separator)
            list_data.append(_mp)
        if len(list_data) == 0:
            return DictTextTable.create_void_dict()
        return concat_table_documents(list_data)

    def to_data(self, separator: str = '\n') -> pd.DataFrame:
        return pd.DataFrame.from_dict(self.to_dict(separator=separator))

    def find(
            self, text: str,
            separator: str = '\n',
            iqual: bool = False,
            case: bool = False,
            silent: bool = False,
            ) -> SearchableTextPdf:
        """
            Filtrar texto retornando a primeira ocorrência do Documento PDF.
        """
        _searchable = SearchableTextPdf(silent)
        pages_pdf: list[PageDocumentPdf] = self.to_pages()
        _page: PageDocumentPdf
        for _page in pages_pdf:
            text_str_in_page = _page.to_string()
            if (text_str_in_page == 'nas') or (text_str_in_page is None):
                continue
            try:
                fd = FindText(text_str_in_page, separator=separator)
                idx = fd.find_index(text, iqual=iqual, case=case)
                if idx is None:
                    continue
                math_text = fd.get_index(idx)
            except Exception as e:
                print(f'{__class__.__name__} {e}')
            else:
                new_line = {
                            ColumnsTable.KEY.value: f'{idx}',
                            ColumnsTable.NUM_PAGE.value: f'{_page.number_page}',
                            ColumnsTable.NUM_LINE.value: f'{idx+1}',
                            ColumnsTable.TEXT: math_text,
                            ColumnsTable.FILE_NAME.value: self.metadata.name,
                            ColumnsTable.FILETYPE.value: self.metadata.extension,
                            ColumnsTable.FILE_PATH.value: self.metadata.file_path,
                            ColumnsTable.DIR.value: self.metadata.dir_path,
                        }
                _searchable.add_line(new_line)
                return _searchable
        return _searchable

    def find_all(
                self, text: str,
                separator: str = '\n',
                iqual: bool = False,
                case: bool = False,
                silent: bool = False,
            ) -> SearchableTextPdf:
        """
            Filtrar texto em documento PDF e retorna todas as ocorrências do texto
        encontradas no documento, incluindo o número da linha, página e nome do arquivo
        em cada ocorrência.
        """
        _searchable = SearchableTextPdf(silent)
        pages_pdf: list[PageDocumentPdf] = self.to_pages()
        _page: PageDocumentPdf
        for _page in pages_pdf:
            text_str_in_page = _page.to_string()
            if (text_str_in_page == 'nas') or (text_str_in_page is None):
                continue
            try:
                fd = FindText(text_str_in_page, separator=separator)
                idx = fd.find_index(text, iqual=iqual, case=case)
                if idx is None:
                    continue
                math_text = fd.get_index(idx)
            except Exception as e:
                print(f'{__class__.__name__} {e}')
            else:
                new_line = {
                    ColumnsTable.KEY.value: f'{idx}',
                    ColumnsTable.NUM_PAGE.value: f'{_page.number_page}',
                    ColumnsTable.NUM_LINE.value: f'{idx + 1}',
                    ColumnsTable.TEXT: math_text,
                    ColumnsTable.FILE_NAME.value: self.metadata.name,
                    ColumnsTable.FILETYPE.value: self.metadata.extension,
                    ColumnsTable.FILE_PATH.value: self.metadata.file_path,
                    ColumnsTable.DIR.value: self.metadata.dir_path,
                }
                _searchable.add_line(new_line)
        return _searchable

    @classmethod
    def create_from_bytes(cls, bt: BytesIO, *, lib_pdf: LibPDF = LibPDF.FITZ) -> DocumentPdf:
        return cls(bt, lib_pdf=lib_pdf)

    @classmethod
    def create_from_file(cls, file: File, *, lib_pdf: LibPDF = DEFAULT_LIB_PDF) -> DocumentPdf:
        return cls(file, lib_pdf=lib_pdf)

    @classmethod
    def create_from_pages(
                cls,
                pages: list[PageDocumentPdf], *,
                lib_pdf: LibPDF = DEFAULT_LIB_PDF
            ) -> DocumentPdf:
        if lib_pdf == LibPDF.FITZ:
            mod_pdf = ImplementDocumentPdfFitz.create_from_pages(pages)
            mod_pdf.metadata.file_path = pages[0].metadata.file_path
            return cls(mod_pdf, lib_pdf=lib_pdf)
        elif lib_pdf == LibPDF.PYPDF:
            mod_pdf = ImplementDocumentPdfPyPdf.create_from_pages(pages)
            return cls(mod_pdf, lib_pdf=lib_pdf)
        else:
            raise NotImplementedError(f'Módulo PDF não implementado: {lib_pdf}')


class CollectionPagePdf(ListItems):
    """
        Gerir uma coleção de páginas PDF.
    """
    def __init__(self, pages: list[PageDocumentPdf]) -> None:
        super().__init__(pages)
        self.pbar: ProgressBarAdapter = ProgressBarAdapter()

    @property
    def name(self) -> str | None:
        if self.is_empty:
            return None
        return self[0].__hash__()

    def set_pbar(self, p: ProgressBarAdapter):
        self.pbar = p

    def set_land_scape(self):
        for page in self:
            page.set_land_scape()

    def set_rotation(self, rotation: int) -> None:
        for page in self:
            page.set_rotation(rotation)

    def add_page(self, page: PageDocumentPdf) -> None:
        page.number_page = self.length + 1
        self.pbar.update_text(f'Adicionando página PDF {page.number_page}')
        self.append(page)

    def add_pages(self, pages: list[PageDocumentPdf]) -> None:
        _counter = len(pages)
        for n, pg in enumerate(pages):
            _counter += 1
            pg.number_page = _counter
            self.append(pg)

    def add_file_pdf(self, file: File, *, lib_pdf: LibPDF = LibPDF.FITZ) -> None:
        self.pbar.update_text(f'Adicionando arquivo PDF {file.basename()}')
        doc_pdf = DocumentPdf(file, lib_pdf=lib_pdf)
        self.add_pages(doc_pdf.to_pages())

    def add_files_pdf(self, files: list[File], lib_pdf: LibPDF = LibPDF.FITZ) -> None:
        max_num: int = len(files)
        for num, f in enumerate(files):
            self.pbar.update(
                ((num + 1) / max_num) * 100,
                f'Adicionando arquivo: [{num+1} de {max_num}] {f.basename()}'
            )
            _doc_pdf = DocumentPdf(f, lib_pdf=lib_pdf)
            self.add_pages(_doc_pdf.to_pages())
            del _doc_pdf

    def add_document(self, doc: DocumentPdf) -> None:
        self.add_pages(doc.to_pages())

    def add_directory_pdf(self, d: Directory, *, max_files: int = 4000):
        input_files = InputFiles(d, maxFiles=max_files)
        self.add_files_pdf(input_files.get_files(file_type=LibraryDocs.PDF))

    def to_document(self, lib_pdf: LibPDF = DEFAULT_LIB_PDF) -> DocumentPdf:
        return DocumentPdf.create_from_pages(self, lib_pdf=lib_pdf)

    def to_file_pdf(self, file: File, *, replace: bool = False) -> None:
        if not replace:
            if file.exists():
                print(f'[PULANDO]: o arquivo já existe {file.absolute()}')
                return
        _doc = DocumentPdf.create_from_pages(self)
        _doc.to_file(file)
        del _doc

    def to_files_pdf(
                self,
                output_dir: Directory, *,
                replace: bool = False,
                prefix: str = None,
            ) -> None:
        max_num = self.length
        self.pbar.start()
        print()
        for n, page in enumerate(self):
            _doc_pdf = DocumentPdf.create_from_pages([page])
            if prefix is None:
                file_path = output_dir.join_file(f'{page.number_page}-{_doc_pdf.name}.pdf')
            else:
                file_path = output_dir.join_file(f'{prefix}-{page.number_page}.pdf')

            if (not replace) and (file_path.exists()):
                continue
            self.pbar.update(
                ((n+1) / max_num) * 100,
                f'Exportando: [{n+1} de {max_num}] {file_path.basename()}'
            )
            try:
                _doc_pdf.to_file(file_path)
            except Exception as e:
                self.pbar.update_text(f'{e}')
            del _doc_pdf
        print()
        self.pbar.stop()
