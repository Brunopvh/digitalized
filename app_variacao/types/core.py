from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any
from app_variacao.types.array import ArrayList


class ObjectAdapter(object):

    def __init__(self):
        super().__init__()

    def get_real_module(self) -> Any:
        raise NotImplementedError()

    def get_implementation(self) -> Any:
        raise NotImplementedError(
            f'{__class__.__name__} Método não implementado no adapter real'
        )

    def iqual(self, other: ObjectAdapter) -> bool:
        return self.__eq__(other)

    def __eq__(self, other: ObjectAdapter) -> bool:
        return self.hash() == other.hash()

    def hash(self) -> int:
        return self.__hash__()

    def __hash__(self) -> int:
        return self.get_implementation().hash()

    @classmethod
    def build_interface(cls) -> BuilderInterface:
        pass


class BuilderInterface(ABC):

    @abstractmethod
    def create(self) -> Any:
        pass


class ObjectCommand(object):

    def __init__(self, **kwargs):
        pass

    def execute(self) -> None:
        pass


class ObjectRunCommands(object):

    def __init__(self, **kwargs):
        self._commands: ArrayList[ObjectCommand] = ArrayList()

    def clear(self):
        self._commands.clear()

    def contains_command(self, command: ObjectCommand) -> bool:
        return self._commands.contains(command)

    def add_command(self, cmd: ObjectCommand) -> None:
        pass

    def run_commands(self) -> None:
        for cmd in self._commands:
            cmd.execute()
