
class TesseractNotFoundError(FileNotFoundError):

    def __init__(self, message: str = 'Tesseract não encontrado') -> None:
        super().__init__(message)


class NotImplementedModuleTesseractError(Exception):

    def __init__(self, message: str = 'Erro, módulo tesseract não implementado') -> None:
        super().__init__(message)
