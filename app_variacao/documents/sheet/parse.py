from __future__ import annotations
from collections.abc import Iterator, Hashable
from app_variacao.documents.sheet import (
    SheetData, WorkbookData, RowSheetIterator, SheetIndexNames
)
import pandas as pd
from soup_files import File, Directory
#from sheet_stream import ListString


class FilterData(object):

    def __init__(self, col_find: str, value_find: str, *, return_cols: list[str] = None):
        self.__col_find = col_find
        self.__value_find = value_find
        if return_cols is None:
            self.__return_cols = []
        else:
            self.__return_cols = return_cols

    def get_col_find(self) -> str:
        return self.__col_find

    def get_value_find(self) -> str:
        return self.__value_find

    def get_return_cols(self) -> list[str]:
        return self.__return_cols

    def set_return_cols(self, return_cols: list[str]):
        self.__return_cols = return_cols


class SearchInData(object):

    def __init__(self, filter_data: FilterData):
        self.__filter_data: FilterData = filter_data

    def get_filter_data(self) -> FilterData:
        return self.__filter_data

    def filter_items(self, data: pd.DataFrame) -> pd.DataFrame[str]:
        _col_find = self.get_filter_data().get_col_find()
        _value_find = self.get_filter_data().get_value_find()
        final = data[data[_col_find] == _value_find].astype('str')

        if len(self.get_filter_data().get_return_cols()) > 0:
            _select = self.get_filter_data().get_return_cols()
            idx: int = final.columns.tolist().index(_col_find)
            _select.insert(idx, _col_find)
            final = final[_select]
        return final.astype('str')


class ParserData(object):

    def __init__(self, data: pd.DataFrame):
        self.__data: pd.DataFrame = data.astype(str)

    def get_data(self) -> pd.DataFrame:
        return self.__data

    def remove_na(self, col: str) -> None:
        self.__data = self.__data.dropna(subset=[col]).astype('str')

    def remove_null(self, col: str) -> None:
        self.remove_na(col)
        self.__data = self.__data[self.__data[col] != ""].astype('str')

    def get_columns(self) -> list[str]:
        if self.get_data().empty:
            raise Exception(f"{__class__.__name__} No data available")
        return self.__data.astype('str').columns.tolist()

    def select_columns(self, columns: list[str]) -> ParserData:
        if self.get_data().empty:
            raise Exception(f"{__class__.__name__} No data available")
        return ParserData(self.__data[columns])

    def concat_columns(
                self,
                columns: list[str], *,
                conc_name: str = 'concatenar',
                sep: str = '_'
            ):
        if self.get_data().empty:
            raise Exception(f"{__class__.__name__} No data available")
        self.__data[conc_name] = self.__data[columns].agg(sep.join, axis=1)


class SplitDataFrame(object):

    def __init__(self, df: pd.DataFrame, *, col_split: str):
        if df.empty:
            raise Exception(f"{__class__.__name__} No data available")

        self.df: pd.DataFrame = df
        self.col_split: str = col_split

    def _get_uniq_values_column(self) -> list[str]:
        return self.df[self.col_split].drop_duplicates().astype('str').values.tolist()

    def split_to_disk(
                self, output_path: str | Directory, *,
                extension: str = "xlsx",
                prefix: str = None
            ) -> None:
        if isinstance(output_path, str):
            output_path: Directory = Directory(output_path)

        list_items: list[str] = self._get_uniq_values_column()
        list_items.sort()
        element: str
        for num, element in enumerate(list_items):
            current = self.df[self.df[self.col_split] == element]
            filename = f"{element}.{extension}"
            if prefix is not None:
                filename = f'{prefix}-{filename}'
            file_path = output_path.join_file(filename)
            try:
                print(f'Exportando: {file_path.basename()}')
                current.to_excel(file_path.absolute(), index=False)
            except Exception as e:
                print(f'{__class__.__name__} {e}')
                print('---------------------------------------------')

    def split_to_tuple(self) -> list[pd.DataFrame]:
        set_items: list[str] = self._get_uniq_values_column()
        values: list[pd.DataFrame] = list()
        for element in set_items:
            current = self.df[self.df[self.col_split] == element]
            values.append(current)
        return values


__all__ = ['SplitDataFrame']
