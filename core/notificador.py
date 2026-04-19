"""
Módulo responsável por enviar e-mails de alerta via SMTP.

Uso:
    from core.notificador import notificar
    notificar("R$ 100", "R$ 120", "destino@email.com", logger)
"""

import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

from config.email_config import (
    EMAIL_REMETENTE,
    EMAIL_SENHA,
    SERVIDOR_SMTP,
    PORTA,
)

load_dotenv()


def notificar(valor_antigo, valor_novo, email_destino, logger):
    """
    Envia um e-mail avisando que o valor monitorado mudou.

    Parâmetros:
        valor_antigo  (str) : valor que estava antes
        valor_novo    (str) : novo valor detectado
        email_destino (str) : e-mail do destinatário
        logger              : objeto de log para registrar o resultado
    """

    # 1. Checar se a senha está configurada
    if not EMAIL_SENHA:
        logger.error("Variável EMAIL_SENHA não configurada.")
        print("⚠️  EMAIL_SENHA não encontrada. E-mail não enviado.")
        return

    # 2. Montar o conteúdo do e-mail
    assunto = "Alerta: o valor que você monitora foi alterado!"

    corpo = (
        f"Olá!\n\n"
        f"O valor que você está monitorando foi alterado.\n\n"
        f"Valor anterior : {valor_antigo}\n"
        f"Novo valor     : {valor_novo}\n\n"
        f"— Assistente de Lances"
    )

    # 3. Criar objeto de e-mail
    mensagem = MIMEText(corpo, "plain", "utf-8")
    mensagem["Subject"] = assunto
    mensagem["From"]    = EMAIL_REMETENTE
    mensagem["To"]      = email_destino

    # 4. Conectar ao Gmail e enviar
    try:
        with smtplib.SMTP(SERVIDOR_SMTP, PORTA) as servidor:
            servidor.starttls()
            servidor.login(EMAIL_REMETENTE, EMAIL_SENHA)
            servidor.sendmail(
                EMAIL_REMETENTE,
                email_destino,
                mensagem.as_string()
            )

        logger.info(f"E-mail enviado para {email_destino}")
        print(f"✅ Notificação enviada para {email_destino}")

    except smtplib.SMTPAuthenticationError:
        logger.error("Falha de login — verifique EMAIL_SENHA")
        print("❌ Erro de autenticação. Verifique a senha de app do Google.")

    except Exception as e:
        logger.error(f"Erro ao enviar e-mail: {e}")
        print(f"❌ Erro inesperado: {e}")