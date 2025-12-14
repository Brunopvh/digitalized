

class UndefinedSheetIndex(Exception):

    def __init__(self, message: str = 'SheetIndexNames não foi definido') -> None:
        super().__init__(message)
