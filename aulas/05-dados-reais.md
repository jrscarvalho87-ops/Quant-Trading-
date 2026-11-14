# Aula 05 — Dados reais, relógio e integridade

Na aula 04 controlámos a geração dos dados. Agora o primeiro objetivo é verificar a série que o modelo vai receber. Nesta aula não medimos rentabilidade.

## Amostra reproduzível

- Mercado: BTCUSDT spot da Binance. Frequência: 1d. Fuso: UTC. Preço: USDT por BTC.
- [Arquivo ZIP de janeiro de 2024](https://data.binance.vision/data/spot/monthly/klines/BTCUSDT/1d/BTCUSDT-1d-2024-01.zip).
- Colunas iniciais: instante de abertura, abertura, máximo, mínimo, fecho, volume e instante de fecho. A data da linha identifica a abertura da vela, não quando o seu fecho já era conhecido.
- Nesta amostra as marcas temporais estão em milissegundos. A [documentação oficial](https://github.com/binance/binance-public-data) indica microssegundos nos arquivos spot desde 1 de janeiro de 2025. Ao juntar arquivos, normalizar para UTC e verificar a unidade por ficheiro.

## O que verificámos

O ficheiro tem 31 velas diárias consecutivas, ordenadas e sem duplicados, de 1 a 31 de janeiro de 2024. Cada vela abre às 00:00 UTC e fecha um milissegundo antes do início da seguinte. Em todas as linhas, o mínimo é positivo e não excede a abertura nem o fecho, o máximo não é inferior a esses dois preços e o volume é não negativo. Estes testes verificam consistência interna, não confirmam cada preço contra uma fonte independente.

| Data da vela (UTC) | Fecho (USDT) |
| --- | ---: |
| 01/01/2024 | 44 179,55 |
| 31/01/2024 | 42 580,00 |

O retorno dos 30 dias é 42 580 / 44 179,55 − 1 = −3,62%. São 31 observações inclusivas para medir 30 intervalos. Pela regra experimental, o estado desejado no fim de 31 de janeiro é «em caixa». Não sabemos se isso gera uma ordem sem saber qual era a posição anterior. O cálculo é um sinal, não o resultado de um trade.

## Regra de validação

1. Guardar a origem e o ficheiro bruto. Normalizar os tempos e identificar cada vela pela abertura.
2. Verificar que existe uma vela fechada por dia de calendário UTC, sem duplicados, lacunas ou inconsistências de preços.
3. Se faltar uma vela, tentar recuperá-la na fonte. Não inventar um preço nem tratar «30 linhas atrás» como «30 dias atrás» sem confirmar o calendário. Se a janela não puder ser validada, marcar o sinal como indisponível.
4. Calcular o sinal só depois do fecho. O backtest não pode preencher a ordem ao fecho que acabou de usar como se ainda pudesse negociar a esse preço. Uma abertura seguinte pode servir de aproximação explícita, não de execução garantida.

## Exercício

Imagina que falta a vela de 15 de janeiro. Com os dois fechos da tabela ainda consegues calcular o retorno dos 30 dias? E podes usar essa janela como se a série estivesse completa? Se tivesses uma posição aberta no fecho de dia 31, em que momento o simulador poderia considerar a saída?

## Decisões a conservar

A primeira hipótese usa momentum de 30 dias em BTC spot. Se for positivo, o estado desejado é «comprado», caso contrário é «em caixa». A simulação não usa shorts, alavancagem nem capital real. Mantemos a regra fixa antes do teste final. Na aula 06 vamos escrever o protocolo de teste, incluindo referência, custos e separação temporal. Janeiro de 2024 é uma amostra didática já vista, não um teste final reservado.
