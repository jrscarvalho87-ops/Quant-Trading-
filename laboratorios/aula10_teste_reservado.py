"""Aula 10. Teste reservado, controlo de exposição e Monte Carlo."""
import argparse
from datetime import date, timedelta
from decimal import Decimal
from itertools import accumulate
from math import expm1, log
from pathlib import Path
from random import Random

from aula07_simulador import simulate
from aula08_dados import load_history
from aula09_backtest import INIT, reconcile

START = date(2025, 1, 1)
END = date(2026, 10, 31)


def quantile(values, q):
    ordered = sorted(values)
    idx = (len(ordered) - 1) * q
    i = int(idx)
    return ordered[i] + (idx - i) * (ordered[min(i + 1, len(ordered) - 1)] - ordered[i])


def monte_carlo(equity, block=30, n=5000, seed=20261115):
    """Reamostra blocos de retornos líquidos; não recalcula o sinal."""
    logs = [log(float(b / a)) for a, b in zip([INIT] + equity, equity)]
    rng = Random(seed)
    returns, drops = [], []
    for _ in range(n):
        sample = []
        while len(sample) < len(logs):
            j = rng.randrange(len(logs))
            sample.extend(logs[(j + k) % len(logs)] for k in range(block))
        peak = dd = total = 0.0
        for total in accumulate(sample[:len(logs)]):
            peak = max(peak, total)
            dd = max(dd, -expm1(total - peak))
        returns.append(expm1(total))
        drops.append(dd)
    return returns, drops


def rotated_exposure(result, candles, bps=10):
    """Testa todas as rotações do calendário de exposição observado."""
    days = {c.day: c for c in candles}
    prices = [(float(days[row[0]].open), float(days[row[0]].close))
              for row in result["daily"]]
    states = [row[2] > 0 for row in result["daily"]]
    n = len(states)
    cost = bps / 10000
    outcomes = []
    for shift in range(n):
        cash, btc = float(INIT), 0.0
        for i, (op, close) in enumerate(prices):
            if states[(i + shift) % n]:
                if not btc:
                    btc, cash = cash / (1 + cost) / op, 0.0
            elif btc:
                cash, btc = btc * op * (1 - cost), 0.0
        outcomes.append((cash + btc * prices[-1][1]) / float(INIT) - 1)
    if abs(outcomes[0] - float(result["return"])) > 1e-10:
        raise ValueError("O controlo não reproduz a rotação zero")
    return outcomes[1:]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    months = ["2024-12"] + [f"{y}-{m:02d}" for y, n in [(2025, 12), (2026, 10)]
                           for m in range(1, n + 1)]
    candles, manifest = load_history([args.directory / f"BTCUSDT-1d-{m}.zip" for m in months])
    if (candles[0].day, candles[-1].day) != (START - timedelta(days=31), END):
        raise ValueError("Cobertura diferente da prevista")
    print(f"{len(manifest)} ficheiros, {len(candles)} velas, {(END-START).days+1} dias")
    for bps in (5, 10, 20):
        for label, benchmark in (("Momentum", False), ("Comprar e manter", True)):
            r = simulate(candles, START, END, bps=bps, benchmark=benchmark)
            cost, peak, trough = reconcile(r, candles, bps, benchmark)
            print(f"{bps} pb | {label} | final {r['daily'][-1][3]:.2f} | "
                  f"retorno {r['return']:.2%} | DD {r['max_drawdown']:.2%} | "
                  f"exposição {r['exposure']:.2%} | ordens {len(r['trades'])} | "
                  f"custo {cost:.2f} | {peak} a {trough}")
            if bps == 10 and not benchmark:
                base = r
    outcomes = rotated_exposure(base, candles)
    print(f"Rotações: {len(outcomes)} | mediana {quantile(outcomes, .5):.2%} | "
          f"abaixo do observado: {sum(r < float(base['return']) for r in outcomes)}")
    equity = [row[3] for row in base["daily"]]
    for block in (15, 30, 60):
        returns, drops = monte_carlo(equity, block)
        print(f"MC {block} dias | retorno P5/P50/P95 " +
              "/".join(f"{quantile(returns,q):.2%}" for q in (.05,.5,.95)) +
              " | DD P50/P95 " +
              "/".join(f"{quantile(drops,q):.2%}" for q in (.5,.95)))


if __name__ == "__main__":
    main()
