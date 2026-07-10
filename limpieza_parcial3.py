"""
LIMPIEZA Y HOMOLOGACIÓN DE DATOS — EXAMEN PARCIAL 3 TIA
Equipo: CruzAzul | Anexo A (seudónimo de 8 letras = PAR)

Fuentes:
  - Semilla:   Anexo A del examen (50 registros, n=50, X=Registros_X miles, Y=Costo_Y miles USD)
  - Externa:   breached_services_info.csv — Have I Been Pwned (HIBP)
               https://haveibeenpwned.com/API/v3#AllBreaches
               Usado para PwnCount real (registros comprometidos) de 50 brechas verificadas

Metodología de construcción de Costo_Y en los externos:
  El costo financiero real de brechas grandes (IBM Cost of a Data Breach Report 2024)
  opera en una escala completamente distinta a la semilla (millones vs miles de USD),
  porque IBM estudia brechas corporativas grandes con costos fijos elevados (forense,
  legal, notificación regulatoria) que no aplican al mismo ritmo en incidentes pequeños.

  Se calibra el costo por registro usando la PENDIENTE IMPLÍCITA de la semilla misma
  (beta1 = 3.66 miles USD por cada mil registros = $3.66 USD/registro), preservando
  la estructura real de diferenciación por Sector y Vector_Ataque que ya existe en el
  Anexo A (confirmada por regresión de subgrupos, r > 0.99 en las 4 combinaciones).

  Multiplicadores relativos de intercepto (beta0) por grupo, calibrados con los
  patrones observados en la semilla:
    Financiero/Ransomware: beta0 ~ -1.4    Financiero/Malware: beta0 ~ 13.0
    Salud/Ransomware:      beta0 ~ 25.3    Salud/Malware:      beta0 ~ 6.9

  Se añade variación aleatoria (ruido gaussiano, sd calibrado a partir del error
  estándar de la regresión de la semilla) para no generar una línea perfecta.

Librerías utilizadas y justificación de cada una:
  - pandas:  manipulación tabular de los datos (semilla, dataset HIBP,
             filtros, agrupaciones y exportación a CSV). Es el estándar
             de la industria para este tipo de tareas y permite operaciones
             vectorizadas sin loops explícitos, reduciendo errores.
  - numpy:   generación de números aleatorios reproducibles (semilla fija
             np.random.seed(42)) para el muestreo balanceado y el ruido
             gaussiano de Costo_Y; y operaciones numéricas vectorizadas
             (percentiles, medias) más eficientes que Python puro.
  - scipy:   cálculo de la correlación de Pearson y la regresión lineal de
             referencia de la semilla (stats.pearsonr, stats.linregress),
             necesarios para calibrar la fórmula de Costo_Y en la Fase 3.
"""

import pandas as pd
import numpy as np

np.random.seed(42)

# ══════════════════════════════════════════════════════════════
# FASE 1 — SEMILLA ANEXO A
# ══════════════════════════════════════════════════════════════
print("="*60)
print("FASE 1 — Carga de semilla Anexo A")
print("="*60)

anexo_a = pd.DataFrame([
    ("A01","Financiero","Malware",12.4,48.2),("A02","Salud","Ransomware",45.1,165.8),
    ("A03","Salud","Malware",18.2,62.1),("A04","Financiero","Ransomware",35.0,128.4),
    ("A05","Financiero","Malware",15.0,54.8),("A06","Salud","Ransomware",48.5,175.2),
    ("A07","Financiero","Malware",9.8,39.1),("A08","Salud","Malware",22.4,75.6),
    ("A09","Financiero","Ransomware",39.2,144.1),("A10","Salud","Ransomware",41.0,151.2),
    ("A11","Financiero","Malware",14.1,51.5),("A12","Salud","Ransomware",49.6,179.8),
    ("A13","Financiero","Ransomware",33.2,122.5),("A14","Financiero","Malware",11.5,45.3),
    ("A15","Salud","Malware",20.3,69.4),("A16","Financiero","Ransomware",37.8,138.9),
    ("A17","Salud","Ransomware",42.7,158.4),("A18","Financiero","Malware",16.9,60.2),
    ("A19","Salud","Malware",19.8,67.5),("A20","Financiero","Ransomware",31.4,115.8),
    ("A21","Salud","Ransomware",46.0,168.1),("A22","Financiero","Malware",13.5,49.8),
    ("A23","Salud","Malware",24.1,80.9),("A24","Financiero","Ransomware",36.5,133.6),
    ("A25","Salud","Ransomware",43.3,160.2),("A26","Financiero","Malware",10.2,41.5),
    ("A27","Salud","Ransomware",47.8,172.4),("A28","Financiero","Ransomware",38.4,142.9),
    ("A29","Salud","Malware",17.6,60.3),("A30","Financiero","Malware",14.9,53.9),
    ("A31","Salud","Ransomware",42.1,155.6),("A32","Financiero","Ransomware",34.9,126.8),
    ("A33","Salud","Malware",23.5,78.4),("A34","Financiero","Malware",12.8,48.9),
    ("A35","Salud","Ransomware",46.2,168.9),("A36","Financiero","Ransomware",36.8,134.2),
    ("A37","Salud","Malware",21.0,71.2),("A38","Financiero","Malware",15.5,56.1),
    ("A39","Salud","Ransomware",44.1,161.5),("A40","Financiero","Ransomware",32.6,120.1),
    ("A41","Salud","Malware",25.8,85.2),("A42","Financiero","Malware",11.9,46.8),
    ("A43","Salud","Ransomware",49.5,178.6),("A44","Financiero","Ransomware",38.3,141.5),
    ("A45","Salud","Malware",19.2,65.8),("A46","Financiero","Malware",14.4,52.6),
    ("A47","Salud","Ransomware",47.4,171.0),("A48","Financiero","Ransomware",36.8,135.4),
    ("A49","Salud","Malware",22.7,76.5),("A50","Financiero","Malware",10.7,42.9),
], columns=["ID","Sector","Vector_Ataque","Registros_X","Costo_Y"])
anexo_a["Fuente"] = "Semilla (Anexo A)"

print(f"Registros cargados: {len(anexo_a)}")
print(f"Nulos: {anexo_a.isnull().sum().sum()}")

from scipy import stats
r_semilla, p_semilla = stats.pearsonr(anexo_a["Registros_X"], anexo_a["Costo_Y"])
slope, intercept, r_val, p_val, se = stats.linregress(anexo_a["Registros_X"], anexo_a["Costo_Y"])
print(f"\nCorrelación semilla: r={r_semilla:.4f}")
print(f"Regresión semilla: Costo_Y = {intercept:.4f} + {slope:.4f} * Registros_X")
print(f"Error estándar residual (aprox): {se:.4f}")

# ══════════════════════════════════════════════════════════════
# FASE 2 — CARGA DE REGISTROS REALES (HIBP)
# ══════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("FASE 2 — Extracción de Registros_X reales (HIBP)")
print("="*60)

hibp = pd.read_csv("breached_services_info.csv")
print(f"Registros HIBP cargados: {len(hibp)}")

real = hibp[(hibp["IsVerified"]==True) & (hibp["IsFabricated"]==False) & (hibp["IsSpamList"]==False)].copy()
real = real.dropna(subset=["PwnCount"])
real = real[real["PwnCount"] > 0]
print(f"Brechas verificadas, no fabricadas, no spam: {len(real)}")

real["Registros_X"] = (real["PwnCount"] / 1000).round(1)
rango_valido = real[(real["Registros_X"] >= 8) & (real["Registros_X"] <= 55)].copy()
print(f"Brechas con Registros_X en rango comparable a la semilla (8-55 miles): {len(rango_valido)}")

# ══════════════════════════════════════════════════════════════
# FASE 3 — ASIGNACIÓN BALANCEADA DE SECTOR/ATAQUE Y CÁLCULO DE COSTO
# ══════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("FASE 3 — Asignación balanceada y cálculo de Costo_Y")
print("="*60)

# Tomar 50 registros reales de Registros_X, distribuidos aleatoriamente
muestra_x = rango_valido.sample(50, random_state=42).reset_index(drop=True)
print(f"Registros_X reales seleccionados: {len(muestra_x)}")

# Asignar Sector y Vector_Ataque de forma balanceada (mismo patrón que semilla: 26 Fin/24 Sal, 25/25 tipo)
# Diseño balanceado EXACTO para ANOVA de dos vías: 25 registros por celda (100 total)
# La semilla ya trae: Fin/Ransom=12, Fin/Malware=14, Salud/Ransom=13, Salud/Malware=11
# Externos deben completar cada celda hasta 25:
celdas = (["Financiero-Ransomware"]*13 + ["Financiero-Malware"]*11 +
          ["Salud-Ransomware"]*12 + ["Salud-Malware"]*14)
np.random.shuffle(celdas)
muestra_x["Sector"] = [c.split("-")[0] for c in celdas]
muestra_x["Vector_Ataque"] = [c.split("-")[1] for c in celdas]

# Interceptos calibrados por grupo (tomados de la regresión de subgrupos de la semilla)
interceptos = {
    ("Financiero","Ransomware"): -1.393,
    ("Financiero","Malware"):    13.040,
    ("Salud","Ransomware"):      25.264,
    ("Salud","Malware"):          6.893,
}
BETA1 = slope  # 3.6613, pendiente global de la semilla
RUIDO_SD = se * 8  # escalado para variación realista entre incidentes individuales

def calcular_costo(row):
    b0 = interceptos[(row["Sector"], row["Vector_Ataque"])]
    costo_base = b0 + BETA1 * row["Registros_X"]
    ruido = np.random.normal(0, RUIDO_SD)
    return round(max(costo_base + ruido, 5.0), 1)  # costo mínimo 5 mil USD

muestra_x["Costo_Y"] = muestra_x.apply(calcular_costo, axis=1)
externos = muestra_x[["Sector","Vector_Ataque","Registros_X","Costo_Y"]].copy()
externos["Fuente"] = "Externo (HIBP + fórmula calibrada)"

print(f"\nDistribución Sector: {externos['Sector'].value_counts().to_dict()}")
print(f"Distribución Ataque: {externos['Vector_Ataque'].value_counts().to_dict()}")

r_ext, p_ext = stats.pearsonr(externos["Registros_X"], externos["Costo_Y"])
print(f"\nCorrelación en bloque externo construido: r={r_ext:.4f}")

# ══════════════════════════════════════════════════════════════
# FASE 4 — UNIÓN Y VALIDACIÓN FINAL
# ══════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("FASE 4 — Unión, validación final y exportación")
print("="*60)

semilla = anexo_a[["Sector","Vector_Ataque","Registros_X","Costo_Y","Fuente"]].copy()
df_final = pd.concat([semilla, externos], ignore_index=True)

# IDs
ids = []
sc, ec = 0, 0
for _, row in df_final.iterrows():
    if row["Fuente"] == "Semilla (Anexo A)":
        sc += 1; ids.append(f"A{sc:02d}")
    else:
        ec += 1; ids.append(f"E{ec:02d}")
df_final.insert(0, "ID", ids)

print(f"Total registros: {len(df_final)}")
print(f"Nulos: {df_final.isnull().sum().sum()}")
print(f"\nDistribución Sector:\n{df_final['Sector'].value_counts().to_string()}")
print(f"\nDistribución Vector_Ataque:\n{df_final['Vector_Ataque'].value_counts().to_string()}")
print(f"\nCeldas ANOVA (Sector x Ataque):")
print(df_final.groupby(["Sector","Vector_Ataque"]).size())

r_final, p_final = stats.pearsonr(df_final["Registros_X"], df_final["Costo_Y"])
slope_f, int_f, r2_f, p2_f, se_f = stats.linregress(df_final["Registros_X"], df_final["Costo_Y"])
print(f"\nCorrelación dataset final (n=100): r={r_final:.4f}, p={p_final:.2e}")
print(f"Regresión final: Costo_Y = {int_f:.4f} + {slope_f:.4f} * Registros_X")
print(f"r² = {r2_f**2:.4f}")

print(f"\nEstadísticas Registros_X:\n{df_final['Registros_X'].describe().round(2).to_string()}")
print(f"\nEstadísticas Costo_Y:\n{df_final['Costo_Y'].describe().round(2).to_string()}")

# Detección de atípicos IQR
print("\nDetección de atípicos (criterio IQR):")
for col in ["Registros_X","Costo_Y"]:
    q1 = df_final[col].quantile(0.25)
    q3 = df_final[col].quantile(0.75)
    iqr = q3-q1
    lower, upper = q1-1.5*iqr, q3+1.5*iqr
    n_out = ((df_final[col]<lower)|(df_final[col]>upper)).sum()
    print(f"  {col}: Q1={q1:.2f}, Q3={q3:.2f}, límite sup={upper:.2f} → {n_out} atípicos")

df_final.to_csv("dataset_parcial3_100.csv", index=False)
print(f"\nArchivo exportado: dataset_parcial3_100.csv ({len(df_final)} registros)")
