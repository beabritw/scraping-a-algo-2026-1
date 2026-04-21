import importlib
import smtplib
import sys
import types
from unittest.mock import MagicMock

import pytest

from config import logger


@pytest.fixture
def notificador_module(monkeypatch):
    try:
        import dotenv  # noqa: F401
    except ModuleNotFoundError:
        dotenv_stub = types.ModuleType("dotenv")
        dotenv_stub.load_dotenv = lambda: None
        monkeypatch.setitem(sys.modules, "dotenv", dotenv_stub)

    sys.modules.pop("config.email_config", None)
    sys.modules.pop("core.notificador", None)
    module = importlib.import_module("core.notificador")
    return importlib.reload(module)


def test_notificar_sem_senha_nao_envia_email(notificador_module, monkeypatch):
    logger = MagicMock()
    smtp_ctor = MagicMock()

    monkeypatch.setattr(notificador_module, "EMAIL_SENHA", None)
    monkeypatch.setattr(notificador_module.smtplib, "SMTP", smtp_ctor)

    notificador_module.notificar("100", "200", "destino@email.com", logger)

    logger.error.assert_called_once()
    smtp_ctor.assert_not_called()


def test_notificar_envia_email_com_sucesso(notificador_module, monkeypatch):
    logger = MagicMock()
    smtp_instance = MagicMock()
    smtp_ctor = MagicMock()
    smtp_ctor.return_value.__enter__.return_value = smtp_instance

    monkeypatch.setattr(notificador_module, "EMAIL_SENHA", "senha-app")
    monkeypatch.setattr(notificador_module.smtplib, "SMTP", smtp_ctor)

    notificador_module.notificar("100", "200", "destino@email.com", logger)

    smtp_ctor.assert_called_once_with(
        notificador_module.SERVIDOR_SMTP,
        notificador_module.PORTA,
    )
    smtp_instance.starttls.assert_called_once()
    smtp_instance.login.assert_called_once_with(
        notificador_module.EMAIL_REMETENTE,
        "senha-app",
    )
    smtp_instance.sendmail.assert_called_once()
    logger.info.assert_called_once_with("E-mail enviado para %s", "destino@email.com")


def test_notificar_trata_erro_de_autenticacao(notificador_module, monkeypatch):
    logger = MagicMock()
    smtp_instance = MagicMock()
    smtp_instance.login.side_effect = smtplib.SMTPAuthenticationError(535, b"Auth failed")
    smtp_ctor = MagicMock()
    smtp_ctor.return_value.__enter__.return_value = smtp_instance

    monkeypatch.setattr(notificador_module, "EMAIL_SENHA", "senha-invalida")
    monkeypatch.setattr(notificador_module.smtplib, "SMTP", smtp_ctor)

    notificador_module.notificar("100", "200", "destino@email.com", logger)

    logger.error.assert_called_once_with("Falha de login — verifique EMAIL_SENHA")

def test_notificar_trata_erro_inesperado(notificador_module, monkeypatch):
    logger = MagicMock()
    smtp_instance = MagicMock()
    smtp_instance.sendmail.side_effect = RuntimeError("falha no envio")
    smtp_ctor = MagicMock()
    smtp_ctor.return_value.__enter__.return_value = smtp_instance

    monkeypatch.setattr(notificador_module, "EMAIL_SENHA", "senha-app")
    monkeypatch.setattr(notificador_module.smtplib, "SMTP", smtp_ctor)

    notificador_module.notificar("100", "200", "destino@email.com", logger)

    logger.error.assert_called_once()
