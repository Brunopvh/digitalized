from __future__ import annotations
from io import BytesIO
from abc import ABC, abstractmethod
from openpyxl import load_workbook, Workbook
from collections.abc import Iterator
from pandas import DataFrame
from documents.erros import *

class RowIterator(Iterator):

    def __init__(self, sheet: SheetData, reverse: bool = False):
        self.sheet: SheetData = sheet
        self.reverse: bool = reverse

        if self.reverse:
            self.__current_idx: int = -1
            self.__max_idx: int = -(len(self.sheet.get_first())) - 1
        else:
            self.__current_idx: int = 0
            self.__max_idx: int = len(self.sheet.get_first())

    def has_next(self) -> bool:
        if self.reverse:
            if self.__current_idx <= self.__max_idx:
                return False
        else:
            if self.__current_idx >= self.__max_idx:
                return False
        return True

    def __next__(self) -> list[str]:
        if not self.has_next():
            raise StopIteration()
        idx_value = self.__current_idx
        if self.reverse:
            self.__current_idx -= 1
        else:
            self.__current_idx += 1
        return self.sheet.get_row(idx_value)


class SheetIndexNames(dict[int, str]):

    def __init__(self):
        super().__init__({})

    def keys(self) -> list[int]:
        return list(super().keys())

    def values(self) -> list[str]:
        return list(super().values())

    def get_index_from_name(self, sheet_name: str) -> int | None:
        for idx in self.keys():
            if self[idx] == sheet_name:
                return idx
        return None

    def get_sheet_names(self) -> list[str]:
        return self.values()


class SheetData(dict[str, list[str]]):

    def __init__(self):
        super().__init__({})

    def get_row(self, idx: int) -> list[str]:
        row = list()
        for _k in self.keys():
            value = self[_k][idx]
            row.append(value)
        return row

    def row_iterator(self, reverse: bool = False) -> RowIterator:
        return RowIterator(self, reverse)

    def get_first(self) -> list[str]:
        _k = self.keys()[0]
        return self[_k]

    def get_last(self) -> list[str]:
        _k = self.keys()[-1]
        return self[_k]

    def header(self) -> list[str]:
        return self.keys()

    def keys(self) -> list[str]:
        return list(super().keys())

    def values(self) -> list[list[str]]:
        return list(super().values())

    def get_max_rows(self) -> int:
        _keys = self.keys()
        _name = _keys[0]
        return len(self[_name])

    def to_data_frame(self) -> DataFrame:
        return DataFrame(self)


class WorkbookData(dict[str, SheetData]):

    def __init__(self):
        super().__init__({})
        self.__sheet_index_names: SheetIndexNames = None

    def get_sheet_index_names(self) -> SheetIndexNames:
        """
        Dicionário com os nomes das planilhas apontando para os respetivos indices.
        :return: Dicionário com int, str
        """
        if self.__sheet_index_names is None:
            raise UndefinedSheetIndex()
        return self.__sheet_index_names

    def set_sheet_index_names(self, sheet_index_names: SheetIndexNames):
        self.__sheet_index_names = sheet_index_names

    def keys(self) -> list[str]:
        return list(super().keys())

    def values(self) -> list[SheetData]:
        return list(super().values())


class ExcelLoad(ABC):

    @abstractmethod
    def get_sheet_index(self) -> SheetIndexNames:
        pass

    @abstractmethod
    def get_workbook_data(self) -> WorkbookData:
        pass

    def get_sheet_at(self, idx: int) -> SheetData:
        idx_workbook: SheetIndexNames = self.get_sheet_index()
        name = idx_workbook[idx]
        return self.get_workbook_data()[name]

    def get_sheet(self, sheet_name: str | None) -> SheetData:
        if sheet_name is not None:
            return self.get_workbook_data()[sheet_name]
        return self.get_sheet_at(0)


class ExcelLoadOpenPyxl(ExcelLoad):

    def __init__(self, file_excel: str | BytesIO):
        super().__init__()
        self.file_excel: str | BytesIO = file_excel
        self.__workbook: Workbook = None

    def __get_wb(self) -> Workbook:
        if self.__workbook is None:
            self.__workbook = load_workbook(self.file_excel)
        return self.__workbook

    def __get_sheet_data_from_name(self, name: str) -> SheetData:
        sheet_data = SheetData()
        wb = self.__get_wb()
        # Assumindo que você quer ler a planilha apenas para obter os dados,
        # o modo ReadOnly é eficiente, mas ReadOnlyWorksheet não tem o
        # atributo .rows direto em algumas versões.
        # Vamos usar a planilha normal para garantir compatibilidade.
        ws = wb[name]  # Acessa a planilha pelo nome

        # 1. Pega o iterador de linhas
        rows_iterator = ws.rows

        # 2. Extrai e processa o cabeçalho (primeira linha)
        try:
            # O 'next' avança o iterador para a segunda linha após esta chamada
            header_cells = next(rows_iterator)
        except StopIteration:
            # Se a planilha estiver vazia (sem cabeçalho), retorna vazio
            return sheet_data

        # Prepara o SheetData com as chaves do cabeçalho
        # É importante armazenar o cabeçalho como uma lista separada para indexação
        header_list: list[str] = []
        for cell in header_cells:
            # Garante que o nome da coluna seja uma string (usando str() no valor)
            col_name = str(cell.value) if cell.value is not None else ''
            # Adiciona o nome da coluna à lista de cabeçalho
            header_list.append(col_name)
            # Inicializa a lista de valores para cada coluna no SheetData
            sheet_data[col_name] = []

        # 3. Itera sobre as linhas restantes (dados)
        for row in rows_iterator:

            # Itera sobre as células da linha
            for col_index, cell in enumerate(row):
                # Garante que a célula tem um índice correspondente ao cabeçalho
                if col_index < len(header_list):
                    # Pega o nome da coluna (chave) usando o índice
                    col_name = header_list[col_index]
                    # Converte o valor da célula para string (conforme o requisito de SheetData)
                    cell_value_str = str(cell.value) if cell.value is not None else ''
                    # Adiciona o valor à lista da coluna correspondente no SheetData
                    sheet_data[col_name].append(cell_value_str)
        return sheet_data

    def get_sheet_index(self) -> SheetIndexNames:
        wb = self.__get_wb()
        sheet_index = SheetIndexNames()
        names = wb.sheetnames
        for num, name in enumerate(names):
            sheet_index[num] = name
        return sheet_index

    def get_workbook_data(self) -> WorkbookData:
        final = WorkbookData()
        sheet_index = self.get_sheet_index()
        final.set_sheet_index_names(sheet_index)
        for sheet_name in sheet_index.get_sheet_names():
            sheet_data = self.__get_sheet_data_from_name(sheet_name)
            final[sheet_name] = sheet_data
        return final


class ReadSheetExcel(object):

    def __init__(self, reader: ExcelLoad):
        self.reader: ExcelLoad = reader

    def get_workbook_data(self) -> WorkbookData:
        return self.reader.get_workbook_data()

    def get_sheet_at(self, idx: int) -> SheetData:
        return self.reader.get_sheet_at(idx)

    def get_sheet(self, sheet_name: str | None = None) -> SheetData:
        return self.reader.get_sheet(sheet_name)

    def get_sheet_index(self) -> SheetIndexNames:
        return self.reader.get_sheet_index()

    @classmethod
    def create_load_open_pyxl(cls, file_excel: str | BytesIO) -> ReadSheetExcel:
        rd = ExcelLoadOpenPyxl(file_excel)
        return cls(rd)
