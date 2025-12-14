from __future__ import annotations
import zipfile
import xml.etree.ElementTree as ET


def read_zip_xml(
        zf: zipfile.ZipFile, path: str
) -> tuple[ET.ElementTree | None, Exception | None]:
    """Auxiliar para ler o conteúdo de um arquivo XML dentro do ZIP."""
    try:
        with zf.open(path) as file:
            return ET.parse(file), None
    except Exception as err:
        return None, err


class WorkbookMappingXML(dict[str, str]):
    """
    Mapeia Nome da Aba -> Sheet ID e Sheet ID -> XML prefix (ex: sheet1).
    """

    def __init__(self):
        super().__init__({})
        # sheetId -> sheet prefix (ex: sheet1)
        # Chaves são os nomes das abas (str)
        # Valores são os sheetId (str)
        self.__map_id_xml: dict[str, str] = dict()

    def get_xml_sheet_prefix_from_id(self, sheet_id: str) -> str:
        """Retorna 'sheetX' a partir do ID."""
        return self.__map_id_xml[sheet_id]

    def get_sheet_id_from_name(self, sheet_name: str) -> str | None:
        """Retorna o ID a partir do nome."""
        return self.get(sheet_name)

    def set_sheet_id_and_prefix(self, sheet_name: str, sheet_id: str, sheet_xml_prefix: str):
        self[sheet_name] = sheet_id
        self.__map_id_xml[sheet_id] = sheet_xml_prefix

    def get_sheet_names(self) -> list[str]:
        return list(self.keys())
