"""
ACTIVIDAD 01 — Módulo 04 (SQL: fundamentos)
===========================================
Tú escribes el SQL. Son preguntas básicas: SELECT, WHERE, ORDER BY, COUNT/SUM/AVG,
GROUP BY, HAVING y DISTINCT. Nada de CTEs ni window functions (eso es el Módulo 05).

Antes de empezar (una vez):  py crear_db.py   → crea data/tienda.duckdb (para el ej. 8).

Cómo funciona:
  - Cada ejercicio te pide RELLENAR una cadena SQL entre las triples comillas.
  - NO cambies los nombres de las variables (SQL_1, SQL_2, ...).
  - Ejercicios 1-7: SQL sobre el CSV '{CSV}' (usa la constante CSV con f-string).
  - Ejercicio 8: SQL sobre las tablas de la base (ventas, dim_producto), sin comillas.
  - Ejecuta:  py actividad_01.py
  - El corrector del final ejecuta tu SQL y te dice qué está bien y qué no.

Pistas: todo está en el README, secciones 4.3 a 4.11. No mires demo_guiado.py hasta
haberlo intentado al menos dos veces.
"""

import duckdb

CSV = "../datasets/ventas_ejemplo.csv"


# ── EJERCICIO 1: contar filas con WHERE ───────────────────────────
# ¿Cuántas filas hay de la región 'Norte'? Devuelve UN número (un COUNT).
SQL_1 = f"""
    -- TODO: SELECT COUNT(*) FROM '{CSV}' WHERE region = '...'
"""


# ── EJERCICIO 2: sumar una columna ────────────────────────────────
# ¿Cuál es el total de TODAS las ventas del dataset? Devuelve UN número (un SUM).
SQL_2 = f"""
    -- TODO: SELECT SUM(...) FROM '{CSV}'
"""


# ── EJERCICIO 3: GROUP BY + ORDER BY ──────────────────────────────
# Total de ventas por región, ordenado de mayor a menor.
# Devuelve dos columnas: region, total. (El primero es la región líder.)
SQL_3 = f"""
    -- TODO: SELECT region, SUM(...) FROM '{CSV}' GROUP BY region ORDER BY ... DESC
"""


# ── EJERCICIO 4: promedio por grupo ───────────────────────────────
# Promedio de ventas por producto, redondeado a 2 decimales, de mayor a menor.
# Devuelve: producto, promedio. (El primero es el producto con ticket medio más alto.)
SQL_4 = f"""
    -- TODO: SELECT producto, ROUND(AVG(...), 2) FROM '{CSV}' GROUP BY producto ORDER BY ... DESC
"""


# ── EJERCICIO 5: contar valores distintos ─────────────────────────
# ¿Cuántos canales DISTINTOS hay? Devuelve UN número.
SQL_5 = f"""
    -- TODO: SELECT COUNT(DISTINCT ...) FROM '{CSV}'
"""


# ── EJERCICIO 6: HAVING ───────────────────────────────────────────
# Muestra solo los canales cuyo total de ventas supere 23500.
# Devuelve: canal, total — ordenado de mayor a menor. (Deben quedar 2 canales.)
SQL_6 = f"""
    -- TODO: SELECT canal, SUM(...) FROM '{CSV}' GROUP BY canal HAVING SUM(...) > 23500 ORDER BY ...
"""


# ── EJERCICIO 7: WHERE con dos condiciones ────────────────────────
# ¿Cuántas ventas del producto 'C' superaron los 200? Devuelve UN número.
SQL_7 = f"""
    -- TODO: SELECT COUNT(*) FROM '{CSV}' WHERE producto = '...' AND ventas > ...
"""


# ── EJERCICIO 8: JOIN sobre la base de datos ──────────────────────
# Requisito: haber ejecutado antes  py crear_db.py  (crea data/tienda.duckdb).
# Une 'ventas' con 'dim_producto' por la columna 'producto' y calcula el
# total de ventas por CATEGORÍA, ordenado de mayor a menor.
# Devuelve: categoria, total. (La categoría líder debe salir primera.)
# Escribe la consulta sobre las tablas 'ventas' y 'dim_producto' (sin comillas ni CSV).
SQL_8 = """
    -- TODO: SELECT p.categoria, SUM(v.ventas) AS total
    --       FROM ventas v JOIN dim_producto p ON v.producto = p.producto
    --       GROUP BY p.categoria ORDER BY total DESC
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

    def rows_db(sql):
        try:
            con = duckdb.connect("data/tienda.duckdb")
            r = con.execute(sql).fetchall()
            con.close()
            return r
        except Exception as e:
            return e

    def ok(r):
        return isinstance(r, list) and len(r) > 0

    r1, r2, r3 = rows(SQL_1), rows(SQL_2), rows(SQL_3)
    r4, r5, r6, r7 = rows(SQL_4), rows(SQL_5), rows(SQL_6), rows(SQL_7)
    r8 = rows_db(SQL_8)

    checks = [
        ("1. Filas de la región Norte = 194",
         ok(r1) and r1[0][0] == 194),
        ("2. Total de ventas = 71942",
         ok(r2) and r2[0][0] == 71942),
        ("3. Región líder es Norte (21387)",
         ok(r3) and r3[0][0] == "Norte" and r3[0][1] == 21387),
        ("3b. Cuatro regiones ordenadas de mayor a menor",
         ok(r3) and [x[0] for x in r3] == ["Norte", "Este", "Oeste", "Sur"]),
        ("4. Producto con mayor promedio es C (143.21)",
         ok(r4) and r4[0][0] == "C" and round(float(r4[0][1]), 2) == 143.21),
        ("5. Canales distintos = 3",
         ok(r5) and r5[0][0] == 3),
        ("6. HAVING deja 2 canales: Movil y Web",
         ok(r6) and len(r6) == 2 and [x[0] for x in r6] == ["Movil", "Web"]),
        ("7. Ventas del producto C > 200 son 2",
         ok(r7) and r7[0][0] == 2),
        ("8. JOIN: categoría líder es Bebidas (41696)",
         ok(r8) and r8[0][0] == "Bebidas" and r8[0][1] == 41696),
        ("8b. Dos categorías: Bebidas 41696, Snacks 30246",
         ok(r8) and {x[0]: x[1] for x in r8} == {"Bebidas": 41696, "Snacks": 30246}),
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
        print("\n  Perfecto. Ya dominas lo básico. Listo para el Módulo 05 (SQL moderno).")
    else:
        print("\n  Revisa los FALLA. Si una consulta lanza error, imprime el resultado")
        print("  con duckdb.sql(SQL_N).show() para depurarla.")


if __name__ == "__main__":
    corregir()
