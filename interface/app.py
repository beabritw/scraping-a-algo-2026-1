from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = '1e516662603a6c6804bf8d4d5375e3bb9c9343caeb34cccd35bcdfce5d8964a5'

@app.route('/', methods=['GET', 'POST'])
def tela1():
    if request.method == 'POST':
        nome  = request.form.get('userName')
        email = request.form.get('userEmail')

        if nome and email:
            session['userName'] = nome
            print(f">>> Dados Recebidos: Nome={nome}, Email={email}")
            return redirect(url_for('tela2')) 
        
    return render_template('tela1_nome.html')


@app.route('/tela2', methods=['GET', 'POST'])
def tela2():
    userSession = session.get('userName', 'Visitante')

    if request.method == 'POST':
        url = request.form.get('urlPagina')
        search = request.form.get('textoBusca')
        
        if url and search:
            print(f"Usuario {userSession} busca: {search} no site: {url}")
            return redirect(url_for('tela3'))
            
    return render_template('tela2_busca.html', nome=userSession)

@app.route('/tela3')
def tela3():
#btnSim
#btnNao


    return render_template('tela3_confirmar.html')

@app.route('/tela4')
def tela4():
    return render_template('tela4_configurar.html')

@app.route('/tela5')
def tela5():
    return render_template('tela5_monitor.html')

if __name__ == '__main__':
    app.run(debug=True)

    
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
