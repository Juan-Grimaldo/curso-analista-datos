"""
ACTIVIDAD MODELADO + OPTIMIZACIÓN — Módulo 05
=============================================
Ya tienes el pipeline (actividad_etl.py). Ahora modelas bien lo que has cargado y
haces que las consultas sean rápidas y baratas: dimensión de tiempo, claves
subrogadas, fan-out, SCD tipo 2, filtros aprovechables, materialización y
particionado.

Este archivo se trabaja en tu repo de práctica `curso-datos`. Cópialo ahí y
ejecútalo desde la raíz del repo con:  uv run actividad_modelado_opt.py

Cómo funciona:
  - Rellena cada cadena SQL entre las triples comillas. Una sola sentencia, sin ';'.
  - NO cambies los nombres de las variables (SQL_1, SQL_2, ...).
  - El corrector trabaja en el esquema `ejercicio` de data/warehouse.duckdb: puedes
    ejecutarlo tantas veces como quieras, siempre parte de cero.

Requisitos (en curso-datos), en este orden:
  uv run crear_fuentes.py
  uv run demo_etl_elt.py      → deja marts.fct_ventas, marts.dim_producto, marts.dim_cliente
Pistas: README secciones 4.18 y 4.19, y los scripts demo_modelado.py / demo_optimizacion.py.
"""

import duckdb

DB = "data/warehouse.duckdb"
LAGO = "data/lake/ejercicio"      # carpeta donde exportarás los datos particionados


# ── EJERCICIO 1: la dimensión de tiempo ───────────────────────────
# Crea la TABLA ejercicio.dim_fecha con un día por fila, del 2025-01-01 al 2026-12-31
# (730 filas), con estas columnas exactas:
#   fecha (DATE), anio, mes_num, trimestre, es_fin_de_semana (BOOLEAN)
# Pista: FROM generate_series(DATE '2025-01-01', DATE '2026-12-31', INTERVAL 1 DAY) AS t(d)
#        y funciones YEAR(d), MONTH(d), QUARTER(d), DAYOFWEEK(d) IN (0, 6)
SQL_1 = """
    -- TODO: CREATE OR REPLACE TABLE ejercicio.dim_fecha AS SELECT d::DATE AS fecha, ... FROM generate_series(...)
"""


# ── EJERCICIO 2: claves subrogadas ────────────────────────────────
# Crea la TABLA ejercicio.dim_producto a partir de marts.dim_producto, con:
#   producto_sk  → entero 1, 2, 3... generado con ROW_NUMBER() ordenando por producto_id
#   producto_nk  → la clave natural que viene del origen (producto_id)
#   nombre, categoria, precio_lista
SQL_2 = """
    -- TODO: CREATE OR REPLACE TABLE ejercicio.dim_producto AS SELECT ROW_NUMBER() OVER (ORDER BY ...) AS producto_sk, ...
"""


# ── EJERCICIO 3: esquivar el FAN-OUT ──────────────────────────────
# El corrector ha creado ejercicio.campanas: 3 campañas por producto (36 filas), con
# una columna `inversion`. Si unes los hechos con esa tabla y sumas, TRIPLICAS los
# ingresos. Escribe la consulta CORRECTA que devuelve, por categoría de producto:
#   categoria, ingresos (SUM del monto de marts.fct_ventas), inversion (SUM de campanas)
# ordenada por ingresos descendente. Pista: agrega CADA fuente a su grano en una CTE
# y únelas después.
# Los ingresos de las 3 categorías deben sumar 5.195.543 (y no el triple). Ojo: el total
# de fct_ventas es 5.195.583; los 39,82 que faltan son las ventas del producto huérfano
# 'P99', que no está en el catálogo y por tanto no entra en ninguna categoría.
SQL_3 = """
    -- TODO: WITH ventas AS (...), inversion AS (...) SELECT ... FROM ventas JOIN inversion USING (categoria)
"""


# ── EJERCICIO 4: consultar una dimensión SCD tipo 2 ───────────────
# El corrector ha creado ejercicio.dim_cliente_scd2, con una fila por VERSIÓN del
# cliente (columnas: cliente_id, nombre, segmento, valido_desde, valido_hasta, es_actual).
# Calcula los ingresos por segmento VIGENTE EN LA FECHA DE LA VENTA (no el actual).
# Devuelve: segmento, ingresos — ordenado de mayor a menor.
# Pista: en el ON, además de la clave, la fecha del hecho debe caer entre valido_desde
# y valido_hasta.
SQL_4 = """
    -- TODO: SELECT d.segmento, ROUND(SUM(f.monto), 0) AS ingresos FROM marts.fct_ventas f JOIN ejercicio.dim_cliente_scd2 d ON ...
"""


# ── EJERCICIO 5: un filtro que el motor pueda aprovechar ──────────
# Cuenta las ventas de 2026 y su importe total: devuelve n_ventas, ingresos.
# ⚠️ Prohibido envolver la columna `fecha` en una función (nada de YEAR(fecha),
#    EXTRACT(...), DATE_TRUNC(...) ni CAST sobre fecha): usa un rango de fechas.
SQL_5 = """
    -- TODO: SELECT COUNT(*) AS n_ventas, ROUND(SUM(monto), 2) AS ingresos FROM marts.fct_ventas WHERE fecha >= ... AND fecha < ...
"""


# ── EJERCICIO 6: materializar el agregado del dashboard ───────────
# Crea la TABLA ejercicio.kpi_mensual desde marts.fct_ventas con:
#   mes, region, ingresos (SUM redondeado a 0), n_ventas, ticket_medio (AVG a 2 decimales)
#   y puesto = posición de la región dentro de su mes por ingresos (1 = la que más vende).
# Pista: agrega en una CTE y luego RANK() OVER (PARTITION BY mes ORDER BY ingresos DESC).
SQL_6 = """
    -- TODO: WITH base AS (SELECT mes, region, SUM(monto) AS ingresos, ... GROUP BY 1,2) SELECT ..., RANK() OVER (...) AS puesto FROM base
"""


# ── EJERCICIO 7: exportar particionado (partition pruning) ────────
# Exporta marts.fct_ventas a Parquet PARTICIONADO POR AÑO en la carpeta data/lake/ejercicio.
# Debe quedar una carpeta por año (anio=2025, anio=2026).
# Pista: COPY (SELECT *, YEAR(fecha) AS anio FROM ...) TO 'data/lake/ejercicio'
#        (FORMAT PARQUET, PARTITION_BY (anio), OVERWRITE_OR_IGNORE)
SQL_7 = """
    -- TODO: COPY (...) TO 'data/lake/ejercicio' (FORMAT PARQUET, PARTITION_BY (anio), OVERWRITE_OR_IGNORE)
"""


# ── EJERCICIO 8: leer solo lo necesario ───────────────────────────
# Sobre los Parquet que acabas de escribir (léelos con
# read_parquet('data/lake/ejercicio/**/*.parquet', hive_partitioning=true)):
# devuelve el TOP 5 de clientes por ingresos SOLO del año 2026.
# Devuelve: cliente_id, ingresos (SUM del monto a 2 decimales).
# Filtra por la columna de partición `anio` — así el motor ni abre los archivos de 2025.
SQL_8 = """
    -- TODO: SELECT cliente_id, ROUND(SUM(monto), 2) AS ingresos FROM read_parquet(...) WHERE anio = 2026 GROUP BY ...
"""


# ══════════════════════════════════════════════════════════════════
#  CORRECTOR — no toques nada de aquí abajo
# ══════════════════════════════════════════════════════════════════
def sin_escribir(sql):
    """True si la cadena solo tiene comentarios o espacios (el TODO sigue ahí)."""
    return not [ln for ln in sql.splitlines()
                if ln.strip() and not ln.strip().startswith("--")]


def corregir():
    import pathlib
    import shutil

    shutil.rmtree(LAGO, ignore_errors=True)      # el ejercicio 7 debe crearlo de cero
    con = duckdb.connect(DB)
    try:
        n_hechos = con.execute("SELECT COUNT(*) FROM marts.fct_ventas").fetchone()[0]
    except Exception:
        raise SystemExit("Falta marts.fct_ventas. Ejecuta primero:  uv run demo_etl_elt.py")
    if n_hechos != 205_872:
        print(f"⚠️  marts.fct_ventas tiene {n_hechos:,} filas y se esperaban 205.872.")
        print("   Vuelve a ejecutar:  uv run crear_fuentes.py  y  uv run demo_etl_elt.py\n")

    con.execute("DROP SCHEMA IF EXISTS ejercicio CASCADE")
    con.execute("CREATE SCHEMA ejercicio")

    # Material de apoyo que usan los ejercicios 3 y 4
    con.execute("""
        CREATE TABLE ejercicio.campanas AS
        SELECT p.producto_id, c.campana, c.inversion
        FROM marts.dim_producto p
        CROSS JOIN (VALUES ('Verano', 1000), ('Navidad', 2500), ('Aniversario', 800))
                   AS c(campana, inversion)
    """)
    con.execute("""
        CREATE TABLE ejercicio.dim_cliente_scd2 AS
        WITH base AS (SELECT cliente_id, nombre, segmento FROM marts.dim_cliente),
        ascendidos AS (
            SELECT cliente_id FROM base
            WHERE segmento = 'Retail' AND CAST(SUBSTR(cliente_id, 2) AS INTEGER) % 5 = 0
        )
        SELECT b.cliente_id, b.nombre, b.segmento,
               DATE '2023-01-01' AS valido_desde,
               CASE WHEN a.cliente_id IS NOT NULL THEN DATE '2025-12-31'
                    ELSE DATE '9999-12-31' END AS valido_hasta,
               a.cliente_id IS NULL AS es_actual
        FROM base b LEFT JOIN ascendidos a ON b.cliente_id = a.cliente_id
        UNION ALL
        SELECT b.cliente_id, b.nombre, 'Corporativo',
               DATE '2026-01-01', DATE '9999-12-31', TRUE
        FROM base b JOIN ascendidos a ON b.cliente_id = a.cliente_id
    """)

    errores = {}

    def ejecutar(n, sql):
        if sin_escribir(sql):
            errores[n] = "todavía sin escribir"
            return
        try:
            con.execute(sql)
        except Exception as e:
            errores[n] = str(e).split("\n")[0]

    def valor(sql, defecto=None):
        try:
            return con.execute(sql).fetchone()[0]
        except Exception:
            return defecto

    def filas(n, sql):
        if sin_escribir(sql):
            errores[n] = "todavía sin escribir"
            return []
        try:
            return con.execute(sql).fetchall()
        except Exception as e:
            errores[n] = str(e).split("\n")[0]
            return []

    for n, sql in zip((1, 2, 6, 7), (SQL_1, SQL_2, SQL_6, SQL_7)):
        ejecutar(n, sql)

    r3, r4 = filas(3, SQL_3), filas(4, SQL_4)
    r5, r8 = filas(5, SQL_5), filas(8, SQL_8)
    PROHIBIDO = ("year(fecha)", "extract(", "date_trunc(", "month(fecha)",
                 "strftime", "cast(fechaas", "fecha::")
    sql5 = SQL_5.lower().replace(" ", "")
    sin_funcion = not sin_escribir(SQL_5) and not any(p in sql5 for p in PROHIBIDO)
    particiones = sorted(p.name for p in pathlib.Path(LAGO).glob("anio=*")) \
        if pathlib.Path(LAGO).exists() else []

    checks = [
        ("1. dim_fecha cubre 730 días (2 años completos)",
         valor("SELECT COUNT(*) FROM ejercicio.dim_fecha") == 730),
        ("1b. 208 días son fin de semana y el rango empieza el 2025-01-01",
         valor("SELECT COUNT(*) FROM ejercicio.dim_fecha WHERE es_fin_de_semana") == 208
         and str(valor("SELECT MIN(fecha) FROM ejercicio.dim_fecha")) == "2025-01-01"),
        ("2. dim_producto: 12 productos con clave subrogada 1..12",
         valor("SELECT COUNT(*) FROM ejercicio.dim_producto") == 12
         and valor("SELECT MIN(producto_sk) || '-' || MAX(producto_sk) FROM ejercicio.dim_producto") == "1-12"),
        ("2b. La subrogada 1 corresponde a la clave natural 'P01'",
         valor("SELECT producto_nk FROM ejercicio.dim_producto WHERE producto_sk = 1") == "P01"),
        ("3. Sin fan-out: 3 categorías y 5.195.543 de ingresos (no el triple)",
         len(r3) == 3 and abs(sum(float(f[1]) for f in r3) - 5_195_543) <= 2),
        ("3b. Lidera Limpieza con 2.054.492 de ingresos y 17.200 de inversión",
         len(r3) == 3 and r3[0][0] == "Limpieza" and round(float(r3[0][1])) == 2_054_492
         and round(float(r3[0][2])) == 17_200),
        ("4. SCD2: Corporativo 1.929.792 (segmento vigente en la fecha de la venta)",
         len(r4) == 3 and r4[0][0] == "Corporativo" and round(float(r4[0][1])) == 1_929_792),
        ("4b. Retail 1.506.330 (con el segmento ACTUAL saldría 1.293.438: no es lo mismo)",
         len(r4) == 3 and round(float(r4[-1][1])) == 1_506_330),
        ("5. Ventas de 2026: 74.742 ventas y 2.011.104,24 de ingresos",
         len(r5) == 1 and r5[0][0] == 74_742 and round(float(r5[0][1]), 2) == 2_011_104.24),
        ("5b. El filtro deja la columna `fecha` desnuda (sin funciones)", sin_funcion),
        ("6. kpi_mensual: 95 filas (19 meses x 5 regiones)",
         valor("SELECT COUNT(*) FROM ejercicio.kpi_mensual") == 95),
        ("6b. Hay una región en puesto 1 por cada mes",
         valor("SELECT COUNT(*) FROM ejercicio.kpi_mensual WHERE puesto = 1") == 19),
        ("6c. En enero de 2025 la región líder es Norte",
         valor("SELECT region FROM ejercicio.kpi_mensual WHERE puesto = 1 AND mes = DATE '2025-01-01'") == "Norte"),
        ("7. Exportado a Parquet particionado por año (anio=2025, anio=2026)",
         particiones == ["anio=2025", "anio=2026"]),
        ("8. Top 5 clientes de 2026 desde el Parquet particionado",
         len(r8) == 5 and r8[0][0] == "C01939"),
        ("8b. El primer cliente suma 16.981,90 en 2026",
         len(r8) == 5 and round(float(r8[0][1]), 2) == 16_981.90),
    ]

    print("\n" + "=" * 66)
    print("RESULTADO DE LA ACTIVIDAD DE MODELADO Y OPTIMIZACIÓN")
    print("=" * 66)
    aciertos = 0
    for nombre, paso in checks:
        try:
            paso = bool(paso)
        except Exception:
            paso = False
        print(f"  {'OK   ' if paso else 'FALLA'}  {nombre}")
        aciertos += paso
    print("-" * 66)
    print(f"  {aciertos}/{len(checks)} correctos")

    if errores:
        print("\n  Errores de SQL (arréglalos primero):")
        for n, msg in sorted(errores.items()):
            print(f"    SQL_{n}: {msg}")

    if aciertos == len(checks):
        print("\n  Modelo sólido y consultas afinadas. Ya puedes con el Reto del módulo.")
    else:
        print("\n  Revisa los FALLA. Para depurar:")
        print("    import duckdb; duckdb.connect('data/warehouse.duckdb').sql(SQL_3).show()")

    con.close()


if __name__ == "__main__":
    corregir()
