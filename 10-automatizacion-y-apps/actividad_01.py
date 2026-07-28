"""
ACTIVIDAD 01 - Modulo 10 (Automatizacion y apps de datos)
=========================================================
Mismo tipo de trabajo que demo_guiado.py, pero ahora el pipeline lo escribes TU,
y sobre otra pregunta (foco en `canal` en vez de `region`).

Este archivo se trabaja en tu repo de practica `curso-datos`. Copialo ahi y
ejecutalo desde la raiz del repo con:  uv run actividad_01.py

Como funciona (leelo entero antes de empezar):
  1. La PRIMERA vez que lo ejecutes crea dos archivos a medias:
        src/pipeline_actividad.py
        app_actividad.py
  2. Abrelos y completa lo que dice TODO.
  3. Vuelve a ejecutar  uv run actividad_01.py . El corrector importa tus
     funciones, ejecuta tu pipeline de verdad (incluso con datos rotos, para
     ver si sabe fallar) y revisa tu app.
  4. Repite hasta 8/8. El script NUNCA sobrescribe lo que ya escribiste.

Requisitos (en curso-datos):  uv add pandas pyarrow
y copiar ventas_ejemplo.csv del material a  data/raw/

Pistas: README secciones 9.2 a 9.7. No mires demo_guiado.py hasta haberlo
intentado al menos dos veces.
"""

import importlib
import os
import pathlib
import subprocess
import sys
import textwrap

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CSV = "data/raw/ventas_ejemplo.csv"
PIPELINE = pathlib.Path("src/pipeline_actividad.py")
APP = pathlib.Path("app_actividad.py")
SALIDA = pathlib.Path("data/processed/ventas_por_canal.parquet")
MARCA = "TODO"


# ══════════════════════════════════════════════════════════════════
#  ANDAMIAJE - crea los archivos solo si no existen
# ══════════════════════════════════════════════════════════════════
def crear(ruta, contenido):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    if ruta.exists():
        return False
    ruta.write_text(textwrap.dedent(contenido).lstrip(), encoding="utf-8")
    print(f"  creado: {ruta}")
    return True


def andamiaje():
    nuevos = [
        crear(PIPELINE, '''
            """Pipeline de ventas por canal.

            Uso:  uv run python src/pipeline_actividad.py [--entrada RUTA] [--salida RUTA]
            Debe devolver 0 si todo va bien y 1 si los datos no pasan las validaciones.
            """

            import argparse
            import logging
            import pathlib
            import sys

            import pandas as pd

            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s | %(levelname)-7s | %(message)s",
                datefmt="%H:%M:%S",
            )
            log = logging.getLogger("pipeline")

            # EJERCICIO 5 ---------------------------------------------------
            # El cron que ejecutaria este pipeline TODOS LOS LUNES A LAS 8:00.
            # Formato: "minuto hora dia_del_mes mes dia_de_la_semana"
            # (lunes = 1). Compruebalo en crontab.guru antes de darlo por bueno.
            CRON_SEMANAL = "TODO"


            def cargar(ruta: str) -> pd.DataFrame:
                """Ya hecho: no lo toques."""
                df = pd.read_csv(ruta, parse_dates=["fecha"])
                log.info("Cargadas %d filas de %s", len(df), ruta)
                return df


            # EJERCICIO 1 ---------------------------------------------------
            # Devuelve el DataFrame limpio:
            #   1. sin filas duplicadas
            #   2. los nulos de `ventas` rellenos con la MEDIANA
            #   3. `canal` sin espacios sobrantes (.str.strip())
            # No cambies la firma ni el nombre.
            def limpiar(df: pd.DataFrame) -> pd.DataFrame:
                # TODO
                ...


            # EJERCICIO 2 ---------------------------------------------------
            # Devuelve UNA fila por mes y canal, con estas columnas EXACTAS y en
            # este orden:  mes, canal, ventas, n_ventas
            #   - mes:      el mes como texto 'AAAA-MM'  (dt.to_period("M").astype(str))
            #   - ventas:   suma de ventas
            #   - n_ventas: numero de transacciones
            # Ordenado por mes y canal, con el indice reiniciado.
            def agregar_por_canal(df: pd.DataFrame) -> pd.DataFrame:
                # TODO
                ...


            # EJERCICIO 3 ---------------------------------------------------
            # Contrato de datos de la SALIDA. Devuelve una LISTA de strings con
            # los problemas encontrados (lista vacia = todo correcto).
            # Tiene que detectar, con estos textos exactos:
            #   "salida vacia"        -> si el DataFrame no tiene filas
            #   "ventas negativas"    -> si alguna venta es < 0
            #   "grano duplicado"     -> si se repite alguna combinacion mes+canal
            def validar(df: pd.DataFrame) -> list:
                # TODO
                ...


            # EJERCICIO 4 ---------------------------------------------------
            # Completa main() para que:
            #   - cargue, limpie y agregue
            #   - si validar() devuelve problemas: los registre con log.error y
            #     devuelva 1 SIN escribir el archivo de salida
            #   - si no hay problemas: guarde el parquet y devuelva 0
            def main() -> int:
                p = argparse.ArgumentParser()
                p.add_argument("--entrada", default="data/raw/ventas_ejemplo.csv")
                p.add_argument("--salida", default="data/processed/ventas_por_canal.parquet")
                args = p.parse_args()

                # TODO: el flujo completo, y el return 0 / return 1
                ...


            if __name__ == "__main__":
                sys.exit(main())
        '''),
        crear(APP, '''
            """Dashboard de ventas por canal.

            Lanzalo con:  uv run streamlit run app_actividad.py
            (necesitas:   uv add streamlit plotly )

            EJERCICIO 6 -------------------------------------------------------
            Tu app tiene que incluir, como minimo:
              - @st.cache_data en la funcion que lee el parquet
              - un st.sidebar.multiselect para filtrar por canal
              - DOS st.metric (dos KPIs distintos)
              - un grafico: st.plotly_chart(...) o st.line_chart(...)
            El corrector revisa que esos elementos esten en el archivo; que la app
            se vea bien lo juzgas tu abriendola en el navegador.
            """

            import pandas as pd
            import streamlit as st

            st.set_page_config(page_title="Ventas por canal", layout="wide")
            st.title("Ventas por canal - 1er semestre 2026")

            # TODO: escribe aqui tu app
        '''),
    ]
    return any(nuevos)


# ══════════════════════════════════════════════════════════════════
#  CORRECTOR - no toques nada de aqui abajo
# ══════════════════════════════════════════════════════════════════
def datos_de_prueba():
    """Dataset diminuto: 5 filas, con 1 duplicado y 1 nulo. Resultado conocido."""
    return pd.DataFrame({
        "fecha": pd.to_datetime(["2026-01-05", "2026-01-05", "2026-01-20",
                                 "2026-02-03", "2026-02-10"]),
        "canal": [" Web ", " Web ", "Movil", "Web", "Movil"],
        "ventas": [100.0, 100.0, 50.0, None, 30.0],
    })


def correr(args, descripcion):
    print(f"\n  $ python {PIPELINE} {' '.join(args)}   ({descripcion})")
    r = subprocess.run([sys.executable, str(PIPELINE), *args],
                       capture_output=True, text=True)
    for linea in (r.stdout + r.stderr).splitlines()[-6:]:
        if linea.strip():
            print(f"  | {linea}")
    print(f"  | [codigo de salida: {r.returncode}]")
    return r.returncode


def corregir():
    if not os.path.exists(CSV):
        raise SystemExit(f"Falta {CSV}. Copia ventas_ejemplo.csv del material a data/raw/")

    print("=" * 68)
    print("ACTIVIDAD 01 - Modulo 10")
    print("=" * 68)
    if andamiaje():
        print("\n  Archivos creados. Completa los TODO y vuelve a ejecutar:")
        print("    uv run actividad_01.py")
        return

    sys.path.insert(0, str(PIPELINE.parent.resolve()))
    try:
        mod = importlib.import_module(PIPELINE.stem)
        importlib.reload(mod)
    except Exception as e:
        print(f"\n  Tu pipeline no se puede ni importar: {type(e).__name__}: {e}")
        print("  Arregla el error de sintaxis y vuelve a ejecutar.")
        return

    def s(fn, *args):
        try:
            return fn(*args)
        except Exception as e:
            return e

    limpio = s(getattr(mod, "limpiar", lambda *_: None), datos_de_prueba())
    agregado = s(getattr(mod, "agregar_por_canal", lambda *_: None),
                 limpio if isinstance(limpio, pd.DataFrame) else datos_de_prueba())

    # Ejecutamos el pipeline de verdad: con datos buenos y con datos rotos
    SALIDA.unlink(missing_ok=True)
    codigo_ok = correr([], "datos correctos: se espera 0")
    roto = pathlib.Path("data/raw/_ventas_roto.csv")
    df_roto = pd.read_csv(CSV)
    df_roto["ventas"] = -df_roto["ventas"].abs()       # todo en negativo: signo invertido
    df_roto.to_csv(roto, index=False)
    codigo_roto = correr(["--entrada", str(roto), "--salida", "data/processed/_tmp.parquet"],
                         "ventas negativas: se espera 1")
    roto.unlink(missing_ok=True)
    pathlib.Path("data/processed/_tmp.parquet").unlink(missing_ok=True)

    app_txt = APP.read_text(encoding="utf-8") if APP.exists() else ""
    pipe_txt = PIPELINE.read_text(encoding="utf-8")

    def c1():
        return (isinstance(limpio, pd.DataFrame) and len(limpio) == 4
                and limpio["ventas"].isna().sum() == 0
                and set(limpio["canal"]) == {"Web", "Movil"})

    def c2():
        return (isinstance(agregado, pd.DataFrame)
                and list(agregado.columns) == ["mes", "canal", "ventas", "n_ventas"]
                and len(agregado) == 4
                and str(agregado["mes"].iloc[0]) == "2026-01"
                and not agregado.duplicated(subset=["mes", "canal"]).any())

    def c3():
        validar = getattr(mod, "validar")
        vacio = pd.DataFrame({"mes": [], "canal": [], "ventas": []})
        neg = pd.DataFrame({"mes": ["2026-01"], "canal": ["Web"], "ventas": [-1.0]})
        dup = pd.DataFrame({"mes": ["2026-01", "2026-01"], "canal": ["Web", "Web"],
                            "ventas": [1.0, 2.0]})
        buena = agregado
        return ("salida vacia" in validar(vacio)
                and "ventas negativas" in validar(neg)
                and "grano duplicado" in validar(dup)
                and validar(buena) == [])

    def c4():
        return codigo_ok == 0 and SALIDA.exists()

    def c5():
        return codigo_roto == 1 and not pathlib.Path("data/processed/_tmp.parquet").exists()

    def c6():
        salida = pd.read_parquet(SALIDA)
        return (len(salida) == 18 and list(salida.columns) == ["mes", "canal", "ventas", "n_ventas"]
                and abs(salida["ventas"].sum() - 72324.0) < 1)

    def c7():
        return getattr(mod, "CRON_SEMANAL", "").strip() in ("0 8 * * 1", "0 8 * * MON")

    def c8():
        t = app_txt
        return ("@st.cache_data" in t and "multiselect" in t
                and t.count(".metric(") >= 2      # st.metric(...) o col.metric(...)
                and ("plotly_chart" in t or "line_chart" in t or "bar_chart" in t))

    checks = [
        ("1. limpiar(): 4 filas, sin nulos, canal normalizado", c1),
        ("2. agregar_por_canal(): 3 filas, columnas y grano correctos", c2),
        ("3. validar(): detecta vacio, negativos y grano duplicado", c3),
        ("4. El pipeline con datos buenos devuelve 0 y escribe el parquet", c4),
        ("5. Con ventas negativas devuelve 1 y NO escribe nada", c5),
        ("6. La salida real tiene 18 filas (6 meses x 3 canales) y 72 324 USD", c6),
        ("7. CRON_SEMANAL es el cron de los lunes a las 8:00", c7),
        ("8. La app trae cache, filtro multiselect, 2 KPIs y un grafico", c8),
    ]

    print("\n" + "=" * 68)
    print("RESULTADO DE LA ACTIVIDAD")
    print("=" * 68)
    aciertos = 0
    for nombre, comprobar in checks:
        try:
            paso = bool(comprobar())
        except Exception:
            paso = False
        print(f"  {'OK  ' if paso else 'FALLA'}  {nombre}")
        aciertos += paso
    print("-" * 68)
    print(f"  {aciertos}/{len(checks)} correctos")

    if MARCA in pipe_txt or MARCA in app_txt:
        print("\n  (Todavia quedan marcas TODO sin completar en tus archivos.)")

    if aciertos == len(checks):
        print("\n  Perfecto. Tienes un pipeline que valida, falla a tiempo y alimenta")
        print("  una app. Remate final, y es el que va en tu CV:")
        print("    1. uv add streamlit plotly && uv run streamlit run app_actividad.py")
        print("    2. escribe tests/ para tus tres funciones (copia el patron del demo)")
        print("    3. publica la app en Streamlit Community Cloud y pon la URL en tu README")
        print("\n  Listo para el Modulo 11: el proyecto final.")
    else:
        print("\n  Revisa los FALLA. Si el 4 y el 5 fallan a la vez, tu main() seguramente")
        print("  no esta devolviendo nada: acuerdate del  return 0 / return 1.")


if __name__ == "__main__":
    corregir()
