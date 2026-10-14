"""Mede tempo e comparações de inserção, intercalação e sorted().

Rodar com:  python medir.py

Refaz do zero, na mesma pasta deste arquivo:
  - dados.csv        uma linha por medição (algoritmo, n, repetição, tempo, comparações)
  - tempos.png       gráfico dos tempos médios
  - comparacoes.png  gráfico das comparações médias
e imprime as tabelas-resumo em Markdown (as mesmas do RELATORIO.md).
"""

import csv
import gc
import math
import random
import statistics
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # gera os PNGs sem precisar de janela/tela
import matplotlib.pyplot as plt

from ordenacao import contar_comparacoes, insercao, intercalacao

TAMANHOS = [5, 10, 20, 30, 50, 75, 100, 200, 500, 1000]
REPETICOES = 100  # o enunciado pede no mínimo 10
SEMENTE = 2026  # semente fixa: as listas sorteadas são sempre as mesmas

ALGORITMOS = {
    "insercao": insercao,
    "intercalacao": intercalacao,
    "sorted": sorted,
}
NOMES = {"insercao": "Inserção", "intercalacao": "Intercalação", "sorted": "sorted()"}
CORES = {"insercao": "#2a78d6", "intercalacao": "#eb6834", "sorted": "#1baf7a"}
MARCADORES = {"insercao": "o", "intercalacao": "s", "sorted": "^"}

PASTA = Path(__file__).resolve().parent
ARQ_CSV = PASTA / "dados.csv"
ARQ_TEMPOS = PASTA / "tempos.png"
ARQ_COMPARACOES = PASTA / "comparacoes.png"


def execucoes_por_medicao(n):
    """Quantas vezes rodar o algoritmo dentro de uma medição.

    Para n pequeno uma ordenação leva poucos microssegundos, perto da resolução
    do relógio. Rodamos várias vezes seguidas e dividimos, para que cada
    medição dure pelo menos ~1000 elementos ordenados.
    """
    return max(1, 1000 // n)


def cronometrar(ordenar, lista, vezes):
    """Tempo médio (em segundos) de uma chamada ordenar(lista)."""
    inicio = time.perf_counter()
    for _ in range(vezes):
        ordenar(lista)
    return (time.perf_counter() - inicio) / vezes


def medir():
    """Roda todas as medições e devolve as linhas brutas."""
    rng = random.Random(SEMENTE)
    linhas = []
    gc_estava_ligado = gc.isenabled()
    gc.disable()  # evita que a coleta de lixo caia no meio de uma medição
    try:
        for n in TAMANHOS:
            vezes = execucoes_por_medicao(n)
            for rep in range(1, REPETICOES + 1):
                # Mesma lista aleatória para os três algoritmos nesta repetição.
                lista = [rng.randint(0, 10 * n) for _ in range(n)]
                ordem = list(ALGORITMOS)
                rng.shuffle(ordem)  # nenhum algoritmo roda sempre primeiro
                for nome in ordem:
                    ordenar = ALGORITMOS[nome]
                    tempo = cronometrar(ordenar, lista, vezes)
                    resultado, comparacoes = contar_comparacoes(ordenar, lista)
                    assert resultado == sorted(lista), f"{nome} errou com n={n}"
                    linhas.append({
                        "algoritmo": nome,
                        "n": n,
                        "repeticao": rep,
                        "tempo_s": tempo,
                        "comparacoes": comparacoes,
                    })
            print(f"  n = {n:4d} pronto", flush=True)
    finally:
        if gc_estava_ligado:
            gc.enable()
    return linhas


def salvar_csv(linhas):
    with open(ARQ_CSV, "w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=["algoritmo", "n", "repeticao", "tempo_s", "comparacoes"])
        escritor.writeheader()
        for linha in linhas:
            escritor.writerow({**linha, "tempo_s": f"{linha['tempo_s']:.9e}"})


def resumir(linhas):
    """{algoritmo: {n: {tempo_medio, tempo_desvio, comp_media, comp_min, comp_max}}}"""
    resumo = {nome: {} for nome in ALGORITMOS}
    for nome in ALGORITMOS:
        for n in TAMANHOS:
            grupo = [l for l in linhas if l["algoritmo"] == nome and l["n"] == n]
            tempos = [l["tempo_s"] for l in grupo]
            comps = [l["comparacoes"] for l in grupo]
            resumo[nome][n] = {
                "tempo_medio": statistics.mean(tempos),
                "tempo_desvio": statistics.stdev(tempos),
                "comp_media": statistics.mean(comps),
                "comp_min": min(comps),
                "comp_max": max(comps),
            }
    return resumo


def log2_fatorial(n):
    """log2(n!), o mínimo de comparações de qualquer ordenação por comparação."""
    return math.lgamma(n + 1) / math.log(2)


def ponto_de_virada(resumo, chave):
    """Menor n a partir do qual a intercalação vence a inserção em todos os n maiores."""
    virada = None
    for n in reversed(TAMANHOS):
        if resumo["intercalacao"][n][chave] < resumo["insercao"][n][chave]:
            virada = n
        else:
            break
    return virada


def grafico(resumo, chave, arquivo, titulo, rotulo_y, escala=1.0, referencias=False):
    """Dois painéis: n ≤ 100 em escala linear (para ver a virada) e todos os n em log-log."""
    fig, (ax_zoom, ax_log) = plt.subplots(1, 2, figsize=(12, 4.8))
    fig.suptitle(titulo, fontsize=13)

    for ax, ns, subtitulo in [
        (ax_zoom, [n for n in TAMANHOS if n <= 100], "n ≤ 100 (escala linear)"),
        (ax_log, TAMANHOS, "todos os n (escala log-log)"),
    ]:
        if referencias:
            ax.plot(ns, [n * math.log2(n) for n in ns], color="#8a8984", linestyle=":",
                    linewidth=1.5, label="n·log₂ n")
            ax.plot(ns, [log2_fatorial(n) for n in ns], color="#52514e", linestyle="--",
                    linewidth=1.5, label="log₂ n!  (limite inferior)")
        for nome in ALGORITMOS:
            ys = [resumo[nome][n][chave] * escala for n in ns]
            ax.plot(ns, ys, color=CORES[nome], marker=MARCADORES[nome], markersize=6,
                    linewidth=2, label=NOMES[nome])
        ax.set_title(subtitulo, fontsize=10, color="#52514e")
        ax.set_xlabel("n (tamanho da lista)")
        ax.set_ylabel(rotulo_y)
        ax.grid(True, color="#e4e3df", linewidth=0.8)
        for lado in ("top", "right"):
            ax.spines[lado].set_visible(False)

    ax_zoom.set_xticks([n for n in TAMANHOS if n <= 100])
    ax_zoom.set_ylim(bottom=0)
    ax_log.set_xscale("log")
    ax_log.set_yscale("log")
    ax_log.set_xticks(TAMANHOS)
    ax_log.set_xticklabels([str(n) for n in TAMANHOS])
    ax_log.minorticks_off()
    ax_zoom.legend(frameon=False)

    fig.tight_layout()
    fig.savefig(arquivo, dpi=130)
    plt.close(fig)


def tabela_markdown(resumo):
    tempos = ["| n | Inserção (µs) | Intercalação (µs) | sorted() (µs) | mais rápido (inserção × intercalação) |",
              "|---:|---:|---:|---:|:---|"]
    comps = ["| n | Inserção | Intercalação | sorted() | n·log₂ n | ⌈log₂ n!⌉ |",
             "|---:|---:|---:|---:|---:|---:|"]
    for n in TAMANHOS:
        t = {nome: resumo[nome][n]["tempo_medio"] * 1e6 for nome in ALGORITMOS}
        c = {nome: resumo[nome][n]["comp_media"] for nome in ALGORITMOS}
        vencedor = "inserção" if t["insercao"] < t["intercalacao"] else "intercalação"
        tempos.append(f"| {n} | {t['insercao']:.2f} | {t['intercalacao']:.2f} | {t['sorted']:.2f} | {vencedor} |")
        comps.append(f"| {n} | {c['insercao']:.1f} | {c['intercalacao']:.1f} | {c['sorted']:.1f} "
                     f"| {n * math.log2(n):.1f} | {math.ceil(log2_fatorial(n))} |")
    return "\n".join(tempos), "\n".join(comps)


def main():
    print(f"Medindo {len(TAMANHOS)} tamanhos × {REPETICOES} repetições × {len(ALGORITMOS)} algoritmos...")
    linhas = medir()
    salvar_csv(linhas)
    resumo = resumir(linhas)

    grafico(resumo, "tempo_medio", ARQ_TEMPOS, "Tempo médio de ordenação (listas aleatórias)",
            "tempo médio (µs)", escala=1e6)
    grafico(resumo, "comp_media", ARQ_COMPARACOES, "Número médio de comparações (listas aleatórias)",
            "comparações", referencias=True)

    tab_tempos, tab_comps = tabela_markdown(resumo)
    print("\nTempo médio por ordenação\n")
    print(tab_tempos)
    print("\nComparações médias por ordenação\n")
    print(tab_comps)

    print()
    print(f"Ponto de virada no TEMPO:       intercalação vence a partir de n = {ponto_de_virada(resumo, 'tempo_medio')}")
    print(f"Ponto de virada nas COMPARAÇÕES: intercalação vence a partir de n = {ponto_de_virada(resumo, 'comp_media')}")
    print(f"\nGerados: {ARQ_CSV.name}, {ARQ_TEMPOS.name}, {ARQ_COMPARACOES.name}")


if __name__ == "__main__":
    main()
