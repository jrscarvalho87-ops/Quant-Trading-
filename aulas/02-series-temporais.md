# Aula 02 — Séries temporais financeiras

**Área:** Econometria · **Nível:** intermédio

## Objetivos
Compreender estacionariedade fraca, autocorrelação, ruído branco e as famílias AR, MA, ARMA e ARIMA.

## 1. Estacionariedade fraca
Uma série `r_t` é fracamente estacionária quando:
- `E[r_t] = μ` é constante;
- `Var(r_t) = σ² < ∞` é constante;
- `Cov(r_t, r_(t-k)) = γ(k)` depende apenas do lag `k`.

Os preços financeiros podem ser não estacionários. Os retornos são muitas vezes mais próximos da estacionariedade, mas podem apresentar heteroscedasticidade e mudanças de regime.

## 2. Autocorrelação
`ρ(k) = γ(k)/γ(0)` mede a dependência linear entre observações separadas por `k` períodos. A função ACF descreve a autocorrelação ao longo de diferentes lags.

Para o AR(1) estacionário `r_t = c + φ r_(t-1) + ε_t`, com `|φ|<1`, a ACF teórica é `ρ(k) = φ^k`.

- `φ>0`: dependência positiva decrescente.
- `φ<0`: alternância de sinal.
- `φ=0`: ausência de autocorrelação linear entre retornos neste modelo.

## 3. Ruído branco
Ruído branco fraco tem média zero, variância constante e covariância zero para lags não nulos. Não exige independência total: dependências não lineares podem persistir.

## 4. Famílias de modelos
- **AR(p):** regressão sobre valores passados.
- **MA(q):** combinação de inovações atuais e passadas.
- **ARMA(p,q):** combinação de AR e MA.
- **ARIMA(p,d,q):** modelo ARMA aplicado após `d` diferenças adequadas.

## 5. Exercícios de compreensão
1. Uma série com média constante mas variância crescente é fracamente estacionária?
2. Se `φ=-0,6` num AR(1), qual é a autocorrelação teórica no lag 2?
3. Porque é que autocorrelação zero não implica independência?
4. Qual é o risco de dividir aleatoriamente observações de uma série temporal entre treino e teste?

### Respostas
1. Não.
2. `(-0,6)^2 = 0,36`.
3. Porque podem existir relações não lineares sem covariância linear.
4. Pode introduzir fuga de informação temporal e criar uma avaliação irrealista.

## Referências
- NIST, definição de estacionariedade e autocorrelação: https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=50809
- Statsmodels, ACF: https://www.statsmodels.org/stable/generated/statsmodels.tsa.stattools.acf.html
- Statsmodels, ARIMA: https://www.statsmodels.org/stable/generated/statsmodels.tsa.arima.model.ARIMA.html
- Statsmodels, tutorial ARIMA e validação temporal: https://www.statsmodels.org/stable/examples/notebooks/generated/autoregressive_integrated_moving_average.html

Material original de estudo. Exemplos teóricos, sem resultados de mercado real.
