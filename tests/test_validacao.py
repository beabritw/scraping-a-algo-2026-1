import unicodedata

import pytest

from core.validacao import (
    validar_email,
    validar_nome,
    validar_numero,
    validar_texto_busca,
    validar_url,
)


def _normalizar(texto):
    decomposed = unicodedata.normalize("NFKD", texto)
    return "".join(char for char in decomposed if not unicodedata.combining(char)).lower()


@pytest.mark.parametrize(
    ("nome", "esperado", "trecho_msg"),
    [
        ("Ana Paula", True, "OK"),
        ("Jo", False, "ao menos 3 letras"),
        ("Ana3", False, "apenas letras"),
        ("   ", False, "nao pode ser vazio"),
    ],
)
def test_validar_nome(nome, esperado, trecho_msg):
    ok, msg = validar_nome(nome)

    assert ok is esperado
    assert _normalizar(trecho_msg) in _normalizar(msg)


@pytest.mark.parametrize(
    ("url", "esperado", "trecho_msg"),
    [
        ("https://example.com/produto", True, "OK"),
        ("ftp://example.com", False, "http://"),
        ("https://", False, "dominio valido"),
        ("", False, "nao pode ser vazia"),
    ],
)
def test_validar_url(url, esperado, trecho_msg):
    ok, msg = validar_url(url)

    assert ok is esperado
    assert _normalizar(trecho_msg) in _normalizar(msg)


@pytest.mark.parametrize(
    ("valor", "esperado", "trecho_msg"),
    [
        ("30", True, "OK"),
        ("0", False, "maior que zero"),
        ("dez", False, "numeros inteiros"),
        ("", False, "nao pode ser vazio"),
    ],
)
def test_validar_numero(valor, esperado, trecho_msg):
    ok, msg = validar_numero(valor)

    assert ok is esperado
    assert _normalizar(trecho_msg) in _normalizar(msg)


@pytest.mark.parametrize(
    ("texto", "esperado", "trecho_msg"),
    [
        ("R$ 199,90", True, "OK"),
        ("a", False, "ao menos 2 caracteres"),
        ("   ", False, "nao pode ser vazio"),
    ],
)
def test_validar_texto_busca(texto, esperado, trecho_msg):
    ok, msg = validar_texto_busca(texto)

    assert ok is esperado
    assert _normalizar(trecho_msg) in _normalizar(msg)


@pytest.mark.parametrize(
    ("email", "esperado", "trecho_msg"),
    [
        ("user@example.com", True, "OK"),
        ("user@", False, "email invalido"),
        ("", False, "nao pode ser vazio"),
    ],
)
def test_validar_email(email, esperado, trecho_msg):
    ok, msg = validar_email(email)

    assert ok is esperado
    assert _normalizar(trecho_msg) in _normalizar(msg)
