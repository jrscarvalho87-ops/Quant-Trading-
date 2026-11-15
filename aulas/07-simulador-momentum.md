# Aula 07 — O primeiro simulador de momentum

## Objetivo

Transformar o protocolo da aula 06 num motor e confirmar as contas com velas fictícias antes de avaliar o histórico real. Os testes validam os casos que cobrem, não a rentabilidade da estratégia.

## O relógio do simulador

1. Com as 31 velas válidas até ao fecho de ontem, comparar esse fecho com o de 30 dias antes.
2. Na abertura de hoje, aplicar o objetivo apenas se for diferente da posição. Sinal indisponível deixa a posição como está. O fecho de hoje ainda não pode ser usado.
3. No fecho de hoje, valorizar o património como saldo em USDT mais quantidade de BTC multiplicada pelo fecho.

## Caso que calculámos à mão

Com saldo fictício de 100,10 USDT, uma compra a 100 permite adquirir 1 BTC e pagar 0,10 USDT de custo. O fecho desse dia é 100 e gera um sinal de saída. A abertura seguinte é 97 e o fecho posterior é 140. A venda acontece a 97, não a 100 nem a 140. O custo de venda é 0,097 USDT e o saldo final é 96,903 USDT.

A perda face ao fecho de 100 é 3,097%. A perda desde o saldo inicial é aproximadamente 3,194%. A diferença é o custo de compra e a base de comparação.

## Laboratório

Executar na raiz do repositório:

```sh
python laboratorios/aula07_simulador.py
```

O script usa apenas a biblioteca padrão e executa seis testes. Confirma preço e custo da venda, dados históricos em falta, falha na valorização do bloco, duplicados, referência comprar e manter sem venda forçada, e sinal igual a zero. O motor recebe preços diários já normalizados e auditados. Ainda não inclui a importação do histórico nem corre o período reservado.

## Exercício

Se o BTC fechar a 140 no dia em que o simulador vendeu a 97 na abertura, a recuperação entra no património da estratégia? E na referência comprar e manter?
