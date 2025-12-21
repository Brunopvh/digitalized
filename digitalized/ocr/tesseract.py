#!/usr/bin/env python3
from __future__ import annotations
import os
from shutil import which
from soup_files import File, KERNEL_TYPE, Directory, InputFiles
from digitalized.types.array import ArrayList, BaseDict
from digitalized.ocr.error import TesseractNotFoundError


def get_tess_common_data_dirs() -> list[Directory]:
    if KERNEL_TYPE == 'Windows':
        return [
            Directory("C:\\Program Files (x86)\\Tesseract-OCR\\tessdata"),
        ]
    elif KERNEL_TYPE == 'Linux':
        return [
            Directory('/usr/share/tesseract-ocr/5/tessdata'),
        ]
    else:
        return []


def __get_path_tesseract_unix() -> File | None:
    out = which('tesseract')
    if out is None:
        return None
    return File(out)


def __get_path_tesseract_windows() -> File | None:
    out = which('tesseract.exe')
    if out is None:
        if os.path.isfile("C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe"):
            return File("C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe")
        return None
    return File(out)


def get_path_tesseract_sys() -> File | None:
    if KERNEL_TYPE == 'Windows':
        return __get_path_tesseract_windows()
    return __get_path_tesseract_unix()


class CheckTesseractSystem(object):

    _instance = None  # Atributo de classe para armazenar a instância singleton

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(CheckTesseractSystem, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # Garante que __init__ não será executado mais de uma vez
        if hasattr(self, '_initialized') and self._initialized:
            return
        self._initialized = True
        self.__tess_data_dir: Directory = None
        self.__file_tesseract: File = None

    def get_file_tesseract(self) -> File | None:
        if self.__file_tesseract is None:
            self.__file_tesseract = get_path_tesseract_sys()
        return self.__file_tesseract

    def set_file_tesseract(self, new: File):
        self.__file_tesseract = new

    def get_tess_data_dir(self) -> Directory | None:
        return self.__tess_data_dir

    def set_tess_data_dir(self, tess_data_dir: Directory) -> None:
        self.__tess_data_dir = tess_data_dir

    @classmethod
    def build(cls) -> CheckTesseractSystem:
        _check = cls()
        if _check.get_file_tesseract() is None:
            _check.set_file_tesseract(get_path_tesseract_sys())
        if _check.get_tess_data_dir() is None:
            for path in get_tess_common_data_dirs():
                if path.path.exists():
                    _check.set_tess_data_dir(path)
        return _check


class BinTesseract(object):
    """
        Fornece o caminho absoluto do tesseract instalado no sistema, se
    disponível. Você pode usar um binário alternativo, basta informar
    o caminho do binário desejado no construtor.
    """
    _instance = None  # Atributo de classe para armazenar a instância singleton

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(BinTesseract, cls).__new__(cls)
        return cls._instance

    def __init__(self, path: File, *, tess_data_dir: Directory = None, lang: str = None) -> None:
        # Garante que __init__ não será executado mais de uma vez
        if hasattr(self, '_initialized') and self._initialized:
            return
        if (path is None) or (not path.exists()):
            raise TesseractNotFoundError(
                f'{__class__.__name__} Tesseract não encontrado em {path.absolute()}'
            )
        self.__path_tesseract: File = path
        self._initialized = True
        self.__tess_data_dir: Directory | None = tess_data_dir
        self.__lang: str = lang

    def __hash__(self):
        return hash(self.__path_tesseract.absolute())

    def set_path_tesseract(self, path: File):
        if not isinstance(path, File):
            return
        self.__path_tesseract = path

    def get_path_tesseract(self) -> File | None:
        return self.__path_tesseract

    def set_lang(self, lang: str):
        if not isinstance(lang, str):
            return
        self.__lang = lang

    def get_lang(self):
        return self.__lang

    def set_tessdata_dir(self, tessdata_dir: Directory) -> None:
        if not isinstance(tessdata_dir, Directory):
            return
        self.__tess_data_dir = tessdata_dir

    def get_tessdata_dir(self) -> Directory | None:
        return self.__tess_data_dir

    def get_local_langs(self) -> ArrayList[File]:
        if self.get_tessdata_dir() is None:
            return ArrayList()
        _in = InputFiles(self.get_tessdata_dir())
        return ArrayList(_in.get_files_with(infile='traineddata'))

    def exists(self) -> bool:
        """Verifica se o binário tesseract existe"""
        if self.__path_tesseract is None:
            return False
        return self.__path_tesseract.exists()

    @classmethod
    def builder(cls) -> BuildTesseract:
        return BuildTesseract()


class BuildTesseract(object):

    def __init__(self):
        self.__TESS_DATA_DIR: Directory | None = CheckTesseractSystem.build().get_tess_data_dir()
        self.__TESS_BIN: File | None = CheckTesseractSystem().get_file_tesseract()
        self.__TESS_LANG: str = None

    def set_lang(self, lang: str) -> BuildTesseract:
        self.__TESS_LANG = lang
        return self

    def set_tessdata_dir(self, tessdata_dir: Directory) -> BuildTesseract:
        self.__TESS_DATA_DIR = tessdata_dir
        return self

    def set_tess_bin(self, tess_bin: File) -> BuildTesseract:
        self.__TESS_BIN = tess_bin
        return self

    def build(self) -> BinTesseract:
        if self.__TESS_BIN is None:
            raise TesseractNotFoundError(
                f'{__class__.__name__} path tesseract não foi definido!'
            )
        if not self.__TESS_BIN.exists():
            raise TesseractNotFoundError(
                f'{__class__.__name__} path tesseract não foi definido!'
            )

        return BinTesseract(
            self.__TESS_BIN,
            tess_data_dir=self.__TESS_DATA_DIR,
            lang=self.__TESS_LANG,
        )


__all__ = ['BinTesseract', 'get_path_tesseract_sys', 'CheckTesseractSystem']
