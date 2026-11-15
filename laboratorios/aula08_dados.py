"""Importa ZIP/CSV diários BTCUSDT spot da Binance. Aula 08."""
import argparse
import csv
import hashlib
import io
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from zipfile import ZipFile

from aula07_simulador import Candle, simulate

EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
CHANGE = date(2025, 1, 1)


def parse_row(row):
    if len(row) != 12:
        raise ValueError("Esperadas 12 colunas")
    first, last = int(row[0]), int(row[6])
    # Os ficheiros spot documentados usam épocas Unix em ms ou µs.
    digits = len(str(first))
    if digits not in (13, 16):
        raise ValueError("Unidade temporal inesperada")
    scale = 1000 if digits == 13 else 1000000
    utc = EPOCH + timedelta(microseconds=first * (1000000 // scale))
    if (scale == 1000000) != (utc.date() >= CHANGE):
        raise ValueError("Unidade temporal incompatível com a data")
    if first % (86400 * scale) or last != first + 86400 * scale - 1:
        raise ValueError("A vela não cobre um dia UTC completo")
    op, high, low, close, volume = map(Decimal, row[1:6])
    if not all(x.is_finite() for x in (op, high, low, close, volume)):
        raise ValueError("Número não finito")
    if not 0 < low <= min(op, close) <= max(op, close) <= high or volume < 0:
        raise ValueError("OHLCV incoerente")
    return Candle(utc.date(), op, close)


def read_archive(path):
    path = Path(path)
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if path.suffix.lower() == ".zip":
        with ZipFile(io.BytesIO(raw)) as archive:
            members = [x for x in archive.infolist() if not x.is_dir()
                       and x.filename.lower().endswith(".csv")]
            if len(members) != 1:
                raise ValueError(f"{path}: esperado um único CSV no ZIP")
            raw = archive.read(members[0])
    elif path.suffix.lower() != ".csv":
        raise ValueError(f"{path}: usar ZIP ou CSV")
    rows = []
    for num, row in enumerate(csv.reader(io.StringIO(raw.decode("utf-8-sig"))), 1):
        try:
            rows.append(parse_row(row))
        except (ValueError, OverflowError, InvalidOperation) as exc:
            raise ValueError(f"{path}, linha {num}: {exc}") from exc
    if not rows:
        raise ValueError(f"{path}: sem velas")
    return rows, digest


def load_history(paths):
    by_day, manifest = {}, []
    for path in paths:
        rows, digest = read_archive(path)
        for candle in rows:
            if candle.day in by_day:
                raise ValueError(f"Vela duplicada em {path}: {candle.day}")
            by_day[candle.day] = candle
        manifest.append((str(path), digest, len(rows)))
    if not by_day:
        raise ValueError("Sem ficheiros")
    days = sorted(by_day)
    for prev, day in zip(days, days[1:]):
        if (day - prev).days != 1:
            raise ValueError(f"Lacuna entre {prev} e {day}")
    return [by_day[d] for d in days], manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+")
    parser.add_argument("--dia", type=date.fromisoformat,
                        help="Audita um único dia no motor, sem avaliar rentabilidade")
    args = parser.parse_args()
    rows, manifest = load_history(args.files)
    for path, digest, count in manifest:
        print(f"{path} | {count} velas | SHA-256 {digest}")
    print(f"Calendário UTC: {rows[0].day} a {rows[-1].day} | {len(rows)} velas")
    if args.dia:
        result = simulate(rows, args.dia, args.dia)
        day, signal, _, _ = result["daily"][0]
        state = "indisponível" if signal is None else "comprado" if signal else "em caixa"
        print(f"Abertura {day} | objetivo anterior: {state} | ordens: {len(result['trades'])}")


if __name__ == "__main__":
    main()
