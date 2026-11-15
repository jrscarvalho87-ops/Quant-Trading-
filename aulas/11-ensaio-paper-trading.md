# Aula 11 — Ensaiar paper trading antes de ligar o mercado

## Objetivo

Trocar a perspetiva do backtest, que já tem a tabela inteira, pela de um sistema que recebe um evento de cada vez. A regra continua a ser momentum de 30 dias, BTCUSDT spot, só comprado ou em caixa. Este laboratório usa mensagens fictícias, não liga a nenhuma conta e não envia ordens reais.

## Do fecho à execução simulada

1. Usar apenas velas diárias UTC fechadas. Na futura integração Binance, o campo k.x indica o fecho. Ignorar uma vela ainda em formação.
2. Validar a janela de 31 velas. O objetivo «comprado» ou «em caixa» só gera intenção se mudar a posição. Se faltar um dia, o sinal está indisponível.
3. A primeira cotação elegível tem de ser recebida depois do sinal. Compra ao ask e vende ao bid. A cotação não pode ter mais de 5 segundos quando usada e a intenção expira 120 segundos após o fecho. São limites pedagógicos, não medições de latência. Receber uma cotação depois do sinal não prova por si só quando foi gerada na origem.
4. Separam-se dois efeitos: o spread já está no bid/ask. O ensaio acrescenta 0,10% de custo residual ilustrativo, não volta a somar o spread como parcela desse custo. Os resultados do backtest, que usava uma abertura e um custo agregado, não são diretamente comparáveis. A simulação não prova liquidez suficiente ao melhor preço.
5. Processar cada fecho uma só vez. Um duplicado idêntico não volta a gerar intenção. Fechos atrasados podem completar o histórico mas não geram ordens tardias. Se a cotação chegar depois do prazo, registar expiração e manter a posição.

## Exemplo

A vela fecha a 101 e dá sinal de compra. Quando recebemos uma cotação elegível, o bid é 101 e o ask 102. A compra simulada usa 102, não o fecho a 101. Na venda testada, o bid é 97 e o ask 98. Vender 1 BTC ao bid com custo residual de 0,10% deixa 96,903 USDT.

## Laboratório

Executar `python laboratorios/aula11_paper_ensaio.py`. O ensaio passou seis testes: vela aberta ignorada, cotação obsoleta e duplicado sem nova ordem, expiração, lacuna, fecho atrasado e venda ao bid. O estado é apenas em memória. Em ligação contínua ainda precisamos de persistência, reconexão, tratamento de falhas e registo durável.

[Documentação Binance dos eventos de velas e do melhor bid/ask](https://github.com/binance/binance-spot-api-docs/blob/master/web-socket-streams.md).

## Exercício

Se chega um sinal válido de compra e só vemos uma cotação utilizável três minutos depois do fecho, o simulador compra ou fica em caixa? Se amanhã o sinal continuar positivo, pode avaliá-lo novamente?
