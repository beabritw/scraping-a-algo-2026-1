"""
Configurações de e-mail lidas do ambiente.
Nunca escreva senhas diretamente aqui.
"""

import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_REMETENTE = "assistentedelances@gmail.com"
EMAIL_SENHA     = os.environ.get("EMAIL_SENHA")
SERVIDOR_SMTP   = "smtp.gmail.com"
PORTA           = 587