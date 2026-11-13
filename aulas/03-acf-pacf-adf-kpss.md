# Aula 03 — ACF, PACF, ADF e KPSS

**Área:** Econometria · **Nível:** intermédio

## ACF e PACF
A ACF mede autocorrelação em cada lag. A PACF mede a associação linear entre a observação atual e a observação de lag k depois de controlar os lags intermédios.

Para AR(1), `r_t = φ r_(t-1) + ε_t`, com `|φ|<1`:
- ACF teórica: `ρ(k)=φ^k`.
- PACF teórica: `PACF(1)=φ`, `PACF(k)=0` para `k>1`.

Padrões clássicos orientadores: AR(p) tem PACF truncada; MA(q) tem ACF truncada; ARMA costuma apresentar caudas nas duas. Estimativas amostrais são ruidosas; validar o modelo.

## ADF (Augmented Dickey-Fuller)
Regressão geral: `Δy_t = α + βt + γ y_(t-1) + Σ δ_i Δy_(t-i) + ε_t`.

Hipótese nula: existe raiz unitária. Rejeitar a nula fornece evidência contra raiz unitária na especificação escolhida, não prova estacionariedade em todos os sentidos.

## KPSS
Hipótese nula: estacionariedade em torno de um nível ou tendência, conforme especificação. É complementar ao ADF.

| ADF | KPSS | Leitura inicial |
|---|---|---|
| Rejeita | Não rejeita | Compatível com estacionariedade |
| Não rejeita | Rejeita | Compatível com não estacionariedade |
| Rejeita | Rejeita | Investigar especificações e quebras |
| Não rejeita | Não rejeita | Inconclusivo |

## Exercícios
1. Num AR(1) com φ=0,7, qual a ACF teórica no lag 3?
2. Porque é que PACF não é igual a ACF?
3. Qual a hipótese nula do ADF?
4. Qual a hipótese nula do KPSS?

**Respostas:** 1) 0,343; 2) controla lags intermédios; 3) raiz unitária; 4) estacionariedade conforme especificação.

## Referências
- https://www.statsmodels.org/stable/generated/statsmodels.tsa.stattools.acf.html
- https://www.statsmodels.org/stable/generated/statsmodels.tsa.stattools.pacf.html
- https://www.statsmodels.org/stable/generated/statsmodels.tsa.stattools.adfuller.html
- https://www.statsmodels.org/stable/generated/statsmodels.tsa.stattools.kpss.html

Texto original, educativo; exemplos teóricos.
