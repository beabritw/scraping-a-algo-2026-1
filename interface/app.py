from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import threading
import requests as req
from lxml import html as lxml_html
import time
import re

app = Flask(__name__)
app.secret_key = '1e516662603a6c6804bf8d4d5375e3bb9c9343caeb34cccd35bcdfce5d8964a5'

# ── Estado global do monitoramento 
estado = {
    "rodando":       False,
    "valor_atual":   None,
    "historico":     [],
    "email_destino": None,
    "xpath":         None,
    "url":           None,
    "thread":        None,
}

# ── Helpers

def validar_numero(intervalo):
    try:
        n = int(intervalo)
        if n < 10:
            return False, "O intervalo mínimo é 10 segundos."
        return True, ""
    except (ValueError, TypeError):
        return False, "Intervalo inválido."


def validar_email(email):
    padrao = r'^[^\s@]+@[^\s@]+\.[^\s@]{2,}$'
    if not email or not re.match(padrao, email):
        return False, "E-mail inválido."
    return True, ""


def _get_xpath(element):
    """Gera o XPath absoluto de um elemento lxml."""
    parts = []
    el = element
    while el is not None and el.tag not in ('html', lxml_html.HtmlElement):
        parent = el.getparent()
        if parent is None:
            parts.append(el.tag)
            break
        irmãos = parent.findall(el.tag)
        if len(irmãos) > 1:
            idx = list(irmãos).index(el) + 1
            parts.append(f'{el.tag}[{idx}]')
        else:
            parts.append(el.tag)
        el = parent
    parts.reverse()
    return '//' + '/'.join(parts)


def buscar_elemento_por_texto(url, texto):
    """
    Faz o scraping da URL e retorna (valor, xpath, erro).
    Busca o menor elemento que contenha o texto de referência.
    """
    try:
        headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/124.0 Safari/537.36'
            )
        }
        resposta = req.get(url, headers=headers, timeout=15)
        resposta.raise_for_status()

        tree = lxml_html.fromstring(resposta.content)

        # Remove scripts e styles para não poluir a busca
        for tag in tree.xpath('//script | //style | //noscript'):
            parent = tag.getparent()
            if parent is not None:
                parent.remove(tag)

        texto_lower = texto.strip().lower()

        # Procura o elemento folha (ou mais profundo) que contém o texto
        candidatos = tree.xpath(
            f'//*[contains(translate(normalize-space(.), '
            f'"ABCDEFGHIJKLMNOPQRSTUVWXYZÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖÙÚÛÜÝÞŸ",'
            f'"abcdefghijklmnopqrstuvwxyzàáâãäåæçèéêëìíîïðñòóôõöùúûüýþÿ"),'
            f'"{texto_lower}")]'
        )

        if not candidatos:
            return None, None, f'Texto "{texto}" não encontrado na página.'

        # Prefere o elemento mais específico (mais profundo / menor conteúdo)
        candidatos.sort(key=lambda e: len(e.text_content()))
        el = candidatos[0]

        valor = el.text_content().strip()
        xpath = _get_xpath(el)

        return valor, xpath, None

    except req.exceptions.ConnectionError:
        return None, None, "Não foi possível conectar ao site. Verifique a URL."
    except req.exceptions.Timeout:
        return None, None, "O site demorou muito para responder (timeout)."
    except req.exceptions.HTTPError as e:
        return None, None, f"O site retornou um erro: {e.response.status_code}."
    except Exception as e:
        return None, None, f"Erro inesperado: {str(e)}"


def buscar_valor_por_xpath(url, xpath):
    """Retorna o texto atual do elemento identificado pelo XPath."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        resposta = req.get(url, headers=headers, timeout=15)
        resposta.raise_for_status()
        tree = lxml_html.fromstring(resposta.content)
        elementos = tree.xpath(xpath)
        if elementos:
            el = elementos[0]
            texto = el.text_content().strip() if hasattr(el, 'text_content') else str(el).strip()
            return texto or None
        return None
    except Exception:
        return None


# Thread de monitoramento 

def _loop_monitoramento(url, xpath, intervalo):
    print(f"[MONITOR] Iniciando loop | URL={url} | intervalo={intervalo}s")
    while estado["rodando"]:
        valor_novo = buscar_valor_por_xpath(url, xpath)

        if valor_novo is not None:
            valor_antigo = estado["valor_atual"]

            if valor_antigo is not None and valor_novo != valor_antigo:
                hora = time.strftime('%H:%M:%S')
                entrada = {"antes": valor_antigo, "depois": valor_novo, "hora": hora}
                estado["historico"].append(entrada)
                print(
                    f"[ALTERAÇÃO] {hora} | "
                    f"Antes: {valor_antigo!r} → Depois: {valor_novo!r} | "
                    f"Email: {estado['email_destino']}"
                )
                # TODO: chamar função de envio de e-mail aqui

            estado["valor_atual"] = valor_novo

        time.sleep(intervalo)

    print("[MONITOR] Loop encerrado.")



@app.route('/', methods=['GET', 'POST'])
def tela1():
    if request.method == 'POST':
        nome  = request.form.get('userName',  '').strip()
        email = request.form.get('userEmail', '').strip()

        if nome and email:
            session['userName']  = nome
            session['userEmail'] = email
            print(f">>> [TELA 1] Nome={nome!r}, Email={email!r}")
            return redirect(url_for('tela2'))

    return render_template('tela1_nome.html')


@app.route('/tela2', methods=['GET', 'POST'])
def tela2():
    nome = session.get('userName', 'Visitante')

    if request.method == 'POST':
        url    = request.form.get('urlPagina',  '').strip()
        texto  = request.form.get('textoBusca', '').strip()

        if url and texto:
            session['urlPagina']  = url
            session['textoBusca'] = texto

            print(f">>> [TELA 2] Usuário={nome!r} | URL={url!r} | Texto={texto!r}")

            valor, xpath, erro = buscar_elemento_por_texto(url, texto)

            if erro:
                print(f">>> [TELA 2] Erro no scraping: {erro}")
                return render_template(
                    'tela2_busca.html',
                    nome=nome,
                    erro=erro,
                    url_preenchida=url,
                    texto_preenchido=texto,
                )

            session['valorEncontrado'] = valor
            session['xpathEncontrado'] = xpath
            print(f">>> [TELA 2] Valor={valor!r} | XPath={xpath!r}")
            return redirect(url_for('tela3'))

    return render_template('tela2_busca.html', nome=nome)


@app.route('/tela3')
def tela3():
    valor = session.get('valorEncontrado', '—')
    xpath = session.get('xpathEncontrado', '—')
    return render_template('tela3_confirmar.html', valor=valor, xpath=xpath)


@app.route('/tela4')
def tela4():
    url = session.get('urlPagina', '—')
    return render_template('tela4_configurar.html', urlPagina=url)


@app.route('/tela5')
def tela5():
    return render_template('tela5_monitor.html')


@app.route('/iniciar', methods=['POST'])
def iniciar():
    dados     = request.get_json(force=True) or {}
    intervalo = dados.get('intervalo')
    email     = dados.get('email', '').strip()

    ok, msg = validar_numero(intervalo)
    if not ok:
        return jsonify({"erro": msg}), 400

    ok, msg = validar_email(email)
    if not ok:
        return jsonify({"erro": msg}), 400

    url   = session.get('urlPagina')
    xpath = session.get('xpathEncontrado')

    if not url or not xpath:
        return jsonify({"erro": "Sessão expirada. Por favor, reinicie o processo."}), 400

    # Para thread anterior se ainda estiver rodando
    if estado["rodando"]:
        estado["rodando"] = False
        t = estado.get("thread")
        if t and t.is_alive():
            t.join(timeout=3)

    # Reseta o estado
    estado["rodando"]       = True
    estado["valor_atual"]   = session.get('valorEncontrado')
    estado["historico"]     = []
    estado["email_destino"] = email
    estado["xpath"]         = xpath
    estado["url"]           = url

    # Log completo com todos os dados do usuário
    nome       = session.get('userName',  '—')
    userEmail  = session.get('userEmail', '—')
    textoBusca = session.get('textoBusca','—')

    print(
        f">>> [INICIAR] Nome={nome!r} | UserEmail={userEmail!r} | "
        f"URL={url!r} | Texto={textoBusca!r} | "
        f"Intervalo={intervalo}s | AlertaEmail={email!r}"
    )

    thread = threading.Thread(
        target=_loop_monitoramento,
        args=(url, xpath, int(intervalo)),
        daemon=True,
    )
    thread.start()
    estado["thread"] = thread

    return jsonify({"ok": True})


@app.route('/status')
def status():
    return jsonify({
        "rodando":     estado["rodando"],
        "valor_atual": estado["valor_atual"],
        "historico":   estado["historico"],
    })


@app.route('/parar', methods=['POST'])
def parar():
    estado["rodando"] = False
    nome = session.get('userName', '—')
    print(f">>> [PARAR] Monitoramento encerrado pelo usuário {nome!r}.")
    return jsonify({"ok": True})


if __name__ == '__main__':
    app.run(debug=True)