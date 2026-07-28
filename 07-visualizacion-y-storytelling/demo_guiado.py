"""
Demo guiado del Modulo 07 - Visualizacion y storytelling, de principio a fin.

A diferencia de los demos anteriores, este NO imprime tablas: genera IMAGENES.
Al terminar tendras 7 PNG en reports/07-visualizacion/ que puedes abrir y comparar.
Ese es el punto del modulo: el mismo dato, contado bien o contado mal.

Este script se ejecuta en tu repo de practica `curso-datos`. Copialo ahi, y desde
la raiz del repo ejecutalo con:  uv run demo_guiado.py
Cada PASO corresponde a una seccion del README.

Requisitos (en curso-datos):  uv add pandas matplotlib seaborn
y copiar ventas_ejemplo.csv del material a  data/raw/
"""

import os
import pathlib

import matplotlib

matplotlib.use("Agg")   # backend sin ventana: guarda a archivo y ya. Ideal en scripts.

import matplotlib.pyplot as plt   # noqa: E402
import pandas as pd               # noqa: E402
import seaborn as sns             # noqa: E402

CSV = "data/raw/ventas_ejemplo.csv"
SALIDA = pathlib.Path("reports/07-visualizacion")

ACENTO = "#2563eb"    # un unico color de acento...
GRIS = "#c9ced6"      # ...y gris para todo lo que es contexto
ALERTA = "#dc2626"

MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun"]


def titulo(n, texto):
    print(f"\n{'=' * 66}\nPASO {n}: {texto}\n{'=' * 66}")


def guardar(fig, nombre):
    fig.tight_layout()
    ruta = SALIDA / nombre
    fig.savefig(ruta, dpi=150)
    plt.close(fig)
    print(f"  -> guardado: {ruta}")


def limpiar_ejes(ax):
    """Los 3 gestos que mas mejoran un grafico de matplotlib."""
    ax.spines[["top", "right"]].set_visible(False)   # 1. fuera el marco
    ax.grid(axis="y", alpha=0.25)                    # 2. rejilla tenue, solo donde ayuda
    ax.set_axisbelow(True)                           # 3. datos por delante de la rejilla


if not os.path.exists(CSV):
    raise SystemExit(f"Falta {CSV}. Copia ventas_ejemplo.csv del material a data/raw/")

SALIDA.mkdir(parents=True, exist_ok=True)

df = (
    pd.read_csv(CSV, parse_dates=["fecha"])
    .drop_duplicates()
    .assign(
        ventas=lambda d: d["ventas"].fillna(d["ventas"].median()),
        region=lambda d: d["region"].str.strip().str.upper(),
    )
)

# El dataset "sin outliers" del Modulo 06: lo necesitamos para el paso 7
q1, q3 = df["ventas"].quantile([0.25, 0.75])
iqr = q3 - q1
sin_outliers = df[df["ventas"].between(q1 - 1.5 * iqr, q3 + 1.5 * iqr)]


# ── PASO 1: EL MENSAJE VA ANTES QUE EL GRAFICO (6.1) ──────────────
titulo(1, "Antes de graficar: cual es el UNICO mensaje? (6.1)")
print("  Hallazgo del Modulo 06:")
print("  'El liderazgo del Norte se sostiene sobre 6 transacciones anomalas;")
print("   por transaccion, las cuatro regiones venden practicamente lo mismo.'")
print("\n  Ese es el mensaje. Todos los graficos de abajo existen para contarlo.")
print("  Si un grafico no ayuda a ese mensaje, sobra. Es asi de brutal.")

# ── PASO 2: ELEGIR EL GRAFICO CORRECTO (6.2) ──────────────────────
titulo(2, "Cada pregunta tiene su grafico (6.2)")
fig, axes = plt.subplots(2, 2, figsize=(11, 7))

# comparar categorias -> barras
por_region = df.groupby("region")["ventas"].sum().sort_values()
axes[0, 0].barh(por_region.index, por_region.values, color=GRIS)
axes[0, 0].set_title("Comparar categorias -> barras")

# evolucion temporal -> lineas
mensual = df.set_index("fecha")["ventas"].resample("MS").sum()
axes[0, 1].plot(MESES, mensual.values, marker="o", color=ACENTO)
axes[0, 1].set_title("Evolucion en el tiempo -> lineas")

# relacion entre dos variables -> dispersion
axes[1, 0].scatter(df["trafico"], df["ventas"], s=12, alpha=0.4, color=ACENTO)
axes[1, 0].set_title("Relacion entre 2 variables -> dispersion")

# distribucion -> boxplot
axes[1, 1].boxplot([g["ventas"].values for _, g in sin_outliers.groupby("producto")],
                   tick_labels=list(sorted(sin_outliers["producto"].unique())))
axes[1, 1].set_title("Distribucion por grupo -> boxplot")

for ax in axes.flat:
    limpiar_ejes(ax)
fig.suptitle("Cuatro preguntas distintas, cuatro graficos distintos", fontsize=13)
guardar(fig, "01_tipos_de_grafico.png")
print("  El scatter ya te avisa de algo: es una nube sin forma. No hay relacion")
print("  entre trafico y ventas, exactamente como dijo la correlacion del M06.")

# ── PASO 3: EL GRAFICO POR DEFECTO (6.3) ──────────────────────────
titulo(3, "El grafico que sale 'solo': tecnicamente correcto, comunicativamente nulo (6.3)")
fig, ax = plt.subplots(figsize=(7, 4.5))
por_region_desord = df.groupby("region")["ventas"].sum()          # sin ordenar
ax.bar(por_region_desord.index, por_region_desord.values,
       color=["#e15759", "#4e79a7", "#f28e2b", "#76b7b2"])        # 4 colores sin significado
ax.set_title("Grafico 1: ventas")                                 # titulo generico
ax.grid(True)                                                     # rejilla en todas partes
guardar(fig, "02_antes.png")
print("  Defectos: titulo que no dice nada, barras en orden alfabetico, un color")
print("  por barra (el color no codifica NADA), rejilla pesada, sin unidades.")

# ── PASO 4: EL MISMO DATO, REDISENADO (6.4) ───────────────────────
titulo(4, "El mismo dato aplicando las 6 reglas de diseno (6.4)")
serie = df.groupby("region")["ventas"].sum().sort_values()
colores = [ACENTO if r == "NORTE" else GRIS for r in serie.index]   # 1 acento, resto contexto

fig, ax = plt.subplots(figsize=(7.5, 4.5))
barras = ax.barh(serie.index, serie.values, color=colores)
ax.bar_label(barras, fmt="%.0f", padding=4, fontsize=9, color="#444")  # etiqueta directa
ax.set_title("El Norte factura un 30% mas que el Sur...\n"
             "...pero el Modulo 06 demostro que son 6 ventas anomalas",
             loc="left", fontsize=12)
ax.set_xlabel("Ventas del semestre (USD)")
ax.set_xlim(0, serie.max() * 1.15)          # el eje EMPIEZA EN 0
ax.spines[["top", "right", "left"]].set_visible(False)
ax.tick_params(left=False)
ax.set_xticks([])                            # si etiquetas cada barra, el eje sobra
fig.text(0.01, 0.01, "Fuente: ventas_ejemplo.csv (ene-jun 2026, n=720)",
         fontsize=7, color="#777")           # fuente y periodo: SIEMPRE
guardar(fig, "03_despues.png")
print("  Cambios: orden por valor, un solo acento, etiquetas directas, eje desde 0,")
print("  sin marco, y el titulo ES la conclusion (incluido el matiz que la mata).")

# ── PASO 5: EL EJE TRUNCADO, EL ENGANO MAS COMUN (6.8) ────────────
titulo(5, "Como mentir sin falsear un solo dato: el eje truncado (6.8)")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))
regiones = serie.sort_values(ascending=False)

ax1.bar(regiones.index, regiones.values, color=ALERTA)
ax1.set_ylim(15000, 22000)                   # <- la trampa
ax1.set_title("ENGANOSO: 'el Norte arrasa'")
ax1.set_ylabel("Ventas (USD)")

ax2.bar(regiones.index, regiones.values, color=ACENTO)
ax2.set_ylim(0, 22000)                       # <- honesto
ax2.set_title("HONESTO: la diferencia real")
ax2.set_ylabel("Ventas (USD)")

for ax in (ax1, ax2):
    limpiar_ejes(ax)
    ax.tick_params(axis="x", labelsize=8)
guardar(fig, "04_eje_truncado.png")
print("  Los dos graficos usan los MISMOS numeros. El de la izquierda hace que el")
print("  Norte parezca 5 veces el Sur. En barras, el eje empieza en 0. Sin excepciones.")

# ── PASO 6: COLOR ACCESIBLE (6.5) ─────────────────────────────────
titulo(6, "Paleta accesible y seaborn (6.5)")
sns.set_theme(style="whitegrid")
sns.set_palette("colorblind")     # segura para daltonismo

fig, ax = plt.subplots(figsize=(8, 4.5))
mensual_canal = (
    df.assign(mes=df["fecha"].dt.month)
    .groupby(["mes", "canal"])["ventas"].sum().reset_index()
)
sns.lineplot(data=mensual_canal, x="mes", y="ventas", hue="canal",
             marker="o", ax=ax)
ax.set_title("Los tres canales caen en junio: el problema no es del canal", loc="left")
ax.set_xlabel("")
ax.set_ylabel("Ventas (USD)")
ax.set_xticks(range(1, 7))
ax.set_xticklabels(MESES)
ax.set_ylim(0, None)
ax.legend(title=None, frameon=False)
guardar(fig, "05_paleta_accesible.png")
print("  Regla practica: el color nunca debe ser la UNICA forma de distinguir series.")
print("  Aqui, ademas del color, cada linea tiene su marcador y su posicion.")

# ── PASO 7: MOSTRAR UNA DISTRIBUCION, NO UN PROMEDIO (6.2 / M06) ──
titulo(7, "El grafico que el Modulo 06 pedia a gritos: la distribucion")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))

ax1.hist(df["ventas"], bins=40, color=GRIS)
ax1.axvline(df["ventas"].mean(), color=ALERTA, lw=2, label=f"media {df['ventas'].mean():.0f}")
ax1.axvline(df["ventas"].median(), color=ACENTO, lw=2, label=f"mediana {df['ventas'].median():.0f}")
ax1.set_title("Con outliers: la media (roja) no representa a nadie", fontsize=11, loc="left")
ax1.legend(frameon=False)

ax2.hist(sin_outliers["ventas"], bins=40, color=GRIS)
ax2.axvline(sin_outliers["ventas"].mean(), color=ALERTA, lw=2)
ax2.axvline(sin_outliers["ventas"].median(), color=ACENTO, lw=2)
ax2.set_title(f"Sin los 10 outliers (n={len(sin_outliers)}): media y mediana coinciden",
              fontsize=11, loc="left")

for ax in (ax1, ax2):
    limpiar_ejes(ax)
    ax.set_xlabel("Venta (USD)")
guardar(fig, "06_distribucion.png")
print("  Una barra con el promedio te habria ocultado esto por completo.")
print("  Cuando presentes un promedio, ensena tambien la distribucion que hay detras.")

# ── PASO 8: ANATOMIA DE UN DASHBOARD (6.6) ────────────────────────
titulo(8, "Un dashboard de una sola imagen: KPIs + heroe + desglose (6.6)")
fig = plt.figure(figsize=(11, 7))
malla = fig.add_gridspec(3, 3, height_ratios=[0.5, 1.4, 1.1], hspace=0.55, wspace=0.3)

fig.suptitle("Ventas 1er semestre 2026  |  n=720 transacciones", fontsize=14, x=0.02, ha="left")

# fila 1: KPIs (numeros grandes, cero adornos)
kpis = [
    ("Ventas totales", f"{df['ventas'].sum():,.0f} USD", ""),
    ("Ticket mediano", f"{df['ventas'].median():.0f} USD", "estable todo el semestre"),
    ("Variacion junio", "-21.4%", "-16% si normalizas por dia"),
]
for i, (etiqueta, valor, nota) in enumerate(kpis):
    ax = fig.add_subplot(malla[0, i])
    ax.axis("off")
    ax.text(0, 0.85, etiqueta.upper(), fontsize=8, color="#777")
    ax.text(0, 0.35, valor, fontsize=19, color=ALERTA if i == 2 else "#222", weight="bold")
    ax.text(0, 0.05, nota, fontsize=7.5, color="#777")

# fila 2: el grafico heroe (la tendencia, ancho completo)
ax = fig.add_subplot(malla[1, :])
ax.plot(MESES, mensual.values, marker="o", color=ACENTO, lw=2)
ax.scatter([MESES[-1]], [mensual.values[-1]], color=ALERTA, zorder=5, s=70)
ax.annotate("junio: -21.4%", xy=(5, mensual.values[-1]), xytext=(4.1, mensual.values[-1] - 1800),
            color=ALERTA, fontsize=10)
ax.set_ylim(0, mensual.max() * 1.2)
ax.set_title("Cinco meses planos y una caida en junio", loc="left", fontsize=11)
limpiar_ejes(ax)

# fila 3: desgloses
ax = fig.add_subplot(malla[2, 0])
s = df.groupby("canal")["ventas"].sum().sort_values()
ax.barh(s.index, s.values, color=GRIS)
ax.set_title("Por canal", fontsize=9, loc="left")
limpiar_ejes(ax)

ax = fig.add_subplot(malla[2, 1])
s = df.groupby("producto")["ventas"].sum().sort_values()
ax.barh(s.index, s.values, color=GRIS)
ax.set_title("Por producto", fontsize=9, loc="left")
limpiar_ejes(ax)

ax = fig.add_subplot(malla[2, 2])
s = df.groupby("region")["ventas"].sum().sort_values()
ax.barh(s.index, s.values, color=[ACENTO if r == "NORTE" else GRIS for r in s.index])
ax.set_title("Por region", fontsize=9, loc="left")
ax.tick_params(labelsize=7)
limpiar_ejes(ax)

fig.savefig(SALIDA / "07_dashboard.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"  -> guardado: {SALIDA / '07_dashboard.png'}")
print("  Lectura en Z: titulo -> KPIs -> tendencia -> desgloses. Lo mas importante,")
print("  arriba a la izquierda. Cuatro bloques, ni uno mas.")

# ── PASO 9: EL TEXTO QUE ACOMPANA (6.7) ───────────────────────────
titulo(9, "Sin narrativa, el grafico se ignora: el framework SCR (6.7)")
print("""
  SITUACION    Las ventas del semestre se mantuvieron planas en ~12 000 USD/mes,
               con un ticket mediano de ~90 USD estable de enero a mayo.

  COMPLICACION En junio cayeron a 10 654 USD (-21.4% vs mayo). Al abrirlo:
               el ticket mediano NO se movio (89 vs 92 USD); lo que cayo fue el
               numero de transacciones (106 vs 132, -20%), y en los tres canales
               a la vez (Movil -20%, Tienda -14%, Web -30%). Ademas junio tiene
               2 dias menos: normalizando por dia la caida es del 16%, no del 21%.

  RESOLUCION   No es un problema de precio ni de un canal concreto: es de
               demanda o de captacion. Recomiendo revisar la inversion en
               marketing y el calendario comercial de junio, no el checkout.
""")
print("  Tres frases. Terminan en algo que alguien puede HACER manana.")
print("  Fijate en dos cosas que separan a un analista de un generador de graficos:")
print("   - descomponer la caida en precio x volumen antes de opinar;")
print("   - normalizar por dias antes de comparar meses (-21% se queda en -16%).")
print("  Un analisis que no termina en una accion es un pasatiempo caro.")

print("\n" + "=" * 66)
print(f"Listo. Abre las 7 imagenes de {SALIDA} y comparalas, sobre todo")
print("02_antes.png contra 03_despues.png, y las dos mitades de 04_eje_truncado.png.")
print("\nAhora hazlo tu:  uv run actividad_01.py")
