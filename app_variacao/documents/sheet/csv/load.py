from __future__ import annotations
from io import BytesIO, StringIO
from abc import ABC, abstractmethod
import csv
import chardet  # Sugestão: pip install chardet (ou use um fallback manual)
from io import StringIO, BytesIO
import pandas as pd
from typing import Literal

# Módulos locais (ajuste os caminhos conforme sua estrutura)
from app_variacao.documents.erros import LoadWorkbookError
from app_variacao.documents.sheet.types import SheetData, WorkbookData, SheetIndexNames
from app_variacao.types.core import ObjectAdapter

CsvEncoding = Literal['utf-8', 'iso-8859-1']


class CsvLoad(ABC):
    """Classe base abstrata para carregadores de CSV."""

    @abstractmethod
    def hash(self) -> int:
        pass

    @abstractmethod
    def get_sheet_index(self) -> SheetIndexNames:
        pass

    @abstractmethod
    def get_workbook_data(self) -> WorkbookData:
        pass

    def get_sheet_at(self, idx: int) -> SheetData:
        idx_sheet_names: SheetIndexNames = self.get_sheet_index()
        name = idx_sheet_names[idx]
        return self.get_workbook_data()[name]

    def get_sheet(self, sheet_name: str | None) -> SheetData:
        if sheet_name is not None:
            return self.get_workbook_data()[sheet_name]
        return self.get_sheet_at(0)


class CsvLoadNative(CsvLoad):
    """Leitura de CSV usando a biblioteca nativa 'csv' do Python."""

    def __init__(self, file_csv: str | BytesIO, delimiter: str = '\t', encoding: str = 'utf-8'):
        super().__init__()
        self.file_csv: str | BytesIO = file_csv
        self.delimiter: str = delimiter
        self.encoding: str = encoding

    def hash(self) -> int:
        return hash(self.file_csv)

    def _get_content(self) -> str:
        if isinstance(self.file_csv, BytesIO):
            return self.file_csv.getvalue().decode(self.encoding)
        with open(self.file_csv, 'r', encoding=self.encoding) as f:
            return f.read()

    def get_sheet_index(self) -> SheetIndexNames:
        sheet_index = SheetIndexNames()
        sheet_index.add_index(0, "Sheet1")
        return sheet_index

    def get_workbook_data(self) -> WorkbookData:
        workbook_data = WorkbookData()
        sheet_data = SheetData()

        try:
            content: str = self._get_content()
            reader = csv.DictReader(StringIO(content), delimiter=self.delimiter)
            # Inicializa colunas baseadas no fieldnames
            if reader.fieldnames:
                for header in reader.fieldnames:
                    sheet_data[header] = []
                for row in reader:
                    for header in reader.fieldnames:
                        sheet_data[header].append(str(row[header] or ''))
            workbook_data.add_sheet("Sheet1", sheet_data)
        except Exception as e:
            raise LoadWorkbookError(f"CsvLoadNative Error: {e}")
        return workbook_data


class CsvLoadPandas(CsvLoad):
    """Leitura de CSV usando a biblioteca Pandas."""

    def __init__(self, file_csv: str | BytesIO, delimiter: str = '\t', encoding: str = 'utf-8'):
        super().__init__()
        self.file_csv = file_csv
        self.delimiter = delimiter
        self.encoding = encoding

    def hash(self) -> int:
        return hash(self.file_csv)

    def get_sheet_index(self) -> SheetIndexNames:
        sheet_index = SheetIndexNames()
        sheet_index.add_index(0, "Sheet1")
        return sheet_index

    def get_workbook_data(self) -> WorkbookData:
        try:
            # Forçamos todos os dados como string para manter consistência com o ExcelLoad
            df = pd.read_csv(self.file_csv, sep=self.delimiter, encoding=self.encoding, dtype=str).fillna('')
            workbook_data = WorkbookData()
            # Utiliza o método auxiliar create_from_data que você já possui no SheetData
            workbook_data.add_sheet("Sheet1", SheetData.create_from_data(df))
            return workbook_data
        except Exception as e:
            raise LoadWorkbookError(f"CsvLoadPandas Error: {e}")


class ReadSheetCsv(ObjectAdapter):
    """Adapter para leitura de planilhas CSV."""

    def __init__(self, reader: CsvLoad):
        super().__init__()
        self.__reader: CsvLoad = reader

    def get_implementation(self) -> CsvLoad:
        return self.__reader

    def hash(self) -> int:
        return self.get_implementation().hash()

    def get_workbook_data(self) -> WorkbookData:
        return self.__reader.get_workbook_data()

    def get_sheet_at(self, idx: int) -> SheetData:
        return self.__reader.get_sheet_at(idx)

    def get_sheet(self, sheet_name: str | None = None) -> SheetData:
        return self.__reader.get_sheet(sheet_name)

    def get_sheet_index(self) -> SheetIndexNames:
        return self.__reader.get_sheet_index()

    @classmethod
    def create_load_native(
                cls, file_csv: str | BytesIO, *,
                delimiter: str = '\t',
                encoding: CsvEncoding = 'utf-8'
            ) -> ReadSheetCsv:
        rd = CsvLoadNative(file_csv, delimiter, encoding)
        return cls(rd)

    @classmethod
    def create_load_pandas(
                cls, file_csv: str | BytesIO, *,
                delimiter: str = '\t',
                encoding: CsvEncoding = 'utf-8'
            ) -> ReadSheetCsv:
        rd = CsvLoadPandas(file_csv, delimiter, encoding)
        return cls(rd)


__all__ = ['ReadSheetCsv', 'CsvLoad']
