"""
Módulo de validação de entradas do usuário.

Complexidade: todas as funções são O(1) ou O(n) onde n = len(string).
"""
import re
from urllib.parse import urlparse


def validar_nome(nome: str) -> tuple[bool, str]:
    """
    Valida o nome do usuário.

    Regras (conforme enunciado):
        - Apenas caracteres alfabéticos (espaços permitidos entre palavras)
        - Mínimo de 3 letras no total (excluindo espaços)
        - Nomes compostos são aceitos (ex: "Ana Paula")

    Complexidade: O(n) — n = len(nome)
    """
    nome = nome.strip()

    if not nome:
        return False, "Nome não pode ser vazio."

    apenas_letras = nome.replace(" ", "")

    if not apenas_letras.isalpha():
        return False, "O nome deve conter apenas letras."

    if len(apenas_letras) < 3:
        return False, f"O nome deve ter ao menos 3 letras."

    return True, "OK"


def validar_url(url: str) -> tuple[bool, str]:
    """
    Valida o formato e a acessibilidade da URL.

    Complexidade: O(1).

    """
    url = url.strip()

    if not url:
        return False, "URL não pode ser vazia."

    try:
        resultado = urlparse(url)

        if resultado.scheme not in ['http', 'https']:
            return False, "O esquema da url deve ser 'http://' ou 'https://'."
        
        if not resultado.netloc:
            return False, "A url deve conter um domínio valido (exemplo: www.site.com)"

        return True, "OK"

    except Exception as e:
        return False, f"Erro ao acessar URL: {e}"


def validar_numero(valor: str) -> tuple[bool, str]:
    """
    Valida que o valor digitado é um número inteiro positivo.

    Complexidade: O(n) — n = len(valor)
    """
    valor = valor.strip()

    if not valor:
        return False, "O intervalo não pode ser vazio."

    if not valor.isdigit():
        return False, "Digite apenas números inteiros (ex: 30)."

    if int(valor) <= 0:
        return False, "O intervalo deve ser maior que zero."

    return True, "OK"


def validar_texto_busca(texto: str) -> tuple[bool, str]:
    """
    Valida o texto visível que o usuário quer monitorar na página.

    Regras:
        - Não pode ser vazio
        - Mínimo de 2 caracteres (pra nao ter buscas genéricas demais)

    Complexidade: O(1)
    """
    texto = texto.strip()

    if not texto:
        return False, "O texto de busca não pode ser vazio."

    if len(texto) < 2:
        return False, "Digite ao menos 2 caracteres para a busca."

    return True, "OK"


def validar_email(email: str) -> tuple[bool, str]:
    """
    Valida o formato do endereço de email do destinatário.

    - Não pode ser vazio
    - Deve seguir o padrão nome@dominio.extensao
    - Extensão deve ter ao menos 2 caracteres

    Complexidade: O(n) — n = len(email)
    """
    email = email.strip()

    if not email:
        return False, "Email não pode ser vazio."

    padrao = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

    if not padrao.match(email):
        return False, "Email inválido. Use o formato nome@dominio.com"

    return True, "OK"