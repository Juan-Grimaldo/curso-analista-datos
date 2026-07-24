"""
Demo guiado del Módulo 04 — SQL moderno con DuckDB, de principio a fin.
Ejecútalo con:  py demo_guiado.py
Cada PASO corresponde a una sección del README. No consultamos un servidor:
DuckDB lee el CSV directamente desde el proceso de Python.

Requisito único:  py -m pip install duckdb
"""

import duckdb

# DuckDB puede leer el CSV directamente por su ruta. Usamos una constante
# para no repetirla en cada consulta.
CSV = "../datasets/ventas_ejemplo.csv"


def titulo(n, texto):
    print(f"\n{'=' * 62}\nPASO {n}: {texto}\n{'=' * 62}")


def correr(sql):
    """Ejecuta SQL sobre el CSV y muestra el resultado como tabla."""
    duckdb.sql(sql).show()


# ── PASO 1: CONSULTAR SIN CARGAR NADA (4.2) ───────────────────────
titulo(1, "DuckDB lee el CSV directo, sin importarlo (4.2)")
correr(f"SELECT * FROM '{CSV}' LIMIT 5")
n = duckdb.sql(f"SELECT COUNT(*) AS filas FROM '{CSV}'").fetchone()[0]
print(f"El archivo tiene {n} filas y 8 columnas.")

# ── PASO 2: LA CONSULTA FUNDAMENTAL Y SU ORDEN (4.3) ──────────────
titulo(2, "SELECT / WHERE / GROUP BY / HAVING / ORDER BY (4.3)")
correr(f"""
    SELECT   region, SUM(ventas) AS ventas_total
    FROM     '{CSV}'
    WHERE    ventas IS NOT NULL
    GROUP BY region
    HAVING   SUM(ventas) > 1000
    ORDER BY ventas_total DESC
""")
print("Recuerda el orden de EJECUCIÓN: FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT")

# ── PASO 3: FILTRAR BIEN (4.4) ────────────────────────────────────
titulo(3, "Filtrado con IN, BETWEEN y IS NOT NULL (4.4)")
correr(f"""
    SELECT canal, COUNT(*) AS n_ventas, SUM(ventas) AS total
    FROM   '{CSV}'
    WHERE  canal IN ('Web', 'Movil')
      AND  ventas BETWEEN 90 AND 500
    GROUP BY canal
    ORDER BY total DESC
""")

# ── PASO 4: AGREGACIONES (4.5) ────────────────────────────────────
titulo(4, "Agregaciones: COUNT, SUM, AVG, MEDIAN (4.5)")
correr(f"""
    SELECT
        region,
        COUNT(*)                 AS n_ventas,
        COUNT(DISTINCT producto) AS productos,
        SUM(ventas)              AS total,
        ROUND(AVG(ventas), 1)    AS promedio,
        MEDIAN(ventas)           AS mediana
    FROM '{CSV}'
    GROUP BY region
    ORDER BY total DESC
""")

# ── PASO 5: JOIN CON UNA TABLA DE REFERENCIA (4.6) ────────────────
titulo(5, "JOIN: enriquecer con nombres de producto (4.6)")
correr(f"""
    WITH ref(producto, nombre) AS (
        VALUES ('A', 'Alfa'), ('B', 'Beta'), ('C', 'Cesar'), ('D', 'Delta')
    )
    SELECT r.nombre, COUNT(*) AS n_ventas, SUM(v.ventas) AS total
    FROM '{CSV}' v
    LEFT JOIN ref r ON v.producto = r.producto
    GROUP BY r.nombre
    ORDER BY total DESC
""")

# ── PASO 6: CTEs Y RANKING (4.7) ──────────────────────────────────
titulo(6, "Dos CTEs encadenadas: top 3 regiones por mes (4.7)")
correr(f"""
    WITH ventas_mes AS (
        SELECT DATE_TRUNC('month', fecha) AS mes, region, SUM(ventas) AS total
        FROM '{CSV}'
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
correr(f"""
    WITH mensual AS (
        SELECT DATE_TRUNC('month', fecha) AS mes, SUM(ventas) AS total
        FROM '{CSV}'
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
correr(f"""
    WITH segmentado AS (
        SELECT
            CASE
                WHEN ventas >= 120 THEN 'Alto'
                WHEN ventas >= 90  THEN 'Medio'
                ELSE 'Bajo'
            END AS segmento
        FROM '{CSV}'
        WHERE ventas IS NOT NULL
    )
    SELECT segmento, COUNT(*) AS n
    FROM segmentado
    GROUP BY segmento
    ORDER BY n DESC
""")

# ── PASO 9: CONSULTA LISTA PARA DASHBOARD (4.10 / Reto) ────────────
titulo(9, "Métrica por 2 dimensiones + variación temporal (4.10)")
correr(f"""
    WITH base AS (
        SELECT DATE_TRUNC('month', fecha) AS mes, region, SUM(ventas) AS total
        FROM '{CSV}'
        WHERE ventas IS NOT NULL
        GROUP BY 1, 2
    )
    SELECT
        mes, region, total,
        total - LAG(total) OVER (PARTITION BY region ORDER BY mes) AS var_vs_mes_previo
    FROM base
    ORDER BY region, mes
""")

print("\nListo. Cada paso es una consulta que puedes copiar a tu propio notebook o script.")
print("Ahora hazlo tú:  py actividad_01.py")
