#!/usr/bin/env python3
#
"""
    Módulo para trabalhar com páginas PDF
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Literal
from digitalized.types.array import ArrayString, BaseTableString
from digitalized.types.core import ObjectAdapter
from convert_stream.mod_types.modules import (
    ModPagePdf, PageObject, fitz
)
from sheet_stream.type_utils import MetaDataFile
from convert_stream.text.find_text import FindText, ArrayString

#=================================================================#
# Módulos para PDF fitz e pypdf
#=================================================================#
MODULE_FITZ = False
MODULE_PYPDF = False

try:
    import fitz
    MODULE_FITZ = True
except ImportError:
    try:
        import pymupdf as fitz
        MODULE_FITZ = True
    except ImportError:
        pass

try:
    from pypdf import PdfWriter, PdfReader, PageObject
    MODULE_PYPDF = True
except ImportError:
    pass


LibPDF = Literal["fitz", "pypdf"]


class InterfacePagePdf(ABC):

    def __init__(self):
        self._num_page: int = None

    @abstractmethod
    def get_real_page(self) -> PageObject | fitz.Page:
        pass

    @abstractmethod
    def get_num_page(self) -> int:
        pass

    def set_num_page(self, num_page: int) -> None:
        if not isinstance(num_page, int):
            raise TypeError("num_page must be an integer")
        if num_page < 1:
            raise ValueError("num_page must be >= 1")
        self._num_page = num_page

    @abstractmethod
    def get_width(self) -> float:
        pass

    @abstractmethod
    def get_height(self) -> float:
        pass

    @abstractmethod
    def set_land_scape(self):
        pass

    @abstractmethod
    def is_land_scape(self) -> bool:
        pass

    @abstractmethod
    def set_rotation(self, num: int):
        pass

    @abstractmethod
    def get_text(self) -> str:
        pass

    @abstractmethod
    def get_current_library(self) -> LibPDF:
        pass


class ImplementPypdf(InterfacePagePdf):

    def __init__(self, page_pdf: PageObject, num_page: int):
        super().__init__()
        self._page_pdf: PageObject = page_pdf
        self.set_num_page(num_page)

    def get_real_page(self) -> PageObject:
        return self._page_pdf

    def set_rotation(self, num: int):
        try:
            self._page_pdf.rotate(90)
        except Exception as e:
            print(e)

    def get_width(self) -> float:
        try:
            # mediaBox retorna RectangleObject
            return float(self._page_pdf.mediabox.width)
        except Exception:
            return 0

    def get_height(self) -> float:
        try:
            return float(self._page_pdf.mediabox.height)
        except Exception:
            return 0

    def set_land_scape(self):
        if self.is_land_scape():
            return
        try:
            # rotacionar para 90° (paisagem)
            self._page_pdf.rotate(90)
        except Exception:
            pass

    def is_land_scape(self) -> bool:
        try:
            return self.get_width() > self.get_height()
        except Exception as err:
            print(f'Error: {err}')
            return False

    def extract_box(self):
        raise NotImplementedError()

    def get_text(self) -> str | None:
        try:
            t = self._page_pdf.extract_text()
        except Exception as e:
            print(f'{__class__.__name__} {e}')
            return None
        else:
            return t

    def get_num_page(self) -> int:
        return self._num_page

    def get_current_library(self) -> LibPDF:
        return "pypdf"

    @classmethod
    def create_from_pypdf(cls, page: PageObject, number: int) -> ImplementPypdf:
        return cls(page, number)


class ImplementFitz(InterfacePagePdf):

    def __init__(self, page_pdf: fitz.Page, page_number: int):
        super().__init__()
        self._page_pdf: fitz.Page = page_pdf
        self.set_num_page(page_number)

    def get_real_page(self) -> fitz.Page:
        return self._page_pdf

    def get_num_page(self) -> int:
        return self._num_page

    def get_current_library(self) -> LibPDF:
        return "fitz"

    def set_rotation(self, num: int):
        try:
            self._page_pdf.set_rotation(num)
        except Exception as e:
            print(e)

    def get_width(self) -> float:
        try:
            rect = self._page_pdf.rect  # fitz.Rect
            return float(rect.width)
        except Exception:
            return 0

    def get_height(self) -> float:
        try:
            rect = self._page_pdf.rect
            return float(rect.height)
        except Exception:
            return 0

    def set_land_scape(self):
        if self.is_land_scape():
            return
        try:
            # Rotaciona para 90 graus
            self._page_pdf.set_rotation(-90)
        except Exception:
            pass

    def is_land_scape(self) -> bool:
        try:
            return self.get_width() > self.get_height()
        except Exception:
            return False

    def extract_box(self) -> fitz.TextPage:
        return self._page_pdf.get_textpage()

    def get_text(self) -> str:
        try:
            text = self._page_pdf.get_textpage().extractTEXT()
        except:
            return None
        else:
            return text

    @classmethod
    def create_from_fitz(cls, page: fitz.Page, number: int) -> InterfacePagePdf:
        return cls(page, number)


class PageDocumentPdf(ObjectAdapter):

    def __init__(self, page_pdf: InterfacePagePdf):
        super().__init__()
        self._implement_page: InterfacePagePdf = page_pdf

    def __repr__(self) -> str:
        return f'{__class__.__name__}() {self.get_num_page()}: {self.get_text()}'

    def __eq__(self, other: PageDocumentPdf) -> bool:
        return self.__hash__() == other.__hash__()

    def __hash__(self):
        return hash(f'{self.get_num_page()}{self.get_text() or ""}')

    def get_implementation(self) -> InterfacePagePdf:
        return self._implement_page

    def hash(self) -> int:
        return self.__hash__()

    def get_num_page(self) -> int:
        return self._implement_page.get_num_page()

    def set_num_page(self, num_page: int) -> None:
        self._implement_page.set_num_page(num_page)

    def get_current_library(self) -> LibPDF:
        return self._implement_page.get_current_library()

    def get_text(self) -> str:
        return self._implement_page.get_text()

    def to_list(self, separator: str = '\n') -> ArrayString:
        txt = self._implement_page.get_text()
        try:
            return ArrayString(txt.split(separator))
        except Exception as e:
            print(f'{__class__.__name__}() Erro: {e}')
            return ArrayString()

    def to_dict(self, separator: str = '\n') -> BaseTableString:
        _values = self.to_list(separator)
        tb = BaseTableString()
        if _values.size() == 0:
            return BaseTableString()

        col_num_page = ArrayString()
        for num, value in enumerate(_values):
            col_num_page.append(f'{num+1}')
        tb.add_column("TEXTO", _values)
        tb.add_column("NUM_PÁGINA", col_num_page)
        return tb

    def get_width(self) -> float:
        return self._implement_page.get_width()

    def get_height(self) -> float:
        return self._implement_page.get_height()

    def set_land_scape(self):
        self._implement_page.set_land_scape()

    def is_land_scape(self) -> bool:
        return self._implement_page.is_land_scape()

    def set_rotation(self, num: int):
        self._implement_page.set_rotation(num)

    @classmethod
    def create_from_page_pypdf(cls, page: PageObject, number: int) -> PageDocumentPdf:
        return cls(ImplementPypdf(page, number))

    @classmethod
    def create_from_page_fitz(cls, page: fitz.Page, number: int) -> PageDocumentPdf:
        if page is None:
            raise ValueError(f'fitz.Page não pode ser None')
        return cls(ImplementFitz(page, number))
