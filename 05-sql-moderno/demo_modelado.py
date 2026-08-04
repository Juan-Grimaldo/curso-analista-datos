"""
Demo guiado del Módulo 05 — MODELADO de datos para un warehouse.

El SQL que ya sabes escribir sirve de poco si las tablas están mal modeladas: los
totales salen inflados, faltan meses en el dashboard y nadie sabe qué significa una
fila. Aquí construyes el modelo bien: grano, claves, dimensión de tiempo, historia
(SCD tipo 2) y desnormalización.

Este script se ejecuta en tu repo de práctica `curso-datos`. Cópialo ahí y, desde la
raíz del repo, ejecútalo con:  uv run demo_modelado.py
Cada PASO corresponde a una sección del README (4.18).

Requisitos (en curso-datos):
  uv run crear_fuentes.py   y   uv run demo_etl_elt.py   → deja data/warehouse.duckdb
"""

import os
import time

import duckdb

DB = "data/warehouse.duckdb"


def titulo(n, texto):
    print(f"\n{'=' * 72}\nPASO {n}: {texto}\n{'=' * 72}")


if not os.path.exists(DB):
    raise SystemExit(f"Falta {DB}. Ejecuta primero:  uv run demo_etl_elt.py")

con = duckdb.connect(DB)
con.execute("CREATE SCHEMA IF NOT EXISTS modelo")


def correr(sql):
    con.sql(sql).show()


def uno(sql):
    return con.sql(sql).fetchone()[0]


def cronometrar(etiqueta, sql):
    t0 = time.perf_counter()
    filas = con.execute(sql).fetchall()
    print(f"    ⏱  {etiqueta}: {time.perf_counter() - t0:.3f} s   ({len(filas)} filas)")
    return filas


# ── PASO 1: EL GRANO — la pregunta que va PRIMERO ────────────────
titulo(1, "EL GRANO: ¿qué representa exactamente UNA fila? (4.18)")
print("""
El grano es la definición de la fila. Aquí es: "una línea de venta de un producto a
un cliente en una fecha". Todo lo demás (métricas, dimensiones) se decide después.
Si no puedes decir el grano en una frase, el modelo está mal.""")
correr("""
    SELECT
        COUNT(*)                                    AS filas,
        COUNT(DISTINCT venta_id)                    AS ventas_distintas,
        COUNT(*) = COUNT(DISTINCT venta_id)         AS el_grano_se_respeta
    FROM marts.fct_ventas
""")

# ── PASO 2: LA TRAMPA DEL FAN-OUT ────────────────────────────────
titulo(2, "FAN-OUT: cómo un JOIN inocente infla tus totales (4.18)")
# Tabla de campañas: cada producto participó en VARIAS campañas → varias filas por producto
con.execute("""
    CREATE OR REPLACE TABLE modelo.campanas AS
    SELECT p.producto_id, c.campana, c.inversion
    FROM marts.dim_producto p
    CROSS JOIN (VALUES ('Verano', 1000), ('Navidad', 2500), ('Aniversario', 800)) AS c(campana, inversion)
""")
correcto = uno("SELECT ROUND(SUM(monto), 0) FROM marts.fct_ventas")
inflado = uno("""
    SELECT ROUND(SUM(f.monto), 0)
    FROM marts.fct_ventas f
    JOIN modelo.campanas c ON f.producto_id = c.producto_id
""")
print(f"  Ingresos reales                    : {correcto:>12,.0f}")
print(f"  Ingresos tras unir con 'campanas'  : {inflado:>12,.0f}   ← ¡x3!")
print("""
No hay ningún error de SQL: la tabla de campañas tiene 3 filas por producto, así que
cada venta se duplicó 3 veces. Es EL error de análisis más caro y más común.

La regla: nunca unas dos tablas de grano distinto y luego sumes. Agrega primero,
une después (o usa una subconsulta escalar):""")
correr("""
    WITH inversion_por_producto AS (          -- lo llevo al grano de producto ANTES de unir
        SELECT producto_id, SUM(inversion) AS inversion
        FROM modelo.campanas
        GROUP BY 1
    ),
    ventas_por_producto AS (
        SELECT producto_id, SUM(monto) AS ingresos
        FROM marts.fct_ventas
        GROUP BY 1
    )
    SELECT v.producto_id, ROUND(v.ingresos, 0) AS ingresos, i.inversion,
           ROUND(v.ingresos / i.inversion, 1) AS retorno
    FROM ventas_por_producto v
    JOIN inversion_por_producto i ON v.producto_id = i.producto_id
    ORDER BY retorno DESC
    LIMIT 5
""")

# ── PASO 3: CLAVES NATURALES vs SUBROGADAS ───────────────────────
titulo(3, "CLAVES: natural ('P01') vs subrogada (1, 2, 3...) (4.18)")
con.execute("""
    CREATE OR REPLACE TABLE modelo.dim_producto AS
    SELECT
        ROW_NUMBER() OVER (ORDER BY producto_id) AS producto_sk,   -- clave SUBROGADA
        producto_id                              AS producto_nk,   -- clave NATURAL (la del origen)
        nombre, categoria, precio_lista, activo
    FROM marts.dim_producto
""")
correr("SELECT * FROM modelo.dim_producto ORDER BY producto_sk LIMIT 4")
print("""
  Natural  → el código que manda el origen ('P01'). Puede cambiar, repetirse entre
             sistemas o venir sucio.
  Subrogada→ un entero que TÚ controlas. Es estable, ocupa menos, une más rápido y
             permite guardar VARIAS versiones del mismo producto (lo verás en el paso 5).
  En el warehouse, los hechos apuntan a la subrogada; la natural se guarda para auditar.""")

# ── PASO 4: LA DIMENSIÓN DE TIEMPO ───────────────────────────────
titulo(4, "dim_fecha: la dimensión que todo warehouse tiene (4.18)")
con.execute("""
    CREATE OR REPLACE TABLE modelo.dim_fecha AS
    SELECT
        d::DATE                      AS fecha,
        YEAR(d)                      AS anio,
        QUARTER(d)                   AS trimestre,
        MONTH(d)                     AS mes_num,
        MONTHNAME(d)                 AS mes_nombre,
        DAYNAME(d)                   AS dia_semana,
        DAYOFWEEK(d) IN (0, 6)       AS es_fin_de_semana,
        DATE_TRUNC('month', d)::DATE AS primer_dia_mes
    FROM generate_series(DATE '2025-01-01', DATE '2026-12-31', INTERVAL 1 DAY) AS t(d)
""")
correr("SELECT * FROM modelo.dim_fecha LIMIT 3")
print("Sirve para dos cosas que no salen solas del dato:\n")

print("  a) Analizar por atributos de calendario sin repetir DATE_TRUNC en cada consulta:")
correr("""
    SELECT d.es_fin_de_semana, COUNT(*) AS n_ventas, ROUND(AVG(f.monto), 2) AS ticket_medio
    FROM marts.fct_ventas f
    JOIN modelo.dim_fecha d ON f.fecha = d.fecha
    GROUP BY 1
""")

print("  b) Mostrar los días SIN ventas (que en la tabla de hechos, sencillamente, no existen):")
correr("""
    SELECT d.fecha, COALESCE(COUNT(f.venta_id), 0) AS n_ventas
    FROM modelo.dim_fecha d
    LEFT JOIN marts.fct_ventas f ON f.fecha = d.fecha     -- LEFT desde el calendario
    WHERE d.fecha BETWEEN DATE '2026-07-28' AND DATE '2026-08-03'
    GROUP BY 1
    ORDER BY 1
""")
print("Sin dim_fecha, un dashboard 'salta' los días vacíos y las series salen mentirosas.")

# ── PASO 5: SCD TIPO 2 — guardar la HISTORIA ─────────────────────
titulo(5, "SCD tipo 2: qué pasa cuando un cliente cambia de segmento (4.18)")
print("""
Un cliente Retail se convierte en Corporativo en enero de 2026. Si machacas el valor
(SCD tipo 1), TODAS sus ventas de 2025 pasan a contarse como 'Corporativo' y el
histórico cambia solo. Con SCD tipo 2 guardas una fila por versión, con vigencia.""")
con.execute("""
    CREATE OR REPLACE TABLE modelo.dim_cliente_scd2 AS
    WITH base AS (
        SELECT cliente_id, nombre, segmento FROM marts.dim_cliente
    ),
    ascendidos AS (                      -- los que cambian de segmento en 2026
        SELECT cliente_id FROM base
        WHERE segmento = 'Retail' AND CAST(SUBSTR(cliente_id, 2) AS INTEGER) % 5 = 0
    )
    -- Versión histórica (vigente hasta el cambio)
    SELECT b.cliente_id, b.nombre, b.segmento,
           DATE '2023-01-01' AS valido_desde,
           CASE WHEN a.cliente_id IS NOT NULL THEN DATE '2025-12-31' ELSE DATE '9999-12-31' END AS valido_hasta,
           a.cliente_id IS NULL AS es_actual
    FROM base b
    LEFT JOIN ascendidos a ON b.cliente_id = a.cliente_id
    UNION ALL
    -- Versión nueva (solo para los que cambiaron)
    SELECT b.cliente_id, b.nombre, 'Corporativo',
           DATE '2026-01-01', DATE '9999-12-31', TRUE
    FROM base b
    JOIN ascendidos a ON b.cliente_id = a.cliente_id
""")
correr("""
    SELECT * FROM modelo.dim_cliente_scd2
    WHERE cliente_id IN (SELECT cliente_id FROM modelo.dim_cliente_scd2 GROUP BY 1 HAVING COUNT(*) > 1)
    ORDER BY cliente_id, valido_desde
    LIMIT 4
""")

print("  Ingresos por segmento VIGENTE EN LA FECHA DE LA VENTA (lo correcto para el histórico):")
correr("""
    SELECT d.segmento, ROUND(SUM(f.monto), 0) AS ingresos
    FROM marts.fct_ventas f
    JOIN modelo.dim_cliente_scd2 d
      ON f.cliente_id = d.cliente_id
     AND f.fecha BETWEEN d.valido_desde AND d.valido_hasta   -- ← la clave del SCD2
    GROUP BY 1 ORDER BY ingresos DESC
""")
print("  Ingresos por segmento ACTUAL (útil para '¿cuánto me compraron mis clientes VIP de hoy?'):")
correr("""
    SELECT d.segmento, ROUND(SUM(f.monto), 0) AS ingresos
    FROM marts.fct_ventas f
    JOIN modelo.dim_cliente_scd2 d ON f.cliente_id = d.cliente_id AND d.es_actual
    GROUP BY 1 ORDER BY ingresos DESC
""")
print("""
Las dos respuestas son correctas: responden a preguntas distintas. Lo grave es no
saber cuál te está dando tu dashboard.""")

# ── PASO 6: ESTRELLA vs COPO DE NIEVE (normalizar o no) ──────────
titulo(6, "Estrella vs copo de nieve: ¿desnormalizo? (4.18)")
con.execute("""
    CREATE OR REPLACE TABLE modelo.dim_categoria AS
    SELECT ROW_NUMBER() OVER (ORDER BY categoria) AS categoria_sk, categoria,
           CASE categoria WHEN 'Bebidas' THEN 'Alimentacion'
                          WHEN 'Snacks'  THEN 'Alimentacion'
                          ELSE 'Hogar' END AS division
    FROM (SELECT DISTINCT categoria FROM marts.dim_producto)
""")
print("  Copo de nieve (hechos → producto → categoría): 2 JOINs")
cronometrar("copo de nieve", """
    SELECT c.division, ROUND(SUM(f.monto), 0) AS ingresos
    FROM marts.fct_ventas f
    JOIN modelo.dim_producto p  ON f.producto_id = p.producto_nk
    JOIN modelo.dim_categoria c ON p.categoria = c.categoria
    GROUP BY 1 ORDER BY ingresos DESC
""")

con.execute("""
    CREATE OR REPLACE TABLE modelo.dim_producto_plana AS      -- estrella: todo en la dimensión
    SELECT p.producto_sk, p.producto_nk, p.nombre, p.categoria, c.division, p.precio_lista
    FROM modelo.dim_producto p
    JOIN modelo.dim_categoria c ON p.categoria = c.categoria
""")
print("  Estrella (hechos → producto ya con la división dentro): 1 JOIN")
cronometrar("estrella", """
    SELECT p.division, ROUND(SUM(f.monto), 0) AS ingresos
    FROM marts.fct_ventas f
    JOIN modelo.dim_producto_plana p ON f.producto_id = p.producto_nk
    GROUP BY 1 ORDER BY ingresos DESC
""")
print("""
Con 200.000 filas la diferencia son milisegundos; con 500 millones y 5 niveles de
copo, es la diferencia entre 2 segundos y medio minuto. Y hay algo que pesa más que
el tiempo: la estrella la entiende cualquiera que monte el dashboard.
En una base transaccional (OLTP) ganaría lo contrario — normalizar evita
inconsistencias al escribir. Modela según el USO, no por dogma.""")

# ── PASO 7: CHECKLIST DE MODELADO ────────────────────────────────
titulo(7, "Checklist antes de dar por bueno un modelo")
print("""
  1. ¿Puedo decir el GRANO de la tabla de hechos en una frase?
  2. ¿Cada métrica es aditiva en ese grano? (si no, márcalo: %, ratios, stock)
  3. ¿Toda dimensión tiene clave única? ¿Los hechos apuntan a ella sin huérfanos?
  4. ¿Hay riesgo de FAN-OUT en algún JOIN? (¿la dimensión tiene 1 fila por clave?)
  5. ¿Necesito HISTORIA en alguna dimensión? → SCD tipo 2
  6. ¿Tengo dim_fecha? (si no, tus series temporales tendrán agujeros)
  7. ¿Los nombres se entienden sin preguntar? (`ingresos`, no `val_2`)""")

con.close()
print("\nModelo guardado en el esquema `modelo` de data/warehouse.duckdb.")
print("Sigue con:  uv run demo_optimizacion.py")
