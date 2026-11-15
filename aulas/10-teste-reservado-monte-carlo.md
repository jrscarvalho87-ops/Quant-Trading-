# Aula 10 — Teste reservado e Monte Carlo

Corremos a regra congelada de momentum de 30 dias em BTCUSDT spot de 1 de janeiro de 2025 a 31 de outubro de 2026. São 669 dias avaliados e 31 velas de preparação. Cada abordagem começa com 1 000 USDT, sem posição herdada nem liquidação forçada no fim. Confirmámos os resultados por reconciliação diária das ordens, dos custos e do património.

## Resultado com 0,10% de custo por ordem

| Métrica | Momentum | Comprar e manter |
| --- | ---: | ---: |
| Património final | 991,25 USDT | 828,25 USDT |
| Retorno líquido | −0,88% | −17,17% |
| Drawdown máximo aos fechos | 32,64% | 52,97% |
| Dias em BTC ao fecho | 51,72% | 100% |
| Ordens | 70 | 1 |
| Custos acumulados | 62,78 USDT | 1,00 USDT |

Com 0,05% por ordem, momentum +2,66% e comprar e manter −17,13%. Com 0,20%, momentum −7,58% e comprar e manter −17,26%. Superar a referência não significa ganhar dinheiro. Não escolhemos o custo mais baixo depois de ver que torna o resultado positivo.

## A estratégia escolheu melhor os dias?

Rodámos circularmente o calendário de exposição observado e reaplicámos o custo base aos preços do mesmo período. As 668 rotações alternativas têm o mesmo número de dias em BTC e deslocam os blocos de exposição. O início e fim podem cortar um bloco e alterar o número de ordens. A regra superou 529 de 668 rotações (79,2%) e a alternativa mediana rendeu −17,20%. É um diagnóstico retrospectivo, não uma estratégia executável nem um teste de significância.

## Monte Carlo

Em cada cenário, gerámos 5 000 percursos de 669 dias, reamostrando com reposição blocos circulares de retornos diários líquidos do momentum ao custo base. Não recalculámos o sinal. Os blocos preservam a sequência dentro de cada segmento e podem quebrar dependência entre segmentos. [Método de bootstrap circular](https://arch.readthedocs.io/en/latest/bootstrap/generated/arch.bootstrap.CircularBlockBootstrap.html).

| Duração do bloco | Retorno P5 | Retorno mediano | Retorno P95 | Drawdown mediano | Drawdown P95 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 15 dias | −43,82% | −2,51% | +80,94% | 31,73% | 53,47% |
| 30 dias | −43,07% | −1,88% | +80,19% | 31,44% | 52,00% |
| 60 dias | −42,90% | −1,59% | +77,40% | 31,49% | 51,14% |

Para blocos de 30 dias, cerca de 5% dos percursos simulados tiveram drawdown superior a 52%. Isso não é uma probabilidade calibrada para o mercado futuro. O modelo reaproveita padrões observados e não cria choques fora da amostra. O resultado pode mudar com a duração dos blocos.

## Reprodução

Descarregar os 23 ZIP mensais de dezembro de 2024 a outubro de 2026 do [arquivo público BTCUSDT diário spot](https://data.binance.vision/?prefix=data/spot/monthly/klines/BTCUSDT/1d/). Executar `python laboratorios/aula10_teste_reservado.py caminho/para/os/zips`. Dezembro de 2024 serve apenas de preparação, sem contar para o retorno.

## Exercício

Se o património terminou quase no ponto de partida, como pôde ter caído mais de 30% a partir de um pico durante o teste?
