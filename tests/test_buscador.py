"""
Teste básico do módulo buscador.
Verifica se a função buscar() se comporta corretamente.
"""

import unittest
from unittest.mock import patch, MagicMock


class TestBuscador(unittest.TestCase):

    def test_sem_resultados(self):
        """Se não encontrar dados, deve retornar vazio."""
        with patch("core.buscador.requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.json.return_value = []
            mock_get.return_value = mock_resp

            from core import buscador

            resultado = buscador.buscar("produto")

            self.assertEqual(resultado, [])
            print("✅ Teste 1 passou: sem resultados.")

    def test_retorna_dados(self):
        """Se encontrar dados, deve retornar corretamente."""
        with patch("core.buscador.requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.json.return_value = [{"preco": 100}]
            mock_get.return_value = mock_resp

            from core import buscador

            resultado = buscador.buscar("produto")

            self.assertEqual(len(resultado), 1)
            print("✅ Teste 2 passou: dados retornados.")

    def test_erro_requisicao(self):
        """Se houver erro na requisição, deve tratar."""
        with patch("core.buscador.requests.get", side_effect=Exception("Erro")):
            from core import buscador

            resultado = buscador.buscar("produto")

            self.assertEqual(resultado, [])
            print("✅ Teste 3 passou: erro tratado.")


if __name__ == "__main__":
    unittest.main()
