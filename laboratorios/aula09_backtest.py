"""Aula 09: backtest no desenvolvimento e reconciliação do diário."""
import argparse
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

from aula07_simulador import simulate
from aula08_dados import load_history

START = date(2021, 1, 1)
END = date(2024, 12, 31)
WARMUP = START - timedelta(days=31)
INIT = Decimal("1000")
TOL = Decimal("1e-20")


def check(a, b):
    if abs(a - b) > TOL:
        raise ValueError(f"A auditoria divergiu: {a} vs {b}")


def reconcile(result, candles, bps, benchmark):
    prices = {c.day: c for c in candles}
    orders = {t[0]: t for t in result["trades"]}
    if len(orders) != len(result["trades"]):
        raise ValueError("Mais de uma ordem no mesmo dia")
    cash, btc, peak, dd, cost = INIT, Decimal(0), INIT, Decimal(0), Decimal(0)
    days_in = 0
    dd_peak, dd_trough, current_peak = None, None, None
    for day, target, engine_btc, equity in result["daily"]:
        c = prices[day]
        if benchmark:
            expected = True
        else:
            prev, lag = day - timedelta(days=1), day - timedelta(days=31)
            expected = prices[prev].close > prices[lag].close
        if target is not expected:
            raise ValueError(f"Sinal incorreto em {day}")
        side_expected = ("buy" if expected and btc == 0 else
                         "sell" if not expected and btc > 0 else None)
        order = orders.pop(day, None)
        if (order[1] if order else None) != side_expected:
            raise ValueError(f"Ordem inesperada ou ausente em {day}")
        if order:
            _, side, price, fee = order
            check(price, c.open)
            if side == "buy":
                check(fee, (cash - fee) * Decimal(bps) / 10000)
                btc, cash = (cash - fee) / price, Decimal(0)
            else:
                check(fee, btc * price * Decimal(bps) / 10000)
                cash, btc = btc * price - fee, Decimal(0)
            cost += fee
        total = cash + btc * c.close
        check(btc, engine_btc)
        check(total, equity)
        days_in += btc > 0
        if total > peak:
            peak, current_peak = total, day
        drop = 1 - total / peak
        if drop > dd:
            dd, dd_peak, dd_trough = drop, current_peak, day
    if orders:
        raise ValueError("Ordens fora do bloco")
    check(total / INIT - 1, result["return"])
    check(dd, result["max_drawdown"])
    check(Decimal(days_in) / len(result["daily"]), result["exposure"])
    return cost, dd_peak, dd_trough


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, help="Pasta com os ZIP mensais")
    args = parser.parse_args()
    months = ["2020-12"] + [f"{y}-{m:02}" for y in range(2021, 2025)
                           for m in range(1, 13)]
    candles, manifest = load_history([args.directory / f"BTCUSDT-1d-{m}.zip"
                                      for m in months])
    if (candles[0].day, candles[-1].day) != (WARMUP, END):
        raise ValueError("Cobertura diferente da prevista")
    print(f"{len(manifest)} ficheiros, {len(candles)} velas, "
          f"{(END - START).days + 1} dias avaliados")
    for bps in (5, 10, 20):
        for name, benchmark in (("Momentum", False), ("Comprar e manter", True)):
            r = simulate(candles, START, END, initial=INIT, bps=bps, benchmark=benchmark)
            cost, peak, trough = reconcile(r, candles, bps, benchmark)
            print(f"{bps:2} pb | {name:17} | saldo {r['daily'][-1][3]:.2f} | "
                  f"retorno {r['return']:.2%} | drawdown {r['max_drawdown']:.2%} | "
                  f"exposição {r['exposure']:.2%} | {len(r['trades'])} ordens | "
                  f"custos {cost:.2f} USDT | {peak} a {trough}")
            if bps == 10:
                print("  Primeiras ordens:", r["trades"][:2])


if __name__ == "__main__":
    main()
