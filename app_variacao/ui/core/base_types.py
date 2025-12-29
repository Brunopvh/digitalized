#!/usr/bin/env python3
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

T = TypeVar('T')


#=================================================================#
# Notificadores e observadores
#=================================================================#
class CoreDict(dict[str, T], Generic[T]):

    def __init__(self, values: dict = None) -> None:
        if values is None:
            super().__init__({})
        else:
            super().__init__(values)

    def __repr__(self):
        return f'{self.__class__.__name__}()\n{super().__repr__()}\n'

    def get_first(self) -> T:
        _k = self.keys()[0]
        return self[_k]

    def set_first(self, value: T) -> None:
        self[self.keys()[0]] = value

    def get_last(self) -> T:
        return self[self.keys()[-1]]

    def set_last(self, value: T) -> None:
        self[self.keys()[-1]] = value

    def keys(self) -> list[str]:
        return list(super().keys())


class MessageNotification(CoreDict):

    def __init__(self, values: dict[str, T] = None) -> None:
        super().__init__(values)

    def __repr__(self):
        return f'{self.__class__.__name__}(\n{super().__repr__()}\n)'

    def get_first(self) -> T:
        _k = self.keys()[0]
        return self[_k]

    def set_first(self, value: T) -> None:
        self[self.keys()[0]] = value

    def get_last(self) -> T:
        return self[self.keys()[-1]]

    def set_last(self, value: T) -> None:
        self[self.keys()[-1]] = value

    def keys(self) -> list[str]:
        return list(super().keys())


# Sujeito notificador
class AbstractNotifyProvider(ABC):
    def __init__(self):
        self.observer_list: list[AbstractObserver] = []
        self._name = None

    def get_name(self) -> str:
        return self._name

    def set_name(self, name: str) -> None:
        return self._name

    def add_observer(self, observer: AbstractObserver):
        self.observer_list.append(observer)

    def remove_observer(self, observer: AbstractObserver):
        if len(self.observer_list) < 1:
            return
        self.observer_list.remove(observer)

    def clear(self):
        self.observer_list.clear()

    @abstractmethod
    def send_notify(self, _obj: MessageNotification[T] = None):
        pass


# Sujeito Observador
class AbstractObserver(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def receiver_notify(self, _obj_receiver: MessageNotification[T]):
        """Receber atualizações."""
        pass

