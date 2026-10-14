"""Ordenação por inserção e ordenação por intercalação (merge sort).

As duas funções usam apenas o operador < para comparar elementos. Isso permite
contar as comparações embrulhando os valores em `Contado` (ver abaixo), sem
precisar de uma segunda versão dos algoritmos com contador embutido. Assim o
código cronometrado é exatamente o mesmo cujas comparações são contadas.
"""


def insercao(lista):
    """Devolve uma nova lista ordenada usando ordenação por inserção.

    Não altera a lista recebida. Estável: elementos iguais mantêm a ordem.
    """
    a = list(lista)
    for i in range(1, len(a)):
        chave = a[i]
        j = i - 1
        # Desloca para a direita os elementos maiores que a chave.
        while j >= 0 and chave < a[j]:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = chave
    return a


def intercalacao(lista):
    """Devolve uma nova lista ordenada usando ordenação por intercalação.

    Não altera a lista recebida. Estável: elementos iguais mantêm a ordem.
    """
    if len(lista) <= 1:
        return list(lista)
    meio = len(lista) // 2
    return _intercalar(intercalacao(lista[:meio]), intercalacao(lista[meio:]))


def _intercalar(esquerda, direita):
    """Junta duas listas ordenadas em uma lista ordenada."""
    resultado = []
    i = j = 0
    while i < len(esquerda) and j < len(direita):
        # Só pega da direita se for estritamente menor: garante estabilidade.
        if direita[j] < esquerda[i]:
            resultado.append(direita[j])
            j += 1
        else:
            resultado.append(esquerda[i])
            i += 1
    # Uma das metades acabou; o resto da outra já está ordenado.
    resultado.extend(esquerda[i:])
    resultado.extend(direita[j:])
    return resultado


class Contado:
    """Embrulha um valor e conta quantas vezes __lt__ foi chamado.

    O contador é compartilhado por todos os elementos criados pela mesma
    chamada de `contar_comparacoes`, então ele soma as comparações de uma
    ordenação inteira.
    """

    __slots__ = ("valor", "_contador")

    def __init__(self, valor, contador):
        self.valor = valor
        self._contador = contador

    def __lt__(self, outro):
        self._contador[0] += 1
        return self.valor < outro.valor


def contar_comparacoes(ordenar, lista):
    """Ordena `lista` com a função `ordenar` e devolve (resultado, comparações).

    Funciona com `insercao`, `intercalacao` e também com o `sorted` do Python,
    porque todos comparam os elementos usando <.
    """
    contador = [0]
    embrulhados = [Contado(v, contador) for v in lista]
    resultado = [e.valor for e in ordenar(embrulhados)]
    return resultado, contador[0]
