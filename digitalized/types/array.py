from __future__ import annotations
from collections.abc import Iterator
from typing import Any, Callable, TypeVar, TypedDict, Generic
import pandas as pd

T = TypeVar('T')


def contains_text(text: str, values: list[str], *, case: bool = True, iqual: bool = False) -> bool:
    """
        Verificar se um texto existe em lista de strings.
    """
    if case:
        if iqual:
            for x in values:
                if text == x:
                    return True
        else:
            for x in values:
                if text in x:
                    return True
    else:
        if iqual:
            for x in values:
                if text.upper() == x.upper():
                    return True
        else:
            for x in values:
                if text.upper() in x.upper():
                    return True
    return False


def find_index(text: str, values: list[str], *, case: bool = True, iqual: bool = False) -> int | None:
    """
        Verificar se um texto existe em lista de ‘strings’ se existir, retorna o índice da posição
    do texto na lista.
    """
    _idx: int | None = None
    if case:
        if iqual:
            for num, x in enumerate(values):
                if text == x:
                    _idx = num
                    break
        else:
            for num, x in enumerate(values):
                if text in x:
                    _idx = num
                    break
    else:
        if iqual:
            for num, x in enumerate(values):
                if text.upper() == x.upper():
                    _idx = num
                    break
        else:
            for num, x in enumerate(values):
                if text.upper() in x.upper():
                    _idx = num
                    break
    return _idx


def find_all_index(text: str, values: list[str], *, case: bool = True, iqual: bool = False) -> list[int]:
    """

    """
    items: list[int] = list()
    if iqual:
        for num, i in enumerate(values):
            if case:
                if i == text:
                    items.append(num)
            else:
                if text.lower() == i.lower():
                    items.append(num)
    else:
        for num, i in enumerate(values):
            if case:
                if text in i:
                    items.append(num)
            else:
                if text.lower() in i.lower():
                    items.append(num)
    return items


class ArrayList(list[T], Generic[T]):

    def __init__(self, items: list[T] = None):
        if items is None:
            super().__init__([])
        else:
            super().__init__(items)

    def __hash__(self):
        return hash(tuple(self))

    def map(self, func: Callable[[T], Any]) -> ArrayList[T]:
        return ArrayList([func(item) for item in self])

    def apply(self, func: Callable[[T], Any]) -> ArrayList[Any]:
        return ArrayList([func(item) for item in self])

    @property
    def empty(self) -> bool:
        return self.size() == 0

    def get_first(self) -> T:
        return self[0]

    def get_last(self) -> T:
        return self[-1]

    def size(self) -> int:
        return len(self)

    def contains(self, _o: Any) -> bool:
        for i in self:
            if _o == i:
                return True
        return False

    def hash(self) -> int:
        return hash(self)

    def for_each(self, func: Callable[[T], Any]) -> None:
        for i in self:
            func(i)


class ArrayString(ArrayList[str]):

    def __init__(self, items: list[str] = None):
        super().__init__(items)

    def get_first(self) -> str:
        return self[0]

    def get_last(self) -> str:
        return self[-1]

    def apply_separator(self, separator: str = ' ') -> ArrayString:
        new = list()
        for x in self:
            if separator in x:
                new.extend(x.split(separator))
            else:
                new.append(x)
        return ArrayString(new)

    def strip(self) -> None:
        for num, value in enumerate(self):
            if (value is None) or (value == ""):
                continue
            self[num] = value.strip()

    def to_upper(self) -> None:
        for num, value in enumerate(self):
            if (value is None) or (value == ""):
                continue
            self[num] = value.upper()

    def to_lower(self) -> None:
        for num, value in enumerate(self):
            if (value is None) or (value == ""):
                continue
            self[num] = value.lower()

    def get_numerics(self) -> ArrayList[int]:
        new: ArrayList[int] = ArrayList()
        for value in self:
            if (value is None) or (value == ""):
                continue
            if value.isnumeric():
                new.append(int(value))
        return new

    def contains_text(self, text: str, *, iqual: bool = True, case: bool = True):
        return contains_text(text, self, iqual=iqual, case=case)

    def find_index(self, text: str, *, iqual: bool = True, case: bool = True) -> int | None:
        return find_index(text, self, iqual=iqual, case=case)

    def find_all_index(self, text: str, *, iqual: bool = True, case: bool = True) -> ArrayList[int]:
        return ArrayList(find_all_index(text, self, iqual=iqual, case=case))

    def find(self, value: str, *, iqual: bool = True, case: bool = True) -> str | None:
        idx = self.find_index(value, iqual=iqual, case=case)
        if idx is None:
            return None
        return self[idx]

    def find_all(self, value: str, *, iqual: bool = True, case: bool = True) -> ArrayString:
        list_index = self.find_all_index(value, iqual=iqual, case=case)
        new = list()
        for num in list_index:
            new.append(self[num])
        return ArrayString(new)

    def append(self, string: str):
        if not isinstance(string, str):
            raise TypeError(f"expected str, got {type(string)}")
        super().append(string)

    def get_next_index(self, value: str, *, iqual: bool = True, case: bool = True) -> int | None:
        idx = self.find_index(value, iqual=iqual, case=case)
        if idx is None:
            return None
        _size = self.size()
        if idx+1 >= _size:
            return None
        return idx + 1

    def get_previous_index(self, value: str, *, iqual: bool = True, case: bool = True) -> int | None:
        idx = self.find_index(value, iqual=iqual, case=case)
        if idx is None:
            return None
        if self.size() == 1:
            return None
        return idx - 1

    def get_next_all_index(self, value: str, *, iqual: bool = True, case: bool = True) -> ArrayList[int]:
        idx = self.find_index(value, iqual=iqual, case=case)
        if (idx is None) or (idx+1 >= self.size()):
            return ArrayList()

        new: ArrayList[int] = ArrayList()
        for num, value in enumerate(self[idx+1:]):
            new.append(num+idx+1)
        return new

    def get_previous_all_index(self, value: str, *, iqual: bool = True, case: bool = True) -> ArrayList[int]:
        idx = self.find_index(value, iqual=iqual, case=case)
        if (idx is None) or (idx == 0):
            return ArrayList()

        list_index = ArrayList()
        for num, value in enumerate(self[0:idx]):
            list_index.append(num)
        return list_index

    def get_next(self, value: str, *, iqual: bool = True, case: bool = True) -> str | None:
        idx = self.get_next_index(value, iqual=iqual, case=case)
        if idx is None:
            return None
        return self[idx]

    def get_previous(self, value: str, *, iqual: bool = True, case: bool = True) -> str | None:
        idx = self.get_previous_index(value, iqual=iqual, case=case)
        if idx is None:
            return None
        return self[idx]

    def get_next_all(self, value: str, *, iqual: bool = True, case: bool = True) -> ArrayString:
        list_idx: ArrayList[int] = self.get_next_all_index(value, iqual=iqual, case=case)
        new = ArrayString()
        for num in list_idx:
            new.append(self[num])
        return new

    def get_back_all(self, value: str, *, iqual: bool = True, case: bool = True) -> ArrayString:
        list_idx: ArrayList[int] = self.get_previous_all_index(value, iqual=iqual, case=case)
        new = ArrayString()
        for num in list_idx:
            new.append(self[num])
        return new


class BaseDict(dict[str, T], Generic[T]):

    def __init__(self, values: dict = None) -> None:
        if values is None:
            super().__init__({})
        else:
            super().__init__(values)

    def get_first(self) -> T:
        _k = self.keys().get_first()
        return self[_k]

    def set_first(self, value: T) -> None:
        self[self.keys().get_first()] = value

    def get_last(self) -> T:
        return self[self.keys().get_last()]

    def set_last(self, value: T) -> None:
        self[self.keys().get_last()] = value

    def size_keys(self) -> int:
        return len(self.keys())

    def size_values(self) -> int:
        return len(self.values())

    def keys(self) -> ArrayString:
        return ArrayString(list(super().keys()))


class TableRow(ArrayList):

    def __init__(self, index: int, items: list[T] = None):
        super().__init__(items)
        self.__idx = index

    def __repr__(self):
        return f'{self.__class__.__name__}() index {self.get_index()}: {super().__repr__()}'

    def set_index(self, idx: int):
        self.__idx = idx

    def get_index(self) -> int:
        return self.__idx

    def to_array_string(self) -> ArrayString:
        return ArrayString([str(x) for x in self])


T_LIST = TypeVar('T_LIST', bound=ArrayList)


class BaseTable(BaseDict[T_LIST], Generic[T_LIST]):

    def __init__(self, values: dict[str, ArrayList[T]] | None = None) -> None:
        super().__init__(values)

    def row_iterator(self, reverse: bool = False) -> RowIterator:
        return RowIterator(self, reverse=reverse)

    @property
    def empty(self) -> bool:
        return self.keys().size() == 0

    def __setitem__(self, key, value):
        if not isinstance(value, ArrayList):
            raise ValueError(f'Use ArrayString() instead of {type(value)}')
        if not self.empty:
            if value.size() != self.get_total_rows():
                raise IndexError(f'As colunas devem ter tamanho igual há: {self.get_total_rows()}')
        super().__setitem__(key, value)

    def get_first(self) -> ArrayList[T]:
        return self[self.keys().get_first()]

    def get_last(self) -> ArrayList[T]:
        return self[self.keys().get_last()]

    def values(self) -> ArrayList[ArrayList[T]]:
        return ArrayList(list(super().values()))

    def get_total_rows(self) -> int:
        if self.empty:
            return 0
        return self.get_first().size()

    def get_row(self, idx: int) -> TableRow:
        _keys = self.keys()
        _items = list()
        for _k in _keys:
            _items.append(self[_k][idx])
        return TableRow(idx, _items)

    def add_column(self, name: str, value: ArrayList):
        self[name] = value

    @classmethod
    def create_from_data(cls, data: pd.DataFrame) -> BaseTable:
        tb = cls()
        cols = data.columns.tolist()
        cols = [str(x) for x in cols]
        for c in cols:
            tb[c] = ArrayList(data[c].values.tolist())
        return tb


class BaseTableString(BaseTable[ArrayString]):

    def __init__(self, values: BaseTable[ArrayString] | dict[str, ArrayString] | None = None) -> None:
        if values is None:
            super().__init__({})
        elif isinstance(values, BaseTable):
            super().__init__(values)
        elif isinstance(values, dict):
            super().__init__(BaseTable(values))
        else:
            raise TypeError(f'Use dict()|BaseTable(), não {type(values)}')

    def __getitem__(self, key: str) -> ArrayString:
        return super().__getitem__(key)

    def get_first(self) -> ArrayString:
        return self[self.keys().get_first()]

    def get_last(self) -> ArrayString:
        return self[self.keys().get_last()]

    def index_key(self, key: str) -> int:
        return self.keys().find_index(key, iqual=True, case=True)

    def exist_key(self, key: str) -> bool:
        return True if self.keys().contains(key) else False

    def contains_column(self, name: str) -> bool:
        return self.keys().contains(name)

    def add_column(self, name: str, values: ArrayString):
        self[name] = values

    def values(self) -> ArrayList[ArrayString]:
        return ArrayList([ArrayString(x) for x in super().values()])

    @classmethod
    def create_from_data(cls, data: pd.DataFrame) -> BaseTableString:
        tb = cls()
        cols = data.columns.tolist()
        cols = [str(x) for x in cols]
        for c in cols:
            tb[c] = ArrayList(data[c].astype('str').values.tolist())
        return tb


class RowIterator(Iterator):

    def __init__(self, table: BaseTable, reverse: bool = False):
        self.table: BaseTable = table
        self.reverse: bool = reverse

        if self.reverse:
            self.__current_idx: int = -1
            self.__final_idx: int = -self.table.get_first().size()-1
        else:
            self.__current_idx: int = 0
            self.__final_idx: int = self.table.get_first().size()

    def has_next(self) -> bool:
        if self.reverse:
            if self.__current_idx <= self.__final_idx:
                return False
        else:
            if self.__current_idx >= self.__final_idx:
                return False
        return True

    def __next__(self) -> TableRow:
        if not self.has_next():
            raise StopIteration()
        idx_value = self.__current_idx
        if self.reverse:
            self.__current_idx -= 1
        else:
            self.__current_idx += 1
        return self.table.get_row(idx_value)


