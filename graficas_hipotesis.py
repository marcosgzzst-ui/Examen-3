"""
GRÁFICAS DE HIPÓTESIS (ESTILO STATDISK) — EXAMEN PARCIAL 3 TIA
Equipo: CruzAzul | Anexo A

Replica el estilo visual de STATDISK v13 (curva de distribución, valores
críticos en rojo, estadístico de prueba en azul) para las 5 pruebas de
hipótesis que STATDISK no grafica directamente:

  1. Prueba de beta1 (pendiente)     — t de Student, df=98, dos colas
  2. Prueba de beta0 (intercepto)    — t de Student, df=98, dos colas
  3. ANOVA — Interacción              — F de Fisher, df1=1, df2=96
  4. ANOVA — Efecto Sector            — F de Fisher, df1=1, df2=96
  5. ANOVA — Efecto Vector_Ataque     — F de Fisher, df1=1, df2=96

Nota: STATDISK no ofrece gráfica para pruebas de regresión con una sola
variable predictora ni para ANOVA de dos vías, por lo que se generan de
forma independiente en Python, replicando su estilo visual estándar.

Librerías: numpy, matplotlib, scipy

Justificación de cada librería:
  - numpy:      construcción de los arreglos de puntos (linspace) sobre
                los que se evalúan las densidades t y F para dibujar la
                curva completa de cada distribución.
  - matplotlib: dibuja la curva, las líneas verticales de valores críticos
                (rojo) y estadístico de prueba (azul), replicando el
                formato exacto de las capturas de STATDISK usadas en
                exámenes anteriores del curso.
  - scipy.stats: provee las funciones de densidad de probabilidad t.pdf
                y f.pdf, y los cuantiles t.ppf/f.ppf necesarios para
                ubicar los valores críticos exactos de cada prueba.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

def grafica_t(t_stat, t_crit, df, titulo, archivo):
    x = np.linspace(-5, 5, 1000)
    y = stats.t.pdf(x, df)

    fig, ax = plt.subplots(figsize=(6, 5))
    fig.patch.set_facecolor("white")
    ax.plot(x, y, color="#444444", linewidth=1.8)

    ax.axvline(t_crit, color="red", linewidth=1.3)
    ax.axvline(-t_crit, color="red", linewidth=1.3)
    ax.axvline(t_stat, color="#1f77b4", linewidth=1.3)

    ax.set_title(f"{titulo}\nStudent t Distribution", fontsize=12, fontweight="bold", pad=34)
    fig.text(0.5, 0.93, f"Critical Values, t: {t_crit:.5f}, and {-t_crit:.5f}",
              ha="center", color="red", fontsize=10)
    fig.text(0.5, 0.885, f"Test Statistic, t: {t_stat:.5f}",
              ha="center", color="#1f77b4", fontsize=10)

    ax.set_xlabel("t Value", fontsize=10)
    ax.set_ylabel("Y Values", fontsize=10)
    ax.set_facecolor("white")
    ax.grid(alpha=0.3, linestyle="-", linewidth=0.5)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_xlim(-max(6, abs(t_stat)+1), max(6, abs(t_stat)+1))

    plt.tight_layout(rect=[0, 0, 1, 0.86])
    plt.savefig(archivo, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Generado: {archivo}")

def grafica_f(f_stat, f_crit, df1, df2, titulo, archivo):
    x_max = max(f_crit * 1.8, f_stat * 1.3, 5)
    x = np.linspace(0.001, x_max, 1000)
    y = stats.f.pdf(x, df1, df2)

    fig, ax = plt.subplots(figsize=(6, 5))
    fig.patch.set_facecolor("white")
    ax.plot(x, y, color="#444444", linewidth=1.8)

    ax.axvline(f_crit, color="red", linewidth=1.3)
    ax.axvline(f_stat, color="#1f77b4", linewidth=1.3)

    ax.set_title(f"{titulo}\nF Distribution", fontsize=12, fontweight="bold", pad=34)
    fig.text(0.5, 0.93, f"Critical Value, F: {f_crit:.5f}",
              ha="center", color="red", fontsize=10)
    fig.text(0.5, 0.885, f"Test Statistic, F: {f_stat:.5f}",
              ha="center", color="#1f77b4", fontsize=10)

    ax.set_xlabel("F Value", fontsize=10)
    ax.set_ylabel("Y Values", fontsize=10)
    ax.set_facecolor("white")
    ax.grid(alpha=0.3, linestyle="-", linewidth=0.5)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_xlim(0, x_max)

    plt.tight_layout(rect=[0, 0, 1, 0.86])
    plt.savefig(archivo, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Generado: {archivo}")


# ══════════════════════════════════════════════════════════════
# 1. Prueba de beta1 (pendiente) — t, df=98, dos colas, alfa=0.05
# ══════════════════════════════════════════════════════════════
df_reg = 98
t_crit_reg = stats.t.ppf(0.975, df_reg)
grafica_t(t_stat=53.9352, t_crit=t_crit_reg, df=df_reg,
          titulo="Hypothesis Test, Slope (beta1)",
          archivo="hip_beta1.png")

# ══════════════════════════════════════════════════════════════
# 2. Prueba de beta0 (intercepto) — t, df=98, dos colas, alfa=0.05
# ══════════════════════════════════════════════════════════════
grafica_t(t_stat=1.2778, t_crit=t_crit_reg, df=df_reg,
          titulo="Hypothesis Test, Intercept (beta0)",
          archivo="hip_beta0.png")

# ══════════════════════════════════════════════════════════════
# 3-5. ANOVA de dos vías — F, df1=1, df2=96, alfa=0.05
# ══════════════════════════════════════════════════════════════
df1, df2 = 1, 96
f_crit_anova = stats.f.ppf(0.95, df1, df2)

grafica_f(f_stat=0.583010, f_crit=f_crit_anova, df1=df1, df2=df2,
          titulo="Hypothesis Test, Interaction (Sector x Vector_Ataque)",
          archivo="hip_interaccion.png")

grafica_f(f_stat=18.903786, f_crit=f_crit_anova, df1=df1, df2=df2,
          titulo="Hypothesis Test, Main Effect (Sector)",
          archivo="hip_sector.png")

grafica_f(f_stat=23.844216, f_crit=f_crit_anova, df1=df1, df2=df2,
          titulo="Hypothesis Test, Main Effect (Vector_Ataque)",
          archivo="hip_ataque.png")

print("\nTodas las gráficas generadas.")
