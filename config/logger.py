"""
Configura o logger principal do sistema.

    - Registrar todas as ações do usuário no console
    - Salvar o log em arquivo com timestamp na pasta logs/
    - Ser o único ponto de configuração de logging do projeto

"""

import logging
import os
from datetime import datetime


def configurar_logger(nome: str = "monitor") -> logging.Logger:
    """
    Cria e retorna o logger principal do sistema.

    Registra em dois lugares simultaneamente:
        - Console  : nível INFO  (o usuário vê as ações em tempo real)
        - Arquivo  : nível DEBUG (histórico completo salvo em logs/)

    O arquivo é criado com timestamp no nome para não sobrescrever
    sessões anteriores. Ex: logs/sessao_20260419_143022.log

    Parâmetros
    ----------
    nome : str
        Nome do logger. Padrão "monitor".

    Retorna
    -------
    logging.Logger
        Logger configurado e pronto para uso.

    Complexidade: O(1)
    """
    logger = logging.getLogger(nome)

    # Evita adicionar handlers duplicados se chamado mais de uma vez
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    formato = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    # --- Handler do console (INFO+) ---
    handler_console = logging.StreamHandler()
    handler_console.setLevel(logging.INFO)
    handler_console.setFormatter(formato)
    logger.addHandler(handler_console)

    # --- Handler de arquivo (DEBUG+) ---
    os.makedirs("logs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_arquivo = os.path.join("logs", f"sessao_{timestamp}.log")

    handler_arquivo = logging.FileHandler(caminho_arquivo, encoding="utf-8")
    handler_arquivo.setLevel(logging.DEBUG)
    handler_arquivo.setFormatter(logging.Formatter(
        fmt="%(asctime)s [%(levelname)-8s] %(name)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))
    logger.addHandler(handler_arquivo)

    logger.info("Logger iniciado. Arquivo de log: %s", caminho_arquivo)

    return logger