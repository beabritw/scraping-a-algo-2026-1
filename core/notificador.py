# -------------------------------------------
# # ATENÇÃO — senha de app do Google
# -------------------------------------------
# # Gmail não aceita a senha normal da conta para SMTP.
# # Precisa gerar uma "senha de app" em:
# # myaccount.google.com → Segurança → Senhas de app
# # A senha gerada tem 16 caracteres (ex: abcd efgh ijkl mnop)
# # Colocar essa senha na variável de ambiente EMAIL_SENHA
# Passo obrigatório: ativar verificação em duas etapas na conta do Gmail antes de gerar a senha de app.
# sem isso, a opção não aparece.

"""
Módulo responsável por enviar e-mails via SMTP.
"""

# core/notificador.py
# smtplib já vem no Python — sem instalar nada. Só precisa da senha de app do Gmail gerada em myaccount.google.com → Segurança → Senhas de app.
# # PSEUDOCÓDIGO — core/notificador.py

# == CONFIGURAÇÕES (ler do ambiente, nunca escrever a senha no código) ==

# EMAIL_REMETENTE = "assistentedelances@gmail.com"
# EMAIL_SENHA     = os.environ.get("EMAIL_SENHA")   # senha de app do Google
# SERVIDOR_SMTP   = "smtp.gmail.com"
# PORTA           = 587                          # TLS

# == FUNÇÃO PRINCIPAL ==

# FUNÇÃO notificar(valor_antigo, valor_novo, email_destino, logger):

#     # 1. Checar se a senha está configurada
#     SE EMAIL_SENHA está vazia ou None:
#         logar erro: "Variável EMAIL_SENHA não configurada."
#         RETORNAR sem enviar

#     # 2. Montar o conteúdo do email
#     assunto = "Alerta: o valor que você monitora foi alterado!"

#     corpo = """
#         Olá!

#         O valor que você está monitorando foi alterado.

#         Valor anterior : {valor_antigo}
#         Novo valor     : {valor_novo}

#         — Assistente de Lances
#     """

#     # 3. Criar objeto de email
#     mensagem = MIMEText(corpo, "plain", "utf-8")
#     mensagem["Subject"] = assunto
#     mensagem["From"]    = EMAIL_REMETENTE
#     mensagem["To"]      = email_destino

#     # 4. Conectar ao Gmail e enviar
#     TENTE:
#         abrir conexão SMTP(SERVIDOR_SMTP, PORTA)
#         chamar starttls()          # ativa criptografia
#         chamar login(EMAIL_REMETENTE, EMAIL_SENHA)
#         chamar sendmail(EMAIL_REMETENTE, email_destino, mensagem)
#         fechar conexão

#         logar: "Email enviado para {email_destino}"
#         imprimir: "Notificação enviada para {email_destino}"

#     SE DER ERRO DE AUTENTICAÇÃO (SMTPAuthenticationError):
#         logar erro: "Falha de login — verifique EMAIL_SENHA"
#         imprimir aviso no console

#     SE DER QUALQUER OUTRO ERRO:
#         logar erro com a mensagem do erro
#         imprimir aviso no console
# Antes da apresentação: entrar em myaccount.google.com na conta assistentedelaces@gmail.com → Segurança → Verificação em duas etapas (ativar) → Senhas de app → gerar. Salvar a senha gerada numa variável de ambiente chamada EMAIL_SENHA.

