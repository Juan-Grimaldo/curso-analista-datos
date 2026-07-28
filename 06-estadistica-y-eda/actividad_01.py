"""
ACTIVIDAD 01 - Modulo 06 (Estadistica aplicada y EDA)
=====================================================
Mismo tipo de analisis que demo_guiado.py, pero ahora TU escribes el codigo, y
sobre otras preguntas (foco en `producto`, `descuento` y `trafico`).

Este archivo se trabaja en tu repo de practica `curso-datos`. Copialo ahi y
ejecutalo desde la raiz del repo con:  uv run actividad_01.py

Como funciona:
  - Cada ejercicio es una FUNCION que debes completar (donde dice TODO).
  - NO cambies los nombres de las funciones ni lo que se te pide devolver.
  - El corrector del final las ejecuta y te dice que esta bien y que no.
  - `cargar()` ya te entrega el dataset limpio: no toques esa parte.

Requisitos (en curso-datos):  uv add pandas scipy
y copiar ventas_ejemplo.csv del material a  data/raw/

Pistas: todo esta en el README, secciones 5.1 a 5.9. No mires demo_guiado.py
hasta haberlo intentado al menos dos veces.
"""

import numpy as np
import pandas as pd
from scipy import stats

CSV = "data/raw/ventas_ejemplo.csv"


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


# ── EJERCICIO 1: la tabla que siempre miras primero ───────────────
# Devuelve un DICCIONARIO con la descriptiva de la columna `trafico`:
#   {"media": ..., "mediana": ..., "std": ..., "q1": ..., "q3": ...}
# Redondea cada valor a 1 decimal.  (Pista: .mean(), .median(), .std(), .quantile())
def ej1_descriptiva_trafico(df):
    # TODO: return {"media": round(...), "mediana": ..., "std": ..., "q1": ..., "q3": ...}
    ...


# ── EJERCICIO 2: media vs mediana por producto ────────────────────
# Devuelve un DataFrame con una fila por producto (A, B, C, D) y las columnas
# exactas: media, mediana, gap   donde gap = media - mediana (redondea todo a 2).
# Ordenalo por `gap` de mayor a menor: arriba quedara el producto cuya media
# esta mas inflada respecto a su mediana (= el mas contaminado por outliers).
# Pista: df.groupby("producto")["ventas"].agg(media="mean", mediana="median")
def ej2_media_vs_mediana_por_producto(df):
    # TODO
    ...


# ── EJERCICIO 3: outliers con la regla IQR ────────────────────────
# Devuelve una TUPLA (lim_inf, lim_sup, n_outliers) para la columna `trafico`.
# Redondea los limites a 1 decimal. n_outliers es un entero.
# Sorpresa esperada: trafico no tiene ninguno. Que NO haya outliers tambien se
# reporta: significa que esa variable esta bien comportada.
def ej3_outliers_trafico(df):
    # TODO: q1, q3 = ...; iqr = q3 - q1; ...
    ...


# ── EJERCICIO 4: el outlier que la regla IQR no ve ────────────────
# El limite inferior del IQR sobre `ventas` es negativo, asi que la regla no
# marca ningun outlier BAJO. Pero hay una venta de 0.0, que es imposible en la
# practica. Devuelve cuantas filas tienen ventas == 0 (un entero).
# Moraleja: las reglas automaticas no sustituyen mirar los datos.
def ej4_ventas_en_cero(df):
    # TODO
    ...


# ── EJERCICIO 5: intervalo de confianza al 95% ────────────────────
# Devuelve (lim_inf, lim_sup) del IC 95% para la MEDIA de `trafico`,
# redondeados a 2 decimales.
# Pasos: n = len(s); error_estandar = s.std(ddof=1) / np.sqrt(n)
#        stats.t.interval(0.95, n - 1, loc=s.mean(), scale=error_estandar)
def ej5_ic95_trafico(df):
    # TODO
    ...


# ── EJERCICIO 6: test de hipotesis con descuento ──────────────────
# Pregunta de negocio: "las ventas con descuento son mayores que las que no?"
# Compara con un t-test de Welch (equal_var=False) las ventas de las filas con
# descuento > 0 contra las de descuento == 0.
# Devuelve la tupla (media_con_desc, media_sin_desc, p_valor) redondeada a 3.
# Spoiler: p sera enorme. Tu conclusion correcta es "no hay evidencia", no
# "el descuento no sirve" (son cosas distintas).
def ej6_test_descuento(df):
    # TODO: con = df.loc[df["descuento"] > 0, "ventas"]; sin_ = ...
    #       stats.ttest_ind(con, sin_, equal_var=False)
    ...


# ── EJERCICIO 7: correlacion dentro de cada subgrupo ──────────────
# En el demo viste que la correlacion global ventas-trafico es ~ -0.035.
# Calculala AHORA dentro de cada canal por separado y devuelve un diccionario
# {"Movil": ..., "Tienda": ..., "Web": ...} con cada correlacion redondeada a 3.
# Veras que el signo cambia entre canales: agregar puede esconder subgrupos
# que se comportan al reves (la idea detras de la paradoja de Simpson).
def ej7_corr_por_canal(df):
    # TODO: for canal, grupo in df.groupby("canal"): grupo["ventas"].corr(grupo["trafico"])
    ...


# ── EJERCICIO 8: tu propia funcion de EDA ─────────────────────────
# Devuelve un diccionario resumen de CUALQUIER DataFrame que reciba:
#   {"filas": ..., "columnas": ..., "duplicados": ..., "col_mas_nulos": ...}
# donde col_mas_nulos es el NOMBRE de la columna con mas nulos (str).
# Debe funcionar tambien sobre el CSV crudo (sin limpiar), no solo sobre el limpio.
# Esta es la funcion que te llevas a src/ para todos tus proyectos futuros.
def ej8_resumen(datos):
    # TODO
    ...


# ══════════════════════════════════════════════════════════════════
#  CORRECTOR - no toques nada de aqui abajo
# ══════════════════════════════════════════════════════════════════
def _seguro(fn, *args):
    try:
        return fn(*args)
    except Exception as e:
        return e


def corregir():
    df = cargar()
    crudo = pd.read_csv(CSV, parse_dates=["fecha"])

    r1 = _seguro(ej1_descriptiva_trafico, df)
    r2 = _seguro(ej2_media_vs_mediana_por_producto, df)
    r3 = _seguro(ej3_outliers_trafico, df)
    r4 = _seguro(ej4_ventas_en_cero, df)
    r5 = _seguro(ej5_ic95_trafico, df)
    r6 = _seguro(ej6_test_descuento, df)
    r7 = _seguro(ej7_corr_por_canal, df)
    r8 = _seguro(ej8_resumen, crudo)

    def dic(r, esperado):
        return isinstance(r, dict) and all(
            k in r and abs(float(r[k]) - v) < 0.15 for k, v in esperado.items()
        )

    def tupla(r, esperado, tol=0.02):
        return (
            isinstance(r, (tuple, list))
            and len(r) == len(esperado)
            and all(abs(float(a) - b) <= tol for a, b in zip(r, esperado))
        )

    checks = [
        ("1. Descriptiva de trafico: media 287.1, mediana 305.5, std 130.9",
         lambda: dic(r1, {"media": 287.1, "mediana": 305.5, "std": 130.9,
                          "q1": 174.0, "q3": 404.2})),
        ("2. El producto con mayor gap media-mediana es A (+11.17)",
         lambda: isinstance(r2, pd.DataFrame) and list(r2.columns) == ["media", "mediana", "gap"]
         and r2.index[0] == "A" and abs(float(r2["gap"].iloc[0]) - 11.17) < 0.1),
        ("2b. Las 4 filas ordenadas por gap: A, D, B, C",
         lambda: isinstance(r2, pd.DataFrame) and list(r2.index) == ["A", "D", "B", "C"]),
        ("3. Trafico: limites [-171.4, 749.6] y 0 outliers",
         lambda: tupla(r3, (-171.4, 749.6, 0), tol=0.15)),
        ("4. Hay exactamente 1 venta con importe 0",
         lambda: int(r4) == 1),
        ("5. IC 95% de la media de trafico: [277.53, 296.70]",
         lambda: tupla(r5, (277.53, 296.70), tol=0.05)),
        ("6. Medias 100.64 (con desc.) vs 100.28 (sin) y p-valor 0.955",
         lambda: tupla(r6, (100.64, 100.28, 0.955), tol=0.02)),
        ("7. Correlacion ventas-trafico por canal: Web +0.121, Movil -0.080, Tienda -0.059",
         lambda: dic(r7, {"Movil": -0.080, "Tienda": -0.059, "Web": 0.121})),
        ("8. Resumen del CSV crudo: 735 filas, 8 columnas, 15 duplicados, mas nulos en 'ventas'",
         lambda: isinstance(r8, dict) and r8.get("filas") == 735 and r8.get("columnas") == 8
         and r8.get("duplicados") == 15 and r8.get("col_mas_nulos") == "ventas"),
    ]

    print("\n" + "=" * 62)
    print("RESULTADO DE LA ACTIVIDAD")
    print("=" * 62)
    aciertos = 0
    for nombre, comprobar in checks:
        try:
            paso = bool(comprobar())
        except Exception:
            paso = False
        print(f"  {'OK  ' if paso else 'FALLA'}  {nombre}")
        aciertos += paso
    print("-" * 62)
    print(f"  {aciertos}/{len(checks)} correctos")

    errores = [(i + 1, r) for i, r in enumerate([r1, r2, r3, r4, r5, r6, r7, r8])
               if isinstance(r, Exception)]
    for i, e in errores:
        print(f"  [ej{i}] lanzo una excepcion: {type(e).__name__}: {e}")

    if aciertos == len(checks):
        print("\n  Perfecto. Listo para el Modulo 07.")
    else:
        print("\n  Revisa los FALLA. Si no sabes que devuelve tu funcion, imprimela:")
        print("    df = cargar(); print(ej1_descriptiva_trafico(df))")

    print("\n  Pregunta final (no la corrige nadie, pero es la que importa):")
    print("  con los resultados de los ejercicios 6 y 7, que le dirias a un jefe")
    print("  que quiere lanzar una campana de descuentos 'porque los descuentos venden'?")


if __name__ == "__main__":
    corregir()
