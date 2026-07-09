"""
ANÁLISIS ESTADÍSTICO — EXAMEN PARCIAL 3 TIA
Equipo: CruzAzul | Anexo A

Este script toma el dataset limpio (dataset_parcial3_100.csv, generado por
limpieza_parcial3.py) y calcula de forma independiente en Python los mismos
resultados obtenidos en STATDISK v13, como verificación cruzada:

  Bloque 1 — Correlación de Pearson y regresión lineal simple
  Bloque 2 — Pruebas de hipótesis para beta0 y beta1, e intervalo de
             predicción al 95% para X = 45.0 (miles de registros)
  Bloque 3 — ANOVA de dos vías con replicación (Sector x Vector_Ataque)

Librerías: pandas, numpy, scipy, statsmodels
"""

import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm

# ══════════════════════════════════════════════════════════════
# CARGA DE DATOS
# ══════════════════════════════════════════════════════════════
df = pd.read_csv("dataset_parcial3_100.csv")
X = df["Registros_X"]
Y = df["Costo_Y"]
n = len(df)

print("="*60)
print(f"Dataset cargado: n = {n} registros")
print("="*60)

# ══════════════════════════════════════════════════════════════
# BLOQUE 1 — CORRELACIÓN Y REGRESIÓN LINEAL SIMPLE
# ══════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("BLOQUE 1 — Correlación y Regresión Lineal Simple")
print("="*60)

r, p_corr = stats.pearsonr(X, Y)
print(f"Coeficiente de correlación de Pearson, r = {r:.5f}")
print(f"Valor p (correlación, dos colas) = {p_corr:.6f}")
print(f"Coeficiente de determinación, r² = {r**2:.5f}")

X_sm = sm.add_constant(X)
model = sm.OLS(Y, X_sm).fit()
b0 = model.params["const"]
b1 = model.params["Registros_X"]
se_reg = np.sqrt(model.mse_resid)

print(f"\nEcuación de regresión estimada:")
print(f"  ŷ = {b0:.5f} + {b1:.5f} * Registros_X")
print(f"\nError estándar de la regresión (residual): {se_reg:.5f}")
print(f"r² (statsmodels, verificación): {model.rsquared:.5f}")

# ══════════════════════════════════════════════════════════════
# BLOQUE 2 — PRUEBAS DE HIPÓTESIS DEL MODELO Y PREDICCIÓN
# ══════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("BLOQUE 2 — Inferencias del Modelo e Intervalo de Predicción")
print("="*60)

t_b1 = model.tvalues["Registros_X"]
p_b1 = model.pvalues["Registros_X"]
t_b0 = model.tvalues["const"]
p_b0 = model.pvalues["const"]

print(f"\nPrueba H0: beta1 = 0 vs H1: beta1 != 0")
print(f"  t = {t_b1:.4f}, p = {p_b1:.6f}")
print(f"  Decisión (alfa=0.05): {'Se rechaza H0' if p_b1 < 0.05 else 'No se rechaza H0'}")

print(f"\nPrueba H0: beta0 = 0 vs H1: beta0 != 0")
print(f"  t = {t_b0:.4f}, p = {p_b0:.6f}")
print(f"  Decisión (alfa=0.05): {'Se rechaza H0' if p_b0 < 0.05 else 'No se rechaza H0'}")

# Intervalo de predicción para X=45
x0 = 45.0
pred = model.get_prediction([1, x0])
summ = pred.summary_frame(alpha=0.05)
y_hat = summ["mean"].values[0]
pi_low = summ["obs_ci_lower"].values[0]
pi_high = summ["obs_ci_upper"].values[0]

print(f"\nPredicción para X = {x0} (miles de registros comprometidos):")
print(f"  Valor predicho puntual, ŷ = {y_hat:.2f} miles USD")
print(f"  Intervalo de Predicción 95% (incidente individual):")
print(f"  [{pi_low:.2f}, {pi_high:.2f}] miles USD")
print(f"  Amplitud del IP: {pi_high-pi_low:.2f} miles USD ({(pi_high-pi_low)/y_hat*100:.1f}% del valor predicho)")

# ══════════════════════════════════════════════════════════════
# BLOQUE 3 — ANOVA DE DOS VÍAS CON REPLICACIÓN
# ══════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("BLOQUE 3 — ANOVA de Dos Vías (Sector x Vector_Ataque)")
print("="*60)

print(f"\nTamaño de celdas:")
print(df.groupby(["Sector","Vector_Ataque"]).size().to_string())

print(f"\nMedias de Costo_Y por celda:")
print(df.groupby(["Sector","Vector_Ataque"])["Costo_Y"].mean().round(2).to_string())

model_anova = ols('Costo_Y ~ C(Sector) * C(Vector_Ataque)', data=df).fit()
anova_table = anova_lm(model_anova, typ=2)
print(f"\nTabla ANOVA:")
print(anova_table.to_string())

print(f"\n--- Interpretación de las 3 hipótesis del examen ---")
p_inter = anova_table.loc['C(Sector):C(Vector_Ataque)', 'PR(>F)']
p_sector = anova_table.loc['C(Sector)', 'PR(>F)']
p_ataque = anova_table.loc['C(Vector_Ataque)', 'PR(>F)']

print(f"\nH1 (Interacción Sector x Ataque): p = {p_inter:.6f} -> "
      f"{'Se rechaza H0 (hay interacción)' if p_inter < 0.05 else 'No se rechaza H0 (sin interacción)'}")
print(f"H2 (Efecto principal Sector):      p = {p_sector:.6f} -> "
      f"{'Se rechaza H0 (difieren)' if p_sector < 0.05 else 'No se rechaza H0 (no difieren)'}")
print(f"H3 (Efecto principal Vector):      p = {p_ataque:.6f} -> "
      f"{'Se rechaza H0 (difieren)' if p_ataque < 0.05 else 'No se rechaza H0 (no difieren)'}")

print("\n" + "="*60)
print("FIN DEL ANÁLISIS")
print("="*60)
