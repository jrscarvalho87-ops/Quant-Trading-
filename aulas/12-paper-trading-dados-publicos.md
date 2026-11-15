# Aula 12 — Primeiro ciclo com dados públicos

A ligação lê 31 velas BTCUSDT spot diárias já fechadas em UTC e calcula o mesmo sinal de momentum. Se o objetivo mudar a posição, só pode haver execução fictícia nos primeiros 120 segundos após o fecho. A compra usa o ask disponível e a venda usa o bid, com custo residual ilustrativo de 0,10%. A resposta REST não fornece a idade efetiva da cotação na origem. O limite de cinco segundos refere-se à duração do pedido, não garante frescura nem liquidez.

## Reinício

O SQLite atualiza a carteira e o diário na mesma transação. A data UTC do fecho é a chave única. Se o mesmo fecho já estiver registado, o programa não volta a processá-lo. Se o histórico não estiver completo ou houver erro de rede não gera ordem. Voltando depois de uma interrupção, o programa lê o último fecho disponível e não executa retroativamente decisões de dias perdidos.

## Verificação

- Dados públicos: dois processos separados na mesma base processaram o fecho de 14 de novembro de 2026. Primeiro «sem mudança», depois «já processado». Carteira fictícia inalterada, 1 000 USDT e 0 BTC. Não houve execução com cotação real neste ensaio.
- Eventos fictícios: uma compra foi simulada, o processo reabriu a base e encontrou a posição e uma única entrada no diário. Confirmámos que a repetição do dia não cria outra ordem, que uma intenção expirada não negocia e que histórico incompleto não altera a carteira.

## Executar

```sh
python laboratorios/aula12_paper.py --self-test
python laboratorios/aula12_paper.py --db paper_btc.sqlite3
```

A segunda instrução executa um ciclo e termina. Usar o mesmo ficheiro SQLite nas execuções seguintes. Ainda não existe serviço contínuo nem ligação a uma conta. O próximo marco operacional é agendar ciclos junto ao fecho UTC, acompanhar falhas e comparar cotações simuladas com referências. Isso não altera a conclusão da aula 10 sobre rentabilidade.

[Documentação da API pública de mercado da Binance](https://github.com/binance/binance-spot-api-docs/blob/master/faqs/market_data_only.md).
