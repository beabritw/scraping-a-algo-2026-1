"""
Teste básico do módulo validacao.
Verifica se a função validar() se comporta corretamente.
"""

import unittest


class TestValidacao(unittest.TestCase):

    def test_valor_valido(self):
        """Valores válidos devem retornar True."""
        from core import validacao

        resultado = validacao.validar("100", "200")

        self.assertTrue(resultado)
        print("✅ Teste 1 passou: valor válido.")

    def test_valor_invalido(self):
        """Valores inválidos devem retornar False."""
        from core import validacao

        resultado = validacao.validar("200", "100")

        self.assertFalse(resultado)
        print("✅ Teste 2 passou: valor inválido.")

    def test_valor_nao_numerico(self):
        """Se valores não forem numéricos, deve retornar False."""
        from core import validacao

        resultado = validacao.validar("abc", "200")

        self.assertFalse(resultado)
        print("✅ Teste 3 passou: valor não numérico tratado.")


if __name__ == "__main__":
    unittest.main()
