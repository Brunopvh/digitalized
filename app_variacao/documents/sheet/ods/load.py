from __future__ import annotations
from io import BytesIO
from abc import ABC, abstractmethod
import pandas as pd
from typing import Any
import zipfile


#===========================================================#
# Leitura de ODS
#===========================================================#

from odf.opendocument import load as odf_load, OpenDocument, OpenDocumentSpreadsheet
from odf.table import Table, TableRow, TableCell
from odf.text import P
from odf import teletype
#from odf.namespaces import OFFICENS

from app_variacao.documents.erros import *
from app_variacao.documents.sheet.types import (
    SheetData, SheetIndexNames, WorkbookData, RowSheetIterator
)
from app_variacao.documents.sheet.xml import (
    read_zip_xml, WorkbookMappingXML
)
from app_variacao.types.core import ObjectAdapter

#===========================================================#
# CLASSES BASE E ADAPTADORES (ODS)
#===========================================================#


class ODSLoad(ABC):
    """
    Classe abstrata base para carregadores de planilhas ODS.
    """

    @abstractmethod
    def hash(self) -> int:
        pass

    @abstractmethod
    def get_sheet_index(self) -> SheetIndexNames:
        pass

    @abstractmethod
    def get_workbook_data(self) -> WorkbookData:
        pass

    def get_sheet_at(self, idx: int) -> SheetData:
        idx_sheet_names: SheetIndexNames = self.get_sheet_index()
        name = idx_sheet_names[idx]
        return self.get_workbook_data()[name]

    def get_sheet(self, sheet_name: str | None) -> SheetData:
        if sheet_name is not None:
            return self.get_workbook_data()[sheet_name]
        return self.get_sheet_at(0)


# --------------------------------------------------------------------------------
# 1. IMPLEMENTAÇÃO COM PANDAS
# --------------------------------------------------------------------------------

class ODSLoadPandas(ODSLoad):
    """Carregador ODS utilizando a biblioteca Pandas."""

    def __init__(self, ods_file: str | BytesIO):
        self.ods_file: str | BytesIO = ods_file
        self.__sheet_names: list[str] | None = None

    def hash(self) -> int:
        return hash(self.ods_file)

    def get_sheet_index(self) -> SheetIndexNames:
        # Pandas suporta ODS via pd.ExcelFile ou pd.read_excel
        if self.__sheet_names is None:
            try:
                rd: pd.ExcelFile = pd.ExcelFile(self.ods_file, "odf")
                self.__sheet_names = [str(x) for x in rd.sheet_names]
            except Exception as e:
                # O pandas falha se o backend (odfpy, por exemplo) não estiver instalado
                raise LoadWorkbookError(
                    f'{__class__.__name__} ODSLoadPandas (odfpy): {e}'
                )
        return SheetIndexNames.create_from_list(self.__sheet_names)

    def get_workbook_data(self) -> WorkbookData:
        try:
            # Se sheet_name=None
            # carrega todas as abas em um dicionário de DataFrames
            data: dict[Any, pd.DataFrame] = pd.read_excel(
                self.ods_file, sheet_name=None, engine='odf'
            )
        except Exception as e:
            raise LoadWorkbookError(f'{__class__.__name__}: {e}')

        workbook_data = WorkbookData()
        for sheet_name, df in data.items():
            # Limpeza opcional de nomes de abas e conversão para SheetData
            workbook_data.add_sheet(str(sheet_name), SheetData.create_from_data(df))
        return workbook_data


# --------------------------------------------------------------------------------
# 2. IMPLEMENTAÇÃO COM ODFPY
# --------------------------------------------------------------------------------

class ODSLoadODFpy(ODSLoad):
    """
    Carregador ODS utilizando a biblioteca odfpy.
    """

    def __init__(self, ods_file: str | BytesIO):
        self.ods_file: str | BytesIO = ods_file
        self.__workbook: OpenDocument | None = None
        self.__workbook_data: WorkbookData | None = None
        self.__index_names: SheetIndexNames | None = None
        # ===========================================================#
        # CONSTANTES ODF
        # ===========================================================#
        # Namespace URI para atributos de Tabela ODS (table:number-rows-repeated, etc.)
        self.ODF_TABLE_NS = 'urn:oasis:names:tc:opendocument:xmlns:table:1.0'

    def hash(self) -> int:
        return hash(self.ods_file)

    def __get_wb(self) -> OpenDocument:
        if self.__workbook is None:
            try:
                # ODFpy espera um path ou um objeto file-like
                if isinstance(self.ods_file, BytesIO):
                    # ODFpy load() não aceita BytesIO diretamente, mas sim um path.
                    # Isso exigiria salvar BytesIO em um arquivo temporário,
                    # ou passar o BytesIO para load(), o que geralmente funciona em versões recentes.
                    # Vamos assumir que load() suporta BytesIO.
                    self.__workbook: OpenDocument = odf_load(self.ods_file)
                else:
                    self.__workbook: OpenDocument = odf_load(self.ods_file)
            except Exception as e:
                raise LoadWorkbookError(f'{__class__.__name__}: Erro ao carregar arquivo ODS: {e}')
        return self.__workbook

    def __get_sheet_data_from_name(self, sheet_name: str) -> SheetData:
        wb: OpenDocument = self.__get_wb()
        sheet_data = SheetData()

        # Omitindo busca pelo target_sheet aqui para brevidade, mas deve estar lá...
        sheets_elements: list[Any] | Any = wb.getElementsByType(Table)
        target_sheet = None
        for table in sheets_elements:
            if table.getAttribute('name') == sheet_name:
                target_sheet = table
                break

        if target_sheet is None:
            return sheet_data

        rows_iterator: list[Any] | Any = target_sheet.getElementsByType(TableRow)
        header_list: list[str] = []
        is_header = True

        # Chave qualificada para repetições
        ROWS_REPEATED_KEY = f'{{{self.ODF_TABLE_NS}}}number-rows-repeated'
        COLS_REPEATED_KEY = f'{{{self.ODF_TABLE_NS}}}number-columns-repeated'

        for row in rows_iterator:
            row_values: list[str] = []

            # Repetição de linha: USANDO O MAPA DE ATRIBUTOS BRUTO (.attributes)
            # O .get() do dicionário é seguro contra KeyError e retorna None/default se não existir.
            rows_repeated_str = row.attributes.get(ROWS_REPEATED_KEY)

            if not rows_repeated_str:
                num_rows_repeated = 1
            else:
                num_rows_repeated = int(rows_repeated_str)

            # --- FIM CORREÇÃO LINHA REPETIDA ---

            cells = row.getElementsByType(TableCell)
            current_col_index = 0

            for cell in cells:
                # Repetição de coluna: USANDO O MAPA DE ATRIBUTOS BRUTO (.attributes)
                cols_repeated_str = cell.attributes.get(COLS_REPEATED_KEY)

                if not cols_repeated_str:
                    num_cols_repeated = 1
                else:
                    num_cols_repeated = int(cols_repeated_str)

                # --- EXTRAÇÃO DO VALOR DA CÉLULA (Reforçada) ---
                #cell_value = ''
                cell_value = teletype.extractText(cell) or ''
                value = cell.getElementsByType(P)

                if value and value[0].firstChild:
                    # 1. Valor de texto em <text:p>
                    #cell_value = str(value[0].firstChild.nodeValue)
                    cell_value = str(value[0].firstChild.data)
                else:
                    # 2. Valor de atributo 'value' (usado para números, datas)
                    attr_value = cell.getAttribute('value')
                    if attr_value:
                        cell_value = str(attr_value)
                    else:
                        cell_value = ''

                # Adiciona o valor para as colunas repetidas
                for _ in range(num_cols_repeated):
                    row_values.append(cell_value)
                    current_col_index += 1

            if is_header:
                # Processa o cabeçalho
                header_list = [v if v and v != '' else f"Col{i + 1}" for i, v in enumerate(row_values)]
                for name in header_list:
                    sheet_data.add_column(name, [])
                is_header = False
            else:
                # Processa os dados
                for repeat_row in range(num_rows_repeated):
                    for col_index, col_name in enumerate(header_list):
                        if col_index < len(row_values):
                            sheet_data[col_name].append(row_values[col_index])
                        else:
                            sheet_data[col_name].append('')

        return sheet_data

    def get_sheet_index(self) -> SheetIndexNames:
        if self.__index_names is None:
            wb: OpenDocument = self.__get_wb()
            _sheet_names = []
            # Busca todas as tabelas (sheets) no documento
            sheets_elements: list[Any] = wb.getElementsByType(Table)

            for table in sheets_elements:
                # O nome da tabela é geralmente o atributo 'table:name'
                name = table.getAttribute('name')
                if name:
                    _sheet_names.append(name)
            self.__index_names = SheetIndexNames.create_from_list(_sheet_names)
        return self.__index_names

    def get_workbook_data(self) -> WorkbookData:
        if self.__workbook_data is None:
            workbook_data = WorkbookData()
            sheet_index: SheetIndexNames = self.get_sheet_index()

            for sheet_name in sheet_index.get_sheet_names():
                sheet_data = self.__get_sheet_data_from_name(sheet_name)
                workbook_data.add_sheet(sheet_name, sheet_data)
            self.__workbook_data = workbook_data
        return self.__workbook_data


# --------------------------------------------------------------------------------
# 3. IMPLEMENTAÇÃO COM LEITURA DIRETA DO XML (ODSLoadXML)
# --------------------------------------------------------------------------------

# As classes e funções de baixo nível para ODS (ODSFileNames, ODSXMLProcessor, etc.)
# DEVEM ser definidas em um novo arquivo, por exemplo:
# digitalized/documents/sheet/ods/_load_xml_ods.py

# A lógica de leitura do ODS XML é diferente do XLSX.
# O ODS é um ZIP, e o conteúdo principal está em /content.xml.

# Classes e Funções Auxiliares (Definidas no novo arquivo _load_xml_ods.py)
class ODSFileNames(dict[str, str]):

    def __init__(self):
        super().__init__({})
        # O arquivo content.xml contém todos os dados e estrutura das abas
        self['content'] = 'content.xml'

    def get_xml_content(self) -> str:
        return self['content']


class ODSXMLProcessor:
    """
    Processador ODS via XML com baixo consumo de memória.
    Usa preenchimento direto em SheetData (coluna-orientado),
    sem buffers intermediários gigantes.
    """

    ODF_TABLE = '{urn:oasis:names:tc:opendocument:xmlns:table:1.0}'
    ODF_TEXT = '{urn:oasis:names:tc:opendocument:xmlns:text:1.0}'

    def __init__(self, ods_input: str | BytesIO):
        self.ods_input = ods_input
        self.xml_file_names = ODSFileNames()
        self.sheet_names: list[str] = []

    def load_sheet_names(self):
        """Carrega apenas os nomes das abas (sem processar dados)."""
        with zipfile.ZipFile(self.ods_input, 'r') as zf:
            content_path = self.xml_file_names.get_xml_content()
            tree, err = read_zip_xml(zf, content_path)
            if tree is None:
                return

            root = tree.getroot()
            self.sheet_names.clear()

            for table in root.findall(f'.//{self.ODF_TABLE}table'):
                name = table.get(f'{self.ODF_TABLE}name')
                if name:
                    self.sheet_names.append(name)

            # libera memória do XML
            root.clear()

    def sheet_to_sheet_data(self, sheet_name: str) -> SheetData:
        """
        Processa UMA aba específica.
        Estratégia:
        - Cabeçalho uma única vez
        - Append direto nas colunas
        - Nenhuma lista intermediária de linhas
        """

        sheet_data = SheetData()

        with zipfile.ZipFile(self.ods_input, 'r') as zf:
            content_path = self.xml_file_names.get_xml_content()
            tree, err = read_zip_xml(zf, content_path)
            if tree is None:
                return sheet_data

            root = tree.getroot()

            target_table = None
            for table in root.findall(f'.//{self.ODF_TABLE}table'):
                if table.get(f'{self.ODF_TABLE}name') == sheet_name:
                    target_table = table
                    break

            if target_table is None:
                root.clear()
                return sheet_data

            is_header = True
            headers: list[str] = []

            for row in target_table.findall(f'{self.ODF_TABLE}table-row'):

                num_rows_repeated = int(
                    row.get(f'{self.ODF_TABLE}number-rows-repeated', '1')
                )

                row_values: list[str] = []

                for cell in row.findall(f'{self.ODF_TABLE}table-cell'):
                    num_cols_repeated = int(
                        cell.get(f'{self.ODF_TABLE}number-columns-repeated', '1')
                    )

                    p = cell.find(f'{self.ODF_TEXT}p')
                    value = p.text if p is not None else ''

                    row_values.extend([value] * num_cols_repeated)

                if is_header:
                    headers = [
                        v if v else f'Col{i + 1}'
                        for i, v in enumerate(row_values)
                    ]
                    for h in headers:
                        sheet_data.add_column(h, [])
                    is_header = False
                else:
                    for _ in range(num_rows_repeated):
                        for idx, col_name in enumerate(headers):
                            val = row_values[idx] if idx < len(row_values) else ''
                            sheet_data[col_name].append(val)

            # libera memória
            root.clear()

        return sheet_data


class ODSLoadXML(ODSLoad):
    """
    Leitor ODS via XML otimizado para baixo uso de memória.
    """

    def __init__(self, ods_file: str | BytesIO):
        self.ods_file = ods_file
        self.__processor = ODSXMLProcessor(ods_file)
        self.__workbook_data: WorkbookData | None = None
        self.__sheet_index_names: SheetIndexNames | None = None

    def hash(self) -> int:
        return hash(self.ods_file)

    def get_sheet_index(self) -> SheetIndexNames:
        if self.__sheet_index_names is None:
            if not self.__processor.sheet_names:
                self.__processor.load_sheet_names()

            self.__sheet_index_names = SheetIndexNames.create_from_list(
                self.__processor.sheet_names
            )

        return self.__sheet_index_names

    def get_workbook_data(self) -> WorkbookData:
        if self.__workbook_data is not None:
            return self.__workbook_data

        workbook_data = WorkbookData()

        if not self.__processor.sheet_names:
            self.__processor.load_sheet_names()

        for sheet_name in self.__processor.sheet_names:
            sheet_data = self.__processor.sheet_to_sheet_data(sheet_name)
            workbook_data.add_sheet(sheet_name, sheet_data)

        self.__workbook_data = workbook_data
        return workbook_data


# --------------------------------------------------------------------------------
# CLASSE PRINCIPAL DE LEITURA (FACTORY)
# --------------------------------------------------------------------------------

class ReadSheetODS(ObjectAdapter):

    def __init__(self, reader: ODSLoad):
        super().__init__()
        self.__reader: ODSLoad = reader

    def get_implementation(self) -> ODSLoad:
        return self.__reader

    def hash(self) -> int:
        return self.get_implementation().hash()

    def get_workbook_data(self) -> WorkbookData:
        return self.__reader.get_workbook_data()

    def get_sheet_at(self, idx: int) -> SheetData:
        return self.__reader.get_sheet_at(idx)

    def get_sheet(self, sheet_name: str | None = None) -> SheetData:
        return self.__reader.get_sheet(sheet_name)

    def get_sheet_index(self) -> SheetIndexNames:
        return self.__reader.get_sheet_index()

    @classmethod
    def create_load_odfpy(cls, ods_file: str | BytesIO) -> ReadSheetODS:
        rd = ODSLoadODFpy(ods_file)
        return cls(rd)
        #raise NotImplementedError()

    @classmethod
    def create_load_pandas(cls, ods_file: str | BytesIO) -> ReadSheetODS:
        rd = ODSLoadPandas(ods_file)
        return cls(rd)

    @classmethod
    def create_load_xml(cls, ods_file: str | BytesIO) -> ReadSheetODS:
        """Cria uma instância usando o carregador XML (ODS do zero)."""
        #rd = ODSLoadXML(ods_file)
        #return cls(rd)
        raise NotImplementedError()
