"""
Teste básico do módulo notificador.
Verifica se a função notificar() se comporta corretamente.
"""

import unittest
from unittest.mock import patch, MagicMock


class TestNotificador(unittest.TestCase):

    def test_sem_senha_nao_envia(self):
        """Se EMAIL_SENHA não estiver configurada, não deve enviar."""
        with patch("core.notificador.EMAIL_SENHA", None):
            from core import notificador
            notificador.EMAIL_SENHA = None

            logger = MagicMock()
            notificador.notificar("100", "200", "teste@email.com", logger)

            logger.error.assert_called_once()
            print("✅ Teste 1 passou: sem senha, não envia.")

    def test_envia_email_com_sucesso(self):
        """Com senha configurada e SMTP mockado, deve enviar com sucesso."""
        with patch("core.notificador.EMAIL_SENHA", "senha-falsa"), \
             patch("smtplib.SMTP") as mock_smtp:

            instancia = MagicMock()
            mock_smtp.return_value.__enter__.return_value = instancia

            from core import notificador
            notificador.EMAIL_SENHA = "senha-falsa"

            logger = MagicMock()
            notificador.notificar("100", "200", "teste@email.com", logger)

            instancia.starttls.assert_called_once()
            instancia.sendmail.assert_called_once()
            logger.info.assert_called_once()
            print("✅ Teste 2 passou: e-mail enviado com sucesso.")

    def test_erro_autenticacao(self):
        """Se a senha for errada, deve logar erro de autenticação."""
        import smtplib

        with patch("core.notificador.EMAIL_SENHA", "senha-errada"), \
             patch("smtplib.SMTP") as mock_smtp:

            instancia = MagicMock()
            instancia.login.side_effect = smtplib.SMTPAuthenticationError(535, "Auth failed")
            mock_smtp.return_value.__enter__.return_value = instancia

            from core import notificador
            notificador.EMAIL_SENHA = "senha-errada"

            logger = MagicMock()
            notificador.notificar("100", "200", "teste@email.com", logger)

            logger.error.assert_called_once()
            print("✅ Teste 3 passou: erro de autenticação tratado.")


if __name__ == "__main__":
    unittest.main()