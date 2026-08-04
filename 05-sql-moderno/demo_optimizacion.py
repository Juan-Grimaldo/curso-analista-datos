"""
Demo guiado del Módulo 05 — OPTIMIZACIÓN de consultas.

Una consulta lenta en tu portátil es una consulta CARA en la nube: en BigQuery pagas
por bytes leídos y en Snowflake por segundos de cómputo. Aquí ves, con cronómetro,
las cinco palancas que de verdad mueven la aguja: formato, columnas, filtros,
particionado y materialización.

Este script se ejecuta en tu repo de práctica `curso-datos`. Cópialo ahí y, desde la
raíz del repo, ejecútalo con:  uv run demo_optimizacion.py
Cada PASO corresponde a una sección del README (4.19).

Requisitos (en curso-datos):
  uv run crear_fuentes.py   y   uv run demo_etl_elt.py   → deja data/warehouse.duckdb

Los tiempos varían entre máquinas y entre ejecuciones (caché del sistema operativo).
Lo que importa no es el número exacto, sino la PROPORCIÓN entre las dos versiones.
"""

import os
import pathlib
import time

import duckdb

DB = "data/warehouse.duckdb"
CRUDO = "data/raw/ventas_crudas.csv"
PARQUET = "data/raw/ventas.parquet"
LAGO = "data/lake/ventas"          # aquí escribiremos datos particionados


def titulo(n, texto):
    print(f"\n{'=' * 72}\nPASO {n}: {texto}\n{'=' * 72}")


if not os.path.exists(DB):
    raise SystemExit(f"Falta {DB}. Ejecuta primero:  uv run demo_etl_elt.py")

con = duckdb.connect(DB)


def medir(etiqueta, sql, repeticiones=3):
    """Ejecuta la consulta varias veces y se queda con el mejor tiempo."""
    mejor = None
    for _ in range(repeticiones):
        t0 = time.perf_counter()
        con.execute(sql).fetchall()
        t = time.perf_counter() - t0
        mejor = t if mejor is None else min(mejor, t)
    print(f"    ⏱  {etiqueta:<46} {mejor * 1000:8.1f} ms")
    return mejor


def comparar(lenta, rapida):
    if lenta and rapida:
        print(f"    → {lenta / rapida:.1f}x más rápida\n")


def mb(ruta):
    p = pathlib.Path(ruta)
    if p.is_dir():
        return sum(f.stat().st_size for f in p.rglob("*")) / 1024 / 1024
    return p.stat().st_size / 1024 / 1024


# ── PASO 1: EL FORMATO DEL DATO (4.19) ───────────────────────────
titulo(1, "El formato manda: CSV vs Parquet vs tabla del warehouse (4.19)")
con.execute(f"COPY (SELECT * FROM raw.ventas) TO '{PARQUET}' (FORMAT PARQUET)")
print(f"  ventas_crudas.csv  {mb(CRUDO):6.1f} MB      ventas.parquet  {mb(PARQUET):6.1f} MB\n")

AGREGADO = "SELECT region, COUNT(*), SUM(TRY_CAST(REPLACE(REPLACE(monto,'$',''),',','') AS DOUBLE)) FROM {origen} GROUP BY 1"
t_csv = medir("leyendo el CSV (hay que parsear texto)", AGREGADO.format(origen=f"read_csv('{CRUDO}')"))
t_pq = medir("leyendo Parquet (columnar y comprimido)", AGREGADO.format(origen=f"read_parquet('{PARQUET}')"))
t_tabla = medir("leyendo la tabla del warehouse", AGREGADO.format(origen="raw.ventas"))
comparar(t_csv, t_pq)
print("""  CSV es texto: hay que leerlo entero y parsear cada carácter. Parquet guarda cada
  COLUMNA por separado, comprimida y con estadísticas (mínimo/máximo por bloque).
  Es el formato del análisis: en el lago se guarda Parquet, no CSV.""")

# ── PASO 2: PEDIR SOLO LAS COLUMNAS QUE USAS (4.19) ──────────────
titulo(2, "SELECT *: el impuesto invisible (4.19)")
t_todo = medir("extraer SELECT * (las 14 columnas)",
               f"CREATE OR REPLACE TEMP TABLE extracto AS SELECT * FROM read_parquet('{PARQUET}')")
t_dos = medir("extraer solo region y monto (2 columnas)",
              f"CREATE OR REPLACE TEMP TABLE extracto AS SELECT region, monto FROM read_parquet('{PARQUET}')")
comparar(t_todo, t_dos)
print("""  En un formato columnar, las columnas que NO pides ni se leen del disco. A esto se
  le llama *projection pushdown*. En BigQuery esto es literalmente tu factura: pagas
  por bytes leídos, y `SELECT *` los multiplica.""")

# ── PASO 3: LEER EL PLAN — EXPLAIN (4.19) ────────────────────────
titulo(3, "EXPLAIN: preguntarle al motor QUÉ va a hacer (4.19)")
plan = con.execute("""
    EXPLAIN
    SELECT p.categoria, SUM(f.monto) AS ingresos
    FROM marts.fct_ventas f
    JOIN marts.dim_producto p ON f.producto_id = p.producto_id
    WHERE f.fecha >= DATE '2026-01-01'
    GROUP BY 1
""").fetchall()[0][1]
# El plan se lee de abajo arriba, así que mostramos su MITAD INFERIOR: los escaneos
# de tabla y el JOIN, que es donde se decide el rendimiento.
lineas = plan.splitlines()
print("   [...parte superior del plan recortada: agregación y proyección final...]\n")
print("\n".join(lineas[-45:]))
print("""
  Se lee DE ABAJO HACIA ARRIBA: primero los escaneos de tabla, luego el JOIN, luego
  la agregación. Fíjate en dos cosas:
    · en el SCAN aparecen solo las columnas necesarias y el filtro ya aplicado
      (*filter pushdown*: el motor filtra al leer, no después);
    · en el HASH_JOIN, la tabla pequeña (dim_producto) es la que se convierte en
      tabla hash. Si ves un NESTED LOOP sobre millones de filas, ahí está tu problema.

  `EXPLAIN ANALYZE` (misma sintaxis) la EJECUTA y añade tiempos y filas reales por
  operador: es la herramienta número uno para saber por dónde se te va el tiempo.""")

# ── PASO 4: FILTROS QUE EL MOTOR PUEDE APROVECHAR (4.19) ─────────
titulo(4, "Filtrar de forma que el motor pueda ayudarte (4.19)")
t_funcion = medir("WHERE YEAR(fecha) = 2026   (función sobre la columna)",
                  "SELECT COUNT(*), SUM(monto) FROM marts.fct_ventas WHERE YEAR(fecha) = 2026")
t_rango = medir("WHERE fecha >= DATE '2026-01-01'   (rango directo)",
                "SELECT COUNT(*), SUM(monto) FROM marts.fct_ventas WHERE fecha >= DATE '2026-01-01'")
comparar(t_funcion, t_rango)
print("""  Al envolver la columna en una función, muchos motores dejan de poder usar índices,
  estadísticas de bloque y particiones: tienen que calcular la función fila a fila.
  Regla: deja la columna DESNUDA a un lado del operador y transforma el otro lado.""")

print("\n  Y el clásico: filtrar ANTES de unir, no después.")
t_tarde = medir("JOIN de todo y filtrar al final",
                """SELECT p.categoria, SUM(f.monto)
                   FROM marts.fct_ventas f
                   JOIN marts.dim_producto p ON f.producto_id = p.producto_id
                   WHERE f.fecha >= DATE '2026-06-01'
                   GROUP BY 1""")
t_pronto = medir("filtrar en una CTE y unir solo lo que queda",
                 """WITH recientes AS (
                        SELECT producto_id, monto FROM marts.fct_ventas
                        WHERE fecha >= DATE '2026-06-01'
                    )
                    SELECT p.categoria, SUM(r.monto)
                    FROM recientes r
                    JOIN marts.dim_producto p ON r.producto_id = p.producto_id
                    GROUP BY 1""")
print("""  Aquí los dos tiempos se parecen: DuckDB (como BigQuery o Snowflake) ya empuja el
  filtro por su cuenta. Pero en cuanto la consulta se complica —subconsultas, UNIONs,
  vistas anidadas— el optimizador deja de poder hacerlo y escribirlo bien vuelve a
  importar. Escribe siempre como si el optimizador no fuera a salvarte.""")

# ── PASO 5: PARTICIONADO Y PRUNING (4.19) ────────────────────────
titulo(5, "Particionar: no leer lo que no hace falta (4.19)")
pathlib.Path(LAGO).parent.mkdir(parents=True, exist_ok=True)
con.execute(f"""
    COPY (
        SELECT * EXCLUDE (mes), YEAR(fecha) AS anio, MONTH(fecha) AS mes_num
        FROM marts.fct_ventas
    ) TO '{LAGO}' (FORMAT PARQUET, PARTITION_BY (anio, mes_num), OVERWRITE_OR_IGNORE)
""")
archivos = list(pathlib.Path(LAGO).rglob("*.parquet"))
print(f"  Escritos {len(archivos)} archivos Parquet en carpetas anio=…/mes_num=…  ({mb(LAGO):.1f} MB en total)")
print(f"  Ejemplo: {archivos[0].as_posix()}\n")

t_todos = medir("escaneando TODAS las particiones",
                f"SELECT SUM(monto) FROM read_parquet('{LAGO}/**/*.parquet', hive_partitioning=true)")
t_una = medir("filtrando por partición (anio=2026, mes_num=7)",
              f"""SELECT SUM(monto) FROM read_parquet('{LAGO}/**/*.parquet', hive_partitioning=true)
                  WHERE anio = 2026 AND mes_num = 7""")
comparar(t_todos, t_una)
print("""  El motor mira el NOMBRE de la carpeta y descarta los archivos que no cumplen el
  filtro: *partition pruning*. No los abre siquiera.
  Equivalencias: BigQuery → tablas particionadas por fecha + clustering; Snowflake →
  micro-particiones + cluster keys; Databricks → particiones Delta + Z-ORDER.
  Es la optimización que más dinero ahorra en la nube.""")

# ── PASO 6: ÍNDICES — para buscar, no para agregar (4.19) ────────
titulo(6, "Índices: sirven para BUSCAR una aguja, no para sumar el pajar (4.19)")
BUSQUEDA = "SELECT COUNT(*) FROM marts.fct_ventas WHERE cliente_id = 'C01234'"
t_sin = medir("buscar un cliente SIN índice", BUSQUEDA)
con.execute("CREATE INDEX IF NOT EXISTS idx_fct_cliente ON marts.fct_ventas (cliente_id)")
t_con = medir("buscar el mismo cliente CON índice", BUSQUEDA)
comparar(t_sin, t_con)

SUMA = "SELECT region, SUM(monto) FROM marts.fct_ventas GROUP BY 1"
medir("agregación completa (el índice no pinta nada aquí)", SUMA)
print("""  Un índice acelera las consultas SELECTIVAS (pocas filas de muchas). Una agregación
  que recorre toda la tabla no lo necesita: el motor columnar ya es óptimo ahí.
  Y ojo: cada índice ocupa espacio y ralentiza las cargas.
  Por eso los warehouses cloud (BigQuery, Snowflake) casi no usan índices: usan
  particionado, clustering y estadísticas.""")
con.execute("DROP INDEX IF EXISTS idx_fct_cliente")

# ── PASO 7: MATERIALIZAR vs RECALCULAR (4.19) ────────────────────
titulo(7, "Vista o tabla: ¿recalculo cada vez o guardo el resultado? (4.19)")
CONSULTA_DASHBOARD = """
    SELECT DATE_TRUNC('month', fecha)::DATE AS mes, region, SUM(monto) AS ingresos
    FROM {origen}
    GROUP BY 1, 2
"""
t_vista = medir("desde la VISTA de staging (limpia 211.000 filas cada vez)",
                CONSULTA_DASHBOARD.format(origen="staging.stg_ventas") + " HAVING SUM(monto) IS NOT NULL")
t_mart = medir("desde la TABLA de hechos ya materializada",
               CONSULTA_DASHBOARD.format(origen="marts.fct_ventas"))
comparar(t_vista, t_mart)
t_agregado = medir("desde el mart mensual YA agregado (90 filas)",
                   "SELECT mes, region, ingresos FROM marts.ventas_mensuales")
comparar(t_vista, t_agregado)
print("""  Materializar = pagar el cálculo UNA vez al día en vez de en cada clic del usuario.
  Regla práctica:
    · staging → VISTAS (cambian a menudo, no cuestan espacio)
    · marts   → TABLAS (se consultan mil veces al día)
    · agregados del dashboard → TABLA, si la consulta tarda o la ve mucha gente
  El precio de materializar es que el dato tiene la antigüedad de la última carga.""")

# ── PASO 8: CHECKLIST ────────────────────────────────────────────
titulo(8, "Checklist de optimización (por orden de impacto)")
print("""
  1. ¿Estoy leyendo más datos de los necesarios?   → columnas concretas, nunca SELECT *
  2. ¿Puedo filtrar antes?                          → WHERE lo más pronto posible
  3. ¿El filtro deja la columna desnuda?            → nada de YEAR(fecha) = 2026
  4. ¿El dato está particionado por lo que filtro?  → fecha suele ser la respuesta
  5. ¿Estoy en formato columnar?                    → Parquet / tabla del warehouse
  6. ¿Repito el mismo cálculo caro?                 → materialízalo en un mart
  7. ¿Hay riesgo de fan-out en los JOINs?           → agrega antes de unir (demo_modelado)
  8. ¿Qué dice EXPLAIN ANALYZE?                     → mide, no adivines

  Traducción a la nube:
    BigQuery   → pagas por BYTES LEÍDOS: particionar + clusterizar + pedir columnas.
    Snowflake  → pagas por TIEMPO de warehouse encendido: consultas cortas, caché,
                 cluster keys en las tablas grandes.
    Databricks → OPTIMIZE + Z-ORDER sobre tablas Delta, y evitar los ficheros pequeños.""")

con.close()
print("\nAhora hazlo tú:  uv run actividad_modelado_opt.py")
