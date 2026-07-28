"""
Demo guiado del Modulo 06 — Estadistica aplicada y EDA, de principio a fin.

Aqui NO hay SQL: todo corre en pandas + scipy sobre el CSV del curso, siguiendo
el mismo flujo de EDA que usaras en cualquier dataset nuevo.

La historia del demo: el Modulo 03 concluyo que "Norte es la region lider" y que
"Movil tiene el mejor ticket medio". En este modulo vas a poner esas dos
afirmaciones a prueba con estadistica... y las dos se caen. Ese es el trabajo.

Este script se ejecuta en tu repo de practica `curso-datos`. Copialo ahi, y desde
la raiz del repo ejecutalo con:  uv run demo_guiado.py
Cada PASO corresponde a una seccion del README.

Requisitos (en curso-datos):  uv add pandas scipy
y copiar ventas_ejemplo.csv del material a  data/raw/
"""

import os

import numpy as np
import pandas as pd
from scipy import stats

CSV = "data/raw/ventas_ejemplo.csv"

pd.set_option("display.width", 100)
pd.set_option("display.max_columns", 20)


def titulo(n, texto):
    print(f"\n{'=' * 66}\nPASO {n}: {texto}\n{'=' * 66}")


def barras(serie, bins=12, ancho=44):
    """Histograma en texto: sirve en cualquier terminal, sin matplotlib."""
    conteo, cortes = np.histogram(serie.dropna(), bins=bins)
    escala = ancho / max(conteo.max(), 1)
    for i, n in enumerate(conteo):
        print(f"  [{cortes[i]:7.0f}, {cortes[i + 1]:7.0f})  {'#' * int(n * escala):<{ancho}} {n}")


if not os.path.exists(CSV):
    raise SystemExit(f"Falta {CSV}. Copia ventas_ejemplo.csv del material a data/raw/")


# ── PASO 0: PARTIR DEL DATASET LIMPIO DEL MODULO 03 ───────────────
titulo(0, "Recuperar el dataset limpio del Modulo 03")
df = (
    pd.read_csv(CSV, parse_dates=["fecha"])
    .drop_duplicates()                                    # 735 -> 720 filas
    .assign(
        ventas=lambda d: d["ventas"].fillna(d["ventas"].median()),   # mediana = 90.5
        region=lambda d: d["region"].str.strip().str.upper(),
    )
)
print(f"Dataset limpio: {df.shape[0]} filas x {df.shape[1]} columnas")
print("Ojo: al imputar 19 nulos con la mediana (90.5) creamos 19 valores identicos.")
print("Eso NO es neutro: aplasta la varianza y hace que la mediana sea aun mas comun.")

# ── PASO 1: EL FLUJO DE EDA EN 5 PASOS (5.1) ──────────────────────
titulo(1, "El flujo de EDA: forma, calidad, distribuciones, relaciones, anomalias (5.1)")
print("1) Forma:", df.shape)
print("\n2) Calidad - % de nulos por columna:")
print((df.isna().mean() * 100).round(1).to_string())
print(f"   duplicados restantes: {df.duplicated().sum()}")
print("\n3) Distribuciones - describe() de las numericas:")
print(df[["ventas", "descuento", "trafico"]].describe().round(2))
print("\n4) Categoricas - cuantas filas por valor:")
for c in ["region", "producto", "canal"]:
    print(f"   {c:9} {df[c].value_counts().to_dict()}")

# ── PASO 2: DESCRIPTIVA — CUANDO LA MEDIA MIENTE (5.2) ────────────
titulo(2, "Media vs mediana: la primera senal de alarma (5.2)")
media, mediana, std = df["ventas"].mean(), df["ventas"].median(), df["ventas"].std()
print(f"  media   = {media:.2f}")
print(f"  mediana = {mediana:.2f}")
print(f"  std     = {std:.2f}   (mas grande que la propia mediana: sospechoso)")
print(f"  skew    = {df['ventas'].skew():.2f}   (>1 ya es asimetria fuerte; esto es enorme)")
print(f"  cuartiles Q1/Q2/Q3 = {df['ventas'].quantile([.25, .5, .75]).round(1).tolist()}")
print("\nLectura: la media supera a la mediana en 10 puntos y la desviacion es gigante.")
print("Alguien esta tirando del promedio hacia arriba. Vamos a buscarlo.")

# ── PASO 3: OUTLIERS CON LA REGLA IQR (5.3) ───────────────────────
titulo(3, "Regla IQR: quien tira del promedio (5.3)")
q1, q3 = df["ventas"].quantile([0.25, 0.75])
iqr = q3 - q1
lim_inf, lim_sup = q1 - 1.5 * iqr, q3 + 1.5 * iqr
es_outlier = (df["ventas"] < lim_inf) | (df["ventas"] > lim_sup)
outliers = df[es_outlier]
limpio = df[~es_outlier]

print(f"  Q1={q1:.1f}  Q3={q3:.1f}  IQR={iqr:.1f}")
print(f"  limites: [{lim_inf:.1f}, {lim_sup:.1f}]")
print(f"  outliers: {len(outliers)} de {len(df)} filas ({100 * len(outliers) / len(df):.1f}%)")
print("\nLos 10 outliers, uno por uno (investigarlos ES el trabajo):")
print(outliers[["fecha", "region", "producto", "canal", "ventas"]].to_string(index=False))
print("\nSon ventas de 200 a 1120 cuando lo normal ronda 90: ~8x. Coinciden con las")
print("anomalias que el dataset trae inyectadas a proposito. 6 de las 10 son del NORTE")
print("y 5 son del canal MOVIL. Guarda ese dato: explica los dos 'hallazgos' del M03.")

# ── PASO 4: DISTRIBUCIONES ANTES Y DESPUES (5.4) ──────────────────
titulo(4, "La forma de la distribucion (5.4)")
print("Con outliers - la cola larga deja el grafico inservible:")
barras(df["ventas"])
print(f"\nSin outliers ({len(limpio)} filas) - aparece la distribucion real:")
barras(limpio["ventas"])
print(f"\n  con outliers:  media {media:.1f}  std {std:.1f}  skew {df['ventas'].skew():.2f}")
print(f"  sin outliers:  media {limpio['ventas'].mean():.1f}  "
      f"std {limpio['ventas'].std():.1f}  skew {limpio['ventas'].skew():.2f}")
print("\n10 filas (1.4% de los datos) transforman una campana casi simetrica en un monstruo.")

# ── PASO 5: CORRELACIONES (5.5) ───────────────────────────────────
titulo(5, "Matriz de correlaciones: cuando el hallazgo es 'no hay nada' (5.5)")
print(df[["ventas", "descuento", "trafico"]].corr().round(3))
print("\nTodo entre -0.04 y 0: NO hay relacion lineal entre trafico y ventas,")
print("ni entre descuento y ventas. Eso contradice la intuicion de negocio")
print("('mas trafico = mas ventas') y por eso mismo es un hallazgo que vale reportar.")
print("\nPearson solo ve relaciones LINEALES. Segunda opinion con Spearman (rangos):")
rho, p_rho = stats.spearmanr(df["ventas"], df["trafico"])
print(f"  Spearman ventas-trafico: rho={rho:.3f}  p={p_rho:.3f}  -> tampoco hay relacion monotona.")

# ── PASO 6: INFERENCIA — INTERVALO DE CONFIANZA (5.6) ─────────────
titulo(6, "De la muestra a la poblacion: intervalo de confianza (5.6)")


def ic95(serie):
    n = len(serie)
    media_ = serie.mean()
    error_estandar = serie.std(ddof=1) / np.sqrt(n)
    lo, hi = stats.t.interval(0.95, n - 1, loc=media_, scale=error_estandar)
    return n, media_, error_estandar, lo, hi


n, m, se, lo, hi = ic95(df["ventas"])
print(f"  con outliers:  media {m:.2f}  error estandar {se:.2f}  IC95% [{lo:.2f}, {hi:.2f}]")
n2, m2, se2, lo2, hi2 = ic95(limpio["ventas"])
print(f"  sin outliers:  media {m2:.2f}  error estandar {se2:.2f}  IC95% [{lo2:.2f}, {hi2:.2f}]")
print(f"\nEl intervalo pasa de {hi - lo:.1f} puntos de ancho a {hi2 - lo2:.1f}: los outliers")
print("no solo mueven la media, tambien destruyen la PRECISION de tu estimacion.")
print("Nunca reportes 'la media es 100.45'. Reporta el intervalo, o no digas nada.")

# ── PASO 7: PRUEBA DE HIPOTESIS — EL TEST A/B (5.7) ───────────────
titulo(7, "Test de hipotesis: 'Movil tiene mejor ticket medio' (5.7)")
web = df.loc[df["canal"] == "Web", "ventas"]
movil = df.loc[df["canal"] == "Movil", "ventas"]
t_stat, p_valor = stats.ttest_ind(web, movil, equal_var=False)   # Welch: no asume varianzas iguales
print("H0: Web y Movil tienen la misma venta media.  H1: son distintas.")
print(f"  Web:   n={len(web)}  media={web.mean():.2f}")
print(f"  Movil: n={len(movil)}  media={movil.mean():.2f}   (+{movil.mean() - web.mean():.1f})")
print(f"  t={t_stat:.3f}   p-valor={p_valor:.4f}")
print("\np = 0.063 > 0.05: NO puedes rechazar H0. Ese +16 de ventaja de Movil")
print("es perfectamente compatible con el azar. Aqui es donde medio mundo hace")
print("p-hacking: prueba otro test hasta que baje de 0.05. No lo hagas.")

web_l = limpio.loc[limpio["canal"] == "Web", "ventas"]
movil_l = limpio.loc[limpio["canal"] == "Movil", "ventas"]
t2, p2 = stats.ttest_ind(web_l, movil_l, equal_var=False)
print("\nAhora el mismo test quitando los 10 outliers:")
print(f"  Web:   media={web_l.mean():.2f}   Movil: media={movil_l.mean():.2f}")
print(f"  t={t2:.3f}   p-valor={p2:.4f}")
print("\nLa ventaja de Movil no se reduce: SE INVIERTE (Web queda por encima).")
print("Todo el 'mejor ticket medio de Movil' del Modulo 03 eran 5 transacciones raras.")

# ── PASO 8: CORRELACION, CAUSALIDAD Y SUBGRUPOS (5.8) ─────────────
titulo(8, "'Que mas podria explicar esto?' - el liderazgo de Norte (5.8)")
print("Hallazgo del Modulo 03: Norte factura mas que nadie (21 367 vs 16 379 de Sur).")
print("\nVentas TOTALES por region (lo que veias antes):")
print(df.groupby("region")["ventas"].sum().sort_values(ascending=False).round(1).to_string())

norte, sur = df.loc[df["region"] == "NORTE", "ventas"], df.loc[df["region"] == "SUR", "ventas"]
t3, p3 = stats.ttest_ind(norte, sur, equal_var=False)
print(f"\nTest Norte vs Sur por transaccion: medias {norte.mean():.1f} vs {sur.mean():.1f}, "
      f"p={p3:.4f}  -> significativo!")

norte_l = limpio.loc[limpio["region"] == "NORTE", "ventas"]
sur_l = limpio.loc[limpio["region"] == "SUR", "ventas"]
t4, p4 = stats.ttest_ind(norte_l, sur_l, equal_var=False)
print(f"El mismo test sin los outliers:      medias {norte_l.mean():.1f} vs {sur_l.mean():.1f}, "
      f"p={p4:.4f}  -> se evapora.")
print("\nLa variable de confusion eran los 6 outliers del Norte. Sin ellos, las cuatro")
print("regiones venden practicamente lo mismo por transaccion:")
print(limpio.groupby("region")["ventas"].agg(["count", "mean", "median"]).round(2))
print("\nRegla: antes de explicar una diferencia, comprueba que la diferencia EXISTE.")

# ── PASO 9: UN EDA REPRODUCIBLE (5.9) ─────────────────────────────
titulo(9, "La funcion que reutilizaras en todos tus proyectos (5.9)")


def resumen_eda(datos, col_objetivo=None):
    """EDA en una llamada. Copiala a src/ de tu repo: la usaras siempre."""
    print("Forma:", datos.shape)
    print("Duplicados:", datos.duplicated().sum())
    print("\n% Nulos:")
    print((datos.isna().mean() * 100).round(1).to_string())
    print("\nNumericas:")
    print(datos.describe(numeric_only=True).T.round(2))
    for c in datos.select_dtypes(include=["object", "string", "category"]).columns[:5]:
        print(f"\n{c}:")
        print(datos[c].value_counts().head().to_string())
    if col_objetivo:
        s = datos[col_objetivo]
        a, b = s.quantile([0.25, 0.75])
        r = b - a
        n_out = ((s < a - 1.5 * r) | (s > b + 1.5 * r)).sum()
        print(f"\nOutliers IQR en '{col_objetivo}': {n_out} ({100 * n_out / len(s):.1f}%)"
              f" | skew {s.skew():.2f}")


resumen_eda(df, col_objetivo="ventas")

print("\n" + "=" * 66)
print("LO QUE TE LLEVAS")
print("=" * 66)
print("  1. La media sin la mediana al lado es una mentira a medias.")
print("  2. 1.4% de filas pueden invertir la conclusion de un analisis entero.")
print("  3. p > 0.05 no es un fracaso: es la respuesta 'no lo sabemos'.")
print("  4. Un outlier no se borra: se investiga y se reporta con y sin el.")
print("\nAhora hazlo tu:  uv run actividad_01.py")
