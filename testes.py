"""Testes que provam que insercao e intercalacao ordenam corretamente.

Rodar com:  python testes.py
(usa só a biblioteca padrão; também funciona com `python -m pytest testes.py`)
"""

import random
import unittest

from ordenacao import contar_comparacoes, insercao, intercalacao

ALGORITMOS = [insercao, intercalacao]


class Registro:
    """Elemento com chave e rótulo, comparado só pela chave (para testar estabilidade)."""

    def __init__(self, chave, rotulo):
        self.chave = chave
        self.rotulo = rotulo

    def __lt__(self, outro):
        return self.chave < outro.chave


class TestaOrdenacao(unittest.TestCase):
    def verificar(self, lista):
        """Confere os dois algoritmos contra sorted() e garante que a entrada não muda."""
        esperado = sorted(lista)
        for ordenar in ALGORITMOS:
            with self.subTest(algoritmo=ordenar.__name__, lista=lista[:20]):
                copia = list(lista)
                resultado = ordenar(lista)
                self.assertEqual(resultado, esperado)
                self.assertEqual(lista, copia, "a lista original foi modificada")

    # --- casos difíceis exigidos ---

    def test_lista_vazia(self):
        self.verificar([])

    def test_um_elemento(self):
        self.verificar([42])

    def test_todos_iguais(self):
        self.verificar([7] * 50)

    def test_ja_ordenada(self):
        self.verificar(list(range(100)))

    def test_invertida(self):
        self.verificar(list(range(100, 0, -1)))

    # --- outros casos ---

    def test_dois_elementos(self):
        self.verificar([2, 1])
        self.verificar([1, 2])

    def test_tamanho_impar_e_par(self):
        self.verificar([3, 1, 2])
        self.verificar([4, 3, 1, 2])

    def test_com_repetidos(self):
        self.verificar([5, 1, 3, 1, 5, 2, 3, 5, 1])

    def test_negativos_e_floats(self):
        self.verificar([-3.5, 2, 0, -1, 1e9, -1e9, 0.0, 2.25])

    def test_strings(self):
        self.verificar(["pera", "banana", "abacaxi", "uva", "Banana"])

    def test_aleatorias(self):
        rng = random.Random(12345)
        for n in [5, 10, 20, 30, 50, 75, 100, 200, 500, 1000]:
            for _ in range(5):
                self.verificar([rng.randint(-1000, 1000) for _ in range(n)])

    def test_aceita_tupla(self):
        for ordenar in ALGORITMOS:
            self.assertEqual(ordenar((3, 1, 2)), [1, 2, 3])

    def test_estabilidade(self):
        """Elementos com chaves iguais saem na mesma ordem em que entraram."""
        rng = random.Random(7)
        registros = [Registro(rng.randint(0, 5), i) for i in range(200)]
        esperado = [r.rotulo for r in sorted(registros, key=lambda r: r.chave)]
        for ordenar in ALGORITMOS:
            with self.subTest(algoritmo=ordenar.__name__):
                self.assertEqual([r.rotulo for r in ordenar(registros)], esperado)


class TestaContagem(unittest.TestCase):
    """Confere o contador de comparações em casos com resposta conhecida."""

    def test_contagem_nao_altera_resultado(self):
        lista = [5, 2, 9, 1, 5, 6]
        for ordenar in ALGORITMOS + [sorted]:
            resultado, _ = contar_comparacoes(ordenar, lista)
            self.assertEqual(resultado, sorted(lista))

    def test_vazia_e_unitaria_nao_comparam(self):
        for ordenar in ALGORITMOS:
            self.assertEqual(contar_comparacoes(ordenar, [])[1], 0)
            self.assertEqual(contar_comparacoes(ordenar, [1])[1], 0)

    def test_insercao_melhor_caso(self):
        # Lista já ordenada: cada elemento é comparado uma vez com o anterior.
        n = 100
        self.assertEqual(contar_comparacoes(insercao, list(range(n)))[1], n - 1)
        self.assertEqual(contar_comparacoes(insercao, [3] * n)[1], n - 1)

    def test_insercao_pior_caso(self):
        # Lista invertida: n(n-1)/2 comparações.
        n = 100
        self.assertEqual(contar_comparacoes(insercao, list(range(n, 0, -1)))[1], n * (n - 1) // 2)

    def test_intercalacao_potencia_de_dois(self):
        # Ordenada ou invertida com n = 2^k: cada intercalação gasta metade
        # do seu tamanho, total (n/2)·log2(n).
        n = 64
        esperado = (n // 2) * 6
        self.assertEqual(contar_comparacoes(intercalacao, list(range(n)))[1], esperado)
        self.assertEqual(contar_comparacoes(intercalacao, list(range(n, 0, -1)))[1], esperado)


if __name__ == "__main__":
    unittest.main(verbosity=2)
