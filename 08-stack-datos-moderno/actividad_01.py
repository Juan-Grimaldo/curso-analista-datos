"""
ACTIVIDAD 01 - Modulo 08 (Modern Data Stack: dbt + DuckDB)
==========================================================
Mismo tipo de proyecto que demo_guiado.py, pero ahora los modelos los escribes TU,
y sobre otras preguntas (foco en `canal` y en la evolucion mensual).

Este archivo se trabaja en tu repo de practica `curso-datos`. Copialo ahi y
ejecutalo desde la raiz del repo con:  uv run actividad_01.py

Como funciona (leelo entero antes de empezar):
  1. La PRIMERA vez que lo ejecutes, crea el proyecto  dbt_actividad/  con los
     archivos a medias: los .sql llevan un TODO donde falta tu SQL.
  2. Abre esos archivos en el editor y complatalos.
  3. Vuelve a ejecutar  uv run actividad_01.py . Ahora ejecuta `dbt build` y
     corrige: comprueba las tablas construidas Y las pruebas que declaraste.
  4. Repite hasta 8/8. El script NUNCA sobrescribe lo que ya escribiste.

Archivos que tienes que tocar (los 3):
  dbt_actividad/models/staging/stg_ventas.sql
  dbt_actividad/models/staging/_models.yml
  dbt_actividad/models/marts/ventas_por_canal.sql
  dbt_actividad/models/marts/evolucion_mensual.sql

Requisitos (en curso-datos):  uv add dbt-core dbt-duckdb duckdb
y copiar ventas_ejemplo.csv del material a  data/raw/

Pistas: README secciones 7.3 a 7.5, y el SQL de los Modulos 04 y 05
(el LAG del mart mensual es literalmente el del Modulo 05).
"""

import json
import os
import pathlib
import subprocess
import sys
import textwrap

import duckdb

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CSV = "data/raw/ventas_ejemplo.csv"
PROYECTO = pathlib.Path("dbt_actividad")
ALMACEN = pathlib.Path("data/warehouse_actividad.duckdb")

MARCA = "-- TODO"    # si un modelo aun tiene esta marca, no lo has completado


# ══════════════════════════════════════════════════════════════════
#  1. ANDAMIAJE - crea los archivos solo si no existen
# ══════════════════════════════════════════════════════════════════
def crear(ruta, contenido):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    if ruta.exists():
        return False
    ruta.write_text(textwrap.dedent(contenido).lstrip(), encoding="utf-8")
    print(f"  creado: {ruta}")
    return True


def preparar_warehouse():
    ALMACEN.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(ALMACEN))
    con.execute("CREATE SCHEMA IF NOT EXISTS raw")
    con.execute(f"CREATE OR REPLACE TABLE raw.ventas AS SELECT * FROM '{CSV}'")
    con.close()


def andamiaje():
    nuevos = []
    nuevos.append(crear(PROYECTO / "dbt_project.yml", """
        name: dbt_actividad
        version: '1.0'
        profile: dbt_actividad

        model-paths: ['models']

        models:
          dbt_actividad:
            staging:
              +materialized: view
            marts:
              +materialized: table
    """))

    nuevos.append(crear(PROYECTO / "profiles.yml", f"""
        # Ruta relativa a la raiz de tu repo, que es desde donde ejecutas todo.
        dbt_actividad:
          target: dev
          outputs:
            dev:
              type: duckdb
              path: {ALMACEN.as_posix()}
              schema: analytics
    """))

    nuevos.append(crear(PROYECTO / "models/staging/_sources.yml", """
        version: 2

        sources:
          - name: raw
            schema: raw
            tables:
              - name: ventas
                description: Ventas crudas, con duplicados y nulos incluidos.
    """))

    nuevos.append(crear(PROYECTO / "models/staging/stg_ventas.sql", """
        -- EJERCICIO 1 -----------------------------------------------------
        -- Capa staging. Escribe un SELECT sobre {{ source('raw', 'ventas') }} que:
        --   1. elimine duplicados exactos            (select distinct ...)
        --   2. descarte las filas con ventas NULL    (where ventas is not null)
        --   3. deje la region en MAYUSCULAS          (upper(trim(region)))
        --   4. castee fecha a date
        --   5. anada una columna `mes` con date_trunc('month', fecha)
        -- Debe devolver 702 filas y estas columnas (los nombres importan):
        --   venta_id, fecha, mes, region, producto, canal, ventas, descuento, trafico
        -- TODO: escribe aqui tu modelo
        select 1 as venta_id
    """))

    nuevos.append(crear(PROYECTO / "models/staging/_models.yml", """
        version: 2

        # EJERCICIO 2 -------------------------------------------------------
        # Declara las pruebas de calidad de stg_ventas. Necesitas exactamente:
        #   - venta_id : unique y not_null
        #   - canal    : accepted_values con los valores 'Web', 'Movil', 'Tienda'
        #   - ventas   : not_null
        # Y una `description` en el modelo y en al menos una columna.
        # El formato exacto esta en el README (7.4) y en el proyecto del demo.
        models:
          - name: stg_ventas
            description: TODO escribe aqui que contiene este modelo
            columns:
              - name: venta_id
                # TODO: data_tests: [...]
    """))

    nuevos.append(crear(PROYECTO / "models/marts/ventas_por_canal.sql", """
        -- EJERCICIO 3 -----------------------------------------------------
        -- Mart de rendimiento por canal, construido SOBRE staging
        -- (usa {{ ref('stg_ventas') }}, nunca la fuente cruda).
        -- Devuelve una fila por canal, ordenadas por ventas_total descendente,
        -- con estas columnas exactas:
        --   canal, n_ventas, ventas_total, ticket_mediano
        -- (n_ventas = count(*), ticket_mediano = median(ventas))
        -- TODO: escribe aqui tu modelo
        select 1 as canal
    """))

    nuevos.append(crear(PROYECTO / "models/marts/evolucion_mensual.sql", """
        -- EJERCICIO 4 -----------------------------------------------------
        -- Mart de evolucion mensual con la variacion respecto al mes anterior.
        -- Sobre {{ ref('stg_ventas') }}, una fila por mes, columnas exactas:
        --   mes, ventas_total, variacion_pct
        -- variacion_pct = 100 * (total - total_mes_anterior) / total_mes_anterior,
        -- redondeado a 1 decimal, con LAG() OVER (ORDER BY mes)  <- Modulo 05.
        -- El primer mes tendra variacion_pct NULL: es correcto.
        -- TODO: escribe aqui tu modelo
        select 1 as mes
    """))

    nuevos.append(crear(PROYECTO / "models/marts/_models.yml", """
        version: 2

        models:
          - name: ventas_por_canal
            description: Rendimiento por canal de venta.
          - name: evolucion_mensual
            description: Ventas por mes y variacion frente al mes anterior.
    """))
    return any(nuevos)


# ══════════════════════════════════════════════════════════════════
#  2. EJECUTAR dbt
# ══════════════════════════════════════════════════════════════════
def dbt(*args):
    cmd = [sys.executable, "-m", "dbt.cli.main", *args,
           "--project-dir", str(PROYECTO), "--profiles-dir", str(PROYECTO)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


# ══════════════════════════════════════════════════════════════════
#  CORRECTOR - no toques nada de aqui abajo
# ══════════════════════════════════════════════════════════════════
def tests_declarados(manifest):
    """Devuelve {(columna, tipo_de_test)} de los tests sobre stg_ventas."""
    encontrados = set()
    for nodo in manifest.get("nodes", {}).values():
        if nodo.get("resource_type") != "test":
            continue
        if not any("stg_ventas" in d for d in nodo.get("depends_on", {}).get("nodes", [])):
            continue
        col = (nodo.get("column_name") or "").lower()
        nombre = nodo.get("name", "")
        for tipo in ("unique", "not_null", "accepted_values", "relationships"):
            if nombre.startswith(tipo):
                encontrados.add((col, tipo))
    return encontrados


def corregir():
    if not os.path.exists(CSV):
        raise SystemExit(f"Falta {CSV}. Copia ventas_ejemplo.csv del material a data/raw/")

    print("=" * 66)
    print("ACTIVIDAD 01 - Modulo 08")
    print("=" * 66)
    preparar_warehouse()
    if andamiaje():
        print("\n  Proyecto creado. Ahora abre los archivos con -- TODO, completalos")
        print("  y vuelve a ejecutar:  uv run actividad_01.py")
        return

    pendientes = [p for p in PROYECTO.rglob("*")
                  if p.suffix in (".sql", ".yml") and MARCA in p.read_text(encoding="utf-8")]
    if pendientes:
        print("\n  Todavia hay archivos sin completar (les queda la marca TODO):")
        for p in pendientes:
            print(f"    - {p}")
        print("\n  Completalos y vuelve a ejecutar. Aun asi intento construir, para")
        print("  que veas los errores de dbt desde el principio.\n")

    print("\n  $ dbt build")
    codigo, salida = dbt("build")
    for linea in salida.splitlines():
        if any(marca in linea for marca in ("PASS", "FAIL", "ERROR", "OK created",
                                            "Done.", "Compilation Error", "Database Error")):
            print(f"  | {linea.strip()}")

    manifest_path = PROYECTO / "target" / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    tests = tests_declarados(manifest)

    con = duckdb.connect(str(ALMACEN))

    def filas(sql):
        try:
            return con.execute(sql).fetchall()
        except Exception:
            return None

    def columnas(tabla):
        r = filas(f"SELECT * FROM analytics.{tabla} LIMIT 0")
        return [d[0].lower() for d in con.description] if r is not None else []

    stg = filas("SELECT COUNT(*) FROM analytics.stg_ventas")
    stg_cols = columnas("stg_ventas")
    regiones = filas("SELECT DISTINCT region FROM analytics.stg_ventas")
    canal = filas("SELECT * FROM analytics.ventas_por_canal")
    canal_cols = columnas("ventas_por_canal")
    mensual = filas("SELECT * FROM analytics.evolucion_mensual ORDER BY mes")

    def c1():
        return stg and stg[0][0] == 702

    def c2():
        necesarias = {"venta_id", "fecha", "mes", "region", "producto",
                      "canal", "ventas", "descuento", "trafico"}
        return necesarias.issubset(set(stg_cols))

    def c3():
        return regiones and {r[0] for r in regiones} == {"NORTE", "SUR", "ESTE", "OESTE"}

    def c4():
        return {("venta_id", "unique"), ("venta_id", "not_null"),
                ("ventas", "not_null")}.issubset(tests)

    def c5():
        return ("canal", "accepted_values") in tests

    def c6():
        return (canal_cols[:4] == ["canal", "n_ventas", "ventas_total", "ticket_mediano"]
                and len(canal) == 3 and canal[0][0] == "Movil"
                and canal[0][1] == 224 and abs(float(canal[0][2]) - 24655.0) < 1)

    def c7():
        if not mensual or len(mensual) != 6:
            return False
        primero, ultimo = mensual[0], mensual[-1]
        return (abs(float(primero[1]) - 11637.0) < 1 and primero[2] is None
                and abs(float(ultimo[1]) - 10564.0) < 1
                and abs(float(ultimo[2]) - (-21.5)) < 0.2)

    def c8():
        return codigo == 0 and "ERROR=0" in salida

    checks = [
        ("1. stg_ventas construido con 702 filas (sin duplicados ni nulos)", c1),
        ("2. stg_ventas tiene las 9 columnas pedidas, incluida `mes`", c2),
        ("3. La region quedo normalizada: NORTE, SUR, ESTE, OESTE", c3),
        ("4. Pruebas declaradas: venta_id unique + not_null, ventas not_null", c4),
        ("5. Prueba accepted_values sobre canal", c5),
        ("6. Mart ventas_por_canal: 3 filas, lidera Movil (224 ventas, 24 655)", c6),
        ("7. Mart evolucion_mensual: 6 meses, junio -21.5% con LAG", c7),
        ("8. `dbt build` termina sin un solo error", c8),
    ]

    print("\n" + "=" * 66)
    print("RESULTADO DE LA ACTIVIDAD")
    print("=" * 66)
    aciertos = 0
    for nombre, comprobar in checks:
        try:
            paso = bool(comprobar())
        except Exception:
            paso = False
        print(f"  {'OK  ' if paso else 'FALLA'}  {nombre}")
        aciertos += paso
    print("-" * 66)
    print(f"  {aciertos}/{len(checks)} correctos")
    con.close()

    if aciertos == len(checks):
        print("\n  Perfecto. Tienes un proyecto dbt completo, probado y versionable.")
        print("  Remate final (2 minutos, y es lo que ensenas en una entrevista):")
        print(f"    uv run dbt docs generate --project-dir {PROYECTO} --profiles-dir {PROYECTO}")
        print(f"    uv run dbt docs serve    --project-dir {PROYECTO} --profiles-dir {PROYECTO}")
        print("  Captura el grafo de linaje y guardalo en tu portafolio.")
        print("\n  Listo para el Modulo 09.")
    else:
        print("\n  Revisa los FALLA. Si dbt dio un error de compilacion, arreglalo")
        print("  primero: hasta que compile, ningun modelo se construye.")
        print(f"  Salida completa:  uv run dbt build --project-dir {PROYECTO} "
              f"--profiles-dir {PROYECTO}")


if __name__ == "__main__":
    corregir()
