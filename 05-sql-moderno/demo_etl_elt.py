"""
Demo guiado del Módulo 05 — ETL vs ELT con SQL, de principio a fin.

Construyes un mini **data warehouse** local con DuckDB a partir de 3 fuentes crudas:
un CSV grande de ventas, un CSV de clientes y un JSON de productos. Primero verás el
camino clásico (ETL: transformar antes de cargar) y luego el camino moderno
(ELT: cargar crudo y transformar dentro con SQL, en capas raw → staging → marts).

Este script se ejecuta en tu repo de práctica `curso-datos`. Cópialo ahí y, desde la
raíz del repo, ejecútalo con:  uv run demo_etl_elt.py
Cada PASO corresponde a una sección del README (4.11 a 4.17).

Requisitos (en curso-datos):
  uv add duckdb
  uv run crear_fuentes.py     → genera las fuentes crudas en data/raw/
"""

import csv
import os
import time

import duckdb

CRUDO = "data/raw/ventas_crudas.csv"
LOTE2 = "data/raw/ventas_crudas_lote2.csv"
CLIENTES = "data/raw/clientes.csv"
PRODUCTOS = "data/raw/productos.json"
DB = "data/warehouse.duckdb"     # nuestro "almacén de datos" local


def titulo(n, texto):
    print(f"\n{'=' * 72}\nPASO {n}: {texto}\n{'=' * 72}")


if not os.path.exists(CRUDO):
    raise SystemExit("Faltan las fuentes. Ejecuta primero:  uv run crear_fuentes.py")

con = duckdb.connect(DB)


def correr(sql):
    """Ejecuta SQL sobre el warehouse y muestra el resultado como tabla."""
    con.sql(sql).show()


def uno(sql):
    """Devuelve el primer valor de la primera fila."""
    return con.sql(sql).fetchone()[0]


def cronometrar(etiqueta, funcion):
    t0 = time.perf_counter()
    resultado = funcion()
    print(f"    ⏱  {etiqueta}: {time.perf_counter() - t0:.2f} s")
    return resultado


# ── PASO 1: EXTRACCIÓN — leer cualquier fuente sin cargarla (4.11) ─
titulo(1, "EXTRACCIÓN: SQL lee CSV y JSON directamente, sin cargar nada (4.11)")
print("Antes de decidir nada, MIRA la fuente. DuckDB consulta el archivo tal cual está.")
correr(f"SELECT * FROM read_csv('{CRUDO}', all_varchar=true) LIMIT 5")

print("\nEl esquema que 'adivina' el lector — fíjate en el tipo de cada columna:")
correr(f"DESCRIBE SELECT * FROM read_csv('{CRUDO}')")

print("\nY una fuente en JSON, con el mismo SQL:")
correr(f"SELECT * FROM read_json_auto('{PRODUCTOS}')")

print("\nRadiografía del crudo: ¿cuánto está roto realmente?")
correr(f"""
    SELECT
        COUNT(*)                                              AS filas,
        COUNT(DISTINCT venta_id)                              AS ids_unicos,
        COUNT(*) - COUNT(DISTINCT venta_id)                   AS duplicados,
        SUM(CASE WHEN monto IN ('', 'N/A') THEN 1 ELSE 0 END) AS montos_perdidos,
        SUM(CASE WHEN fecha LIKE '%/%' THEN 1 ELSE 0 END)     AS fechas_formato_europeo,
        SUM(CASE WHEN region <> TRIM(region) THEN 1 ELSE 0 END) AS regiones_con_espacios
    FROM read_csv('{CRUDO}', all_varchar=true)
""")

# ── PASO 2: EL CAMINO ETL — transformar ANTES de cargar (4.13) ────
titulo(2, "ETL: transformo en Python y cargo ya limpio (el camino clásico) (4.13)")


def etl_en_python():
    """Extract → Transform → Load: la limpieza vive FUERA de la base, fila a fila."""
    limpias, descartadas, vistos = [], 0, set()
    with open(CRUDO, newline="", encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            if fila["venta_id"] in vistos:          # deduplicar
                descartadas += 1
                continue
            vistos.add(fila["venta_id"])

            texto = fila["monto"].replace("$", "").replace(",", "")
            try:                                    # castear el importe
                monto = float(texto)
            except ValueError:
                monto = None

            f_txt = fila["fecha"]                   # normalizar la fecha
            if "/" in f_txt:
                d, m, a = f_txt.split("/")
                f_txt = f"{a}-{m}-{d}"

            limpias.append((
                int(fila["venta_id"]), f_txt, fila["cliente_id"].strip().upper(),
                fila["region"].strip().title(), fila["producto"],
                fila["canal"].strip().title(), int(fila["unidades"]), monto,
            ))
    return limpias, descartadas


filas, descartadas = cronometrar("transformar 201.000 filas en Python", etl_en_python)

# Un INSERT fila a fila de 200.000 filas tarda MINUTOS. Por eso toda herramienta ETL
# real escribe un archivo intermedio y hace una CARGA MASIVA (bulk load). Igual aquí:
INTERMEDIO = "data/raw/_etl_intermedio.csv"
with open(INTERMEDIO, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["venta_id", "fecha", "cliente_id", "region", "producto", "canal", "unidades", "monto"])
    w.writerows(filas)

con.execute("CREATE SCHEMA IF NOT EXISTS etl")
cronometrar("cargar en bloque el resultado ya limpio", lambda: con.execute(f"""
    CREATE OR REPLACE TABLE etl.ventas_limpias AS SELECT * FROM read_csv('{INTERMEDIO}')
"""))
os.remove(INTERMEDIO)
print(f"    Cargadas {len(filas):,} filas limpias; {descartadas} duplicados descartados EN EL CAMINO.")
print("""
    Funciona… pero fíjate en el precio que pagas:
      · La lógica de negocio vive en Python, no en SQL: el resto del equipo no la ve.
      · Hizo falta un archivo intermedio para cargar rápido (fila a fila serían MINUTOS).
      · Lo que descartaste (duplicados, importes rotos) YA NO EXISTE en ningún sitio.
      · Si mañana cambia una regla, hay que reprocesar el archivo original entero.
      · No escala: el límite es la RAM de tu máquina, no el motor de datos.""")

# ── PASO 3: EL CAMINO ELT — E + L: cargar el crudo TAL CUAL (4.14) ─
titulo(3, "ELT (E+L): cargo el crudo SIN TOCARLO en la capa raw (4.14)")
for esquema in ("raw", "staging", "marts"):
    con.execute(f"CREATE SCHEMA IF NOT EXISTS {esquema}")


def cargar_raw():
    # all_varchar=true: nada se castea al entrar. La capa raw es un ESPEJO de la fuente.
    con.execute(f"""
        CREATE OR REPLACE TABLE raw.ventas AS
        SELECT *, 'lote1' AS _lote, CURRENT_LOCALTIMESTAMP() AS _cargado_en
        FROM read_csv('{CRUDO}', all_varchar=true)
    """)
    con.execute(f"""
        CREATE OR REPLACE TABLE raw.clientes AS
        SELECT *, CURRENT_LOCALTIMESTAMP() AS _cargado_en FROM read_csv('{CLIENTES}', all_varchar=true)
    """)
    con.execute(f"""
        CREATE OR REPLACE TABLE raw.productos AS
        SELECT *, CURRENT_LOCALTIMESTAMP() AS _cargado_en FROM read_json_auto('{PRODUCTOS}')
    """)


cronometrar("cargar las 3 fuentes crudas con SQL", cargar_raw)
correr("""
    SELECT 'raw.ventas' AS tabla, COUNT(*) AS filas FROM raw.ventas
    UNION ALL SELECT 'raw.clientes', COUNT(*) FROM raw.clientes
    UNION ALL SELECT 'raw.productos', COUNT(*) FROM raw.productos
""")
print("Nada se limpió todavía, y eso es lo bueno: el crudo queda guardado y auditable.")

# ── PASO 4: T — STAGING: limpiar con SQL, en vistas (4.15) ────────
titulo(4, "ELT (T): capa STAGING — limpiar y tipar con SQL puro (4.15)")
print("Una VISTA no ocupa espacio: es la consulta guardada con nombre. Si cambia la regla,")
print("cambias la vista y todo lo que cuelga de ella se recalcula solo.\n")

con.execute("""
    CREATE OR REPLACE VIEW staging.stg_ventas AS
    SELECT
        CAST(venta_id AS INTEGER)                                        AS venta_id,
        -- Dos formatos de fecha conviviendo: intento ISO y, si falla, europeo
        COALESCE(TRY_CAST(fecha AS DATE),
                 TRY_STRPTIME(fecha, '%d/%m/%Y')::DATE)                  AS fecha,
        UPPER(TRIM(cliente_id))                                          AS cliente_id,
        -- Sin INITCAP en DuckDB: primera letra en mayúscula, resto en minúscula
        UPPER(SUBSTR(TRIM(region), 1, 1)) || LOWER(SUBSTR(TRIM(region), 2)) AS region,
        producto,
        UPPER(SUBSTR(TRIM(canal), 1, 1)) || LOWER(SUBSTR(TRIM(canal), 2))   AS canal,
        CAST(unidades AS INTEGER)                                        AS unidades,
        CAST(precio_unitario AS DECIMAL(10,2))                           AS precio_unitario,
        CAST(descuento AS DECIMAL(4,2))                                  AS descuento,
        -- '$1,450.00' → 1450.00. TRY_CAST devuelve NULL en vez de reventar con 'N/A'
        TRY_CAST(REPLACE(REPLACE(monto, '$', ''), ',', '') AS DECIMAL(12,2)) AS monto,
        CAST(trafico AS INTEGER)                                         AS trafico,
        _lote
    FROM raw.ventas
    -- Deduplicar: me quedo con UNA fila por venta_id (la última ingestada)
    QUALIFY ROW_NUMBER() OVER (PARTITION BY venta_id ORDER BY _cargado_en DESC) = 1
""")

con.execute("""
    CREATE OR REPLACE VIEW staging.stg_clientes AS
    SELECT
        UPPER(TRIM(cliente_id))    AS cliente_id,
        TRIM(nombre)               AS nombre,
        segmento,
        TRIM(region)               AS region,
        COALESCE(TRY_CAST(fecha_alta AS DATE),
                 TRY_STRPTIME(fecha_alta, '%d/%m/%Y')::DATE) AS fecha_alta,
        LOWER(TRIM(email))         AS email
    FROM raw.clientes
    QUALIFY ROW_NUMBER() OVER (PARTITION BY UPPER(TRIM(cliente_id)) ORDER BY cliente_id) = 1
""")

con.execute("""
    CREATE OR REPLACE VIEW staging.stg_productos AS
    SELECT producto, nombre, categoria,
           CAST(precio_lista AS DECIMAL(10,2)) AS precio_lista, activo
    FROM raw.productos
""")

print("Antes (crudo) y después (staging), la misma venta:")
correr("SELECT venta_id, fecha, region, canal, monto FROM raw.ventas ORDER BY venta_id LIMIT 4")
correr("SELECT venta_id, fecha, region, canal, monto FROM staging.stg_ventas ORDER BY venta_id LIMIT 4")

correr("""
    SELECT
        (SELECT COUNT(*) FROM raw.ventas)                                   AS raw_filas,
        (SELECT COUNT(*) FROM staging.stg_ventas)                           AS staging_filas,
        (SELECT COUNT(*) FROM staging.stg_ventas WHERE monto IS NULL)       AS montos_nulos,
        (SELECT COUNT(DISTINCT region) FROM raw.ventas)                     AS regiones_crudo,
        (SELECT COUNT(DISTINCT region) FROM staging.stg_ventas)             AS regiones_limpias
""")
print("15 escrituras distintas de 5 regiones se convirtieron en 5. Eso es 'estandarizar'.")

# ── PASO 5: T — MARTS: el modelo de negocio (4.14 / 4.18) ─────────
titulo(5, "ELT (T): capa MARTS — esquema estrella listo para el dashboard (4.14)")
con.execute("""
    CREATE OR REPLACE TABLE marts.dim_producto AS
    SELECT producto AS producto_id, nombre, categoria, precio_lista, activo
    FROM staging.stg_productos
""")
con.execute("""
    CREATE OR REPLACE TABLE marts.dim_cliente AS
    SELECT cliente_id, nombre, segmento, region AS region_cliente, fecha_alta
    FROM staging.stg_clientes
""")
con.execute("""
    CREATE OR REPLACE TABLE marts.fct_ventas AS
    SELECT
        v.venta_id, v.fecha, v.cliente_id, v.producto AS producto_id,
        v.region, v.canal, v.unidades, v.precio_unitario, v.descuento,
        v.monto,
        DATE_TRUNC('month', v.fecha)::DATE AS mes
    FROM staging.stg_ventas v
    WHERE v.monto IS NOT NULL          -- una venta sin importe no es un hecho medible
""")
print("Hechos y dimensiones creados. Ahora una pregunta de negocio de verdad:")
correr("""
    SELECT
        p.categoria,
        f.canal,
        COUNT(*)                 AS n_ventas,
        ROUND(SUM(f.monto), 0)   AS ingresos,
        ROUND(AVG(f.monto), 2)   AS ticket_medio
    FROM marts.fct_ventas f
    JOIN marts.dim_producto p ON f.producto_id = p.producto_id
    GROUP BY 1, 2
    ORDER BY ingresos DESC
    LIMIT 8
""")

con.execute("""
    CREATE OR REPLACE TABLE marts.ventas_mensuales AS
    WITH base AS (
        SELECT mes, region, SUM(monto) AS ingresos, COUNT(*) AS n_ventas
        FROM marts.fct_ventas
        GROUP BY 1, 2
    )
    SELECT
        mes, region, ROUND(ingresos, 0)::BIGINT AS ingresos, n_ventas,
        ROUND(100.0 * (ingresos - LAG(ingresos) OVER (PARTITION BY region ORDER BY mes))
              / LAG(ingresos) OVER (PARTITION BY region ORDER BY mes), 1) AS var_pct
    FROM base
""")
print("\nMart mensual (el que consumiría Power BI), últimos meses:")
correr("SELECT * FROM marts.ventas_mensuales ORDER BY mes DESC, ingresos DESC LIMIT 6")

# ── PASO 6: TESTS DE CALIDAD (4.17) ──────────────────────────────
titulo(6, "TESTS DE CALIDAD: consultas que DEBEN devolver 0 filas (4.17)")
TESTS = {
    "venta_id único en staging":
        "SELECT venta_id FROM staging.stg_ventas GROUP BY 1 HAVING COUNT(*) > 1",
    "ninguna fecha sin parsear":
        "SELECT venta_id FROM staging.stg_ventas WHERE fecha IS NULL",
    "ningún importe negativo":
        "SELECT venta_id FROM marts.fct_ventas WHERE monto < 0",
    "región dentro de los valores aceptados":
        """SELECT DISTINCT region FROM staging.stg_ventas
           WHERE region NOT IN ('Norte','Sur','Este','Oeste','Centro')""",
    "sin claves huérfanas (todo producto existe en el catálogo)":
        """SELECT DISTINCT f.producto_id FROM marts.fct_ventas f
           LEFT JOIN marts.dim_producto d ON f.producto_id = d.producto_id
           WHERE d.producto_id IS NULL""",
    "monto coherente con unidades x precio x descuento":
        """SELECT venta_id FROM marts.fct_ventas
           WHERE ABS(monto - ROUND(unidades * precio_unitario * (1 - descuento), 2)) > 0.05""",
}


def pasar_tests():
    fallos = 0
    for nombre, sql in TESTS.items():
        n = len(con.execute(sql).fetchall())
        print(f"  {'OK   ' if n == 0 else 'FALLA'}  {nombre}" + (f"  → {n} filas malas" if n else ""))
        fallos += n > 0
    return fallos


pasar_tests()
print("""
El último test FALLA a propósito: hay ventas cuyo importe no cuadra con
unidades × precio × (1 - descuento). Son errores de carga del origen. Un test que
falla no es un fracaso: es el pipeline avisándote ANTES de que lo vea el jefe.""")

# ── PASO 7: CARGA INCREMENTAL E IDEMPOTENCIA (4.16) ──────────────
titulo(7, "CARGA INCREMENTAL: llega el lote de julio sin recargar 18 meses (4.16)")
antes = uno("SELECT COUNT(*) FROM raw.ventas")

# Patrón DELETE + INSERT: borro el lote y lo vuelvo a insertar. Ejecutarlo 2 veces
# deja EXACTAMENTE el mismo resultado → es idempotente.
con.execute("DELETE FROM raw.ventas WHERE _lote = 'lote2'")
con.execute(f"""
    INSERT INTO raw.ventas
    SELECT *, 'lote2' AS _lote, CURRENT_LOCALTIMESTAMP() AS _cargado_en
    FROM read_csv('{LOTE2}', all_varchar=true)
""")
print(f"  raw.ventas: {antes:,} filas → {uno('SELECT COUNT(*) FROM raw.ventas'):,} filas")

# El mart NO se reconstruye entero: solo el período afectado
con.execute("DELETE FROM marts.fct_ventas WHERE fecha >= DATE '2026-07-01'")
con.execute("""
    INSERT INTO marts.fct_ventas
    SELECT venta_id, fecha, cliente_id, producto, region, canal, unidades,
           precio_unitario, descuento, monto, DATE_TRUNC('month', fecha)::DATE
    FROM staging.stg_ventas
    WHERE monto IS NOT NULL AND fecha >= DATE '2026-07-01'
""")
correr("""
    SELECT DATE_TRUNC('month', fecha)::DATE AS mes, COUNT(*) AS n_ventas, ROUND(SUM(monto), 0) AS ingresos
    FROM marts.fct_ventas
    WHERE fecha >= DATE '2026-05-01'
    GROUP BY 1 ORDER BY 1
""")
print("Las vistas de staging NO se tocaron: al ser vistas, ya reflejan el lote nuevo.\n")

print("Y ahora repasamos los tests sobre los datos nuevos:")
pasar_tests()
print("""
Salta la clave huérfana: el lote de julio trae el producto 'P99', que no está en el
catálogo. Con ETL lo habrías descartado en silencio; aquí lo VES y decides:
lo mandas a cuarentena, o pides al origen que lo dé de alta.""")
correr("""
    SELECT producto_id, COUNT(*) AS filas_en_cuarentena, ROUND(SUM(monto), 2) AS importe_afectado
    FROM marts.fct_ventas f
    WHERE NOT EXISTS (SELECT 1 FROM marts.dim_producto d WHERE d.producto_id = f.producto_id)
    GROUP BY 1
""")

# ── PASO 8: ETL vs ELT, lado a lado ──────────────────────────────
titulo(8, "Resumen: cuándo ETL y cuándo ELT")
print("""
                        ETL (paso 2)                 ELT (pasos 3-7)
  Orden                 E → T → L                    E → L → T
  Dónde transformas     fuera (Python/herramienta)   dentro del warehouse, con SQL
  El crudo              se pierde                    queda guardado en raw
  Cambiar una regla     reprocesar el archivo         cambias una vista y listo
  Quién lo mantiene     quien sepa Python             cualquiera que sepa SQL
  Escala                la RAM de tu máquina          el motor del warehouse
  Trazabilidad          difícil                       raw → staging → marts, paso a paso

  ELT es hoy el estándar (es exactamente lo que hace dbt, Módulo 08).
  ETL sigue teniendo sentido cuando debes filtrar datos sensibles ANTES de cargarlos,
  o cuando el origen es tan enorme que no quieres pagar por almacenar todo el crudo.""")

con.close()
print(f"\nWarehouse guardado en {DB} (esquemas raw, staging, marts).")
print("Ahora hazlo tú:  uv run actividad_etl.py")
