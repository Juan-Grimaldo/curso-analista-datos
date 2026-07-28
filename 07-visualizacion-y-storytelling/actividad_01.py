"""
ACTIVIDAD 01 - Modulo 07 (Visualizacion y storytelling)
=======================================================
Mismo tipo de graficos que demo_guiado.py, pero ahora los dibujas TU.

Lo distinto de esta actividad: el corrector no compara numeros, INSPECCIONA tus
graficos. Comprueba si el eje empieza en 0, si ordenaste las barras, si quitaste
el marco, si tu titulo dice algo o es un "Grafico 1". Es decir, corrige lo que
un jefe vera de un vistazo.

Este archivo se trabaja en tu repo de practica `curso-datos`. Copialo ahi y
ejecutalo desde la raiz del repo con:  uv run actividad_01.py

Como funciona:
  - Cada ejercicio debe DEVOLVER un objeto Figure de matplotlib (`fig`).
  - NO llames a plt.show(): el corrector guarda las figuras por ti en
    reports/07-actividad/ para que las abras y las mires.
  - `cargar()` te entrega el dataset limpio: no toques esa parte.

Requisitos (en curso-datos):  uv add pandas matplotlib
y copiar ventas_ejemplo.csv del material a  data/raw/

Pistas: todo esta en el README, secciones 6.2 a 6.5. No mires demo_guiado.py
hasta haberlo intentado al menos dos veces.
"""

import pathlib

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt   # noqa: E402
import pandas as pd               # noqa: E402

CSV = "data/raw/ventas_ejemplo.csv"
SALIDA = pathlib.Path("reports/07-actividad")

ACENTO = "#2563eb"
GRIS = "#c9ced6"


def cargar():
    """Dataset limpio del Modulo 03: 720 filas. No modifiques esta funcion."""
    return (
        pd.read_csv(CSV, parse_dates=["fecha"])
        .drop_duplicates()
        .assign(
            ventas=lambda d: d["ventas"].fillna(d["ventas"].median()),
            region=lambda d: d["region"].str.strip().str.upper(),
        )
    )


# ── EJERCICIO 1: barras honestas ──────────────────────────────────
# Ventas TOTALES por canal, en barras verticales (ax.bar). Requisitos:
#   - barras ordenadas de MAYOR a MENOR
#   - eje Y empezando en 0            -> ax.set_ylim(0, ...)
#   - sin marco arriba ni a la derecha -> ax.spines[["top","right"]].set_visible(False)
#   - un titulo que sea una CONCLUSION, no una etiqueta (min. 25 caracteres;
#     "Ventas por canal" no vale, "Movil factura un 7% mas que Web" si)
# Devuelve el objeto fig.
def ej1_barras_por_canal(df):
    fig, ax = plt.subplots(figsize=(7, 4.5))
    # TODO: serie = df.groupby(...)["ventas"].sum().sort_values(ascending=False)
    #       ax.bar(...); ax.set_ylim(0, ...); ax.spines[...]; ax.set_title(...)
    return fig


# ── EJERCICIO 2: la tendencia ─────────────────────────────────────
# Una LINEA (ax.plot) con las ventas totales de cada uno de los 6 meses.
# Requisitos: exactamente 6 puntos, eje Y desde 0, sin marco arriba/derecha,
# y un titulo que mencione lo unico que pasa en la serie (la palabra "junio").
# Pista: mensual = df.set_index("fecha")["ventas"].resample("MS").sum()
def ej2_linea_mensual(df):
    fig, ax = plt.subplots(figsize=(7, 4.5))
    # TODO
    return fig


# ── EJERCICIO 3: un solo color de acento ──────────────────────────
# Barras HORIZONTALES (ax.barh) con las ventas totales por producto (A, B, C, D).
# El producto D es el peor del catalogo: pintalo con ACENTO y los otros TRES con
# GRIS (las constantes estan arriba). Ordena las barras por valor.
# Regla que estas practicando: el color solo se usa cuando SIGNIFICA algo.
def ej3_acento_en_el_peor(df):
    fig, ax = plt.subplots(figsize=(7, 4))
    # TODO: colores = [ACENTO if p == "D" else GRIS for p in serie.index]
    return fig


# ── EJERCICIO 4: la relacion que no existe ────────────────────────
# Dispersion (ax.scatter) de trafico (eje X) contra ventas (eje Y), con las 720
# filas y transparencia (alpha entre 0.1 y 0.6, porque hay muchos puntos
# encimados). Etiqueta ambos ejes con ax.set_xlabel / ax.set_ylabel.
# Titulo honesto: aqui la conclusion es que NO hay relacion.
def ej4_scatter_trafico_ventas(df):
    fig, ax = plt.subplots(figsize=(6.5, 5))
    # TODO
    return fig


# ── EJERCICIO 5: distribucion, no promedio ────────────────────────
# Un boxplot (ax.boxplot) de `ventas` por REGION: 4 cajas, una por region,
# usando el dataset SIN los outliers de la regla IQR (los del Modulo 06).
# Pista para filtrar:
#   q1, q3 = df["ventas"].quantile([0.25, 0.75]); iqr = q3 - q1
#   limpio = df[df["ventas"].between(q1 - 1.5 * iqr, q3 + 1.5 * iqr)]
# Pista para dibujar: ax.boxplot([lista de arrays], tick_labels=[nombres])
def ej5_boxplot_por_region(df):
    fig, ax = plt.subplots(figsize=(7, 4.5))
    # TODO
    return fig


# ── EJERCICIO 6: el grafico enganoso, corregido ───────────────────
# Recibes una figura YA hecha con el truco del eje truncado (empieza en 15000,
# lo que hace parecer que el Norte quintuplica al Sur). Arreglala:
#   - pon el eje Y desde 0
#   - cambia el titulo por uno honesto (min. 25 caracteres)
# y devuelve la MISMA figura. Pista: ax = fig.axes[0]
def ej6_arreglar_enganoso(fig_rota):
    # TODO
    return fig_rota


def _figura_enganosa(df):
    """La figura mentirosa que te toca arreglar en el ejercicio 6. No la toques."""
    serie = df.groupby("region")["ventas"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.bar(serie.index, serie.values, color="#dc2626")
    ax.set_ylim(15000, 22000)
    ax.set_title("Grafico 1")
    return fig


# ══════════════════════════════════════════════════════════════════
#  CORRECTOR - no toques nada de aqui abajo
# ══════════════════════════════════════════════════════════════════
GENERICOS = {"grafico 1", "grafico", "ventas", "ventas por canal", "ventas por region",
             "ventas por producto", "grafico de ventas", "titulo", ""}


def _ax(fig):
    return fig.axes[0]


def _titulo_bueno(ax):
    t = ax.get_title().strip()
    return len(t) >= 25 and t.lower() not in GENERICOS


def _sin_marco(ax):
    return not ax.spines["top"].get_visible() and not ax.spines["right"].get_visible()


def _alturas_barras(ax):
    return [p.get_height() for p in ax.patches]


def _anchos_barras(ax):
    return [p.get_width() for p in ax.patches]


def _colores_barras(ax):
    return [tuple(round(c, 3) for c in p.get_facecolor()) for p in ax.patches]


def _seguro(fn, *args):
    try:
        r = fn(*args)
        return r if isinstance(r, plt.Figure) else TypeError("no devolviste un objeto Figure")
    except Exception as e:
        return e


def corregir():
    df = cargar()
    SALIDA.mkdir(parents=True, exist_ok=True)

    figs = {
        "ej1_barras_canal": _seguro(ej1_barras_por_canal, df),
        "ej2_linea_mensual": _seguro(ej2_linea_mensual, df),
        "ej3_acento": _seguro(ej3_acento_en_el_peor, df),
        "ej4_scatter": _seguro(ej4_scatter_trafico_ventas, df),
        "ej5_boxplot": _seguro(ej5_boxplot_por_region, df),
        "ej6_arreglado": _seguro(ej6_arreglar_enganoso, _figura_enganosa(df)),
    }
    f1, f2, f3, f4, f5, f6 = figs.values()

    def ok(f):
        return isinstance(f, plt.Figure) and len(f.axes) > 0

    def c1():
        ax = _ax(f1)
        alturas = _alturas_barras(ax)
        return (ok(f1) and len(alturas) == 3
                and alturas == sorted(alturas, reverse=True)
                and abs(max(alturas) - 25288.5) < 1
                and ax.get_ylim()[0] == 0 and _sin_marco(ax) and _titulo_bueno(ax))

    def c2():
        ax = _ax(f2)
        ys = list(ax.lines[0].get_ydata())
        return (ok(f2) and len(ax.lines) >= 1 and len(ys) == 6
                and abs(ys[-1] - 10654.5) < 1 and abs(ys[4] - 13554.5) < 1
                and ax.get_ylim()[0] == 0 and _sin_marco(ax)
                and "junio" in ax.get_title().lower())

    def c3():
        ax = _ax(f3)
        anchos = _anchos_barras(ax)      # en barh, el "ancho" es el valor
        colores = _colores_barras(ax)
        acento = tuple(round(c, 3) for c in matplotlib.colors.to_rgba(ACENTO))
        ordenadas = anchos == sorted(anchos) or anchos == sorted(anchos, reverse=True)
        return (ok(f3) and len(anchos) == 4 and ordenadas
                and abs(max(anchos) - 21298.5) < 1        # producto C, el mayor
                and len(set(colores)) == 2 and colores.count(acento) == 1)

    def c4():
        ax = _ax(f4)
        col = ax.collections[0]
        alpha = col.get_alpha()
        if alpha is None:
            alpha = float(col.get_facecolor()[0][3])
        return (ok(f4) and len(col.get_offsets()) == 720 and 0.1 <= alpha <= 0.6
                and ax.get_xlabel().strip() != "" and ax.get_ylabel().strip() != "")

    def c5():
        ax = _ax(f5)
        etiquetas = {t.get_text().strip().upper() for t in ax.get_xticklabels()}
        # matplotlib dibuja 5 lineas por caja (2 bigotes, 2 topes, 1 mediana)
        return (ok(f5) and etiquetas == {"ESTE", "NORTE", "OESTE", "SUR"}
                and len(ax.lines) >= 20)

    def c6():
        ax = _ax(f6)
        return ok(f6) and ax.get_ylim()[0] == 0 and _titulo_bueno(ax)

    checks = [
        ("1. Barras por canal: 3 barras ordenadas, eje desde 0, sin marco, titulo con mensaje", c1),
        ("2. Linea mensual: 6 puntos correctos, eje desde 0, sin marco, titulo que nombra junio", c2),
        ("3. Barras por producto: 4 barras, solo D con el color de acento", c3),
        ("4. Scatter: 720 puntos, con transparencia y los dos ejes etiquetados", c4),
        ("5. Boxplot: 4 cajas (una por region) sobre los datos sin outliers", c5),
        ("6. Grafico enganoso arreglado: eje desde 0 y titulo honesto", c6),
    ]

    print("\n" + "=" * 66)
    print("RESULTADO DE LA ACTIVIDAD")
    print("=" * 66)
    aciertos = 0
    for nombre, comprobar in checks:
        try:
            paso = bool(comprobar())
        except Exception:
            paso = False
        print(f"  {'OK  ' if paso else 'FALLA'}  {nombre}")
        aciertos += paso
    print("-" * 66)
    print(f"  {aciertos}/{len(checks)} correctos")

    guardadas = 0
    for nombre, fig in figs.items():
        if isinstance(fig, plt.Figure):
            fig.savefig(SALIDA / f"{nombre}.png", dpi=150, bbox_inches="tight")
            guardadas += 1
        else:
            print(f"  [{nombre}] {type(fig).__name__}: {fig}")
    print(f"\n  {guardadas} figuras guardadas en {SALIDA}/ - abrelas y MIRALAS.")
    print("  El corrector solo comprueba lo mecanico. Que el grafico comunique")
    print("  algo lo decides tu, y eso solo se ve abriendo el PNG.")

    if aciertos == len(checks):
        print("\n  Perfecto. Listo para el Modulo 08.")
        print("  Ultimo paso, el que de verdad importa: escribe debajo de tus 6 graficos")
        print("  un parrafo SCR (Situacion / Complicacion / Resolucion) que los ate.")


if __name__ == "__main__":
    corregir()
