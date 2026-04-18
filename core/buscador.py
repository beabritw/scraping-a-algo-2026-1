"""
Web Scraping com Selenium headless.

    - Carregar a URL fornecida pelo usuário
    - Localizar o campo via XPath ou CSS Selector
    - Logar a posição do elemento no DOM (XPath real via JS)
    - Executar loop de monitoramento com intervalo configurável
    - Detectar alterações de valor e notificar via callback

Complexidade (Big O):
    - localizar_elemento()  : O(n)     — n = nós no DOM
    - monitorar() por iter  : O(n)     — recarrega e relocaliza
    - monitorar() total     : O(k * n) — k = número de iterações
"""

import time
import logging
from dataclasses import dataclass, field
from typing import Optional, Callable

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException,
    InvalidSelectorException,
)
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)


@dataclass
class ResultadoLocalizacao:
    """Resultado da tentativa de localizar um elemento na página."""
    encontrado: bool
    valor_atual: Optional[str] = None
    xpath_utilizado: Optional[str] = None
    estrategia: Optional[str] = None   # 'xpath' ou 'css'
    mensagem_erro: Optional[str] = None


@dataclass
class AlteracaoDetectada:
    """Representa uma mudança de valor capturada durante o monitoramento."""
    valor_antigo: str
    valor_novo: str
    timestamp: float = field(default_factory=time.time)

    def __str__(self) -> str:
        ts = time.strftime("%H:%M:%S", time.localtime(self.timestamp))
        return f"[{ts}] {self.valor_antigo!r} -> {self.valor_novo!r}"


class Buscador:
    """
    Gerencia o browser headless e a logica de monitoramento.

    Parametros
    ----------
    timeout_pagina : int
        Segundos maximos para carregar a pagina (padrao: 15).
    timeout_elemento : int
        Segundos maximos para o elemento aparecer (padrao: 10).
    """

    def __init__(self, timeout_pagina: int = 15, timeout_elemento: int = 10) -> None:
        self.timeout_pagina = timeout_pagina
        self.timeout_elemento = timeout_elemento
        self._driver: Optional[webdriver.Chrome] = None

    # ------------------------------------------------------------------
    # Ciclo de vida — suporte a context manager
    # ------------------------------------------------------------------

    def iniciar_driver(self) -> None:
        """Inicializa o Chrome em modo headless com técnicas de evasão anti-bot."""
        opcoes = Options()
        opcoes.add_argument("--headless=new")
        opcoes.add_argument("--no-sandbox")
        opcoes.add_argument("--disable-dev-shm-usage")
        opcoes.add_argument("--disable-gpu")
        opcoes.add_argument("--window-size=1920,1080")
        
        # --- TÉCNICAS DE EVASÃO (STEALTH) ---
        
        # Remove a flag que avisa que o navegador está sendo controlado por automação
        opcoes.add_argument("--disable-blink-features=AutomationControlled")
        opcoes.add_experimental_option("excludeSwitches", ["enable-automation"])
        opcoes.add_experimental_option("useAutomationExtension", False)
        
        # Falsifica o User-Agent
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        opcoes.add_argument(f"user-agent={user_agent}")

        servico = Service(ChromeDriverManager().install())
        self._driver = webdriver.Chrome(service=servico, options=opcoes)
        
        # Apaga a assinatura do 'webdriver' direto no motor JavaScript
        self._driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
                """
            }
        )

        self._driver.set_page_load_timeout(self.timeout_pagina)
        logger.info("Driver Chrome headless iniciado com camuflagem stealth.")

    def encerrar_driver(self) -> None:
        """Fecha o browser e libera recursos."""
        if self._driver:
            self._driver.quit()
            self._driver = None
            logger.info("Driver encerrado.")

    def __enter__(self) -> "Buscador":
        self.iniciar_driver()
        return self

    def __exit__(self, *_) -> None:
        self.encerrar_driver()


    def carregar_pagina(self, url: str) -> bool:
        """
        Navega ate a URL informada.

        Retorna True em sucesso, False em timeout ou erro de driver.
        Complexidade: O(1).
        """
        self._garantir_driver()
        try:
            logger.info("Carregando URL: %s", url)
            self._driver.get(url)
            logger.info("Pagina carregada.")
            return True
        except TimeoutException:
            logger.error("Timeout ao carregar: %s", url)
            return False
        except WebDriverException as exc:
            logger.error("Erro de driver ao carregar pagina: %s", exc)
            return False

    def localizar_elemento(self, seletor: str) -> ResultadoLocalizacao:
        """
        Localiza o elemento via XPath ou CSS Selector e loga sua posicao no DOM.

        A estrategia e inferida automaticamente:
            - Comeca com '/' ou '(' -> XPath
            - Caso contrario        -> CSS Selector

        Loga o XPath absoluto do elemento.
        Complexidade: O(n) — n = nos no DOM.
        """
        self._garantir_driver()
        estrategia, by = self._inferir_estrategia(seletor)
        logger.info("Buscando elemento | estrategia=%s | seletor=%s", estrategia, seletor)

        try:
            wait = WebDriverWait(self._driver, self.timeout_elemento)
            elemento = wait.until(EC.presence_of_element_located((by, seletor)))

            valor = self._extrair_texto(elemento)
            xpath_real = self._obter_xpath(elemento)

            logger.info(
                "Elemento encontrado."
            )

            return ResultadoLocalizacao(
                encontrado=True,
                valor_atual=valor,
                xpath_utilizado=xpath_real,
                estrategia=estrategia,
            )

        except TimeoutException:
            msg = f"Elemento nao encontrado apos {self.timeout_elemento}s | seletor={seletor}"
            logger.warning(msg)
            return ResultadoLocalizacao(encontrado=False, mensagem_erro=msg)

        except (NoSuchElementException, InvalidSelectorException) as exc:
            msg = f"Seletor invalido ou elemento inexistente: {exc}"
            logger.error(msg)
            return ResultadoLocalizacao(encontrado=False, mensagem_erro=msg)

    def monitorar(
        self,
        url: str,
        seletor: str,
        intervalo: float,
        callback_alteracao: Callable[[AlteracaoDetectada], None],
        max_iteracoes: Optional[int] = None,
    ) -> list[AlteracaoDetectada]:
        """
        Loop de monitoramento continuo.

        A cada intervalo, recarrega a pagina e compara o valor
        do elemento com o anterior. Se houver mudanca, cria AlteracaoDetectada,
        adiciona ao historico e chama callback_alteracao (notificador.py).

        Parametros
        ----------
        url               : pagina a monitorar
        seletor           : XPath ou CSS Selector do campo
        intervalo         : segundos entre verificacoes
        callback_alteracao: funcao chamada a cada mudanca (ex: notificador.enviar)
        max_iteracoes     : limita iteracoes (None = infinito; util em testes)

        Retorna lista de todas as AlteracaoDetectada registradas.

        Complexidade: O(k * n) — k iteracoes, cada uma com custo O(n).
        """
        self._garantir_driver()
        historico: list[AlteracaoDetectada] = []

        if not self.carregar_pagina(url):
            logger.error("Falha na carga inicial. Monitoramento abortado.")
            return historico

        resultado_inicial = self.localizar_elemento(seletor)
        if not resultado_inicial.encontrado:
            logger.error("Elemento nao encontrado na carga inicial. Abortando.")
            return historico

        valor_anterior = resultado_inicial.valor_atual
        logger.info(
            "Monitoramento iniciado | url=%s | seletor=%s | valor_inicial=%r | intervalo=%ss",
            url, seletor, valor_anterior, intervalo,
        )

        iteracao = 0
        try:
            while max_iteracoes is None or iteracao < max_iteracoes:
                time.sleep(intervalo)
                iteracao += 1

                if not self.carregar_pagina(url):
                    logger.warning("Falha ao recarregar na iteracao %d. Pulando." \
                    "Reiniciando a sessão do Chrome para recuperar o monitoramento...", iteracao)
                    self.encerrar_driver()
                    self.iniciar_driver()
                    continue

                resultado = self.localizar_elemento(seletor)
                if not resultado.encontrado:
                    logger.warning("Elemento ausente na iteracao %d.", iteracao)
                    continue

                valor_atual = resultado.valor_atual

                if valor_atual != valor_anterior:
                    alteracao = AlteracaoDetectada(
                        valor_antigo=valor_anterior,
                        valor_novo=valor_atual,
                    )
                    historico.append(alteracao)
                    logger.info("ALTERACAO DETECTADA | %s", alteracao)
                    callback_alteracao(alteracao)
                    valor_anterior = valor_atual
                else:
                    logger.debug("Iter %d: sem alteracao | valor=%r", iteracao, valor_atual)

        except KeyboardInterrupt:
            logger.info("Monitoramento interrompido pelo usuario apos %d iteracoes.", iteracao)

        return historico


    def _garantir_driver(self) -> None:
        if not self._driver:
            raise RuntimeError(
                "Driver nao iniciado. Use 'with Buscador() as b:' ou chame iniciar_driver()."
            )

    @staticmethod
    def _inferir_estrategia(seletor: str) -> tuple[str, By]:
        """O(1) — verificacao de prefixo."""
        if seletor.startswith("/") or seletor.startswith("("):
            return "xpath", By.XPATH
        return "css", By.CSS_SELECTOR

    @staticmethod
    def _extrair_texto(elemento) -> str:
        """O(1) — le .text com fallback para value (inputs)."""
        texto = elemento.text.strip()
        if not texto:
            texto = elemento.get_attribute("value") or ""
        return texto.strip()

    def _obter_xpath(self, elemento) -> str:
        """
        Gera o XPath absoluto do elemento via JavaScript.
        Complexidade: O(d) — d = profundidade do elemento na arvore DOM.
        """
        script = """
        function xpath(el) {
            if (el.id) return '//*[@id="' + el.id + '"]';
            if (el === document.body) return '/html/body';
            var ix = 0, sibs = el.parentNode ? el.parentNode.childNodes : [];
            for (var i = 0; i < sibs.length; i++) {
                var s = sibs[i];
                if (s === el)
                    return xpath(el.parentNode) + '/' + el.tagName.toLowerCase() + '[' + (ix+1) + ']';
                if (s.nodeType === 1 && s.tagName === el.tagName) ix++;
            }
        }
        return xpath(arguments[0]);
        """
        try:
            return self._driver.execute_script(script, elemento) or "xpath_indisponivel"
        except Exception:
            return "xpath_indisponivel"
        
    def localizar_por_texto(self, texto: str) -> ResultadoLocalizacao:
        """
        Localiza o elemento baseando-se no texto visível na página.
        Usa '.' no XPath para garantir a extração de textos em nós aninhados.
        """
        # Proteção contra quebra de sintaxe caso o texto contenha aspas simples
        texto_seguro = texto.replace("'", '"') 
        
        # O uso do '.' varre toda a árvore de texto do elemento de forma unificada
        seletor_xpath = f"//*[contains(normalize-space(.), '{texto_seguro}')]"
        return self.localizar_elemento(seletor_xpath)