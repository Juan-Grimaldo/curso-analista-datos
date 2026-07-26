"""
Demo guiado del Módulo 04 — SQL: fundamentos, TODO sobre la BASE DE DATOS (DuckDB).

Versión gemela de demo_guiado.py, pero aquí NADA consulta el CSV: todas las
consultas corren sobre la tabla `ventas` (y las dimensiones) de data/tienda.duckdb.
Así se ve cómo, una vez que los datos viven en una base, las tablas tienen NOMBRE
y se consultan sin comillas ni rutas.

Este script se ejecuta en tu repo de práctica `curso-datos`. Cópialo ahí, y desde
la raíz del repo ejecútalo con:  uv run demo_guiado_bd.py
Cada PASO corresponde a una sección del README.

Requisito (en curso-datos):  uv add duckdb  y haber creado la base UNA vez:
    uv run crear_db.py        → genera data/tienda.duckdb (ventas + dimensiones)
"""

import os

import duckdb

DB = "data/tienda.duckdb"   # la base que creaste con crear_db.py


def titulo(n, texto):
    print(f"\n{'=' * 62}\nPASO {n}: {texto}\n{'=' * 62}")


if not os.path.exists(DB):
    raise SystemExit(
        f"Falta la base {DB}. Ejecuta primero:  uv run crear_db.py"
    )

con = duckdb.connect(DB)


def correr(sql):
    """Ejecuta SQL sobre la base y muestra el resultado como tabla."""
    con.sql(sql).show()


# ── PASO 1: MIRAR LA TABLA (4.2) ──────────────────────────────────
titulo(1, "La tabla 'ventas' vive en la base: se consulta por su nombre (4.2)")
correr("SELECT * FROM ventas LIMIT 5")

# ── PASO 2: SELECT — ELEGIR COLUMNAS (4.3) ────────────────────────
titulo(2, "SELECT: pedir solo las columnas que interesan (4.3)")
correr("""
    SELECT fecha, region, ventas
    FROM ventas
    LIMIT 10
""")

# ── PASO 3: WHERE — FILTRAR FILAS (4.4) ───────────────────────────
titulo(3, "WHERE: quedarse con las filas que cumplen una condición (4.4)")
correr("""
    SELECT region, producto, ventas
    FROM ventas
    WHERE region = 'Norte' AND ventas > 150
""")

# ── PASO 4: ORDER BY + LIMIT — TOP N (4.5) ────────────────────────
titulo(4, "ORDER BY + LIMIT: las 5 ventas más altas (4.5)")
correr("""
    SELECT fecha, region, producto, ventas
    FROM ventas
    ORDER BY ventas DESC
    LIMIT 5
""")

# ── PASO 5: AGREGACIONES — RESUMIR EN UN NÚMERO (4.6) ─────────────
titulo(5, "COUNT / SUM / AVG / MIN / MAX (4.6)")
correr("""
    SELECT
        COUNT(*)              AS n_filas,
        SUM(ventas)           AS total,
        ROUND(AVG(ventas), 2) AS promedio,
        MIN(ventas)           AS minimo,
        MAX(ventas)           AS maximo
    FROM ventas
""")

# ── PASO 6: GROUP BY — RESUMIR POR CATEGORÍA (4.7) ────────────────
titulo(6, "GROUP BY: total de ventas por región (4.7)")
correr("""
    SELECT region, SUM(ventas) AS total
    FROM ventas
    GROUP BY region
    ORDER BY total DESC
""")

# ── PASO 7: HAVING — FILTRAR LOS GRUPOS (4.8) ─────────────────────
titulo(7, "HAVING: solo los canales que superan 23500 en ventas (4.8)")
correr("""
    SELECT canal, SUM(ventas) AS total
    FROM ventas
    GROUP BY canal
    HAVING SUM(ventas) > 23500
    ORDER BY total DESC
""")

# ── PASO 8: ALIAS Y COLUMNA CALCULADA (4.9) ───────────────────────
titulo(8, "Columna calculada: ventas con IVA (4.9)")
correr("""
    SELECT
        producto,
        ventas,
        ROUND(ventas * 1.18, 2) AS ventas_con_iva
    FROM ventas
    LIMIT 5
""")

# ── PASO 9: DISTINCT — VALORES ÚNICOS (4.10) ──────────────────────
titulo(9, "DISTINCT: cuántos productos y canales distintos hay (4.10)")
correr("""
    SELECT
        COUNT(DISTINCT producto) AS productos_distintos,
        COUNT(DISTINCT canal)    AS canales_distintos
    FROM ventas
""")

# ── PASO 10: JOIN CON LAS DIMENSIONES (4.11) ──────────────────────
titulo(10, "JOIN: unir la tabla de hechos con sus dimensiones (4.11)")

print("INNER JOIN — ventas por CATEGORÍA de producto:")
correr("""
    SELECT p.categoria, SUM(v.ventas) AS total
    FROM ventas v
    JOIN dim_producto p ON v.producto = p.producto
    GROUP BY p.categoria
    ORDER BY total DESC
""")

print("INNER JOIN — ventas por ZONA (uniendo con dim_region):")
correr("""
    SELECT r.zona, r.responsable, SUM(v.ventas) AS total
    FROM ventas v
    JOIN dim_region r ON v.region = r.region
    GROUP BY r.zona, r.responsable
    ORDER BY total DESC
""")

con.close()

print("\nListo. La misma SQL de siempre, pero sobre tablas con nombre en una base.")
print("Ahora hazlo tú:  uv run actividad_bd.py")
