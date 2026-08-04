"""
ACTIVIDAD ETL/ELT — Módulo 05
=============================
Ahora construyes TÚ el pipeline ELT completo: cargas 200.000 filas crudas, las
limpias con SQL en una capa de staging, montas el mart de negocio, escribes un
test de calidad y haces una carga incremental.

Este archivo se trabaja en tu repo de práctica `curso-datos`. Cópialo ahí y
ejecútalo desde la raíz del repo con:  uv run actividad_etl.py

Cómo funciona:
  - Cada ejercicio te pide RELLENAR una cadena SQL entre las triples comillas.
  - NO cambies los nombres de las variables (SQL_1, SQL_2, ...).
  - Cada cadena debe contener UNA sola sentencia SQL (sin ';' al final).
  - El corrector crea una base limpia, ejecuta tu SQL en orden y comprueba resultados.

⚠️ CONTRATO DE NOMBRES (el corrector busca exactamente esto):
     raw.ventas · raw.productos · staging.stg_ventas
     marts.fct_ventas · marts.ventas_mensuales
   y en staging.stg_ventas las columnas:
     venta_id, fecha, cliente_id, region, producto, canal,
     unidades, precio_unitario, descuento, monto, trafico

Requisitos (en curso-datos):
  uv add duckdb
  uv run crear_fuentes.py     → genera las fuentes crudas en data/raw/
Pistas: README secciones 4.11 a 4.17. Mira demo_etl_elt.py solo después de
intentarlo dos veces por tu cuenta.
"""

import duckdb

CRUDO = "data/raw/ventas_crudas.csv"
LOTE2 = "data/raw/ventas_crudas_lote2.csv"
PRODUCTOS = "data/raw/productos.json"


# ── EJERCICIO 1: EXTRAER + CARGAR el crudo tal cual ───────────────
# Crea la tabla raw.ventas leyendo data/raw/ventas_crudas.csv SIN transformar nada:
# todas las columnas deben quedar como TEXTO (VARCHAR). Pista: read_csv(..., all_varchar=true).
# Deben entrar las 201.000 filas, duplicados incluidos: la capa raw es un espejo del origen.
SQL_1 = """
    -- TODO: CREATE OR REPLACE TABLE raw.ventas AS SELECT * FROM read_csv('...', all_varchar=true)
"""


# ── EJERCICIO 2: cargar la segunda fuente (JSON) ──────────────────
# Crea raw.productos a partir de data/raw/productos.json. Pista: read_json_auto(...).
SQL_2 = """
    -- TODO: CREATE OR REPLACE TABLE raw.productos AS SELECT * FROM read_json_auto('...')
"""


# ── EJERCICIO 3: la capa STAGING (el ejercicio grande) ────────────
# Crea la VISTA staging.stg_ventas sobre raw.ventas, con las 11 columnas del contrato
# de nombres de arriba y estas reglas:
#   · venta_id, unidades, trafico → INTEGER;  precio_unitario y descuento → DECIMAL
#   · fecha → DATE. Ojo: conviven 'YYYY-MM-DD' y 'DD/MM/YYYY'.
#     Pista: COALESCE(TRY_CAST(...), TRY_STRPTIME(fecha, '%d/%m/%Y')::DATE)
#   · region y canal → sin espacios y con la primera letra en mayúscula ('  ESTE ' → 'Este').
#     Pista: UPPER(SUBSTR(TRIM(x),1,1)) || LOWER(SUBSTR(TRIM(x),2))
#   · cliente_id → UPPER(TRIM(...))
#   · monto → DECIMAL. Llega como '$1,450.00' y a veces como 'N/A' o vacío:
#     quita '$' y ',' con REPLACE y usa TRY_CAST (los no numéricos quedan NULL).
#   · una sola fila por venta_id. Pista: QUALIFY ROW_NUMBER() OVER (PARTITION BY ...) = 1
SQL_3 = """
    -- TODO: CREATE OR REPLACE VIEW staging.stg_ventas AS SELECT ... FROM raw.ventas QUALIFY ...
"""


# ── EJERCICIO 4: comprobar que la limpieza funcionó ───────────────
# Consulta sobre staging.stg_ventas: para cada canal, número de ventas y ticket medio
# (AVG del monto redondeado a 2 decimales), ordenado por número de ventas descendente.
# Devuelve: canal, n_ventas, ticket_medio. Si la limpieza está bien, salen 4 canales.
SQL_4 = """
    -- TODO: SELECT canal, COUNT(*) AS n_ventas, ROUND(AVG(monto), 2) AS ticket_medio ...
"""


# ── EJERCICIO 5: la capa MARTS — tabla de hechos ──────────────────
# Crea la TABLA marts.fct_ventas desde staging.stg_ventas con las columnas:
#   venta_id, fecha, cliente_id, producto, region, canal, unidades, monto
#   y una columna mes = DATE_TRUNC('month', fecha)::DATE
# Deja fuera las ventas sin importe (monto IS NULL): un hecho sin métrica no es un hecho.
SQL_5 = """
    -- TODO: CREATE OR REPLACE TABLE marts.fct_ventas AS SELECT ... WHERE monto IS NOT NULL
"""


# ── EJERCICIO 6: el mart que consume el dashboard ─────────────────
# Crea la TABLA marts.ventas_mensuales desde marts.fct_ventas con:
#   mes, region, ingresos (SUM del monto redondeado a 0 decimales),
#   n_ventas (COUNT) y var_pct = variación % de ingresos frente al mes anterior
#   DE LA MISMA REGIÓN, redondeada a 1 decimal.
# Pista: agrega en una CTE y usa LAG(...) OVER (PARTITION BY region ORDER BY mes).
SQL_6 = """
    -- TODO: WITH base AS (SELECT mes, region, SUM(monto) ... GROUP BY 1,2) SELECT ..., LAG(...) ...
"""


# ── EJERCICIO 7: un test de calidad ───────────────────────────────
# Escribe la consulta que DETECTA los venta_id repetidos en raw.ventas.
# Devuelve una fila por venta_id duplicado: venta_id, veces (cuántas veces aparece).
# (En un pipeline real este test debería devolver 0 filas; aquí devuelve las que el
#  origen envió por duplicado, y por eso deduplicaste en staging.)
SQL_7 = """
    -- TODO: SELECT venta_id, COUNT(*) AS veces FROM raw.ventas GROUP BY ... HAVING ...
"""


# ── EJERCICIO 8: carga INCREMENTAL ────────────────────────────────
# Llega el lote de julio (data/raw/ventas_crudas_lote2.csv). Añádelo a raw.ventas
# SIN borrar ni recargar lo anterior. Pista: INSERT INTO ... SELECT * FROM read_csv(...).
# Después, staging y el resto se recalculan solos (son vistas). Eso es ELT.
SQL_8 = """
    -- TODO: INSERT INTO raw.ventas SELECT * FROM read_csv('...', all_varchar=true)
"""


# ══════════════════════════════════════════════════════════════════
#  CORRECTOR — no toques nada de aquí abajo
# ══════════════════════════════════════════════════════════════════
DB = "data/warehouse_actividad.duckdb"


def sin_escribir(sql):
    """True si la cadena solo tiene comentarios o espacios (el TODO sigue ahí)."""
    return not [ln for ln in sql.splitlines()
                if ln.strip() and not ln.strip().startswith("--")]


def corregir():
    con = duckdb.connect(DB)
    for esquema in ("raw", "staging", "marts"):     # base limpia en cada intento
        con.execute(f"DROP SCHEMA IF EXISTS {esquema} CASCADE")
        con.execute(f"CREATE SCHEMA {esquema}")

    errores = {}

    def ejecutar(n, sql):
        if sin_escribir(sql):
            errores[n] = "todavía sin escribir"
            return False
        try:
            con.execute(sql)
            return True
        except Exception as e:
            errores[n] = str(e).split("\n")[0]
            return False

    def valor(sql, defecto=None):
        try:
            return con.execute(sql).fetchone()[0]
        except Exception:
            return defecto

    def filas(sql):
        try:
            return con.execute(sql).fetchall()
        except Exception:
            return []

    for n, sql in enumerate([SQL_1, SQL_2, SQL_3, SQL_4, SQL_5, SQL_6, SQL_7], start=1):
        ejecutar(n, sql)

    tipos = [t for t in filas("SELECT data_type FROM information_schema.columns "
                              "WHERE table_schema='raw' AND table_name='ventas'")]
    r4 = filas(SQL_4) if not sin_escribir(SQL_4) else []
    r7 = filas(SQL_7) if not sin_escribir(SQL_7) else []

    checks = [
        ("1. raw.ventas tiene las 201.000 filas del crudo",
         valor("SELECT COUNT(*) FROM raw.ventas") == 201_000),
        ("1b. raw.ventas es un espejo: TODAS las columnas son texto",
         len(tipos) >= 12 and all(t[0] == "VARCHAR" for t in tipos)),
        ("2. raw.productos tiene los 12 productos del JSON",
         valor("SELECT COUNT(*) FROM raw.productos") == 12),
        ("3. stg_ventas deduplicó: 200.000 filas (una por venta_id)",
         valor("SELECT COUNT(*) FROM staging.stg_ventas") == 200_000),
        ("3b. Todas las fechas se parsearon (0 nulas), tipo DATE",
         valor("SELECT COUNT(*) FROM staging.stg_ventas WHERE fecha IS NULL") == 0
         and valor("SELECT COUNT(*) FROM staging.stg_ventas WHERE fecha >= DATE '2025-01-01'") == 200_000),
        ("3c. Las 15 escrituras de región quedaron en 5 limpias",
         [r[0] for r in filas("SELECT DISTINCT region FROM staging.stg_ventas ORDER BY 1")]
         == ["Centro", "Este", "Norte", "Oeste", "Sur"]),
        ("3d. El monto se convirtió a número: 3.946 nulos y 4.881.951,01 de ingresos",
         valor("SELECT COUNT(*) FROM staging.stg_ventas WHERE monto IS NULL") == 3_946
         and round(float(valor("SELECT SUM(monto) FROM staging.stg_ventas", 0)), 2) == 4_881_951.01),
        ("4. Ticket medio por canal: 4 canales, lidera Web con 50.117 ventas",
         len(r4) == 4 and r4[0][0] == "Web" and r4[0][1] == 50_117),
        ("5. marts.fct_ventas: 196.054 hechos (sin los montos nulos)",
         valor("SELECT COUNT(*) FROM marts.fct_ventas") == 196_054),
        ("5b. fct_ventas tiene la columna mes truncada al mes",
         valor("SELECT COUNT(DISTINCT mes) FROM marts.fct_ventas") == 18),
        ("6. ventas_mensuales: 90 filas (18 meses x 5 regiones)",
         valor("SELECT COUNT(*) FROM marts.ventas_mensuales") == 90),
        ("6b. El mejor mes del negocio es diciembre 2025",
         str(valor("SELECT mes FROM marts.ventas_mensuales GROUP BY mes "
                   "ORDER BY SUM(ingresos) DESC LIMIT 1")) == "2025-12-01"),
        ("6c. var_pct calculada por región con LAG (la primera fila de cada región es NULL)",
         valor("SELECT COUNT(*) FROM marts.ventas_mensuales WHERE var_pct IS NULL") == 5),
        ("7. El test detecta 998 venta_id duplicados en el crudo",
         len(r7) == 998 and all(r[1] >= 2 for r in r7)),
    ]

    ejecutar(8, SQL_8)
    checks += [
        ("8. Tras la carga incremental, raw.ventas llega a 211.020 filas",
         valor("SELECT COUNT(*) FROM raw.ventas") == 211_020),
        ("8b. Staging se actualizó SOLO (es una vista): 210.000 filas",
         valor("SELECT COUNT(*) FROM staging.stg_ventas") == 210_000),
    ]

    print("\n" + "=" * 62)
    print("RESULTADO DE LA ACTIVIDAD ETL/ELT")
    print("=" * 62)
    aciertos = 0
    for nombre, paso in checks:
        try:
            paso = bool(paso)
        except Exception:
            paso = False
        print(f"  {'OK   ' if paso else 'FALLA'}  {nombre}")
        aciertos += paso
    print("-" * 62)
    print(f"  {aciertos}/{len(checks)} correctos")

    if errores:
        print("\n  Errores de SQL (arréglalos primero):")
        for n, msg in sorted(errores.items()):
            print(f"    SQL_{n}: {msg}")

    if aciertos == len(checks):
        print("\n  Pipeline ELT completo y verificado. Sigue con actividad_modelado_opt.py")
    else:
        print("\n  Revisa los FALLA. Para depurar una consulta suelta:")
        print("    import duckdb; duckdb.connect('data/warehouse_actividad.duckdb').sql(SQL_3).show()")

    con.close()


if __name__ == "__main__":
    corregir()
