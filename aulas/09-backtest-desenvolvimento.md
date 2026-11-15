# Aula 09 — Auditar o backtest de desenvolvimento

## O que corremos

Momentum de 30 dias em BTCUSDT spot diário, 1 de janeiro de 2021 a 31 de dezembro de 2024. O desenvolvimento usa 1 461 sessões UTC e 31 velas anteriores para preparar o primeiro sinal. A referência compra na primeira abertura e mantém até ao último fecho. Ambas começam com 1 000 USDT fictícios e são valorizadas a mercado sem venda forçada no fim. O período reservado de janeiro de 2025 a outubro de 2026 não foi executado.

## Cenário base, com custo hipotético de 0,10% por ordem

| Medida | Momentum | Comprar e manter |
| --- | ---: | ---: |
| Património final | 4 220,44 USDT | 3 232,05 USDT |
| Retorno líquido acumulado | +322,04% | +223,20% |
| Drawdown máximo entre fechos | 46,00% | 76,63% |
| Dias em BTC, medidos ao fecho | 54,96% | 100,00% |
| Ordens | 118 | 1 |
| Custos registados | 249,68 USDT | 1,00 USDT |

Com custo de 0,05% por ordem, o retorno do momentum é +347,69% e o da referência +223,37%. A 0,20%, é +275,07% contra +222,88%. Estes valores são cenários agregados simulados, não tarifas efetivas nem previsões. O drawdown máximo é a maior descida desde um pico até um fecho posterior, incluindo o saldo inicial como ponto de partida. Não mede a pior queda intradiária.

## Como verificámos as contas

O segundo cálculo reconstrói caixa e BTC ordem a ordem. Confirma que cada sinal usa os fechos corretos e que as ordens que mudam a posição usam a abertura seguinte. Recalcula o custo sobre o valor da ordem, o património diário, o drawdown e a exposição. Os seis resultados, duas abordagens em três cenários, coincidiram com o motor.

A primeira compra do momentum ocorreu na abertura de 1 de janeiro de 2021 a 28 923,63 USDT por BTC. Dos 1 000 USDT, o valor da compra foi 1 000 / 1,001, ou aproximadamente 999,001 USDT. O custo foi aproximadamente 0,999 USDT e o saldo em caixa ficou a zero. Na primeira venda, em 7 de fevereiro, a abertura foi 39 181,01 USDT e o custo foi cerca de 1,353 USDT.

## Reprodução

Na raiz do repositório, correr `python laboratorios/aula09_backtest.py caminho/para/os/zips`. Usar os 49 ZIP mensais de BTCUSDT spot, frequência 1d, de dezembro de 2020 a dezembro de 2024. Os nomes seguem o formato BTCUSDT-1d-AAAA-MM.zip. Ver [arquivo de origem](https://data.binance.vision/?prefix=data/spot/monthly/klines/BTCUSDT/1d/) e [protocolo da aula 06](06-protocolo-backtest.md).

## O que não podemos concluir

O momentum bateu a referência neste período, mas isso não valida uma vantagem fora dele. O drawdown menor também não isola o efeito de escolher bem os dias, pois a estratégia esteve exposta apenas 54,96% do tempo. Na aula 10 vamos avaliar a regra congelada no período reservado e estudar a robustez sem alterar a regra com base nesse resultado.

## Exercício

Quanto precisa de subir uma carteira que caiu 46% desde o pico para recuperar o valor anterior?