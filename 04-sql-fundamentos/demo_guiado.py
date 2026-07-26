"""
Demo guiado del Módulo 04 — SQL: fundamentos, de principio a fin con DuckDB.

Este script se ejecuta en tu repo de práctica `curso-datos`. Cópialo ahí, y desde
la raíz del repo ejecútalo con:  uv run demo_guiado.py
Cada PASO corresponde a una sección del README. DuckDB lee el CSV directamente,
sin servidores ni configuración.

Requisito (en curso-datos):  uv add duckdb   y copiar ventas_ejemplo.csv a data/raw/
"""

import os

import duckdb

# DuckDB consulta el CSV por su ruta, como si fuera una tabla.
CSV = "data/raw/ventas_ejemplo.csv"   # el CSV que copiaste a tu repo curso-datos


def titulo(n, texto):
    print(f"\n{'=' * 62}\nPASO {n}: {texto}\n{'=' * 62}")


def correr(sql):
    """Ejecuta SQL sobre el CSV y muestra el resultado como tabla."""
    duckdb.sql(sql).show()


# ── PASO 1: MIRAR LA TABLA (4.2) ──────────────────────────────────
titulo(1, "DuckDB lee el CSV directo, sin importar nada (4.2)")
correr(f"SELECT * FROM '{CSV}' LIMIT 5")

# ── PASO 2: SELECT — ELEGIR COLUMNAS (4.3) ────────────────────────
titulo(2, "SELECT: pedir solo las columnas que interesan (4.3)")
correr(f"""
    SELECT fecha, region, ventas
    FROM '{CSV}'
    LIMIT 10
""")

# ── PASO 3: WHERE — FILTRAR FILAS (4.4) ───────────────────────────
titulo(3, "WHERE: quedarse con las filas que cumplen una condición (4.4)")
correr(f"""
    SELECT region, producto, ventas
    FROM '{CSV}'
    WHERE region = 'Norte' AND ventas > 150
""")

# ── PASO 4: ORDER BY + LIMIT — TOP N (4.5) ────────────────────────
titulo(4, "ORDER BY + LIMIT: las 5 ventas más altas (4.5)")
correr(f"""
    SELECT fecha, region, producto, ventas
    FROM '{CSV}'
    ORDER BY ventas DESC
    LIMIT 5
""")

# ── PASO 5: AGREGACIONES — RESUMIR EN UN NÚMERO (4.6) ─────────────
titulo(5, "COUNT / SUM / AVG / MIN / MAX (4.6)")
correr(f"""
    SELECT
        COUNT(*)              AS n_filas,
        SUM(ventas)           AS total,
        ROUND(AVG(ventas), 2) AS promedio,
        MIN(ventas)           AS minimo,
        MAX(ventas)           AS maximo
    FROM '{CSV}'
""")

# ── PASO 6: GROUP BY — RESUMIR POR CATEGORÍA (4.7) ────────────────
titulo(6, "GROUP BY: total de ventas por región (4.7)")
correr(f"""
    SELECT region, SUM(ventas) AS total
    FROM '{CSV}'
    GROUP BY region
    ORDER BY total DESC
""")

# ── PASO 7: HAVING — FILTRAR LOS GRUPOS (4.8) ─────────────────────
titulo(7, "HAVING: solo los canales que superan 23500 en ventas (4.8)")
correr(f"""
    SELECT canal, SUM(ventas) AS total
    FROM '{CSV}'
    GROUP BY canal
    HAVING SUM(ventas) > 23500
    ORDER BY total DESC
""")

# ── PASO 8: ALIAS Y COLUMNA CALCULADA (4.9) ───────────────────────
titulo(8, "Columna calculada: ventas con IVA (4.9)")
correr(f"""
    SELECT
        producto,
        ventas,
        ROUND(ventas * 1.18, 2) AS ventas_con_iva
    FROM '{CSV}'
    LIMIT 5
""")

# ── PASO 9: DISTINCT — VALORES ÚNICOS (4.10) ──────────────────────
titulo(9, "DISTINCT: cuántos productos y canales distintos hay (4.10)")
correr(f"""
    SELECT
        COUNT(DISTINCT producto) AS productos_distintos,
        COUNT(DISTINCT canal)    AS canales_distintos
    FROM '{CSV}'
""")

# ── PASO 10: JOIN SOBRE UNA BASE DE DATOS REAL (4.11) ─────────────
titulo(10, "JOIN: unir la tabla de hechos con sus dimensiones (4.11)")
DB = "data/tienda.duckdb"
if not os.path.exists(DB):
    print("  Falta la base. Ejecuta primero:  uv run crear_db.py")
else:
    con = duckdb.connect(DB)

    print("INNER JOIN — ventas por CATEGORÍA de producto:")
    con.sql("""
        SELECT p.categoria, SUM(v.ventas) AS total
        FROM ventas v
        JOIN dim_producto p ON v.producto = p.producto
        GROUP BY p.categoria
        ORDER BY total DESC
    """).show()

    print("INNER JOIN — ventas por ZONA (uniendo con dim_region):")
    con.sql("""
        SELECT r.zona, r.responsable, SUM(v.ventas) AS total
        FROM ventas v
        JOIN dim_region r ON v.region = r.region
        GROUP BY r.zona, r.responsable
        ORDER BY total DESC
    """).show()

    con.close()

print("\nListo. Estas consultas son todo lo que necesitas para empezar en SQL.")
print("Ahora hazlo tú:  uv run actividad_01.py")
