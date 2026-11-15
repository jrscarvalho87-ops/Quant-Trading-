"""Aula 11: ensaio em memória, sem rede, credenciais ou ordens reais."""
from datetime import date, timedelta
from decimal import Decimal
import unittest

DAY = timedelta(days=1)
COST = Decimal("0.001")


class Paper:
    def __init__(self, history):
        self.history = dict(history)  # apenas fechos diários UTC validados
        self.cash = Decimal("1000")
        self.btc = Decimal(0)
        self.pending = None
        self.events = []

    def candle(self, day, close, closed, received, ended):
        """received e ended são instantes em segundos no mesmo relógio."""
        if not closed:
            return "vela_aberta"
        if day in self.history:
            if self.history[day] != close:
                self.pending = None
                raise ValueError("Fecho duplicado com preço diferente")
            return "duplicado"
        if not close.is_finite() or close <= 0 or received < ended:
            raise ValueError("Fecho ou relógio inválido")
        if self.history and day < max(self.history):
            raise ValueError("Vela fora de ordem")
        self.history[day] = close
        self.pending = None
        if received - ended > 120:
            state = "fecho_atrasado"
        elif any(day - i * DAY not in self.history for i in range(31)):
            state = "historico_incompleto"
        else:
            target = close > self.history[day - 30 * DAY]
            if target != (self.btc > 0):
                self.pending = (day, target, received, ended + 120)
                state = "compra_pendente" if target else "venda_pendente"
            else:
                state = "sem_mudanca"
        self.events.append((day, state))
        return state

    def quote(self, bid, ask, quote_received, now):
        if self.pending is None:
            return "sem_ordem"
        day, buy, signal_received, deadline = self.pending
        if now > deadline:
            self.pending = None
            self.events.append((day, "ordem_expirada"))
            return "ordem_expirada"
        if not signal_received < quote_received <= now or now - quote_received > 5:
            return "cotacao_nao_utilizavel"
        if not bid.is_finite() or not ask.is_finite() or not 0 < bid <= ask:
            raise ValueError("Cotação inválida")
        price = ask if buy else bid
        if buy:
            value = self.cash / (1 + COST)
            self.btc, self.cash = value / price, Decimal(0)
        else:
            value = self.btc * price
            self.cash, self.btc = value * (1 - COST), Decimal(0)
        self.pending = None
        self.events.append((day, "compra" if buy else "venda", price, value * COST))
        return "executada_em_simulacao"


class TestReplay(unittest.TestCase):
    def setUp(self):
        self.day = date(2024, 2, 1)
        self.paper = Paper({self.day - i * DAY: Decimal("100") for i in range(1, 31)})
        self.bid, self.ask = Decimal("101"), Decimal("102")

    def close(self):
        return self.paper.candle(self.day, self.bid, True, 102, 100)

    def test_open_candle_is_ignored(self):
        self.assertEqual(self.paper.candle(self.day, self.bid, False, 99, 100),
                         "vela_aberta")
        self.assertIsNone(self.paper.pending)

    def test_only_fresh_quote_after_signal_and_one_fill(self):
        self.assertEqual(self.close(), "compra_pendente")
        self.assertEqual(self.paper.quote(self.bid, self.ask, 102, 103),
                         "cotacao_nao_utilizavel")
        self.assertEqual(self.paper.quote(self.bid, self.ask, 103, 109),
                         "cotacao_nao_utilizavel")
        self.assertEqual(self.paper.quote(self.bid, self.ask, 110, 110),
                         "executada_em_simulacao")
        self.assertEqual(self.paper.events[-1][2], self.ask)
        self.assertEqual(self.close(), "duplicado")
        self.assertEqual(self.paper.quote(self.bid, self.ask, 111, 111), "sem_ordem")
        self.assertEqual(len(self.paper.events), 2)

    def test_expired_intent(self):
        self.close()
        self.assertEqual(self.paper.quote(self.bid, self.ask, 221, 221), "ordem_expirada")
        self.assertEqual(self.paper.cash, Decimal("1000"))

    def test_gap_blocks_signal(self):
        del self.paper.history[self.day - 15 * DAY]
        self.assertEqual(self.close(), "historico_incompleto")
        self.assertIsNone(self.paper.pending)

    def test_late_close_does_not_trade(self):
        self.assertEqual(self.paper.candle(self.day, self.bid, True, 221, 100),
                         "fecho_atrasado")
        self.assertIsNone(self.paper.pending)

    def test_sell_at_bid(self):
        self.paper.cash, self.paper.btc = Decimal(0), Decimal(1)
        self.assertEqual(self.paper.candle(self.day, Decimal("99"), True, 102, 100),
                         "venda_pendente")
        self.assertEqual(self.paper.quote(Decimal("97"), Decimal("98"), 103, 103),
                         "executada_em_simulacao")
        self.assertEqual(self.paper.cash, Decimal("96.903"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
