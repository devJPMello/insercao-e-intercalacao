# Ordenação por inserção × ordenação por intercalação

**Dupla:** João Pedro Mello e Lucas Vieira

Implementação dos dois algoritmos, testes e medição de tempo e de comparações,
com comparação contra o `sorted()` do Python. A análise está em
[RELATORIO.md](RELATORIO.md).

## Arquivos

| arquivo | o que é |
|---|---|
| `ordenacao.py` | `insercao`, `intercalacao` e o contador de comparações (`contar_comparacoes`) |
| `testes.py` | testes de correção (vazia, um elemento, todos iguais, já ordenada, invertida, aleatórias, estabilidade) e da contagem |
| `medir.py` | roda todas as medições, gera `dados.csv`, `tempos.png` e `comparacoes.png` |
| `dados.csv` | números brutos: uma linha por medição |
| `tempos.png`, `comparacoes.png` | gráficos |
| `RELATORIO.md` | a análise |

## Como rodar

Precisa de Python 3.8 ou mais novo e do matplotlib (só para os gráficos).

```bash
pip install -r requirements.txt

python testes.py     # roda os testes
python medir.py      # refaz dados.csv e os dois gráficos do zero (~15 s)
```

No Windows, se `python` não for encontrado, use `py` no lugar.
`medir.py` grava os arquivos na mesma pasta dele, então pode ser chamado de
qualquer diretório. Ele também imprime as tabelas-resumo em Markdown e o ponto
de virada.

## Como as medições são feitas

- Tamanhos: n = 5, 10, 20, 30, 50, 75, 100, 200, 500, 1000.
- 100 repetições por tamanho (o mínimo pedido é 10). Em cada repetição é
  sorteada uma lista nova de inteiros, e os três algoritmos ordenam **a mesma**
  lista, em ordem embaralhada. A semente é fixa (`SEMENTE` em `medir.py`), então
  as listas são sempre as mesmas.
- **Tempo:** `time.perf_counter()`, com o coletor de lixo desligado durante a
  medição. Para n pequeno uma ordenação leva menos de 1 µs, então cada medição
  roda o algoritmo `max(1, 1000 // n)` vezes seguidas e divide o tempo — o valor
  gravado é sempre o tempo de **uma** ordenação. O relatório usa a média das 100
  medições.
- **Comparações:** cada valor é embrulhado num objeto `Contado` cujo `__lt__`
  incrementa um contador. Como inserção, intercalação e `sorted()` só comparam
  com `<`, o mesmo mecanismo conta os três. A contagem é feita numa execução
  separada da cronometrada, para o contador não pesar no tempo.

Formato de `dados.csv`:

```
algoritmo,n,repeticao,tempo_s,comparacoes
intercalacao,5,1,2.323999070e-06,5
sorted,5,1,7.950002328e-08,4
insercao,5,1,3.385008313e-07,4
```

Os tempos dependem da máquina; as comparações não (com a mesma semente, saem
idênticas em qualquer computador).
