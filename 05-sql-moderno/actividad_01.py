"""
ACTIVIDAD 01 — Módulo 05 (SQL moderno con DuckDB)
=================================================
Mismo tipo de análisis que demo_guiado.py, pero ahora TÚ escribes el SQL, y
sobre otras preguntas (foco en `canal` y `producto`).

Este archivo se trabaja en tu repo de práctica `curso-datos`. Cópialo ahí y ejecútalo
desde la raíz del repo con:  uv run actividad_01.py

Cómo funciona:
  - Cada ejercicio te pide RELLENAR una cadena SQL entre las triples comillas.
  - NO cambies los nombres de las variables (SQL_1, SQL_2, ...).
  - Escribe SQL sobre la tabla `{CSV}` (usa la constante CSV con f-string, como en el demo).
  - El corrector del final ejecuta tu SQL y te dice qué está bien y qué no.

Requisito (en curso-datos):  uv add duckdb   y copiar ventas_ejemplo.csv a data/raw/
Pistas: todo está en el README, secciones 4.3 a 4.9. No mires demo_guiado.py
hasta haberlo intentado al menos dos veces.
"""

import duckdb

CSV = "data/raw/ventas_ejemplo.csv"   # el CSV que copiaste a tu repo curso-datos


# ── EJERCICIO 1: total de ventas por canal ────────────────────────
# Devuelve dos columnas: canal, total (SUM de ventas), ordenado de mayor a
# menor total. Ignora las ventas nulas (WHERE ventas IS NOT NULL).
SQL_1 = f"""
    -- TODO: SELECT canal, SUM(...) ... FROM '{CSV}' ... GROUP BY ... ORDER BY ...
"""


# ── EJERCICIO 2: filtrar con IN ───────────────────────────────────
# Cuenta cuántas ventas de los canales 'Web' y 'Movil' superaron 150.
# Devuelve UNA sola columna con ese número (un COUNT).
SQL_2 = f"""
    -- TODO: SELECT COUNT(*) FROM '{CSV}' WHERE canal IN (...) AND ventas > ...
"""


# ── EJERCICIO 3: segmentar con CASE ───────────────────────────────
# Clasifica cada venta (no nula) en 'Alto' (>=120), 'Medio' (>=90) o 'Bajo',
# y cuenta cuántas hay en cada segmento. Devuelve: segmento, n — ordenado por
# n de mayor a menor. (Envuelve el CASE en una CTE, como en el demo paso 8.)
SQL_3 = f"""
    -- TODO: WITH segmentado AS (SELECT CASE ... END AS segmento ...) SELECT segmento, COUNT(*) ...
"""


# ── EJERCICIO 4: promedio por producto ────────────────────────────
# Para cada producto, calcula el promedio de ventas redondeado a 2 decimales.
# Devuelve: producto, promedio — ordenado por promedio de mayor a menor.
# (El primero de la lista es el producto con el ticket medio más alto.)
SQL_4 = f"""
    -- TODO: SELECT producto, ROUND(AVG(ventas), 2) ... GROUP BY producto ORDER BY ...
"""


# ── EJERCICIO 5: top 3 productos con window function ──────────────
# Usa RANK() OVER (ORDER BY SUM(ventas) DESC) para rankear los productos por
# ventas totales, y quédate solo con los 3 primeros.
# Devuelve: producto, total, puesto (1, 2, 3).
SQL_5 = f"""
    -- TODO: envuelve el RANK() en una CTE y filtra WHERE puesto <= 3
"""


# ── EJERCICIO 6: variación mes a mes con LAG ──────────────────────
# Agrega ventas por mes (DATE_TRUNC('month', fecha)) y calcula la variación
# porcentual respecto al mes anterior con LAG (como el demo paso 7).
# Devuelve: mes, total, variacion_pct — ordenado por mes ascendente.
SQL_6 = f"""
    -- TODO: WITH mensual AS (...) SELECT mes, total, ROUND(100.0*(...)/LAG(...), 1) ...
"""


# ══════════════════════════════════════════════════════════════════
#  CORRECTOR — no toques nada de aquí abajo
# ══════════════════════════════════════════════════════════════════
def corregir():
    def rows(sql):
        try:
            return duckdb.sql(sql).fetchall()
        except Exception as e:
            return e

    r1 = rows(SQL_1)
    r2 = rows(SQL_2)
    r3 = rows(SQL_3)
    r4 = rows(SQL_4)
    r5 = rows(SQL_5)
    r6 = rows(SQL_6)

    def ok(r):
        return isinstance(r, list) and len(r) > 0

    checks = [
        ("1. Total por canal: líder es Movil con 24854",
         ok(r1) and r1[0][0] == "Movil" and r1[0][1] == 24854),
        ("1b. Canales ordenados de mayor a menor",
         ok(r1) and len(r1) == 3 and [x[0] for x in r1] == ["Movil", "Web", "Tienda"]),
        ("2. Ventas Web+Movil > 150 son 39",
         ok(r2) and r2[0][0] == 39),
        ("3. Segmento más frecuente es 'Bajo' con 353",
         ok(r3) and r3[0][0] == "Bajo" and r3[0][1] == 353),
        ("3b. Tres segmentos: Bajo 353, Medio 191, Alto 172",
         ok(r3) and {row[0]: row[1] for row in r3} == {"Bajo": 353, "Medio": 191, "Alto": 172}),
        ("4. Producto con mayor promedio es C (143.21)",
         ok(r4) and r4[0][0] == "C" and round(float(r4[0][1]), 2) == 143.21),
        ("5. Top 3 productos por RANK: C, A, B",
         ok(r5) and [x[0] for x in r5] == ["C", "A", "B"]),
        ("6. Junio es la mayor caída (-21.0%)",
         _mayor_caida(r6) == -21.0),
        ("6b. Mayo es la mayor subida (+12.5%)",
         _mayor_subida(r6) == 12.5),
    ]

    print("\n" + "=" * 52)
    print("RESULTADO DE LA ACTIVIDAD")
    print("=" * 52)
    aciertos = 0
    for nombre, paso in checks:
        try:
            paso = bool(paso)
        except Exception:
            paso = False
        print(f"  {'OK  ' if paso else 'FALLA'}  {nombre}")
        aciertos += paso
    print("-" * 52)
    print(f"  {aciertos}/{len(checks)} correctos")
    if aciertos == len(checks):
        print("\n  Perfecto. Listo para el Módulo 06.")
    else:
        print("\n  Revisa los FALLA. Si una consulta lanza error, imprime el resultado")
        print("  con duckdb.sql(SQL_N).show() para depurarla.")


def _mayor_caida(r):
    if not isinstance(r, list):
        return None
    vals = [row[2] for row in r if len(row) >= 3 and row[2] is not None]
    return round(min(vals), 1) if vals else None


def _mayor_subida(r):
    if not isinstance(r, list):
        return None
    vals = [row[2] for row in r if len(row) >= 3 and row[2] is not None]
    return round(max(vals), 1) if vals else None


if __name__ == "__main__":
    corregir()
