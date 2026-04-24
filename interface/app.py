import os
import sys
import threading
import time
import requests as req
from lxml import html as lxml_html
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

diretorio_atual = os.path.dirname(os.path.abspath(__file__))
diretorio_raiz = os.path.abspath(os.path.join(diretorio_atual, '..'))
sys.path.append(diretorio_raiz)

from dotenv import load_dotenv
load_dotenv()  # ← carrega o .env antes de qualquer coisa

from config.logger import configurar_logger
from core.notificador import notificar
from core.validacao import validar_numero, validar_email, validar_nome

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'chave-local-desenvolvimento')
logger = configurar_logger()

estado = {
    "rodando":       False,
    "valor_atual":   None,
    "historico":     [],
    "email_destino": None,
    "xpath":         None,
    "url":           None,
    "thread":        None,
}


def _get_xpath(element):
    parts = []
    el = element
    while el is not None and el.tag not in ('html', lxml_html.HtmlElement):
        parent = el.getparent()
        if parent is None:
            parts.append(el.tag)
            break
        irmaos = parent.findall(el.tag)
        if len(irmaos) > 1:
            idx = list(irmaos).index(el) + 1
            parts.append(f'{el.tag}[{idx}]')
        else:
            parts.append(el.tag)
        el = parent
    parts.reverse()
    return '//' + '/'.join(parts)


def buscar_elemento_por_texto(url, texto):
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
        
        for tag in tree.xpath('//script | //style | //noscript'):
            parent = tag.getparent()
            if parent is not None:
                parent.remove(tag)

        texto_lower = texto.strip().lower()

        candidatos = tree.xpath(
            f'//*[contains(translate(normalize-space(.), '
            f'"ABCDEFGHIJKLMNOPQRSTUVWXYZÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖÙÚÛÜÝÞŸ",'
            f'"abcdefghijklmnopqrstuvwxyzàáâãäåæçèéêëìíîïðñòóôõöùúûüýþÿ"),'
            f'"{texto_lower}")]'
        )

        if not candidatos:
            return None, None, f'Texto "{texto}" não encontrado na página.'

        candidatos.sort(key=lambda e: len(e.text_content()))
        el = candidatos[0]

        valor = el.text_content().strip()
        xpath = _get_xpath(el)

        return valor, xpath, None

    except Exception as e:
        return None, None, f"Erro ao acessar site: {str(e)}"


def buscar_valor_por_xpath(url, xpath):
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


def _loop_monitoramento(url, xpath, intervalo):
    logger.info(f"Thread de monitoramento iniciada | URL={url} | intervalo={intervalo}s")
    while estado["rodando"]:
        valor_novo = buscar_valor_por_xpath(url, xpath)

        if valor_novo is not None:
            valor_antigo = estado["valor_atual"]

            if valor_antigo is not None and valor_novo != valor_antigo:
                hora = time.strftime('%H:%M:%S')
                entrada = {"antes": valor_antigo, "depois": valor_novo, "hora": hora}
                estado["historico"].append(entrada)
                
                logger.info(f"ALTERAÇÃO DETECTADA: {valor_antigo} -> {valor_novo}")
                
                try:
                    notificar(valor_antigo, valor_novo, estado["email_destino"], logger)
                except Exception as e:
                    logger.error(f"Erro ao notificar no background: {e}")

            estado["valor_atual"] = valor_novo
        time.sleep(intervalo)
    logger.info("Loop de monitoramento encerrado.")


@app.route('/', methods=['GET', 'POST'])
def tela1():
    erro_msg = None
    
    if request.method == 'POST':
        nome  = request.form.get('userName',  '').strip()
        email = request.form.get('userEmail', '').strip()

        valido_nome, msg_nome = validar_nome(nome)
        valido_email, msg_email = validar_email(email)

        if not valido_nome:
            erro_msg = msg_nome
            logger.warning(f"Tentativa web bloqueada | Campo: Nome | Motivo: {msg_nome}")
            
        elif not valido_email:
            erro_msg = msg_email
            logger.warning(f"Tentativa web bloqueada | Campo: Email | Motivo: {msg_email}")
            
        else:
            session['userName']  = nome
            session['userEmail'] = email
            logger.info(f"Dados da Tela 1 validados com sucesso | Nome: {nome}")
            return redirect(url_for('tela2'))

    return render_template('tela1_nome.html', erro=erro_msg)


@app.route('/tela2', methods=['GET', 'POST'])
def tela2():
    nome = session.get('userName', 'Visitante')

    if request.method == 'POST':
        url    = request.form.get('urlPagina',  '').strip()
        texto  = request.form.get('textoBusca', '').strip()

        if url and texto:
            session['urlPagina']  = url
            session['textoBusca'] = texto

            logger.info(f"Buscando elemento | URL={url} | Texto={texto}")
            valor, xpath, erro = buscar_elemento_por_texto(url, texto)

            if erro:
                logger.error(f"Erro no scraping: {erro}")
                return render_template('tela2_busca.html', nome=nome, erro=erro, url_preenchida=url, texto_preenchido=texto)

            session['valorEncontrado'] = valor
            session['xpathEncontrado'] = xpath
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
    email     = session.get('userEmail', '').strip()

    ok, msg = validar_nome(session.get('userName', ''))
    if not ok:
        return jsonify({"erro": msg}), 400
    
    ok, msg = validar_numero(str(intervalo))
    if not ok:
        return jsonify({"erro": msg}), 400

    ok, msg = validar_email(email)
    if not ok:
        return jsonify({"erro": msg}), 400

    url   = session.get('urlPagina')
    xpath = session.get('xpathEncontrado')

    if not url or not xpath:
        return jsonify({"erro": "Sessão expirada. Por favor, reinicie o processo."}), 400

    if estado["rodando"]:
        estado["rodando"] = False
        t = estado.get("thread")
        if t and t.is_alive():
            t.join(timeout=3)

    estado["rodando"]       = True
    estado["valor_atual"]   = session.get('valorEncontrado')
    estado["historico"]     = []
    estado["email_destino"] = email
    estado["xpath"]         = xpath
    estado["url"]           = url

    logger.info(f"Comando de inicialização recebido para a URL: {url}")

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
    logger.info(f"Monitoramento encerrado pelo usuário {nome}.")
    return jsonify({"ok": True})


if __name__ == '__main__':
    app.run(debug=True)