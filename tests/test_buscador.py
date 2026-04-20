import importlib
import sys
import types
from unittest.mock import MagicMock

import pytest


def _instalar_stubs_selenium(monkeypatch):
    selenium = types.ModuleType("selenium")
    webdriver = types.ModuleType("selenium.webdriver")
    webdriver.Chrome = object

    chrome = types.ModuleType("selenium.webdriver.chrome")
    chrome_options = types.ModuleType("selenium.webdriver.chrome.options")
    chrome_service = types.ModuleType("selenium.webdriver.chrome.service")

    class Options:
        def add_argument(self, *_args, **_kwargs):
            return None

        def add_experimental_option(self, *_args, **_kwargs):
            return None

    class Service:
        def __init__(self, *_args, **_kwargs):
            pass

    chrome_options.Options = Options
    chrome_service.Service = Service

    webdriver_common = types.ModuleType("selenium.webdriver.common")
    by_module = types.ModuleType("selenium.webdriver.common.by")

    class By:
        XPATH = "xpath"
        CSS_SELECTOR = "css selector"

    by_module.By = By

    webdriver_support = types.ModuleType("selenium.webdriver.support")
    ui_module = types.ModuleType("selenium.webdriver.support.ui")
    ec_module = types.ModuleType("selenium.webdriver.support.expected_conditions")

    class WebDriverWait:
        def __init__(self, *_args, **_kwargs):
            pass

        def until(self, *_args, **_kwargs):
            return None

    def presence_of_element_located(locator):
        return locator

    ui_module.WebDriverWait = WebDriverWait
    ec_module.presence_of_element_located = presence_of_element_located

    selenium_common = types.ModuleType("selenium.common")
    exceptions_module = types.ModuleType("selenium.common.exceptions")

    class TimeoutException(Exception):
        pass

    class NoSuchElementException(Exception):
        pass

    class WebDriverException(Exception):
        pass

    class InvalidSelectorException(Exception):
        pass

    exceptions_module.TimeoutException = TimeoutException
    exceptions_module.NoSuchElementException = NoSuchElementException
    exceptions_module.WebDriverException = WebDriverException
    exceptions_module.InvalidSelectorException = InvalidSelectorException

    webdriver_manager = types.ModuleType("webdriver_manager")
    chrome_manager = types.ModuleType("webdriver_manager.chrome")

    class ChromeDriverManager:
        def install(self):
            return "chromedriver"

    chrome_manager.ChromeDriverManager = ChromeDriverManager

    monkeypatch.setitem(sys.modules, "selenium", selenium)
    monkeypatch.setitem(sys.modules, "selenium.webdriver", webdriver)
    monkeypatch.setitem(sys.modules, "selenium.webdriver.chrome", chrome)
    monkeypatch.setitem(sys.modules, "selenium.webdriver.chrome.options", chrome_options)
    monkeypatch.setitem(sys.modules, "selenium.webdriver.chrome.service", chrome_service)
    monkeypatch.setitem(sys.modules, "selenium.webdriver.common", webdriver_common)
    monkeypatch.setitem(sys.modules, "selenium.webdriver.common.by", by_module)
    monkeypatch.setitem(sys.modules, "selenium.webdriver.support", webdriver_support)
    monkeypatch.setitem(sys.modules, "selenium.webdriver.support.ui", ui_module)
    monkeypatch.setitem(
        sys.modules,
        "selenium.webdriver.support.expected_conditions",
        ec_module,
    )
    monkeypatch.setitem(sys.modules, "selenium.common", selenium_common)
    monkeypatch.setitem(sys.modules, "selenium.common.exceptions", exceptions_module)
    monkeypatch.setitem(sys.modules, "webdriver_manager", webdriver_manager)
    monkeypatch.setitem(sys.modules, "webdriver_manager.chrome", chrome_manager)


@pytest.fixture
def buscador_module(monkeypatch):
    try:
        import selenium  # noqa: F401
        import webdriver_manager  # noqa: F401
    except ModuleNotFoundError:
        _instalar_stubs_selenium(monkeypatch)

    sys.modules.pop("core.buscador", None)
    module = importlib.import_module("core.buscador")
    return importlib.reload(module)


def test_inferir_estrategia_reconhece_xpath_e_css(buscador_module):
    estrategia_xpath, by_xpath = buscador_module.Buscador._inferir_estrategia("//div[@id='preco']")
    estrategia_css, by_css = buscador_module.Buscador._inferir_estrategia(".preco")

    assert estrategia_xpath == "xpath"
    assert by_xpath == buscador_module.By.XPATH
    assert estrategia_css == "css"
    assert by_css == buscador_module.By.CSS_SELECTOR


def test_extrair_texto_usa_value_quando_texto_esta_vazio(buscador_module):
    elemento = MagicMock()
    elemento.text = "   "
    elemento.get_attribute.return_value = "  R$ 199,90  "

    assert buscador_module.Buscador._extrair_texto(elemento) == "R$ 199,90"


def test_localizar_elemento_retorna_dados_quando_encontra_resultado(buscador_module, monkeypatch):
    buscador = buscador_module.Buscador(timeout_elemento=7)
    buscador._driver = MagicMock()

    elemento = MagicMock()
    elemento.text = "R$ 100"

    wait_instance = MagicMock()
    wait_instance.until.return_value = elemento
    wait_ctor = MagicMock(return_value=wait_instance)

    monkeypatch.setattr(buscador_module, "WebDriverWait", wait_ctor)
    monkeypatch.setattr(
        buscador_module.EC,
        "presence_of_element_located",
        lambda locator: locator,
    )
    monkeypatch.setattr(buscador, "_obter_xpath", lambda _elemento: "/html/body/div[1]")

    resultado = buscador.localizar_elemento(".preco")

    wait_ctor.assert_called_once_with(buscador._driver, 7)
    wait_instance.until.assert_called_once_with((buscador_module.By.CSS_SELECTOR, ".preco"))
    assert resultado.encontrado is True
    assert resultado.valor_atual == "R$ 100"
    assert resultado.xpath_utilizado == "/html/body/div[1]"
    assert resultado.estrategia == "css"


def test_monitorar_registra_alteracao_e_chama_callback(buscador_module, monkeypatch):
    buscador = buscador_module.Buscador()
    buscador._driver = object()

    resultados = [
        buscador_module.ResultadoLocalizacao(encontrado=True, valor_atual="100"),
        buscador_module.ResultadoLocalizacao(encontrado=True, valor_atual="100"),
        buscador_module.ResultadoLocalizacao(encontrado=True, valor_atual="120"),
    ]
    callback = MagicMock()

    monkeypatch.setattr(buscador_module.time, "sleep", lambda _intervalo: None)
    monkeypatch.setattr(buscador, "carregar_pagina", MagicMock(side_effect=[True, True, True]))
    monkeypatch.setattr(buscador, "localizar_elemento", MagicMock(side_effect=resultados))

    historico = buscador.monitorar(
        url="https://example.com",
        seletor=".preco",
        intervalo=0,
        callback_alteracao=callback,
        max_iteracoes=2,
    )

    assert len(historico) == 1
    assert historico[0].valor_antigo == "100"
    assert historico[0].valor_novo == "120"
    callback.assert_called_once()
    alteracao_enviada = callback.call_args.args[0]
    assert alteracao_enviada.valor_antigo == "100"
    assert alteracao_enviada.valor_novo == "120"


def test_monitorar_aborta_quando_carga_inicial_falha(buscador_module, monkeypatch):
    buscador = buscador_module.Buscador()
    buscador._driver = object()

    monkeypatch.setattr(buscador, "carregar_pagina", MagicMock(return_value=False))
    callback = MagicMock()

    historico = buscador.monitorar(
        url="https://example.com",
        seletor=".preco",
        intervalo=0,
        callback_alteracao=callback,
        max_iteracoes=1,
    )

    assert historico == []
    callback.assert_not_called()
