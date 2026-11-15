# Aula 06 — O protocolo do primeiro backtest

## Pergunta

Queremos saber se o momento escolhido para estar exposto a BTC acrescenta valor após custos. O primeiro teste usa BTCUSDT spot diário em UTC. Sem shorts, alavancagem ou capital real. Esta versão fixa o protocolo antes de vermos o desempenho, não apresenta resultados.

## Calendário da experiência

| Bloco | Datas UTC | Utilização |
| --- | --- | --- |
| Desenvolvimento | 01/01/2021 a 31/12/2024 | Verificar dados e testar manualmente o motor. Janeiro de 2024, usado na aula 05, pertence aqui. |
| Teste final histórico | 01/01/2025 a 31/10/2026 | Executar a regra congelada, sem escolher parâmetros pelos resultados. |

Os intervalos referem-se aos dias das velas. Obter dados anteriores ao início de cada bloco para preparar a primeira decisão. A simulação de cada bloco começa com o mesmo saldo fictício em USDT para todas as abordagens, sem posição herdada. O período final é reservado no projeto, não é garantia de que os movimentos históricos do BTC nos sejam desconhecidos. Se alterarmos a estratégia em resposta ao resultado, este período deixa de ser uma avaliação independente da nova versão.

## Regras da simulação

1. Depois de fechado o dia t, calcular M(t) = C(t) / C(t−30 dias) − 1. Exigir 31 velas completas e válidas. Se M(t) > 0, o objetivo é estar comprado, caso contrário é estar em USDT. Para a primeira abertura do bloco, usar o sinal do último dia anterior ao bloco, se disponível.
2. Só simular uma ordem se o objetivo diferir da posição. Usar o preço de abertura de t+1 como aproximação de execução, não como fill garantido. Se o objetivo for comprado, aplicar o saldo disponível líquido dos custos. Se for caixa, vender a posição completa.
3. Sinal indisponível não é sinal de saída. Não gerar ordens com sinal inválido e não transportar ordens falhadas para datas posteriores. Registar a falha, tentar recuperar o dado e reavaliar com o próximo sinal válido. Se faltarem preços de valorização ou de execução que impeçam a comparação, reportar o bloco como incompleto e não tratar o resultado como teste válido.
4. Aplicar um custo total hipotético de 10 pontos-base (0,10%) ao valor de cada ordem, quer seja compra quer seja venda. Fazer também os cenários de 5 e 20 pontos-base por ordem. São pressupostos agregados para comissões, spread e slippage, não uma tabela de preços da corretora. Não acrescentar os mesmos custos uma segunda vez.
5. Valorizar as posições ao fecho de cada dia. No fim, avaliar BTC a mercado sem forçar liquidação para nenhuma abordagem. Caixa em USDT sem remuneração simulada.

## Comparação

Comprar e manter BTC desde a primeira abertura do bloco, com o mesmo saldo e custo de compra. Reportar retorno líquido acumulado, drawdown máximo, percentagem de dias em BTC medida no fecho e número de ordens. Se o drawdown baixar, mas a exposição também, não atribuir a melhoria ao sinal sem um controlo adicional de exposição. Na leitura, separar redução de risco de evidência de melhor escolha dos dias. A taxa de acerto é secundária.

## Exercício

Na segunda-feira, o fecho dá momentum positivo e o simulador está em caixa. Na terça-feira, o mercado abre 2% acima do fecho de segunda. Qual é o preço de referência para a compra e a quem pertence essa subida de 2%, ao simulador ou a quem já tinha BTC?

## Fonte de apoio

[Validação cronológica em séries temporais, scikit-learn](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html). Os blocos, parâmetros e pressupostos de custos acima são escolhas pedagógicas do projeto.
