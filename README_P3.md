# Correlación, Regresión y ANOVA en Ciberseguridad
**Equipo CruzAzul — Examen Parcial 3 TIA, Verano 2026**  
Facultad de Ciencias Físico Matemáticas — UANL

---

## Descripción

Scripts de limpieza, homologación y análisis estadístico de 100 incidentes de ciberseguridad (Sectores Financiero y Salud) para responder al Comité de Finanzas y Gestión de Riesgos sobre: correlación entre registros comprometidos y costo de mitigación, capacidad predictiva del modelo de regresión, y efectos factoriales de Sector y Vector de Ataque sobre el costo (ANOVA de dos vías).

---

## Requisitos

**Python 3.8 o superior**

```bash
pip install pandas numpy scipy statsmodels
```

---

## Archivos necesarios

Coloca en la misma carpeta antes de ejecutar:

| Archivo | Descripción | Fuente |
|---|---|---|
| `limpieza_parcial3.py` | Script de limpieza y homologación | Este repositorio |
| `analisis_parcial3.py` | Script de análisis estadístico | Este repositorio |
| `breached_services_info.csv` | Brechas reales verificadas (PwnCount) | [Have I Been Pwned API](https://haveibeenpwned.com/API/v3#AllBreaches) |

---

## Cómo ejecutar

```bash
python3 limpieza_parcial3.py      # Genera dataset_parcial3_100.csv
python3 analisis_parcial3.py      # Corre el análisis estadístico completo
```

---

## Archivos de salida

| Archivo | Descripción |
|---|---|
| `dataset_parcial3_100.csv` | Dataset final de 100 registros (50 semilla + 50 externos) |
| `anova_long_format.txt` | Formato Row/Column/Value para cargar el ANOVA en STATDISK |

---

## Estructura del dataset final

| Columna | Tipo | Descripción |
|---|---|---|
| `ID` | string | A01–A50 (semilla), E01–E50 (externos) |
| `Sector` | string | Financiero, Salud |
| `Vector_Ataque` | string | Ransomware, Malware |
| `Registros_X` | float | Miles de registros comprometidos |
| `Costo_Y` | float | Miles de USD en costo de mitigación |
| `Fuente` | string | Semilla (Anexo A) o Externo (HIBP + fórmula calibrada) |

---

## Metodología de construcción de Costo_Y en los registros externos

**El problema de escala:** los benchmarks reales de costo de brecha (IBM Cost of a Data Breach Report 2024: $150–$408 USD/registro) están calibrados sobre brechas corporativas grandes con costos fijos elevados (forense, legal, notificación regulatoria). Aplicados directamente a la escala de la semilla (10–50 mil registros, $40–180 mil USD), producirían costos de millones de USD — completamente fuera de escala respecto al Anexo A.

**La solución adoptada:**
1. `Registros_X` de los 50 externos proviene de **datos reales**: `PwnCount` de brechas verificadas en HIBP (Have I Been Pwned), filtradas al rango 8–55 mil registros para ser comparables con la semilla.
2. `Costo_Y` se **calcula** (no se observa) aplicando la pendiente implícita de la semilla (β₁ ≈ 3.66 miles USD por cada mil registros), con interceptos diferenciados por combinación Sector × Vector_Ataque, calibrados a partir de los patrones ya presentes en el Anexo A (confirmados por regresión de subgrupos, r > 0.99 en las 4 combinaciones).
3. Se añade ruido aleatorio gaussiano para que los puntos no caigan perfectamente sobre la línea de regresión.

Esta metodología se declara explícitamente como **variable derivada por fórmula documentada**, siguiendo el mismo criterio de transparencia usado en el Parcial 1 con `Dias_Deteccion`.

---

## Fases del script de limpieza

**Fase 1 — Semilla Anexo A:** carga de 50 registros, cálculo de la regresión de referencia (r=0.998, β₁=3.66).

**Fase 2 — Registros reales (HIBP):** carga de `breached_services_info.csv`, filtro a brechas verificadas/no fabricadas/no spam, conversión de `PwnCount` a miles de registros, filtro al rango 8–55 miles.

**Fase 3 — Asignación balanceada y cálculo de costo:** se completan las 4 celdas Sector×Ataque hasta 25 cada una (considerando lo que ya aporta la semilla), y se calcula `Costo_Y` con la fórmula calibrada.

**Fase 4 — Unión y validación:** se combinan semilla y externos, se verifican 0 nulos y se documentan los atípicos (0 en el dataset final). Exporta `dataset_parcial3_100.csv`.

---

## Bloques del análisis estadístico (STATDISK v13 + Python)

### Bloque 1 — Correlación y Regresión
```
Analysis → Correlation and Regression
→ x column: Registros_X | y column: Costo_Y
```
Resultado: r=0.98335, r²=0.96698, ŷ = 3.126 + 3.720·x

### Bloque 2 — Inferencias y predicción
La prueba de significancia de r (dada por STATDISK) equivale a H₀: β₁=0.  
La prueba de H₀: β₀=0 y el intervalo de predicción para X=45 se calculan manualmente con las fórmulas de Triola, usando b₀, b₁ y el error estándar que reporta STATDISK (ver `analisis_parcial3.py` para la verificación cruzada en Python).

Resultado: β₁ significativo (p<0.001); β₀ no significativo (p=0.168); IP 95% para X=45: [151.82, 189.21] miles USD.

### Bloque 3 — ANOVA de dos vías
```
Analysis → Two-Way Analysis of Variance
→ Row categories: 2 | Column categories: 2 | Values per cell: 25
```
Usa el archivo `anova_long_format.txt` para llenar la tabla (Row 1=Financiero, Row 2=Salud, Column 1=Ransomware, Column 2=Malware).

Resultado: interacción no significativa (p=0.447); efecto Sector significativo (p=0.00003); efecto Vector_Ataque significativo (p=0.000004).

---

## Reproducibilidad

Ambos scripts usan `np.random.seed(42)`. Ejecutar múltiples veces con los mismos archivos de entrada produce siempre el mismo `dataset_parcial3_100.csv`.

---

## Fuentes

- Have I Been Pwned. (2024). API v3 — All Breaches. https://haveibeenpwned.com/API/v3#AllBreaches
- IBM Security / Ponemon Institute. (2024). Cost of a Data Breach Report 2024.
- Triola, M. F. (2018). Estadística (13.ª ed.). Pearson Education.
- STATDISK v13. Software estadístico desarrollado por Mario F. Triola.
