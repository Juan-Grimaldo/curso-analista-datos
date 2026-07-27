"""
Demo guiado del Módulo 05 — SQL moderno con DuckDB, de principio a fin.

Aquí NADA consulta un CSV: todo corre sobre la BASE DE DATOS data/tienda.duckdb,
que ya creaste en el Módulo 04. Las tablas tienen NOMBRE (`ventas`, `dim_producto`,
`dim_region`) y se consultan sin comillas ni rutas.

Este script se ejecuta en tu repo de práctica `curso-datos`. Cópialo ahí, y desde
la raíz del repo ejecútalo con:  uv run demo_guiado.py
Cada PASO corresponde a una sección del README.

Requisito (en curso-datos):  uv add duckdb  y haber creado la base UNA vez con el
script del Módulo 04:  uv run crear_db.py   → genera data/tienda.duckdb.
"""

import os

import duckdb

DB = "data/tienda.duckdb"   # la base que creaste en el Módulo 04 con crear_db.py


def titulo(n, texto):
    print(f"\n{'=' * 62}\nPASO {n}: {texto}\n{'=' * 62}")


if not os.path.exists(DB):
    raise SystemExit(
        f"Falta la base {DB}. Ejecuta primero el script del Módulo 04:  uv run crear_db.py"
    )

con = duckdb.connect(DB)


def correr(sql):
    """Ejecuta SQL sobre la base y muestra el resultado como tabla."""
    con.sql(sql).show()


# ── PASO 1: CONSULTAR UNA TABLA CON NOMBRE (4.2) ──────────────────
titulo(1, "La tabla 'ventas' vive en la base: se consulta por su nombre (4.2)")
correr("SELECT * FROM ventas LIMIT 5")
n = con.sql("SELECT COUNT(*) AS filas FROM ventas").fetchone()[0]
print(f"La tabla tiene {n} filas y 8 columnas.")

# ── PASO 2: LA CONSULTA FUNDAMENTAL Y SU ORDEN (4.3) ──────────────
titulo(2, "SELECT / WHERE / GROUP BY / HAVING / ORDER BY (4.3)")
correr("""
    SELECT   region, SUM(ventas) AS ventas_total
    FROM     ventas
    WHERE    ventas IS NOT NULL
    GROUP BY region
    HAVING   SUM(ventas) > 1000
    ORDER BY ventas_total DESC
""")
print("Recuerda el orden de EJECUCIÓN: FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT")

# ── PASO 3: FILTRAR BIEN (4.4) ────────────────────────────────────
titulo(3, "Filtrado con IN, BETWEEN y IS NOT NULL (4.4)")
correr("""
    SELECT canal, COUNT(*) AS n_ventas, SUM(ventas) AS total
    FROM   ventas
    WHERE  canal IN ('Web', 'Movil')
      AND  ventas BETWEEN 90 AND 500
    GROUP BY canal
    ORDER BY total DESC
""")

# ── PASO 4: AGREGACIONES (4.5) ────────────────────────────────────
titulo(4, "Agregaciones: COUNT, SUM, AVG, MEDIAN (4.5)")
correr("""
    SELECT
        region,
        COUNT(*)                 AS n_ventas,
        COUNT(DISTINCT producto) AS productos,
        SUM(ventas)              AS total,
        ROUND(AVG(ventas), 1)    AS promedio,
        MEDIAN(ventas)           AS mediana
    FROM ventas
    GROUP BY region
    ORDER BY total DESC
""")

# ── PASO 5: JOIN CON UNA DIMENSIÓN REAL (4.6) ─────────────────────
titulo(5, "JOIN: enriquecer con el nombre del producto desde dim_producto (4.6)")
correr("""
    SELECT p.nombre, COUNT(*) AS n_ventas, SUM(v.ventas) AS total
    FROM ventas v
    LEFT JOIN dim_producto p ON v.producto = p.producto
    GROUP BY p.nombre
    ORDER BY total DESC
""")

# ── PASO 6: CTEs Y RANKING (4.7) ──────────────────────────────────
titulo(6, "Dos CTEs encadenadas: top 3 regiones por mes (4.7)")
correr("""
    WITH ventas_mes AS (
        SELECT DATE_TRUNC('month', fecha) AS mes, region, SUM(ventas) AS total
        FROM ventas
        GROUP BY 1, 2
    ),
    ranking AS (
        SELECT mes, region, total,
               RANK() OVER (PARTITION BY mes ORDER BY total DESC) AS puesto
        FROM ventas_mes
    )
    SELECT * FROM ranking WHERE puesto <= 3 ORDER BY mes, puesto
""")

# ── PASO 7: WINDOW FUNCTIONS — VARIACIÓN MES A MES (4.8) ───────────
titulo(7, "Window function LAG: variación % mes a mes (4.8)")
correr("""
    WITH mensual AS (
        SELECT DATE_TRUNC('month', fecha) AS mes, SUM(ventas) AS total
        FROM ventas
        GROUP BY 1
    )
    SELECT
        mes, total,
        LAG(total) OVER (ORDER BY mes) AS mes_anterior,
        ROUND(100.0 * (total - LAG(total) OVER (ORDER BY mes))
              / LAG(total) OVER (ORDER BY mes), 1) AS variacion_pct
    FROM mensual
    ORDER BY mes
""")
print("El mayor salto es en mayo (+12.5%) y la mayor caída en junio (-21.0%).")

# ── PASO 8: CASE — SEGMENTAR (4.9) ────────────────────────────────
titulo(8, "CASE: segmentar ventas y contar cada segmento (4.9)")
correr("""
    WITH segmentado AS (
        SELECT
            CASE
                WHEN ventas >= 120 THEN 'Alto'
                WHEN ventas >= 90  THEN 'Medio'
                ELSE 'Bajo'
            END AS segmento
        FROM ventas
        WHERE ventas IS NOT NULL
    )
    SELECT segmento, COUNT(*) AS n
    FROM segmentado
    GROUP BY segmento
    ORDER BY n DESC
""")

# ── PASO 9: CONSULTA LISTA PARA DASHBOARD (4.10 / Reto) ────────────
titulo(9, "Métrica por 2 dimensiones + variación temporal (4.10)")
correr("""
    WITH base AS (
        SELECT DATE_TRUNC('month', fecha) AS mes, region, SUM(ventas) AS total
        FROM ventas
        WHERE ventas IS NOT NULL
        GROUP BY 1, 2
    )
    SELECT
        mes, region, total,
        total - LAG(total) OVER (PARTITION BY region ORDER BY mes) AS var_vs_mes_previo
    FROM base
    ORDER BY region, mes
""")

con.close()

print("\nListo. Cada paso es una consulta que puedes copiar a tu propio notebook o script.")
print("Ahora hazlo tú:  uv run actividad_01.py")
