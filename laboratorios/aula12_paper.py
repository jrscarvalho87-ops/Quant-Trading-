"""Paper trading local BTCUSDT, exclusivamente com dados públicos."""
import argparse
import json
import sqlite3
import time
from contextlib import closing
from datetime import datetime, timezone
from decimal import Decimal
from urllib.error import URLError
from urllib.request import Request, urlopen

BASE = "https://data-api.binance.vision"
DAY = 86400000
COST = Decimal("0.001")


def utc_day(ms):
    return datetime.fromtimestamp(ms // 1000, timezone.utc).date().isoformat()


def api(path):
    with urlopen(Request(BASE + path, headers={"Cache-Control": "no-cache"}),
                 timeout=12) as response:
        return json.load(response)


def open_db(path):
    db = sqlite3.connect(path, timeout=10)
    db.executescript("""
    CREATE TABLE IF NOT EXISTS wallet (id INTEGER PRIMARY KEY, cash TEXT, btc TEXT);
    INSERT OR IGNORE INTO wallet VALUES (1, '1000', '0');
    CREATE TABLE IF NOT EXISTS journal (
      day TEXT PRIMARY KEY, status TEXT NOT NULL, signal TEXT,
      price TEXT, cost TEXT, cash TEXT NOT NULL, btc TEXT NOT NULL
    );
    """)
    return db


def cycle(db, server_ms, rows, get_quote):
    # O relógio do servidor é lido antes das velas. Sem usar a vela em formação.
    ended = server_ms // DAY * DAY
    day = utc_day(ended - DAY)
    expected = [ended - n * DAY for n in range(31, 0, -1)]
    eligible = [r for r in rows if r[0] < ended]
    if [r[0] for r in eligible] != expected:
        return day, "histórico indisponível; tentar novamente"
    if any(r[6] != r[0] + DAY - 1 for r in eligible):
        raise ValueError("Fecho UTC incoerente")
    closes = [Decimal(r[4]) for r in eligible]
    if not all(p.is_finite() and p > 0 for p in closes):
        raise ValueError("Fecho inválido")
    target = closes[-1] > closes[0]

    # Um único escritor por vez. Carteira e diário só são alterados juntos.
    with db:
        db.execute("BEGIN IMMEDIATE")
        previous = db.execute("SELECT status FROM journal WHERE day=?", (day,)).fetchone()
        if previous:
            return day, "já processado (" + previous[0] + ")"
        latest = db.execute("SELECT MAX(day) FROM journal").fetchone()[0]
        if latest and day < latest:
            raise ValueError("Data anterior ao último evento")
        cash, btc = map(Decimal, db.execute("SELECT cash, btc FROM wallet WHERE id=1").fetchone())
        price = fee = None
        if target == (btc > 0):
            status = "sem_mudança"
        elif server_ms - ended >= 120000:
            status = "intenção_expirada"
        else:
            bid, ask, observed_ms = get_quote()
            if observed_ms < server_ms or observed_ms - ended >= 120000:
                status = "intenção_expirada"
            else:
                if not all(p.is_finite() for p in (bid, ask)) or not 0 < bid <= ask:
                    raise ValueError("Bid/ask inválido")
                price = ask if target else bid
                if target:
                    notional = cash / (1 + COST)
                    btc, fee, cash = notional / price, cash - notional, Decimal(0)
                else:
                    notional = btc * price
                    fee = notional * COST
                    cash, btc = notional - fee, Decimal(0)
                status = "compra_simulada" if target else "venda_simulada"
        signal = "comprado" if target else "em_caixa"
        db.execute("INSERT INTO journal VALUES (?,?,?,?,?,?,?)",
                   (day, status, signal, None if price is None else str(price),
                    None if fee is None else str(fee), str(cash), str(btc)))
        db.execute("UPDATE wallet SET cash=?, btc=? WHERE id=1", (str(cash), str(btc)))
        return day, status


def public_cycle(db):
    tick = time.monotonic()
    server = int(api("/api/v3/time")["serverTime"])
    end = server // DAY * DAY - 1
    rows = api(f"/api/v3/klines?symbol=BTCUSDT&interval=1d&limit=31&endTime={end}")
    def quote():
        start = time.monotonic()
        q = api("/api/v3/ticker/bookTicker?symbol=BTCUSDT")
        now = time.monotonic()
        if now - start > 5:
            raise ValueError("Pedido de cotação demorou mais de 5 segundos")
        # Estimativa conservadora da hora de receção, inclui todo o pedido de relógio.
        observed = server + int((now - tick) * 1000)
        return Decimal(q["bidPrice"]), Decimal(q["askPrice"]), observed
    return cycle(db, server, rows, quote)


def self_test():
    from pathlib import Path
    from tempfile import TemporaryDirectory

    ended = DAY * 20000
    rows = [[ended-i*DAY, 0, 0, 0, "101" if i == 1 else "100", 0,
             ended-(i-1)*DAY-1] for i in range(31, 0, -1)]

    def unexpected_quote():
        raise AssertionError("Não devia pedir cotação")

    with TemporaryDirectory() as directory:
        path = Path(directory) / "test.sqlite3"
        with closing(open_db(path)) as db:
            assert cycle(db, ended+1000, rows,
                         lambda: (Decimal("101"), Decimal("102"), ended+2000))[1] == "compra_simulada"
            wallet = db.execute("SELECT cash, btc FROM wallet").fetchone()
        with closing(open_db(path)) as db:
            assert cycle(db, ended+3000, rows, unexpected_quote)[1] == "já processado (compra_simulada)"
            assert db.execute("SELECT count(*) FROM journal").fetchone() == (1,)
            assert db.execute("SELECT cash, btc FROM wallet").fetchone() == wallet
            assert Decimal(wallet[1]) > 0
            following = rows[1:] + [[ended, 0, 0, 0, "99", 0, ended+DAY-1]]
            assert cycle(db, ended+DAY+120000, following, unexpected_quote)[1] == "intenção_expirada"
            assert cycle(db, ended+2*DAY, [], unexpected_quote)[1].startswith("histórico indisponível")
            assert db.execute("SELECT cash, btc FROM wallet").fetchone() == wallet
    print("OK: compra, reinício sem duplicado, expiração e histórico incompleto")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default="paper_btc.sqlite3")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    with closing(open_db(args.db)) as db:
        try:
            print(*public_cycle(db))
        except (URLError, TimeoutError, ValueError) as exc:
            parser.exit(1, f"Ciclo interrompido, sem ordem: {exc}\n")
        print("Carteira fictícia (USDT, BTC):",
              db.execute("SELECT cash, btc FROM wallet WHERE id=1").fetchone())


if __name__ == "__main__":
    main()
