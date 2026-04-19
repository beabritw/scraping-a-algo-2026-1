
# interface/app.py — Davi
# O monitoramento precisa rodar em thread separada para não travar o Flask. O frontend consulta /status a cada poucos segundos para atualizar a tela ao vivo.
# # PSEUDOCÓDIGO — interface/app.py

# IMPORTAR Flask, threading
# IMPORTAR Buscador, AlteracaoDetectada  # do core
# IMPORTAR notificar                      # do core
# IMPORTAR validar_url, validar_email, validar_numero, validar_texto_busca
# IMPORTAR configurar_logger

# app    = Flask(__name__)
# logger = configurar_logger()

# # Estado global compartilhado entre Flask e a thread de monitoramento
# estado = {
#     buscador       : None,
#     rodando        : False,
#     valor_atual    : None,
#     historico      : [],     # lista de {antes, depois, hora}
#     email_destino  : None,
#     xpath          : None,
# }

# ============================================================
#  ROTAS
# ============================================================

# ROTA GET "/":
#     renderizar templates/tela1_nome.html

# ------------------------------------------------------------

# ROTA POST "/buscar":
#     # Recebe: { nome, url, texto_busca }

#     pegar nome, url, texto_busca do corpo JSON

#     # Validar os três campos
#     PARA CADA (valor, validador) em [(url, validar_url), (texto_busca, validar_texto_busca)]:
#         ok, msg = validador(valor)
#         SE não ok:
#             RETORNAR JSON { erro: msg }, status 400

#     # Abrir buscador e procurar o elemento
#     estado["buscador"] = novo Buscador()
#     estado["buscador"].iniciar_driver()
#     estado["buscador"].carregar_pagina(url)

#     resultado = estado["buscador"].localizar_por_texto(texto_busca)

#     SE não resultado.encontrado:
#         RETORNAR JSON { erro: "Texto não encontrado na página" }, status 404

#     guardar resultado.xpath_utilizado em estado["xpath"]
#     guardar resultado.valor_atual em estado["valor_atual"]

#     RETORNAR JSON {
#         valor : resultado.valor_atual,
#         xpath : resultado.xpath_utilizado
#     }

# ------------------------------------------------------------

# ROTA POST "/iniciar":
#     # Recebe: { url, intervalo, email }

#     pegar url, intervalo, email do corpo JSON

#     ok, msg = validar_numero(intervalo)
#     SE não ok: RETORNAR JSON { erro: msg }, status 400

#     ok, msg = validar_email(email)
#     SE não ok: RETORNAR JSON { erro: msg }, status 400

#     estado["email_destino"] = email
#     estado["rodando"]       = True

#     # Inicia o monitoramento em thread separada
#     thread = threading.Thread(
#         target = _loop_monitoramento,
#         args   = (url, estado["xpath"], int(intervalo)),
#         daemon = True     # encerra junto com o programa
#     )
#     thread.start()

#     RETORNAR JSON { ok: True }

# ------------------------------------------------------------

# ROTA GET "/status":
#     # Chamada pelo frontend a cada 5s para atualizar a tela
#     RETORNAR JSON {
#         rodando      : estado["rodando"],
#         valor_atual  : estado["valor_atual"],
#         historico    : estado["historico"]
#     }

# ------------------------------------------------------------

# ROTA POST "/parar":
#     estado["rodando"] = False
#     SE estado["buscador"] não é None:
#         estado["buscador"].encerrar_driver()
#         estado["buscador"] = None
#     RETORNAR JSON { ok: True }

# ============================================================
#  THREAD DE MONITORAMENTO (função auxiliar)
# ============================================================

# FUNÇÃO _loop_monitoramento(url, xpath, intervalo):

#     FUNÇÃO INTERNA ao_detectar_alteracao(alteracao):
#         adicionar { antes, depois, hora } em estado["historico"]
#         notificar(alteracao.valor_antigo, alteracao.valor_novo,
#                   estado["email_destino"], logger)

#     estado["buscador"].monitorar(
#         url                = url,
#         seletor            = xpath,
#         intervalo          = intervalo,
#         callback_alteracao = ao_detectar_alteracao,
#     )

#     estado["rodando"] = False   # ao encerrar

# ============================================================

# SE executado direto:
#     app.run(debug=True)
