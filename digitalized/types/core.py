from __future__ import annotations
from typing import Any


class ObjectAdapter(object):

    def __init__(self):
        pass

    def get_implementation(self) -> Any:
        raise NotImplementedError(
            f'{__class__.__name__} Método não implementado no adapter real'
        )

    def iqual(self, other: Any) -> bool:
        return self.__eq__(other)

    def __eq__(self, other: ObjectAdapter) -> bool:
        return self.hash() == other.hash()

    def hash(self) -> int:
        raise NotImplementedError(
            f'{__class__.__name__} Método não implementado no adapter real'
        )
