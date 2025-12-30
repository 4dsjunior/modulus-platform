import unicodedata

def normalizar_texto(texto):
    """
    Remove acentos, caracteres especiais e converte para MAIÚSCULAS.
    """
    if not texto or not isinstance(texto, str):
        return texto
    
    # Remove acentos usando normalização Unicode (NFD separa o caractere do acento)
    texto_sem_acento = ''.join(
        char for char in unicodedata.normalize('NFD', texto)
        if unicodedata.category(char) != 'Mn'
    )
    
    # Retorna em caixa alta e remove espaços extras nas extremidades
    return texto_sem_acento.upper().strip()