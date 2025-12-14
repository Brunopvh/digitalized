import zipfile
import xml.etree.ElementTree as ET
import re


class XLSXReader:
    def __init__(self, filename):
        """Inicializa com o nome do arquivo .xlsx."""
        self.filename = filename
        self.shared_strings = []
        self.worksheets = {}

    def _get_xml_content(self, zf, path):
        """Auxiliar para ler o conteúdo de um arquivo XML dentro do ZIP."""
        try:
            with zf.open(path) as file:
                return ET.parse(file)
        except KeyError:
            # Arquivo não encontrado (ex: 'xl/sharedStrings.xml' pode não existir se não houver strings)
            return None

    def _load_shared_strings(self, zf: zipfile.ZipFile):
        """
        Carrega strings compartilhadas de 'xl/sharedStrings.xml'.
        O Excel armazena strings únicas aqui para economizar espaço; as células
        referenciam o índice desta lista.
        """
        tree = self._get_xml_content(zf, 'xl/sharedStrings.xml')
        if tree is None:
            return

        # A tag para string compartilhada é <si> ou <t> dentro de <si>
        # Vamos procurar todas as tags <t> (texto)
        root = tree.getroot()
        # O namespace do XML é geralmente 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
        # Usamos o método 'find' com o namespace
        namespace = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

        # Iterar sobre todos os elementos <si> e extrair o texto de <t>
        for si in root.findall('s:si', namespace):
            t = si.find('s:t', namespace)
            if t is not None:
                self.shared_strings.append(t.text if t.text is not None else '')
            else:
                # Se não houver <t> diretamente, pode haver formatação rica (rich text)
                # simplificamos para uma string vazia
                self.shared_strings.append('')

    def _parse_cell_value(self, cell_element):
        """
        Analisa o valor de uma célula (<c>).
        O tipo da célula é determinado pelo atributo 't'.
        """
        # Valor da célula
        v = cell_element.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')

        if v is None or v.text is None:
            return None

        cell_type = cell_element.get('t')
        value = v.text

        if cell_type == 's':
            # Tipo 's' (string) -> o valor é um índice para shared_strings
            try:
                index = int(value)
                return self.shared_strings[index]
            except (ValueError, IndexError):
                return None

        elif cell_type == 'b':
            # Tipo 'b' (boolean) -> 0 é False, 1 é True
            return True if value == '1' else False

        elif cell_type == 'n' or cell_type is None:
            # Tipo 'n' (number) ou None (padrão é número/data)
            try:
                # Tenta converter para int se não tiver ponto decimal, senão float
                if '.' not in value:
                    return int(value)
                return float(value)
            except ValueError:
                return value  # Retorna como string se a conversão falhar

        else:
            # Outros tipos (datas, erros, etc.)
            return value

    def _parse_sheet(self, zf, sheet_id):
        """
        Lê e analisa um arquivo de aba ('xl/worksheets/sheet*.xml').
        Retorna uma lista de listas (linhas) representando a folha.
        """
        sheet_data = []
        tree = self._get_xml_content(zf, f'xl/worksheets/sheet{sheet_id}.xml')
        if tree is None:
            return sheet_data

        root = tree.getroot()
        namespace = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

        # O elemento principal dos dados é <sheetData>
        sheet_data_element = root.find('s:sheetData', namespace)
        if sheet_data_element is None:
            return sheet_data

        # Itera sobre as linhas <row>
        for row_element in sheet_data_element.findall('s:row', namespace):
            # Para manter a ordem correta das colunas, usaremos um dicionário
            # temporário mapeando o endereço da célula (ex: 'A1', 'B1') ao valor.
            row_dict = {}

            # Itera sobre as células <c> na linha
            for cell_element in row_element.findall('s:c', namespace):
                cell_ref = cell_element.get('r')  # Ex: 'A1', 'B1'
                cell_value = self._parse_cell_value(cell_element)

                # Extrai a letra da coluna (Ex: 'A' de 'A1')
                col_letter = re.match(r'([A-Za-z]+)', cell_ref).group(1)
                row_dict[col_letter] = cell_value

            # Converte o dicionário de linha em uma lista, ordenando pelas letras das colunas
            # Isso é complexo pois 'AA' vem depois de 'Z'. Simplificamos:
            # A forma mais simples para esta demonstração é apenas pegar os valores do dicionário.
            # Uma solução robusta exigiria uma função de conversão de letra para índice numérico (A=1, B=2, AA=27) e ordenação.

            # Vamos pegar os valores e assumir a ordem de leitura do XML para simplicidade.
            sheet_data.append(list(row_dict.values()))

        return sheet_data

    def read_xlsx(self):
        """
        Método principal para ler o arquivo .xlsx e popular o atributo worksheets.
        O resultado é um DICIONÁRIO onde a chave é o nome da aba e o valor
        é uma LISTA de LISTAS (uma lista para cada linha).
        """
        print(f"Lendo o arquivo: {self.filename}...")
        try:
            with zipfile.ZipFile(self.filename, 'r') as zf:
                # 1. Carregar strings compartilhadas
                self._load_shared_strings(zf)
                print("Strings compartilhadas carregadas.")

                # 2. Encontrar nomes das abas (do arquivo 'xl/workbook.xml')
                # Este é um passo essencial para mapear o 'sheetId' (ex: 1, 2) ao Nome (ex: 'Dados', 'Plan1')
                workbook_tree = self._get_xml_content(zf, 'xl/workbook.xml')
                if workbook_tree is None:
                    print("Erro: Não foi possível ler xl/workbook.xml.")
                    return {}

                sheet_names_map = {}
                namespace = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

                # Procura a tag <sheets>
                sheets_element = workbook_tree.getroot().find('s:sheets', namespace)
                if sheets_element:
                    for sheet in sheets_element.findall('s:sheet', namespace):
                        name = sheet.get('name')
                        sheetId = sheet.get('sheetId')
                        sheet_names_map[sheetId] = name

                print(f"Abas encontradas: {sheet_names_map.values()}")

                # 3. Ler dados de cada aba
                for sheet_id, sheet_name in sheet_names_map.items():
                    data = self._parse_sheet(zf, sheet_id)
                    self.worksheets[sheet_name] = data
                    print(f"Dados da aba '{sheet_name}' carregados.")

            print("Leitura concluída com sucesso.")
            return self.worksheets

        except FileNotFoundError:
            print(f"Erro: O arquivo '{self.filename}' não foi encontrado.")
            return {}
        except zipfile.BadZipFile:
            print(f"Erro: O arquivo '{self.filename}' não é um arquivo ZIP válido.")
            return {}
        except Exception as e:
            print(f"Ocorreu um erro inesperado: {e}")
            return {}


# Exemplo de Uso:
if __name__ == "__main__":
    # Crie um arquivo .xlsx de teste manualmente e salve-o como 'teste.xlsx'
    # ou use um arquivo existente.
    reader = XLSXReader('teste.xlsx')
    dados = reader.read_xlsx()

    if dados:
        for sheet_name, sheet_data in dados.items():
            print(f"\n--- Dados da Aba: {sheet_name} ---")
            for row in sheet_data:
                print(row)
