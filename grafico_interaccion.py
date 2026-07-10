"""
GRÁFICO DE INTERACCIÓN — EXAMEN PARCIAL 3 TIA
Equipo: CruzAzul | Anexo A

Genera el gráfico de líneas de medias (interaction plot) para visualizar
el efecto de interacción entre Sector y Vector_Ataque sobre Costo_Y,
evaluado formalmente en el ANOVA de dos vías (Bloque 3, Hipótesis 1).

Nota: STATDISK v13 no incluye una herramienta de gráfico de interacción
entre su catálogo de gráficos (Histogram, Boxplot, Normal Quantile Plot,
Scatterplot, Run Chart), por lo que se genera de forma independiente en
Python a partir del mismo dataset_parcial3_100.csv usado en STATDISK.

Interpretación: líneas aproximadamente paralelas indican ausencia de
interacción (el efecto de un factor es consistente en todos los niveles
del otro factor); líneas que se cruzan o divergen marcadamente indicarían
interacción significativa.

Librerías: pandas, numpy, matplotlib

Justificación de cada librería:
  - pandas:     carga del dataset y groupby().unstack() para obtener la
                tabla de medias por combinación Sector x Vector_Ataque.
  - numpy:      generación del arreglo de posiciones en el eje X (arange)
                para ubicar los dos sectores en el gráfico.
  - matplotlib: única librería de graficación necesaria; se usa en modo
                blanco y negro con líneas de estilo distinto (sólida/
                discontinua) para diferenciar Ransomware de Malware sin
                depender del color, replicando el criterio de reportes
                anteriores del curso (blanco y negro, sin decoración).
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv("dataset_parcial3_100.csv")

medias = df.groupby(["Sector", "Vector_Ataque"])["Costo_Y"].mean().unstack()
print("Medias de Costo_Y por celda (miles USD):")
print(medias.round(2))

fig, ax = plt.subplots(figsize=(7, 5))
fig.patch.set_facecolor("white")

sectores = ["Financiero", "Salud"]
x = np.arange(len(sectores))

for ataque, marker, ls, color in [("Ransomware", "o", "-", "black"),
                                    ("Malware", "s", "--", "#666666")]:
    valores = [medias.loc[s, ataque] for s in sectores]
    ax.plot(x, valores, marker=marker, linestyle=ls, linewidth=2,
            markersize=9, color=color, label=ataque)
    for xi, yi in zip(x, valores):
        ax.annotate(f"{yi:.1f}", (xi, yi), textcoords="offset points",
                    xytext=(8, 6), fontsize=10)

ax.set_xticks(x)
ax.set_xticklabels(sectores, fontsize=11)
ax.set_ylabel("Costo_Y medio (miles USD)", fontsize=11)
ax.set_title("Gráfico de Interacción — Costo Medio por Sector y Vector de Ataque",
             fontsize=12, fontweight="bold", pad=14)
ax.legend(fontsize=10, title="Vector_Ataque")
ax.set_facecolor("#F9F9F9")
ax.grid(axis="y", linestyle="--", alpha=0.4, color="gray")
ax.spines[["top", "right"]].set_visible(False)

plt.tight_layout()
plt.savefig("grafico_interaccion_anova.png", dpi=150, bbox_inches="tight")
plt.close()
print("\nGráfico exportado: grafico_interaccion_anova.png")
