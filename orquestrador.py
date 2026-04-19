"""
1. Pede e valida o nome do usuário
2. Pede e valida a URL
3. Abre a página e busca o elemento pelo texto visível
4. Confirma o valor encontrado com o usuário
5. Pede e valida o intervalo de monitoramento
6. Pede e valida o email do destinatário
7. Inicia o loop de monitoramento (buscador.py)
8. Em caso de alteração, chama notificador.py

Complexidade geral: O(k * n)
    k = número de iterações do monitoramento
    n = número de nós no DOM por iteração
"""

import sys
from config.logger import configurar_logger
from core.validacao import (
    validar_nome,
    validar_url,
    validar_numero,
    validar_texto_busca,
    validar_email,
)
from core.buscador import Buscador, AlteracaoDetectada
from core.notificador import notificar


def _perguntar(logger, pergunta: str, validador, nome_campo: str) -> str:
    """
    Faz uma pergunta ao usuário em loop até receber uma entrada válida.

    Complexidade: O(t) — t = número de tentativas até entrada válida.
    """
    while True:
        try:
            resposta = input(f"\n  {pergunta} ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nSistema encerrado pelo usuário.")
            logger.info("Sistema encerrado na etapa: %s", nome_campo)
            sys.exit(0)

        logger.info("Entrada recebida | campo=%s | valor=%r", nome_campo, resposta)

        ok, msg = validador(resposta)
        if ok:
            return resposta

        print(f"  {msg}")
        logger.warning("Entrada inválida | campo=%s | motivo=%s", nome_campo, msg)


def _confirmar(pergunta: str) -> bool:
    """Pergunta sim/não. Retorna True para 's', False para 'n'."""
    while True:
        resp = input(f"\n  {pergunta} [s/n] ").strip().lower()
        if resp in ("s", "sim", "y", "yes"):
            return True
        if resp in ("n", "nao", "não", "no"):
            return False
        print("Digite 's' para sim ou 'n' para não.")


def _etapa_nome(logger) -> str:
    """Coleta e valida o nome do usuário."""
    nome = _perguntar(
        logger,
        "Digite o seu nome:",
        validar_nome,
        "nome",
    )
    print(f"Bem-vindo, {nome}!")
    logger.info("Sessão iniciada por: %s", nome)
    return nome


def _etapa_url(logger) -> str:
    """Coleta e valida a URL da página."""
    print("\nInsira a URL desejada:")
    url = _perguntar(
        logger,
        "URL da página:",
        validar_url,
        "url",
    )
    print("Formato da URL válido.")
    return url


def _etapa_localizar(logger, buscador: Buscador, url: str) -> tuple[str, str]:
    """
    O usuário informa um texto visível na página.
    O sistema localiza o elemento e confirma com o usuário.

    Retorna (texto_busca, xpath_encontrado).
    """
    print("\nLocalizar o valor a monitorar")
    print("Dica: olhe a página e digite o texto que aparece")
    print("      próximo ao preço (ex: R$ 189  ou  189,00)")

    while True:
        texto = _perguntar(
            logger,
            "Texto visível na página:",
            validar_texto_busca,
            "texto_busca",
        )

        print("Buscando elemento na página...")
        resultado = buscador.localizar_por_texto(texto)

        if not resultado.encontrado:
            print(f"Texto '{texto}' não encontrado na página.")
            print("Tente um trecho diferente do valor.")
            logger.warning("Texto não encontrado na página | texto=%r", texto)
            continue

        print(f"\nElemento encontrado!")
        print(f"Valor capturado : {resultado.valor_atual!r}")
        print(f"Posição (XPath) : {resultado.xpath_utilizado}")
        logger.info(
            "Elemento localizado | texto=%r | valor=%r | xpath=%s",
            texto, resultado.valor_atual, resultado.xpath_utilizado,
        )

        if _confirmar("Esse é o valor que você quer monitorar?"):
            return texto, resultado.xpath_utilizado

        print("Ok, vamos tentar outro texto.")


def _etapa_intervalo(logger) -> int:
    """Define o intervalo de monitoramento em segundos."""
    print("\nFrequência de verificação")
    intervalo_str = _perguntar(
        logger,
        "Verificar a cada quantos segundos?:",
        validar_numero,
        "intervalo",
    )
    intervalo = int(intervalo_str)
    print(f"O assistente verificará a cada {intervalo}s.")
    logger.info("Intervalo configurado: %ds", intervalo)
    return intervalo


def _etapa_email(logger) -> str:
    """Coleta e valida o email do destinatário dos alertas."""
    print("\n Insira o email de envio de alertas de alteração")
    email = _perguntar(
        logger,
        "Email de destino:",
        validar_email,
        "email_destinatario",
    )
    print(f"Alertas serão enviados para: {email}")
    logger.info("Email de destino configurado: %s", email)
    return email


def _etapa_monitorar(
    logger,
    buscador: Buscador,
    url: str,
    xpath: str,
    intervalo: int,
    email_destino: str,
) -> None:
    """
    Inicia o loop de monitoramento.

    Passa notificar() como callback: toda vez que o valor mudar,
    o notificador.py é chamado com o email do destinatário.
    """
    print("\nMonitoramento ativo")
    print("-" * 55)

    def ao_detectar_alteracao(alteracao: AlteracaoDetectada) -> None:
        """Callback chamado pelo buscador quando o valor muda."""
        print(f"\nALTERAÇÃO DETECTADA!")
        print(f"Valor Antigo: {alteracao.valor_antigo}")
        print(f"Valor Atual : {alteracao.valor_novo}")
        logger.info("Alteração detectada: %s", alteracao)

        try:
            notificar(alteracao.valor_antigo, alteracao.valor_novo, email_destino, logger)
        except Exception as e:
            logger.error("Falha na notificação: %s", e)
            print(f"Erro ao notificar: {e}")

    historico = buscador.monitorar(
        url=url,
        seletor=xpath,
        intervalo=intervalo,
        callback_alteracao=ao_detectar_alteracao,
    )

    print("\n" + "-" * 55)
    print(f"Monitoramento encerrado.")
    logger.info("Monitoramento encerrado | total_alteracoes=%d", len(historico))

    if historico:
        print("\nHistórico de alterações:")
        for alt in historico:
            print(f" {alt}")



def main() -> None:
    """
    Orquestra todas as etapas do sistema.

    Fluxo: nome -> url -> localizar elemento -> intervalo -> email -> monitorar

    Qualquer entrada inválida faz o sistema pedir novamente
    (nunca trava, nunca passa com dado errado — critério 0 pontos).
    """
    logger = configurar_logger()
    logger.info("Sistema iniciado.")

    nome = _etapa_nome(logger)
    url  = _etapa_url(logger)

    with Buscador() as buscador:
        print("\nCarregando a página, aguarde...")
        if not buscador.carregar_pagina(url):
            print("Não foi possível carregar a página. Verifique a URL.")
            logger.error("Falha ao carregar página | url=%s", url)
            sys.exit(1)
        print("Página carregada.")

        _, xpath  = _etapa_localizar(logger, buscador, url)
        intervalo = _etapa_intervalo(logger)
        email     = _etapa_email(logger)

        _etapa_monitorar(logger, buscador, url, xpath, intervalo, email)

    logger.info("Sistema encerrado. Sessão de: %s", nome)

if __name__ == "__main__":
    main()