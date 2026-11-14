# Aula 04 — Econometria aplicada com Python

## Objetivo
Construir um pipeline reproduzível para diagnosticar séries temporais: dados → validação → ACF/PACF → ADF/KPSS → relatório.

## Fundamentos
- Ruído branco: média e variância constantes, autocovariâncias nulas nos lags não zero.
- AR(1): r_t = φ r_(t-1) + ε_t. Para |φ|<1, ACF teórica ρ(k)=φ^k.
- ADF: H0 de raiz unitária; KPSS: H0 de estacionariedade de nível (regression="c").
- Rejeitar ou não rejeitar uma hipótese não constitui prova absoluta; resultados dependem da especificação, amostra e quebras estruturais.

## Laboratório
Executar `python laboratorios/aula04_diagnostico.py` após instalar dependências de `requirements.txt`.

O laboratório usa séries simuladas e uma semente fixa. Não é um backtest nem uma demonstração de rentabilidade.

## Interpretação
- Ruído branco: ACF e PACF estimadas próximas de zero fora do lag 0.
- AR(1) com φ=0,65: ACF lag 1 próxima de 0,65 e decaimento geométrico.
- Ambas as séries são estacionárias por construção (desprezando o curto transiente inicial no AR(1)).
- ADF e KPSS testam hipóteses distintas; não medem diretamente capacidade preditiva ou lucro.

## Próximo passo
Aplicar o pipeline a preços históricos reais, documentando fonte, fuso horário, frequência, ajustamentos, lacunas e qualidade dos dados.

## Fontes
- https://www.statsmodels.org/stable/examples/notebooks/generated/stationarity_detrending_adf_kpss.html
- https://www.statsmodels.org/stable/generated/statsmodels.tsa.stattools.acf.html
- https://www.statsmodels.org/stable/generated/statsmodels.tsa.stattools.pacf.html
- https://www.statsmodels.org/stable/generated/statsmodels.tsa.stattools.adfuller.html
- https://www.statsmodels.org/stable/generated/statsmodels.tsa.stattools.kpss.html
