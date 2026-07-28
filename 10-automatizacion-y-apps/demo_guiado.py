"""
Demo guiado del Modulo 10 - Automatizacion y apps de datos, de principio a fin.

Este demo no habla de automatizar: automatiza. Genera en tu repo un pipeline de
verdad (con logging, validaciones y codigo de salida), lo ejecuta, comprueba que
es reproducible, lo rompe a proposito para que veas como falla, le escribe las
pruebas, el workflow de GitHub Actions y una app de Streamlit.

Al terminar tendras en curso-datos:
    src/pipeline_ventas.py          el pipeline
    tests/test_pipeline.py          sus pruebas
    .github/workflows/pipeline.yml  la ejecucion diaria automatica
    app.py                          el dashboard
    data/processed/ventas_mensuales.parquet

Este script se ejecuta en tu repo de practica `curso-datos`. Copialo ahi, y desde
la raiz del repo ejecutalo con:  uv run demo_guiado.py
Cada PASO corresponde a una seccion del README.

Requisitos (en curso-datos):  uv add pandas pyarrow
Opcionales:  uv add pytest         (PASO 5, las pruebas)
             uv add streamlit plotly   (PASO 7, lanzar la app)
y copiar ventas_ejemplo.csv del material a  data/raw/
"""

import hashlib
import os
import pathlib
import shutil
import subprocess
import sys
import textwrap

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CSV = "data/raw/ventas_ejemplo.csv"
PIPELINE = pathlib.Path("src/pipeline_ventas.py")
SALIDA = pathlib.Path("data/processed/ventas_mensuales.parquet")


def titulo(n, texto):
    print(f"\n{'=' * 68}\nPASO {n}: {texto}\n{'=' * 68}")


def escribir(ruta, contenido):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(textwrap.dedent(contenido).lstrip(), encoding="utf-8")
    print(f"  escrito: {ruta}")


def correr(cmd, descripcion):
    """Ejecuta un comando y muestra su salida y su codigo de retorno."""
    print(f"\n  $ {' '.join(cmd)}   ({descripcion})")
    r = subprocess.run(cmd, capture_output=True, text=True)
    for linea in (r.stdout + r.stderr).splitlines():
        if linea.strip():
            print(f"  | {linea}")
    print(f"  | [codigo de salida: {r.returncode}]")
    return r.returncode


def sha256(ruta):
    return hashlib.sha256(pathlib.Path(ruta).read_bytes()).hexdigest()[:16]


if not os.path.exists(CSV):
    raise SystemExit(f"Falta {CSV}. Copia ventas_ejemplo.csv del material a data/raw/")


# ── PASO 1: DE NOTEBOOK A SCRIPT (9.1, 9.2) ───────────────────────
titulo(1, "El notebook no es un producto: escribir el pipeline (9.1, 9.2)")
print("Tu notebook del Modulo 03 hace el trabajo, pero nadie mas puede ejecutarlo:")
print("hay que abrirlo, correr las celdas en orden y esperar que ninguna falle.")
print("Un pipeline es lo mismo, pero que se ejecuta solo y avisa si algo va mal.\n")

escribir(PIPELINE, '''
    """Pipeline de ventas: lee el CSV crudo, limpia, agrega por mes y region.

    Uso:  uv run python src/pipeline_ventas.py [--entrada RUTA] [--salida RUTA]
    Devuelve codigo 0 si todo fue bien, 1 si los datos no pasan las validaciones.
    """

    import argparse
    import logging
    import sys

    import pandas as pd

    # logging, no print: lleva hora, nivel y se puede redirigir a un archivo
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%H:%M:%S",
    )
    log = logging.getLogger("pipeline")


    def cargar(ruta: str) -> pd.DataFrame:
        """Lee el CSV crudo. Nunca lo modifica."""
        df = pd.read_csv(ruta, parse_dates=["fecha"])
        log.info("Cargadas %d filas de %s", len(df), ruta)
        return df


    def limpiar(df: pd.DataFrame) -> pd.DataFrame:
        """Duplicados fuera, nulos imputados con la mediana, region normalizada."""
        antes = len(df)
        df = (
            df.drop_duplicates()
            .assign(
                ventas=lambda d: d["ventas"].fillna(d["ventas"].median()),
                region=lambda d: d["region"].str.strip().str.upper(),
            )
        )
        log.info("Limpieza: %d -> %d filas (%d duplicados)", antes, len(df), antes - len(df))
        return df


    def agregar_mensual(df: pd.DataFrame) -> pd.DataFrame:
        """Una fila por mes y region. Este es el grano del dato de salida."""
        return (
            df.assign(mes=lambda d: d["fecha"].dt.to_period("M").astype(str))
            .groupby(["mes", "region"], as_index=False)
            .agg(ventas=("ventas", "sum"), n_ventas=("ventas", "size"))
            .sort_values(["mes", "region"])
            .reset_index(drop=True)
        )


    def validar_entrada(df: pd.DataFrame) -> list[str]:
        """Contrato de ENTRADA: se comprueba antes de transformar nada.

        Validar aqui es lo que evita un traceback ilegible 40 lineas mas abajo.
        """
        errores = []
        if len(df) == 0:
            errores.append("la fuente llego vacia (0 filas)")
        faltan = {"fecha", "region", "ventas"} - set(df.columns)
        if faltan:
            errores.append(f"faltan columnas obligatorias: {sorted(faltan)}")
        return errores


    def validar(df: pd.DataFrame) -> list[str]:
        """Contrato de SALIDA: lo que SIEMPRE tiene que cumplirse en el resultado.

        Devuelve la lista de incumplimientos. Vacia = todo correcto.
        """
        errores = []
        if len(df) == 0:
            errores.append("la salida esta vacia")
        if df["ventas"].isna().any():
            errores.append("hay ventas nulas en la salida")
        if (df["ventas"] < 0).any():
            errores.append("hay ventas negativas")
        if df.duplicated(subset=["mes", "region"]).any():
            errores.append("hay filas duplicadas de mes+region (el grano esta roto)")
        return errores


    def main() -> int:
        p = argparse.ArgumentParser(description=__doc__)
        p.add_argument("--entrada", default="data/raw/ventas_ejemplo.csv")
        p.add_argument("--salida", default="data/processed/ventas_mensuales.parquet")
        args = p.parse_args()

        crudo = cargar(args.entrada)
        errores = validar_entrada(crudo)
        if errores:
            for e in errores:
                log.error("ENTRADA INVALIDA: %s", e)
            log.error("El pipeline PARA antes de transformar nada.")
            return 1

        resultado = agregar_mensual(limpiar(crudo))

        errores = validar(resultado)
        if errores:
            for e in errores:
                log.error("VALIDACION FALLIDA: %s", e)
            log.error("El pipeline PARA. No se sobrescribe la salida anterior.")
            return 1        # codigo != 0: el orquestador se entera de que fallo

        import pathlib
        pathlib.Path(args.salida).parent.mkdir(parents=True, exist_ok=True)
        resultado.to_parquet(args.salida, index=False)
        log.info("Escritas %d filas agregadas en %s", len(resultado), args.salida)
        return 0


    if __name__ == "__main__":
        sys.exit(main())
''')
print("\n  Lo que lo separa de un notebook, y que en una entrevista se nota:")
print("   - funciones pequenas de un solo proposito, con type hints")
print("   - logging con hora y nivel, no print sueltos")
print("   - argparse: las rutas son parametros, no constantes escondidas")
print("   - validar_entrada() y validar(): contratos de datos en los dos extremos")
print("   - sys.exit(main()): devuelve 0 o 1, que es como avisa a quien lo lanzo")

# ── PASO 2: EJECUTARLO ────────────────────────────────────────────
titulo(2, "Ejecutar el pipeline (9.2)")
codigo = correr([sys.executable, str(PIPELINE)], "ejecucion normal")
if codigo != 0:
    raise SystemExit("El pipeline fallo; revisa la salida de arriba.")
print(f"\n  Codigo 0 = todo bien. Salida en {SALIDA}")

# ── PASO 3: REPRODUCIBILIDAD (9.7) ────────────────────────────────
titulo(3, "Reproducible = mismo dato de entrada, mismo byte de salida (9.7)")
hash1 = sha256(SALIDA)
correr([sys.executable, str(PIPELINE)], "segunda ejecucion, sin tocar nada")
hash2 = sha256(SALIDA)
print(f"\n  hash de la 1a ejecucion: {hash1}")
print(f"  hash de la 2a ejecucion: {hash2}")
print(f"  -> {'IDENTICOS: el pipeline es reproducible' if hash1 == hash2 else 'DISTINTOS: algo no es determinista'}")
print("\n  Si te salieran distintos, el culpable suele ser: un timestamp dentro del")
print("  dato, un orden de filas no fijado, o un random sin semilla (random_state=42).")

# ── PASO 4: QUE PASA CUANDO LOS DATOS LLEGAN MAL ──────────────────
titulo(4, "El dia que la fuente llega rota (y por que validar salva el dashboard)")
malo = pathlib.Path("data/raw/_ventas_corrupto.csv")
lineas = pathlib.Path(CSV).read_text(encoding="utf-8-sig").splitlines()
malo.write_text("\n".join(lineas[:1]), encoding="utf-8")   # solo la cabecera: 0 filas
print("  Simulamos que hoy la fuente llega vacia (solo la cabecera).")
codigo = correr([sys.executable, str(PIPELINE), "--entrada", str(malo)],
                "misma orden, datos rotos")
print(f"\n  Codigo {codigo}: el pipeline se niega a escribir. El dashboard sigue")
print("  ensenando los datos de ayer, que son correctos, en vez de una tabla vacia.")
print("  Ese codigo distinto de 0 es lo que hace que GitHub Actions te mande el correo.")
print("\n  Sin validar(), este pipeline habria sobrescrito la salida con 0 filas y")
print("  nadie se habria enterado hasta que alguien mirase el dashboard.")
malo.unlink(missing_ok=True)

# Rehacemos la salida buena
subprocess.run([sys.executable, str(PIPELINE)], capture_output=True)

# ── PASO 5: PRUEBAS (9.7) ─────────────────────────────────────────
titulo(5, "Pruebas: la diferencia entre 'a mi me funciona' y 'funciona' (9.7)")
escribir(pathlib.Path("tests/test_pipeline.py"), '''
    """Pruebas del pipeline. Ejecutalas con:  uv run pytest -q"""

    import pandas as pd
    import sys
    import pathlib

    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
    from pipeline_ventas import limpiar, agregar_mensual, validar


    def datos_de_prueba():
        """Un dataset minusculo hecho a mano: sabemos el resultado de memoria."""
        return pd.DataFrame({
            "fecha": pd.to_datetime(["2026-01-05", "2026-01-05", "2026-01-20", "2026-02-03"]),
            "region": [" norte ", " norte ", "Sur", "SUR"],
            "ventas": [100.0, 100.0, None, 50.0],
        })


    def test_limpiar_quita_duplicados():
        df = limpiar(datos_de_prueba())
        assert len(df) == 3


    def test_limpiar_normaliza_region():
        df = limpiar(datos_de_prueba())
        assert set(df["region"]) == {"NORTE", "SUR"}


    def test_limpiar_no_deja_nulos():
        df = limpiar(datos_de_prueba())
        assert df["ventas"].isna().sum() == 0


    def test_agregar_devuelve_una_fila_por_mes_y_region():
        salida = agregar_mensual(limpiar(datos_de_prueba()))
        assert not salida.duplicated(subset=["mes", "region"]).any()
        assert list(salida.columns) == ["mes", "region", "ventas", "n_ventas"]


    def test_validar_detecta_ventas_negativas():
        malo = pd.DataFrame({"mes": ["2026-01"], "region": ["NORTE"], "ventas": [-5.0]})
        assert "hay ventas negativas" in validar(malo)


    def test_validar_acepta_una_salida_correcta():
        buena = agregar_mensual(limpiar(datos_de_prueba()))
        assert validar(buena) == []
''')
codigo = correr([sys.executable, "-m", "pytest", "-q", "tests/test_pipeline.py"],
                "ejecutar las pruebas")
if codigo == 5 or "No module named pytest" in str(codigo):
    print("\n  (Si dice que falta pytest:  uv add pytest  y vuelve a ejecutar.)")
print("\n  Seis pruebas sobre un dataset de 4 filas inventado a mano. Ese es el truco:")
print("  pruebas con datos pequenos cuyo resultado conoces de memoria, no con los")
print("  720 registros reales. Cuando manana cambies limpiar(), estas te avisan.")

# ── PASO 6: AUTOMATIZAR LA EJECUCION (9.3) ────────────────────────
titulo(6, "Que se ejecute solo: GitHub Actions y cron (9.3)")
escribir(pathlib.Path(".github/workflows/pipeline.yml"), '''
    name: Pipeline diario

    on:
      schedule:
        - cron: "0 6 * * *"       # todos los dias a las 06:00 UTC
      workflow_dispatch:          # y un boton para lanzarlo a mano

    jobs:
      run:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v4
          - uses: astral-sh/setup-uv@v3
          - name: Pruebas
            run: uv run pytest -q
          - name: Pipeline
            run: uv run python src/pipeline_ventas.py
          - name: Guardar el resultado
            uses: actions/upload-artifact@v4
            with:
              name: ventas-mensuales
              path: data/processed/ventas_mensuales.parquet
''')
print("\n  Lee el orden del workflow: PRIMERO las pruebas, DESPUES el pipeline.")
print("  Si las pruebas fallan, el pipeline no llega a correr. Es el mismo principio")
print("  que viste en dbt (Modulo 08): no propagues datos que no has verificado.")
print("\n  El cron '0 6 * * *' se lee:  minuto hora dia mes dia_semana")
print("    '0 6 * * *'    -> todos los dias a las 06:00")
print("    '0 8 * * 1'    -> todos los lunes a las 08:00")
print("    '*/15 * * * *' -> cada 15 minutos")
print("  Comprueba siempre el tuyo en crontab.guru antes de confiar en el.")
print("\n  Sin GitHub: Programador de tareas (Windows) o crontab -e (Mac/Linux).")

# ── PASO 7: LA APP (9.4, 9.5) ─────────────────────────────────────
titulo(7, "De pipeline a producto: el dashboard en Streamlit (9.4)")
escribir(pathlib.Path("app.py"), '''
    """Dashboard de ventas. Lanzalo con:  uv run streamlit run app.py"""

    import pandas as pd
    import plotly.express as px
    import streamlit as st

    st.set_page_config(page_title="Ventas 2026", layout="wide")
    st.title("Ventas del primer semestre 2026")


    @st.cache_data          # sin esto, relee el archivo en cada clic
    def cargar():
        return pd.read_parquet("data/processed/ventas_mensuales.parquet")


    df = cargar()

    # --- Filtros (barra lateral) -------------------------------------
    regiones = st.sidebar.multiselect(
        "Region", sorted(df["region"].unique()), default=sorted(df["region"].unique())
    )
    d = df[df["region"].isin(regiones)]

    if d.empty:
        st.warning("No hay datos con esos filtros.")
        st.stop()

    # --- KPIs ---------------------------------------------------------
    c1, c2, c3 = st.columns(3)
    c1.metric("Ventas totales", f"{d['ventas'].sum():,.0f} USD")
    c2.metric("Transacciones", f"{int(d['n_ventas'].sum()):,}")
    ultimo, previo = sorted(d["mes"].unique())[-2:]
    var = 100 * (d.loc[d["mes"] == ultimo, "ventas"].sum()
                 / d.loc[d["mes"] == previo, "ventas"].sum() - 1)
    c3.metric(f"Variacion {ultimo}", f"{var:.1f}%", delta=f"{var:.1f}%")

    # --- Grafico heroe ------------------------------------------------
    fig = px.line(
        d.groupby("mes", as_index=False)["ventas"].sum(),
        x="mes", y="ventas", markers=True,
        title="La caida de junio es transversal a todas las regiones",
    )
    fig.update_yaxes(rangemode="tozero")     # el eje empieza en 0 (Modulo 07)
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Ver los datos"):
        st.dataframe(d, use_container_width=True)
''')
print("\n  Para verla:")
print("    uv add streamlit plotly")
print("    uv run streamlit run app.py")
print("\n  Fijate en que la app NO limpia datos: lee el parquet que ya produjo el")
print("  pipeline. Esa separacion (pipeline calcula / app muestra) es la que hace")
print("  que la app cargue en un segundo aunque el dataset crezca a millones.")
print("\n  Para publicarla gratis: Streamlit Community Cloud conectado a tu repo de")
print("  GitHub. Una URL publica en tu CV vale mas que diez notebooks.")

# ── PASO 8: LA CHECKLIST DE REPRODUCIBILIDAD (9.7) ────────────────
titulo(8, "Checklist: por que otro puede ejecutar tu proyecto (9.7)")
comprobaciones = [
    ("pyproject.toml (dependencias declaradas)", pathlib.Path("pyproject.toml").exists()),
    ("uv.lock (versiones exactas fijadas)", pathlib.Path("uv.lock").exists()),
    ("README.md (que hace y como se ejecuta)", pathlib.Path("README.md").exists()),
    ("src/pipeline_ventas.py (transformacion por codigo)", PIPELINE.exists()),
    ("tests/ (pruebas)", pathlib.Path("tests").exists()),
    (".github/workflows/ (ejecucion automatica)", pathlib.Path(".github/workflows").exists()),
    ("data/processed/ (salida regenerable)", SALIDA.exists()),
    (".gitignore", pathlib.Path(".gitignore").exists()),
]
for nombre, existe in comprobaciones:
    print(f"  [{'x' if existe else ' '}] {nombre}")
print("\n  Las casillas vacias son tu tarea de hoy. La mas importante es el README:")
print("  si otra persona no puede ejecutar tu proyecto en 5 minutos con lo que hay")
print("  escrito ahi, el proyecto no cuenta para tu portafolio.")

print("\n" + "=" * 68)
print("LO QUE TE LLEVAS")
print("=" * 68)
print("  1. Un pipeline valida sus datos y devuelve un codigo de salida.")
print("  2. Fallar a tiempo es mejor que publicar un numero equivocado.")
print("  3. Las pruebas van con datos pequenos cuyo resultado conoces.")
print("  4. Pipeline calcula, app muestra. Nunca al reves.")
print("  5. Reproducible = otro lo ejecuta y obtiene tus mismos bytes.")
print("\nAhora hazlo tu:  uv run actividad_01.py")
