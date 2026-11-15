"""Aula 07. Motor diário didático para BTCUSDT spot. Sem dependências."""
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
import unittest

DAY = timedelta(days=1)
ZERO = Decimal("0")


@dataclass(frozen=True)
class Candle:
    day: date  # Data UTC da abertura
    open: Decimal
    close: Decimal


def simulate(candles, start, end, initial=Decimal("1000"), bps=10,
             benchmark=False):
    """Recebe velas já normalizadas e auditadas. Devolve ordens e património."""
    if start > end or not initial.is_finite() or initial <= ZERO or not 0 <= bps < 10000:
        raise ValueError("Período, capital ou custo inválido")
    by_day = {}
    for c in candles:
        if c.day in by_day:
            raise ValueError(f"Vela repetida: {c.day}")
        if not all(x.is_finite() and x > ZERO for x in (c.open, c.close)):
            raise ValueError(f"Preço inválido: {c.day}")
        by_day[c.day] = c

    days = [start + i * DAY for i in range((end - start).days + 1)]
    missing = [day for day in days if day not in by_day]
    if missing:
        raise ValueError(f"Bloco incompleto; primeira vela em falta: {missing[0]}")

    def signal(day):
        days_back = [day - n * DAY for n in range(31)]
        if any(d not in by_day for d in days_back):
            return None
        return by_day[day].close > by_day[day - 30 * DAY].close

    cost = Decimal(bps) / 10000
    cash, btc = initial, ZERO
    trades, daily = [], []
    peak, max_drawdown = initial, ZERO
    for day in days:
        candle = by_day[day]
        target = True if benchmark else signal(day - DAY)
        side, fee = None, ZERO
        if target is True and btc == ZERO:
            # Reserva parte do saldo para o custo agregado da compra.
            notional = cash / (1 + cost)
            btc, fee, cash = notional / candle.open, cash - notional, ZERO
            side = "buy"
        elif target is False and btc > ZERO:
            notional = btc * candle.open
            fee = notional * cost
            cash, btc = notional - fee, ZERO
            side = "sell"
        if side:
            trades.append((day, side, candle.open, fee))
        equity = cash + btc * candle.close
        peak = max(peak, equity)
        max_drawdown = max(max_drawdown, 1 - equity / peak)
        daily.append((day, target, btc, equity))
    return {
        "trades": trades,
        "daily": daily,
        "return": daily[-1][3] / initial - 1,
        "max_drawdown": max_drawdown,
        "exposure": Decimal(sum(row[2] > ZERO for row in daily)) / len(days),
    }


class Tests(unittest.TestCase):
    def setUp(self):
        self.start = date(2024, 2, 1)
        self.rows = [Candle(self.start - n * DAY, Decimal("90"), Decimal("90"))
                     for n in range(31, 0, -1)]
        self.rows[-1] = Candle(self.start - DAY, Decimal("90"), Decimal("110"))
        self.rows[-31] = Candle(self.start - 31 * DAY, Decimal("90"), Decimal("100"))
        self.rows[-30] = Candle(self.start - 30 * DAY, Decimal("90"), Decimal("101"))
        self.rows += [
            Candle(self.start, Decimal("100"), Decimal("100")),
            Candle(self.start + DAY, Decimal("97"), Decimal("140")),
        ]

    def test_sell_at_next_open_and_pay_cost(self):
        r = simulate(self.rows, self.start, self.start + DAY, Decimal("100.10"))
        self.assertEqual(r["daily"][0][2:], (Decimal("1"), Decimal("100")))
        self.assertEqual(r["trades"][-1],
                         (self.start + DAY, "sell", Decimal("97"), Decimal("0.097")))
        self.assertEqual(r["daily"][-1][3], Decimal("96.903"))

    def test_missing_history_is_not_cash_signal(self):
        r = simulate(self.rows[1:], self.start, self.start)
        self.assertIsNone(r["daily"][0][1])
        self.assertEqual(r["trades"], [])

    def test_missing_valuation_rejects_block(self):
        with self.assertRaisesRegex(ValueError, "Bloco incompleto"):
            simulate(self.rows[:-1], self.start, self.start + DAY)

    def test_duplicate_rejected(self):
        with self.assertRaisesRegex(ValueError, "Vela repetida"):
            simulate(self.rows + self.rows[-1:], self.start, self.start)

    def test_benchmark_buys_once_and_no_forced_sale(self):
        r = simulate(self.rows, self.start, self.start + DAY, Decimal("100.10"),
                     benchmark=True)
        self.assertEqual(len(r["trades"]), 1)
        self.assertEqual(r["daily"][-1][3], Decimal("140"))
        self.assertEqual(r["exposure"], Decimal("1"))

    def test_equal_momentum_stays_in_cash(self):
        rows = self.rows.copy()
        rows[-3] = Candle(self.start - DAY, Decimal("90"), Decimal("100"))
        r = simulate(rows, self.start, self.start)
        self.assertIs(r["daily"][0][1], False)
        self.assertEqual(r["trades"], [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
