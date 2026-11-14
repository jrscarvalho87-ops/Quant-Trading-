"""Aula 04: diagnóstico de duas séries simuladas e reproduzíveis."""
import warnings
import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import acf, pacf, adfuller, kpss

SEED = 42
N = 2000
PHI = 0.65

def generate_data():
    rng = np.random.default_rng(SEED)
    white_noise = rng.normal(0, 1, N)
    errors = rng.normal(0, 1, N)
    ar1 = np.zeros(N)
    for t in range(1, N):
        ar1[t] = PHI * ar1[t - 1] + errors[t]
    index = pd.date_range("2020-01-01", periods=N, freq="D")
    return pd.DataFrame({"white_noise": white_noise, "ar1": ar1}, index=index)

def diagnose(series):
    x = series.dropna().astype(float)
    if len(x) < 50 or not np.isfinite(x).all() or x.std() == 0:
        raise ValueError("Série inválida ou insuficiente para o diagnóstico.")
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        adf = adfuller(x, regression="c", autolag="AIC")
        kpss_result = kpss(x, regression="c", nlags="auto")
    return {
        "n": len(x),
        "acf_lag1": float(acf(x, nlags=10, fft=True)[1]),
        "pacf_lag1": float(pacf(x, nlags=10, method="ywm")[1]),
        "adf_stat": float(adf[0]),
        "adf_pvalue": float(adf[1]),
        "kpss_stat": float(kpss_result[0]),
        "kpss_pvalue": float(kpss_result[1]),
        "warnings": [str(w.message) for w in caught],
    }

if __name__ == "__main__":
    df = generate_data()
    for name in df.columns:
        print(f"\n{name}")
        for key, value in diagnose(df[name]).items():
            print(f"  {key}: {value}")
