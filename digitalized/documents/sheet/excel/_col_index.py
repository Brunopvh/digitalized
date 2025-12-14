from __future__ import annotations
import re


#===========================================================#
# Funções Auxiliares de Leitura XML
#===========================================================#

def column_coord_to_index(coord: str) -> int:
    """
    Converte coordenada de célula (ex: 'AZ25') para o índice da coluna (AZ=52).
    """
    match = re.match(r'([A-Za-z]+)', coord)
    if not match:
        raise ValueError(f"Coordenada inválida: {coord}")

    coluna_letras: str = match.group(1)
    idx: int = 0
    for char in coluna_letras.upper():
        col_valor = ord(char) - ord('A') + 1
        idx = (idx * 26) + col_valor
    return idx



