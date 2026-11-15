# Aula 08 — Do ficheiro histórico ao simulador

## Objetivo

Ler arquivos da Binance de BTCUSDT spot diário, validar as velas e entregar ao motor da aula 07 os campos de que precisa. Usamos apenas a amostra de desenvolvimento. Não abrimos o teste reservado.

## O laboratório

1. Regista o SHA-256 do ficheiro original para verificar se uma repetição usa os mesmos bytes. A impressão digital, por si só, não prova a origem nem a correção dos preços.
2. Converte as marcas temporais para dias UTC. Os arquivos spot usam microssegundos a partir de janeiro de 2025. Os da amostra de 2024 estão em milissegundos.
3. Verifica o calendário, os limites de cada vela e a coerência de OHLCV. Recusa duplicados e lacunas internas. Um mês inteiro ausente no início ou no fim não aparece como lacuna interna, pelo que é necessário confirmar a cobertura esperada e o histórico de preparação antes de cada backtest.
4. Entrega data, abertura e fecho ao simulador, que já sabe separar o sinal do dia anterior da execução de hoje. Este leitor pressupõe que a origem é mesmo BTCUSDT spot diário da Binance. As linhas não identificam o par.

## Reproduzir

Descarregar [janeiro](https://data.binance.vision/data/spot/monthly/klines/BTCUSDT/1d/BTCUSDT-1d-2024-01.zip) e [fevereiro de 2024](https://data.binance.vision/data/spot/monthly/klines/BTCUSDT/1d/BTCUSDT-1d-2024-02.zip) para a raiz do repositório. Executar:

```sh
python laboratorios/aula08_dados.py BTCUSDT-1d-2024-01.zip BTCUSDT-1d-2024-02.zip --dia 2024-02-01
```

Resultado verificado: 31 velas em janeiro, 29 em fevereiro, 60 dias consecutivos em UTC. Na abertura de 1 de fevereiro, o sinal do fecho de 31 de janeiro é «em caixa». O simulador começa em caixa nesta auditoria de um dia, por isso não gera nenhuma ordem. Isto verifica a integração com o motor, não o desempenho do modelo.

## Exercício

O leitor deteta uma lacuna se eliminarmos 15 de janeiro. Se entregarmos apenas fevereiro, é possível passar na auditoria interna do calendário? E teríamos os dados necessários para reproduzir o sinal na abertura de 1 de fevereiro?

## Fonte

[Documentação dos arquivos públicos da Binance](https://github.com/binance/binance-public-data).
