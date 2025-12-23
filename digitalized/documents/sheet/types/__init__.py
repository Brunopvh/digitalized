from __future__ import annotations
from collections.abc import Iterator
import pandas as pd


class RowSheetIterator(Iterator):

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

    def add_index(self, idx: int, name: str):
        self[idx] = name

    def get_index_from_name(self, sheet_name: str) -> int | None:
        """
        Retorna o indíce de uma planilha a partir do nome.
        :param sheet_name: string nome da planilha
        :return: int indíce de uma planilha
        """
        for idx in self.keys():
            if self[idx] == sheet_name:
                return idx
        return None

    def get_sheet_name_at(self, idx: int) -> str:
        return self[idx]

    def get_sheet_names(self) -> list[str]:
        return self.values()

    def get_first(self) -> str:
        _key = self.keys()[0]
        return self[_key]

    def get_last(self) -> str:
        _key = self.keys()[-1]
        return self[_key]

    @classmethod
    def create_from_list(cls, sheet_names: list[str]):
        sheet_idx = cls()
        for n, name in enumerate(sheet_names):
            sheet_idx.add_index(n, name)
        return sheet_idx


class SheetData(dict[str, list[str]]):

    def __init__(self):
        super().__init__({})

    def __repr__(self):
        return f"{__class__.__name__}(): {self.keys()}\n{self.values()}"

    def get_row(self, idx: int) -> list[str]:
        row = list()
        for _k in self.keys():
            value = self[_k][idx]
            row.append(value)
        return row

    def row_iterator(self, reverse: bool = False) -> RowSheetIterator:
        return RowSheetIterator(self, reverse)

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

    def add_column(self, head: str, column: list[str]):
        self[head] = column

    def get_max_rows(self) -> int:
        _keys = self.keys()
        _name = _keys[0]
        return len(self[_name])

    def to_data_frame(self) -> pd.DataFrame:
        return pd.DataFrame.from_dict(self, orient='index').transpose()

    @classmethod
    def create_from_data(cls, data: pd.DataFrame) -> SheetData:
        columns: list[str] = data.astype('str').columns.to_list()
        sheet_data = cls()
        for col in columns:
            sheet_data.add_column(col, data[col].astype('str').values.tolist())
        return sheet_data


class WorkbookData(dict[str, SheetData]):

    def __init__(self):
        super().__init__({})
        self.__sheet_index_names: SheetIndexNames | None = None

    def __repr__(self):
        return f"{__class__.__name__}() {super().__repr__()}"

    def get_sheet_index_names(self) -> SheetIndexNames:
        """
        Dicionário com os nomes das planilhas apontando para os respetivos indices.
        :return: Dicionário com int, str
        """
        if self.__sheet_index_names is None:
            self.__sheet_index_names = SheetIndexNames()
            for n, name in enumerate(self.keys()):
                self.__sheet_index_names.add_index(n, name)
        return self.__sheet_index_names

    def set_sheet_index_names(self, sheet_index_names: SheetIndexNames):
        self.__sheet_index_names = sheet_index_names

    def get_first(self) -> SheetData:
        return self.get_sheet_at(0)

    def get_last(self) -> SheetData:
        _keys = self.keys()
        _last_key = _keys[-1]
        return self[_last_key]

    def get_sheet_at(self, idx: int) -> SheetData:
        _keys = self.keys()
        return self[_keys[idx]]

    def get_sheet(self, name: str) -> SheetData:
        return self[name]

    def keys(self) -> list[str]:
        return list(super().keys())

    def values(self) -> list[SheetData]:
        return list(super().values())

    def add_sheet(self, name: str, sheet: SheetData):
        self[name] = sheet
