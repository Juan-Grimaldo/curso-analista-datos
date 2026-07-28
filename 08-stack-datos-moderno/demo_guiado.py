"""
Demo guiado del Modulo 08 - El Modern Data Stack, de principio a fin.

Este demo no explica dbt: MONTA un proyecto dbt real y lo ejecuta delante de ti.
Al terminar tendras en tu repo la carpeta dbt_ventas/ con un proyecto completo
(fuentes, staging, marts, pruebas y documentacion) construido sobre DuckDB, que
es exactamente lo que pide el Reto del modulo y lo que puedes ensenar en una
entrevista.

Este script se ejecuta en tu repo de practica `curso-datos`. Copialo ahi, y desde
la raiz del repo ejecutalo con:  uv run demo_guiado.py
Cada PASO corresponde a una seccion del README.

Requisitos (en curso-datos):  uv add dbt-core dbt-duckdb duckdb
y copiar ventas_ejemplo.csv del material a  data/raw/

Es idempotente: puedes ejecutarlo las veces que quieras.
"""

import os
import pathlib
import subprocess
import sys
import textwrap

import duckdb

# DuckDB dibuja sus tablas con caracteres unicode; en la consola de Windows hay
# que pedir UTF-8 explicitamente o revienta al imprimir.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CSV = "data/raw/ventas_ejemplo.csv"
PROYECTO = pathlib.Path("dbt_ventas")          # el proyecto dbt que vamos a generar
ALMACEN = pathlib.Path("data/warehouse.duckdb")  # nuestro "data warehouse" local


def titulo(n, texto):
    print(f"\n{'=' * 66}\nPASO {n}: {texto}\n{'=' * 66}")


def escribir(ruta, contenido):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(textwrap.dedent(contenido).lstrip(), encoding="utf-8")
    print(f"  escrito: {ruta}")


def dbt(*args, esperar_exito=True):
    """Ejecuta un comando dbt dentro del proyecto y devuelve (codigo, salida)."""
    cmd = [sys.executable, "-m", "dbt.cli.main", *args,
           "--project-dir", str(PROYECTO), "--profiles-dir", str(PROYECTO)]
    print(f"\n  $ dbt {' '.join(args)}")
    r = subprocess.run(cmd, capture_output=True, text=True)
    salida = r.stdout + r.stderr
    for linea in salida.splitlines():
        if linea.strip() and not linea.startswith("<frozen runpy>"):
            print(f"  | {linea}")
    if esperar_exito and r.returncode != 0:
        raise SystemExit("dbt fallo. Revisa la salida de arriba.")
    return r.returncode, salida


if not os.path.exists(CSV):
    raise SystemExit(f"Falta {CSV}. Copia ventas_ejemplo.csv del material a data/raw/")


# ── PASO 1: EL WAREHOUSE Y LOS DATOS CRUDOS (7.1 / 7.2) ───────────
titulo(1, "El warehouse y la capa RAW: lo que dejaria ahi Fivetran/Airbyte (7.1, 7.2)")
print("En una empresa, una herramienta de ingesta (EL) copia los datos tal cual")
print("llegan al warehouse. Nadie los limpia todavia: eso es trabajo de dbt (la T).")
print("Aqui hacemos ese paso a mano, una vez, para tener de que partir.\n")

ALMACEN.parent.mkdir(parents=True, exist_ok=True)
con = duckdb.connect(str(ALMACEN))
con.execute("CREATE SCHEMA IF NOT EXISTS raw")
con.execute(f"CREATE OR REPLACE TABLE raw.ventas AS SELECT * FROM '{CSV}'")
con.execute("""
    CREATE OR REPLACE TABLE raw.productos AS
    SELECT * FROM (VALUES
        ('A', 'Alfa',  'Bebidas'),
        ('B', 'Beta',  'Snacks'),
        ('C', 'Cesar', 'Bebidas'),
        ('D', 'Delta', 'Snacks')
    ) AS t(producto, nombre, categoria)
""")
n_raw = con.execute("SELECT COUNT(*) FROM raw.ventas").fetchone()[0]
n_nulos = con.execute("SELECT COUNT(*) FROM raw.ventas WHERE ventas IS NULL").fetchone()[0]
n_dups = con.execute("""
    SELECT COUNT(*) FROM (
        SELECT venta_id, COUNT(*) c FROM raw.ventas GROUP BY venta_id HAVING c > 1
    )
""").fetchone()[0]
con.close()
print(f"  raw.ventas:    {n_raw} filas  ({n_nulos} con ventas NULL, "
      f"{n_dups} venta_id repetidos)")
print("  raw.productos: 4 filas")
print("\nCrudo significa crudo: nulos y duplicados incluidos. dbt los arregla, y")
print("sobre todo DEJA CONSTANCIA de que los arreglo. Eso es lo que no da un notebook.")

# ── PASO 2: LA ESTRUCTURA DE UN PROYECTO dbt (7.3) ────────────────
titulo(2, "Generar el proyecto dbt: configuracion y perfil (7.3, 7.5)")
escribir(PROYECTO / "dbt_project.yml", """
    name: dbt_ventas
    version: '1.0'
    profile: dbt_ventas

    model-paths: ['models']

    models:
      dbt_ventas:
        staging:
          +materialized: view      # staging: vistas, se recalculan siempre, cuestan 0
        marts:
          +materialized: table     # marts: tablas, se consultan mil veces al dia
""")

escribir(PROYECTO / "profiles.yml", f"""
    # El perfil dice DONDE construye dbt. Cambiar DuckDB por Snowflake o BigQuery
    # es cambiar este archivo: los modelos SQL no se tocan.
    # OJO: la ruta es relativa al directorio DESDE EL QUE ejecutas dbt, que en
    # este curso es siempre la raiz de tu repo curso-datos.
    dbt_ventas:
      target: dev
      outputs:
        dev:
          type: duckdb
          path: {ALMACEN.as_posix()}
          schema: analytics
""")
print("\n  materialized: view vs table es la decision de coste/velocidad mas comun")
print("  en dbt. Staging = vista (barata). Mart = tabla (rapida de consultar).")

# ── PASO 3: SOURCES Y CAPA STAGING (7.3) ──────────────────────────
titulo(3, "Declarar las fuentes y construir la capa staging (7.3)")
escribir(PROYECTO / "models/staging/_sources.yml", """
    version: 2

    sources:
      - name: raw
        description: Datos crudos tal como los deja la ingesta. Nadie los edita a mano.
        schema: raw
        tables:
          - name: ventas
            description: Una fila por venta registrada en el sistema de origen.
            columns:
              - name: venta_id
                description: Identificador de la venta en el sistema de origen.
                data_tests: [not_null]
              - name: ventas
                description: Importe vendido. En crudo VIENE CON NULOS (19).
                data_tests: [not_null]      # <- esta prueba VA A FALLAR. A proposito.
          - name: productos
            description: Catalogo de productos.
            columns:
              - name: producto
                data_tests: [unique, not_null]
""")

escribir(PROYECTO / "models/staging/stg_ventas.sql", """
    -- Capa STAGING: 1 fila por venta, limpia y estandarizada. Sin logica de negocio.
    -- Reglas que aplica (y que quedan documentadas para siempre en el repo):
    --   1. quita duplicados exactos
    --   2. descarta ventas sin importe
    --   3. normaliza la region a mayusculas
    with crudo as (
        select distinct * from {{ source('raw', 'ventas') }}
    )

    select
        venta_id,
        cast(fecha as date)               as fecha,
        upper(trim(region))               as region,
        producto,
        canal,
        cast(ventas as double)            as ventas,
        cast(descuento as double)         as descuento,
        trafico,
        ventas * (1 - descuento)          as ingreso_neto
    from crudo
    where ventas is not null
""")

escribir(PROYECTO / "models/staging/stg_productos.sql", """
    select
        producto,
        nombre,
        categoria
    from {{ source('raw', 'productos') }}
""")

escribir(PROYECTO / "models/staging/_models.yml", """
    version: 2

    models:
      - name: stg_ventas
        description: Ventas limpias, sin duplicados ni nulos. La base de todo lo demas.
        columns:
          - name: venta_id
            description: Clave primaria de la venta.
            data_tests: [unique, not_null]
          - name: region
            description: Region normalizada en mayusculas.
            data_tests:
              - not_null
              - accepted_values:
                  arguments:
                    values: ['NORTE', 'SUR', 'ESTE', 'OESTE']
          - name: ventas
            data_tests: [not_null]
          - name: producto
            description: Clave foranea al catalogo de productos.
            data_tests:
              - relationships:
                  arguments:
                    to: ref('stg_productos')
                    field: producto

      - name: stg_productos
        description: Catalogo de productos estandarizado.
        columns:
          - name: producto
            data_tests: [unique, not_null]
""")
print("\n  Fijate en el test `relationships`: comprueba que TODO producto vendido")
print("  existe en el catalogo. Es un JOIN que se verifica solo, cada dia.")

# ── PASO 4: LOS MARTS (7.3) ───────────────────────────────────────
titulo(4, "La capa marts: las tablas que consume el negocio (7.3)")
escribir(PROYECTO / "models/marts/ventas_mensuales.sql", """
    -- MART: la tabla que alimenta el dashboard de direccion.
    with ventas as (
        select * from {{ ref('stg_ventas') }}
    )

    select
        date_trunc('month', fecha)          as mes,
        region,
        count(*)                            as n_ventas,
        sum(ventas)                         as ventas_total,
        round(median(ventas), 2)            as ticket_mediano,
        round(sum(ingreso_neto), 2)         as ingreso_neto
    from ventas
    group by 1, 2
    order by 1, 2
""")

escribir(PROYECTO / "models/marts/ventas_por_producto.sql", """
    -- MART: rendimiento por producto, con el NOMBRE legible (no el codigo A/B/C/D).
    with ventas as (
        select * from {{ ref('stg_ventas') }}
    ),

    productos as (
        select * from {{ ref('stg_productos') }}
    )

    select
        p.nombre                            as producto,
        p.categoria,
        count(*)                            as n_ventas,
        sum(v.ventas)                       as ventas_total,
        round(avg(v.ventas), 2)             as ticket_medio,
        round(median(v.ventas), 2)          as ticket_mediano
    from ventas v
    left join productos p on v.producto = p.producto
    group by 1, 2
    order by ventas_total desc
""")

escribir(PROYECTO / "models/marts/_models.yml", """
    version: 2

    models:
      - name: ventas_mensuales
        description: |
          Ventas agregadas por mes y region. Fuente unica de verdad para el
          dashboard de direccion. Grano: una fila por mes y region.
        columns:
          - name: mes
            data_tests: [not_null]
          - name: ventas_total
            data_tests: [not_null]

      - name: ventas_por_producto
        description: Rendimiento por producto con su nombre y categoria.
        columns:
          - name: producto
            data_tests: [unique, not_null]
""")
print("\n  Ninguno de los dos marts sabe de donde salen los datos crudos: solo")
print("  conocen `ref('stg_ventas')`. Cambia la fuente manana y solo tocas staging.")

# ── PASO 5: LOS TESTS SOBRE EL CRUDO FALLAN (7.4) ─────────────────
titulo(5, "dbt test sobre las fuentes: el fallo que QUIERES ver (7.4)")
print("Probamos los datos crudos ANTES de transformarlos. Deberia fallar:")
print("declaramos que raw.ventas.ventas no admite nulos, y sabemos que hay 19.")
codigo, salida = dbt("test", "--select", "source:raw", esperar_exito=False)
if "FAIL" in salida or codigo != 0:
    print("\n  Fallo, como estaba previsto. Eso es exactamente lo que compras con dbt:")
    print("  el pipeline te avisa de que el dato de origen esta roto ANTES de que el")
    print("  dashboard ensene un numero equivocado. En una empresa esto manda una")
    print("  alerta a Slack a las 6:05 de la manana y nadie llega a ver el error.")
else:
    print("\n  (No fallo; revisa la salida de arriba.)")

# ── PASO 6: dbt build - CONSTRUIR Y PROBAR EN ORDEN (7.4) ─────────
titulo(6, "dbt build: construye el DAG en orden y prueba cada paso (7.4)")
print("Nadie le dice a dbt en que orden construir. Lo deduce de los ref() y source().")
dbt("build", "--exclude", "source:raw")
print("\n  Lee el orden de la salida: primero las vistas de staging, luego sus")
print("  pruebas, y solo si pasan, los marts. Si stg_ventas fallara, los marts")
print("  NO se construirian: te quedas con los datos de ayer, que son correctos,")
print("  en vez de con datos nuevos que estan mal. Esa es la diferencia.")

# ── PASO 7: EL RESULTADO EN EL WAREHOUSE ──────────────────────────
titulo(7, "Lo que quedo construido en el warehouse")
con = duckdb.connect(str(ALMACEN))
print("Objetos creados por dbt en el esquema analytics:")
con.sql("""
    SELECT table_schema, table_name, table_type
    FROM information_schema.tables
    WHERE table_schema NOT IN ('raw', 'information_schema')
    ORDER BY table_type DESC, table_name
""").show()

print("El mart ventas_por_producto, listo para el dashboard:")
con.sql("SELECT * FROM analytics.ventas_por_producto").show()

staging = con.execute("SELECT COUNT(*) FROM analytics.stg_ventas").fetchone()[0]
print("Trazabilidad de la limpieza, paso a paso:")
print(f"  raw.ventas                       {n_raw} filas")
print("  - duplicados exactos (distinct)  -15")
print("  - ventas sin importe (is null)   -18")
print(f"  = analytics.stg_ventas           {staging} filas")
print("\n  Ojo al matiz: en el Modulo 03 rellenamos los nulos con la mediana y nos")
print(f"  quedaban 720 filas; aqui los DESCARTAMOS y quedan {staging}. Ninguna de las dos")
print("  es 'la correcta': lo que importa es que la decision este escrita en el")
print("  modelo, versionada en git, y no escondida en la celda 14 de un notebook.")
print("  Si manana alguien pregunta por que faltan 33 ventas, la respuesta esta")
print("  en 4 lineas de stg_ventas.sql, no en la memoria de quien hizo el analisis.")
con.close()

# ── PASO 8: DOCUMENTACION Y LINAJE (7.4) ──────────────────────────
titulo(8, "dbt docs: documentacion y grafo de linaje (7.4)")
dbt("docs", "generate")
print(f"\n  Generado en {PROYECTO}/target/. Para verlo en el navegador:")
print(f"    uv run dbt docs serve --project-dir {PROYECTO} --profiles-dir {PROYECTO}")
print("  Ahi tienes el DAG interactivo: raw.ventas -> stg_ventas -> ventas_mensuales.")
print("  Captura ese diagrama: es lo que ensenas en una entrevista cuando te")
print("  preguntan 'has trabajado con dbt?'.")

# ── PASO 9: ORQUESTACION (7.6) ────────────────────────────────────
titulo(9, "Que haria un orquestador con todo esto cada manana (7.6)")
print("""
  06:00  Airbyte/Fivetran copia las ventas de ayer   -> raw.ventas
  06:10  dbt build                                   -> staging -> tests -> marts
  06:20  si algun test fallo: alerta a Slack y PARA (los marts no se refrescan)
  06:25  si todo paso: refresca el dashboard de Power BI
  06:30  el equipo comercial abre el dashboard con datos de ayer, correctos

  Airflow, Dagster o dbt Cloud solo son formas de escribir esa secuencia.
  El concepto que te piden entender en una entrevista es ese: orden, dependencias
  y que hacer cuando algo falla.
""")

print("=" * 66)
print("LO QUE TE LLEVAS")
print("=" * 66)
print("  1. dbt no es una herramienta nueva de SQL: es SQL con git, pruebas y docs.")
print("  2. raw -> staging -> marts. Cada capa tiene un unico trabajo.")
print("  3. Un test que falla es el sistema funcionando, no el sistema roto.")
print("  4. El DAG lo deduce dbt de tus ref(): tu nunca ordenas nada a mano.")
print(f"\n  Tu proyecto quedo en {PROYECTO}/ - hazle commit, es material de portafolio.")
print("\nAhora hazlo tu:  uv run actividad_01.py")
