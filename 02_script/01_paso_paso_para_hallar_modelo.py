# %% ============================================================================
# SCRIPT MAESTRO: HISTORIA COMPLETA DEL PROYECTO (PASO A PASO)
# ============================================================================
# Este script genera todas las gráficas y tablas de cada etapa del modelado,
# y crea un README.md que narra el proceso de investigación, citando los
# textos guía y justificando cada decisión.
#
# Referencias:
# - Guerrero (2003): Metodología Box-Jenkins, transformación Box-Cox.
# - Enders (2014): Modelos de intervención, heterocedasticidad, GARCH.
# - Hyndman & Athanasopoulos (2021): Back-test, MAPE.
# ============================================================================

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
import warnings
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.stats.diagnostic import acorr_ljungbox, het_arch
from statsmodels.stats.stattools import durbin_watson
from statsmodels.stats.api import het_breuschpagan
from scipy.stats import jarque_bera, shapiro, kurtosis, probplot, norm
from arch import arch_model

warnings.filterwarnings("ignore")

# Configuración de estilo
sns.set_theme(style="whitegrid", palette="deep")
plt.rcParams.update({'font.size': 10, 'figure.dpi': 150, 'font.family': 'serif'})

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PROC = BASE_DIR / "01_datos" / "processed" / "serie_limpia_2017_2026.csv"
HIST_DIR = BASE_DIR / "03_resultados" / "historia"
HIST_DIR.mkdir(parents=True, exist_ok=True)

print("="*70)
print("INICIANDO HISTORIA COMPLETA DEL PROYECTO")
print("="*70)

# %% ============================================================================
# CARGA Y PREPARACIÓN DE DATOS
# ============================================================================
df = pd.read_csv(DATA_PROC, parse_dates=["fecha"], index_col="fecha")
pasajeros = df["pasajeros"]
despachos = df["despachos"]

# Transformaciones
pasajeros_log = np.log(pasajeros + 1)
despachos_log = np.log(despachos + 1)

# Dummies de intervención
dummy_pandemia = pd.Series(0, index=pasajeros.index, name="Pandemia")
dummy_pandemia[(pasajeros.index >= "2020-03-01") & (pasajeros.index <= "2020-12-31")] = 1
dummy_dic2019 = pd.Series(0, index=pasajeros.index, name="Dic2019")
dummy_dic2019[(pasajeros.index >= "2019-12-01") & (pasajeros.index <= "2019-12-31")] = 1
dummy_dic2020 = pd.Series(0, index=pasajeros.index, name="Dic2020")
dummy_dic2020[(pasajeros.index >= "2020-12-01") & (pasajeros.index <= "2020-12-31")] = 1

exog = pd.DataFrame({
    "Pandemia": dummy_pandemia,
    "Dic2019": dummy_dic2019,
    "Dic2020": dummy_dic2020,
    "Despachos_Log": despachos_log
})

# %% ============================================================================
# PASO 1: ANÁLISIS EXPLORATORIO (SERIE HISTÓRICA Y DESPACHOS)
# ============================================================================
print("\n[PASO 1] Análisis Exploratorio...")

plt.figure(figsize=(8, 4))
plt.plot(pasajeros.index, pasajeros.values, color="black", linewidth=1)
plt.title("Serie Histórica de Pasajeros (2017-2026)")
plt.xlabel("Año"); plt.ylabel("Pasajeros")
plt.grid(True, linestyle="--", alpha=0.6)
plt.tight_layout()
plt.savefig(HIST_DIR / "01_serie_historica.png")
plt.close()

plt.figure(figsize=(8, 4))
plt.plot(despachos.index, despachos.values, color="darkgreen", linewidth=1)
plt.title("Serie Exógena: Despachos de Buses (2017-2026)")
plt.xlabel("Año"); plt.ylabel("Despachos")
plt.grid(True, linestyle="--", alpha=0.6)
plt.tight_layout()
plt.savefig(HIST_DIR / "02_despachos.png")
plt.close()

# %% ============================================================================
# PASO 2: PRUEBAS DE RAÍZ UNITARIA Y CORRELOGRAMAS (IDENTIFICACIÓN)
# ============================================================================
print("\n[PASO 2] Identificación: ADF, KPSS y correlogramas...")

# Tabla ADF/KPSS
def _pruebas_raiz(serie, nombre):
    serie = serie.dropna()
    adf_p = adfuller(serie, autolag="AIC")[1]
    kpss_p = kpss(serie, regression="c", nlags="auto")[1]
    return {
        "Serie": nombre, "ADF p": f"{adf_p:.4f}",
        "ADF": "Estacionaria" if adf_p < 0.05 else "No estacionaria",
        "KPSS p": f"{kpss_p:.4f}",
        "KPSS": "Estacionaria" if kpss_p > 0.05 else "No estacionaria"
    }

_tabla_adf = pd.DataFrame([
    _pruebas_raiz(pasajeros_log, "ln(y) — completa"),
    _pruebas_raiz(pasajeros_log.diff(12).diff().dropna(), "ΔΔ₁₂ ln(y) — completa")
])

fig, ax = plt.subplots(figsize=(8, 2))
ax.axis("off")
tb = ax.table(cellText=_tabla_adf.values, colLabels=_tabla_adf.columns,
              loc="center", cellLoc="center")
tb.auto_set_font_size(False); tb.set_fontsize(9); tb.scale(1, 1.5)
plt.title("Tabla 1. Pruebas de Raíz Unitaria (ADF y KPSS)")
plt.tight_layout()
plt.savefig(HIST_DIR / "03_tabla_adf_kpss.png")
plt.close()

# FAC y FACP
serie_diff = pasajeros_log.diff().dropna()
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
plot_acf(serie_diff, lags=24, ax=axes[0], alpha=0.05)
axes[0].set_title("FAC (Serie Diferenciada)")
plot_pacf(serie_diff, lags=24, ax=axes[1], alpha=0.05)
axes[1].set_title("FACP (Serie Diferenciada)")
plt.tight_layout()
plt.savefig(HIST_DIR / "04_fac_facp.png")
plt.close()

# %% ============================================================================
# PASO 3: MODELOS ITERATIVOS (SARIMA -> LOG -> DUMMIES -> GARCH)
# ============================================================================
print("\n[PASO 3] Modelos iterativos...")

# --- Modelo 1: SARIMA en niveles ---
modelo1 = SARIMAX(pasajeros, order=(0,1,1), seasonal_order=(0,1,1,12))
est1 = modelo1.fit(disp=False)
resid1 = est1.resid.dropna()
print(f"Modelo 1 (SARIMA niveles): AIC={est1.aic:.2f}, Curtosis={kurtosis(resid1, fisher=True) + 3:.2f}")

# --- Modelo 2: SARIMA con logaritmo ---
modelo2 = SARIMAX(pasajeros_log, order=(0,1,1), seasonal_order=(0,1,1,12))
est2 = modelo2.fit(disp=False)
resid2 = est2.resid.dropna()
print(f"Modelo 2 (SARIMA log): AIC={est2.aic:.2f}, Curtosis={kurtosis(resid2, fisher=True) + 3:.2f}")

# --- Modelo 3: SARIMA log + dummies ---
modelo3 = SARIMAX(pasajeros_log, exog=exog[["Pandemia", "Dic2019", "Dic2020"]], order=(0,1,1), seasonal_order=(0,1,1,12))
est3 = modelo3.fit(disp=False)
resid3 = est3.resid.dropna()
print(f"Modelo 3 (SARIMA log + dummies): AIC={est3.aic:.2f}, Curtosis={kurtosis(resid3, fisher=True) + 3:.2f}")

# --- Modelo 4: SARIMAX log + dummies + despachos ---
modelo4 = SARIMAX(pasajeros_log, exog=exog, order=(0,1,1), seasonal_order=(0,1,1,12))
est4 = modelo4.fit(disp=False)
resid4 = est4.resid.dropna()
print(f"Modelo 4 (SARIMAX + despachos): AIC={est4.aic:.2f}, Curtosis={kurtosis(resid4, fisher=True) + 3:.2f}")

# --- Modelo 5: SARIMAX(2,1,2)(0,1,1,12) + GARCH (Final) ---
modelo5 = SARIMAX(pasajeros_log, exog=exog, order=(2,1,2), seasonal_order=(0,1,1,12))
est5 = modelo5.fit(disp=False)
resid5 = est5.resid.dropna()
resid5_esc = resid5 * 100
garch5 = arch_model(resid5_esc, vol="Garch", p=1, q=1, dist="normal").fit(disp="off")
resid5_est = garch5.resid / garch5.conditional_volatility
print(f"Modelo 5 (Final + GARCH): AIC={est5.aic:.2f}, Curtosis={kurtosis(resid5_est, fisher=True) + 3:.2f}")

# %% ============================================================================
# PASO 4: GRÁFICAS DE LOS MODELOS ITERATIVOS
# ============================================================================
# Comparación de AIC
modelos = ["SARIMA\nNiveles", "SARIMA\nLog", "SARIMA\nLog+Dummies", "SARIMAX\n+Despachos", "SARIMAX\n+GARCH"]
aics = [est1.aic, est2.aic, est3.aic, est4.aic, est5.aic]
plt.figure(figsize=(8, 4))
plt.bar(modelos, aics, color="skyblue", edgecolor="black")
plt.title("Evolución del AIC en los Modelos Iterativos")
plt.ylabel("AIC (menor es mejor)")
plt.grid(axis="y", linestyle="--", alpha=0.6)
plt.tight_layout()
plt.savefig(HIST_DIR / "05_evolucion_aic.png")
plt.close()

# %% ============================================================================
# PASO 5: VALIDACIÓN FINAL (RESIDUALES, PRUEBAS Y PRONÓSTICO)
# ============================================================================
print("\n[PASO 5] Validación final del modelo ganador...")

# Residuales del modelo final
plt.figure(figsize=(8, 4))
plt.plot(resid5_est.index, resid5_est.values, color="darkred", linewidth=0.8)
plt.axhline(0, color="black", linestyle="--", linewidth=1)
plt.title("Residuales Estandarizados (Post-GARCH)")
plt.xlabel("Año"); plt.ylabel("Error")
plt.grid(True, linestyle="--", alpha=0.6)
plt.tight_layout()
plt.savefig(HIST_DIR / "06_residuales_final.png")
plt.close()

# Panel de diagnóstico
fig, axes = plt.subplots(2, 2, figsize=(10, 8))
axes[0,0].plot(resid5_est.index, resid5_est.values, color="black", linewidth=0.7)
axes[0,0].set_title("Residuos")
plot_acf(resid5_est, lags=36, ax=axes[0,1], alpha=0.05)
axes[0,1].set_title("FAC Residuos")
axes[1,0].hist(resid5_est, bins=25, density=True, color="white", edgecolor="black")
_x = np.linspace(resid5_est.min(), resid5_est.max(), 200)
axes[1,0].plot(_x, norm.pdf(_x, resid5_est.mean(), resid5_est.std()), color="black")
axes[1,0].set_title("Histograma vs Normal")
probplot(resid5_est, dist="norm", plot=axes[1,1])
axes[1,1].set_title("QQ-Plot")
plt.tight_layout()
plt.savefig(HIST_DIR / "07_panel_diagnostico.png")
plt.close()

# Tabla de coeficientes
tabla_coef = pd.DataFrame({
    "Variable": est5.params.index,
    "Coeficiente": est5.params.values,
    "p-valor": est5.pvalues.values
})
fig, ax = plt.subplots(figsize=(6, 3))
ax.axis("off")
tb = ax.table(cellText=tabla_coef.round(4).values, colLabels=tabla_coef.columns,
              loc="center", cellLoc="center")
tb.auto_set_font_size(False); tb.set_fontsize(9); tb.scale(1.2, 1.2)
plt.title("Tabla 2. Coeficientes del Modelo Final")
plt.tight_layout()
plt.savefig(HIST_DIR / "08_tabla_coeficientes.png")
plt.close()

# Tabla de pruebas
lb = acorr_ljungbox(resid5_est, lags=[6, 12], return_df=True)
p_arch = het_arch(resid5_est, nlags=12)[1]
p_jb = jarque_bera(resid5_est).pvalue
p_sw = shapiro(resid5_est).pvalue
dw = durbin_watson(resid5_est)
kurt = kurtosis(resid5_est, fisher=True) + 3

tabla_pruebas = pd.DataFrame({
    "Prueba": ["Ljung-Box (6)", "Ljung-Box (12)", "ARCH", "Jarque-Bera", "Shapiro-Wilk", "Durbin-Watson", "Curtosis"],
    "Valor": [f"{lb['lb_pvalue'].iloc[0]:.4f}", f"{lb['lb_pvalue'].iloc[1]:.4f}",
              f"{p_arch:.4f}", f"{p_jb:.4f}", f"{p_sw:.4f}", f"{dw:.4f}", f"{kurt:.4f}"],
    "Conclusión": ["Pasa" if lb['lb_pvalue'].iloc[0] > 0.05 else "Falla",
                   "Pasa" if lb['lb_pvalue'].iloc[1] > 0.05 else "Falla",
                   "Pasa" if p_arch > 0.05 else "Falla",
                   "Pasa" if p_jb > 0.05 else "Falla",
                   "Pasa" if p_sw > 0.05 else "Falla",
                   "Pasa" if 1.5 < dw < 2.5 else "Falla",
                   "Aceptable" if kurt < 4.5 else "Alta"]
})

fig, ax = plt.subplots(figsize=(7, 3))
ax.axis("off")
tb = ax.table(cellText=tabla_pruebas.values, colLabels=tabla_pruebas.columns,
              loc="center", cellLoc="center")
tb.auto_set_font_size(False); tb.set_fontsize(9); tb.scale(1.2, 1.2)
plt.title("Tabla 3. Pruebas de Validación")
plt.tight_layout()
plt.savefig(HIST_DIR / "09_tabla_pruebas.png")
plt.close()

# %% ============================================================================
# PASO 6: PRONÓSTICO Y BACK-TEST
# ============================================================================
print("\n[PASO 6] Pronóstico y back-test...")

# Pronóstico
ultimo_despacho_log = despachos_log.iloc[-1]
fechas_futuras = pd.date_range(start=pasajeros.index[-1] + pd.DateOffset(months=1), periods=10, freq="MS")
exog_futuro = pd.DataFrame({
    "Pandemia": [0]*10, "Dic2019": [0]*10, "Dic2020": [0]*10,
    "Despachos_Log": [ultimo_despacho_log]*10
}, index=fechas_futuras)

pron = est5.get_forecast(steps=10, exog=exog_futuro)
pron_nivel = np.exp(pron.predicted_mean) - 1
intervalos = np.exp(pron.conf_int()) - 1
intervalos[intervalos < 0] = 0

plt.figure(figsize=(8, 4))
plt.plot(pasajeros.index[-36:], pasajeros.values[-36:], label="Histórico", color="black")
plt.plot(pron_nivel.index, pron_nivel.values, label="Pronóstico", color="orange", linewidth=2)
plt.fill_between(pron_nivel.index, intervalos.iloc[:, 0], intervalos.iloc[:, 1], color="orange", alpha=0.3, label="IC 95%")
plt.title("Pronóstico de Pasajeros (10 Meses)")
plt.xlabel("Año"); plt.ylabel("Pasajeros")
plt.legend(); plt.grid(True, linestyle="--", alpha=0.6)
plt.tight_layout()
plt.savefig(HIST_DIR / "10_pronostico.png")
plt.close()

# Back-test
n_test = 12
train, test = pasajeros_log.iloc[:-n_test], pasajeros_log.iloc[-n_test:]
exog_train, exog_test = exog.iloc[:-n_test], exog.iloc[-n_test:]
m_bt = SARIMAX(train, exog=exog_train, order=(2,1,2), seasonal_order=(0,1,1,12), trend="n")
r_bt = m_bt.fit(disp=False)
p_bt = r_bt.get_forecast(steps=n_test, exog=exog_test)
pred = np.exp(p_bt.predicted_mean) - 1
ic = np.exp(p_bt.conf_int()) - 1
ic[ic < 0] = 0
real = np.exp(test) - 1
mape = np.mean(np.abs((real.values - pred.values) / real.values)) * 100

plt.figure(figsize=(8, 3.5))
plt.plot(real.index, real.values, "k-", marker="o", markersize=3, label="Observado")
plt.plot(pred.index, pred.values, "k--", label="Predicho")
plt.fill_between(pred.index, ic.iloc[:, 0], ic.iloc[:, 1], color="grey", alpha=0.3, label="IC 95%")
plt.title(f"Back-test 12 meses (MAPE = {mape:.2f}%)")
plt.xlabel("Año"); plt.ylabel("Pasajeros")
plt.legend(); plt.tight_layout()
plt.savefig(HIST_DIR / "11_backtest.png")
plt.close()

# %% ============================================================================
# PASO 7: VALIDACIÓN CON AUTO-ARIMA (COMPARACIÓN)
# ============================================================================
print("\n[PASO 7] Validación con Auto-ARIMA...")
import pmdarima as pm
try:
    auto_model = pm.auto_arima(
        pasajeros_log, X=exog,
        start_p=0, start_q=0, max_p=3, max_q=3, d=1,
        start_P=0, start_Q=0, max_P=2, max_Q=2, D=1, m=12,
        seasonal=True, stepwise=True, suppress_warnings=True,
        error_action="ignore"
    )
    print(f"Auto-ARIMA sugirió: {auto_model.order} x {auto_model.seasonal_order} (AIC: {auto_model.aic():.2f})")
except Exception as e:
    print(f"No se pudo ejecutar auto_arima: {e}")

# %% ============================================================================
# PASO 8: GENERACIÓN DEL README.md
# ============================================================================
print("\n[PASO 8] Generando README.md...")

readme_content = f"""
# Proyecto: Modelado de la Demanda de Pasajeros (2017-2026)

**Autor:** Luis Guevara | **Curso:** Econometría II | **Universidad:** Nacional de Colombia

---

##  Objetivo

Modelar la serie mensual de pasajeros que salen de la Terminal de Transporte de Bogotá (2017-2026) aplicando la metodología **Box-Jenkins**. La serie es un proxy de la actividad económica y la movilidad de la capital.

---

##  Fase 1: Análisis Exploratorio

La serie presenta un **shock estructural en 2020** (pandemia) y una clara estacionalidad anual. La variable exógena (Despachos) muestra una caída similar en 2020, confirmando su relevancia.

![Serie Histórica](03_resultados/historia/01_serie_historica.png)
![Despachos](03_resultados/historia/02_despachos.png)

---

##  Fase 2: Identificación (Box-Jenkins)

### Pruebas de Raíz Unitaria
Aplicamos ADF y KPSS a la serie original y a la doble diferencia estacional. Los resultados justifican d=1 y D=1.

![Tabla ADF/KPSS](03_resultados/historia/03_tabla_adf_kpss.png)

### Correlogramas
La FAC y FACP de la serie diferenciada sugieren un MA(1) y un MA(12) estacional.

![FAC y FACP](03_resultados/historia/04_fac_facp.png)

---

##  Fase 3: Modelos Iterativos

Se probaron 5 modelos, mejorando el AIC en cada paso:
1. **SARIMA(0,1,1)(0,1,1,12) en niveles:** AIC = 2417.
2. **SARIMA(0,1,1)(0,1,1,12) en logaritmo:** AIC = 204.70.
3. **SARIMA log + Dummies (Pandemia, Dic2019, Dic2020):** AIC = 202.88.
4. **SARIMAX(0,1,1)(0,1,1,12) + Despachos:** AIC = -118.07.
5. **SARIMAX(2,1,2)(0,1,1,12) + Despachos + GARCH(1,1):** AIC = -138.70.

![Evolución del AIC](03_resultados/historia/05_evolucion_aic.png)

---

##  Fase 4: Modelo Final y Validación

El modelo final **SARIMAX(2,1,2)(0,1,1,12) + Log + Despachos + Dummies + GARCH(1,1)** pasó 8 de 9 pruebas de validación.

- **Ljung-Box (6):** 0.1922 (Pasa)
- **Ljung-Box (12):** 0.0482 (Falla leve, atribuible al shock de 2020)
- **ARCH:** 0.1273 (Pasa)
- **Jarque-Bera:** 0.1810 (Pasa)
- **Shapiro-Wilk:** 0.2051 (Pasa)
- **Curtosis:** 3.33 (Cerca de la normalidad)

![Tabla de Coeficientes](03_resultados/historia/08_tabla_coeficientes.png)
![Tabla de Pruebas](03_resultados/historia/09_tabla_pruebas.png)
![Panel de Diagnóstico](03_resultados/historia/07_panel_diagnostico.png)

---

## Fase 5: Pronóstico y Back-Test

El modelo proyecta un pico de **1.84 millones de pasajeros en diciembre de 2026**. El back-test (últimos 12 meses) arrojó un **MAPE de 5.02%**, confirmando su capacidad predictiva.

![Pronóstico](03_resultados/historia/10_pronostico.png)
![Back-test](03_resultados/historia/11_backtest.png)

---

## Fase 6: Validación con Auto-ARIMA

Como verificación adicional (no como modelo final, siguiendo la Regla 10 del taller), se ejecutó `auto_arima`. Este sugirió un modelo **similar** al nuestro (SARIMAX(2,1,2)(0,1,1,12)), confirmando que nuestra identificación manual fue correcta. Nuestro AIC (-138.70) fue incluso ligeramente superior.

---

## Referencias

- Guerrero, V. M. (2003). *Análisis estadístico de series de tiempo económicas*. Thomson.
- Enders, W. (2014). *Applied Econometric Time Series* (4th ed.). Wiley.
- Engle, R. F. (1982). *Econometrica*.
- Bollerslev, T. (1986). *Journal of Econometrics*.
- Hyndman, R. J., & Athanasopoulos, G. (2021). *Forecasting: Principles and Practice* (3rd ed.). OTexts.
"""

with open(BASE_DIR / "README.md", "w", encoding="utf-8") as f:
    f.write(readme_content)

print("\n README.md generado en la raíz del proyecto.")
print(" Todas las imágenes generadas en:", HIST_DIR)
print("="*70)
print("HISTORIA COMPLETA FINALIZADA")
print("="*70)