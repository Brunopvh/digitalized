

class UndefinedSheetIndex(Exception):

    def __init__(self, message: str = 'SheetIndexNames não foi definido') -> None:
        super().__init__(message)


class LoadWorkbookError(Exception):

    def __init__(self, message: str = 'Erro ao tentar ler Workbook') -> None:
        super().__init__(message)


class InvalidSourceImageError(Exception):

    def __init__(self, message: str = 'Erro, use bytes de imagem') -> None:
        super().__init__(message)


class NotImplementedModuleError(Exception):

    def __init__(self, message: str = 'Erro, módulo não implementado') -> None:
        super().__init__(message)


class NotImplementedModuleImageError(NotImplementedModuleError):

    def __init__(self, message: str = 'Erro, módulo IMAGEM não implementado') -> None:
        super().__init__(message)


class NotImplementedModulePdfError(NotImplementedModuleError):

    def __init__(self, message: str = 'Erro, módulo PDF não implementado') -> None:
        super().__init__(message)


class NotImplementedInvertColor(NotImplementedError):

    def __init__(self, message: str = 'Adaptador InvertColor não implementado...') -> None:
        super().__init__(message)




