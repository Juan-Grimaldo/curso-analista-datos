"""
Demo guiado del Modulo 09 - IA generativa aplicada al analisis, de principio a fin.

Este demo NO te ensena a "usar ChatGPT". Te ensena lo unico que te hace
contratable en 2026: usar un LLM dentro de un pipeline y VERIFICAR su salida.
Cada paso tiene la misma estructura: la IA propone, tu codigo comprueba.

Funciona SIN clave de API: los pasos que llamarian al modelo usan respuestas
grabadas (marcadas como [SIMULADO]) y el resto del codigo es real. Si tienes
una clave, exportala y el PASO 4 hara llamadas de verdad:
    setx ANTHROPIC_API_KEY "sk-ant-..."     (Windows, reabre la terminal)
    export ANTHROPIC_API_KEY="sk-ant-..."   (Mac/Linux)

Este script se ejecuta en tu repo de practica `curso-datos`. Copialo ahi, y desde
la raiz del repo ejecutalo con:  uv run demo_guiado.py
Cada PASO corresponde a una seccion del README.

Requisitos (en curso-datos):  uv add pandas duckdb
Opcional (solo para el PASO 4 con API real):  uv add anthropic
y copiar ventas_ejemplo.csv del material a  data/raw/
"""

import os
import re
import sys

import duckdb
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CSV = "data/raw/ventas_ejemplo.csv"
MODELO = "claude-sonnet-5"   # equilibrio calidad/coste para clasificar en volumen


def titulo(n, texto):
    print(f"\n{'=' * 68}\nPASO {n}: {texto}\n{'=' * 68}")


if not os.path.exists(CSV):
    raise SystemExit(f"Falta {CSV}. Copia ventas_ejemplo.csv del material a data/raw/")

df = (
    pd.read_csv(CSV, parse_dates=["fecha"])
    .drop_duplicates()
    .assign(
        ventas=lambda d: d["ventas"].fillna(d["ventas"].median()),
        region=lambda d: d["region"].str.strip().str.upper(),
    )
)

# Datos NO estructurados: esto es lo que pandas no sabe analizar y un LLM si.
# La columna `humano` es la etiqueta que puso una persona: es tu patron de oro.
RESENAS = pd.DataFrame([
    ("Alfa",  "Llego en dos dias y funciona perfecto. Repetire sin duda.", "POSITIVO"),
    ("Alfa",  "El producto bien, pero el embalaje venia roto.", "NEUTRO"),
    ("Beta",  "Se rompio a la semana. Escribi a soporte y nadie contesta.", "NEGATIVO"),
    ("Beta",  "Cumple lo que promete por el precio que tiene.", "NEUTRO"),
    ("Cesar", "Es caro pero se nota la calidad. Muy contento.", "POSITIVO"),
    ("Cesar", "Excelente, aunque tardo mas de lo prometido en llegar.", "POSITIVO"),
    ("Delta", "Una decepcion total, no lo recomiendo a nadie.", "NEGATIVO"),
    ("Delta", "Ni bueno ni malo, hace su funcion.", "NEUTRO"),
    ("Delta", "Pedi dos y me mandaron uno. Un desastre de gestion.", "NEGATIVO"),
    ("Alfa",  "Contactad conmigo en ana.ruiz@correo.com o al 612 345 678, "
              "mi pedido 4471 sigue sin llegar.", "NEGATIVO"),
], columns=["producto", "resena", "humano"])


# ── PASO 1: DONDE APORTA LA IA Y DONDE NO (8.1, 8.2) ──────────────
titulo(1, "Lo que pandas no puede hacer y un LLM si (8.1, 8.2)")
print("Tu dataset de ventas tiene 8 columnas numericas y categoricas: pandas y SQL")
print("lo resuelven todo. Pero el negocio tambien tiene esto:\n")
for _, r in RESENAS.head(3).iterrows():
    print(f"  [{r['producto']}] {r['resena']}")
print("\nNinguna funcion de pandas te dice si eso es una queja. Ahi entra el LLM.")
print("\n  La IA SI ayuda con: texto libre, clasificar, extraer entidades, resumir,")
print("  redactar un borrador de codigo o de informe, explicarte un error.")
print("  La IA NO decide: que es un outlier legitimo, si un p-valor importa,")
print("  ni que le recomiendas al negocio. Eso lo firmas tu.")

# ── PASO 2: PROMPTING (8.3) ───────────────────────────────────────
titulo(2, "El mismo trabajo, dos prompts: por que uno sirve y el otro no (8.3)")
prompt_malo = "analiza estas resenas"

prompt_bueno = """\
Eres un analista de datos de una empresa de retail.

TAREA: clasifica el sentimiento de cada resena.
CATEGORIAS: POSITIVO, NEUTRO, NEGATIVO. No inventes otras.
FORMATO: devuelve SOLO un CSV con dos columnas: id,sentimiento. Sin explicaciones.
REGLA: si la resena mezcla algo bueno y algo malo, decide por el tono dominante.
Si no puedes decidir, responde NEUTRO.

RESENAS:
1. Llego en dos dias y funciona perfecto. Repetire sin duda.
2. El producto bien, pero el embalaje venia roto.
3. Se rompio a la semana. Escribi a soporte y nadie contesta."""

print("PROMPT MALO:")
print(f"  {prompt_malo!r}")
print("\n  Que devuelve: un parrafo distinto cada vez, imposible de meter en un DataFrame.")
print("\nPROMPT BUENO:")
for linea in prompt_bueno.splitlines():
    print(f"  {linea}")
print("\n  Los 5 ingredientes que lo hacen util:")
print("    1. ROL       -> fija el vocabulario y el punto de vista")
print("    2. TAREA     -> un verbo, una sola cosa")
print("    3. CATEGORIAS-> cierra el espacio de respuestas (evita inventos)")
print("    4. FORMATO   -> CSV parseable; 'sin explicaciones' evita el parrafo de cortesia")
print("    5. REGLA     -> le dices que hacer con los casos dudosos, en vez de rezar")

# ── PASO 3: VERIFICACION, LA HABILIDAD CLAVE (8.5) ────────────────
titulo(3, "La IA te da un numero. Nunca lo publiques sin comprobarlo (8.5)")
respuesta_ia = {
    "texto": "Segun los datos, la region NORTE facturo 21.367,50 USD en el semestre, "
             "lo que representa el 42% del total de ventas, y el producto D es el "
             "de mayor facturacion.",
    "afirmaciones": {
        "ventas_norte": 21367.5,
        "porcentaje_norte": 42.0,
        "producto_top": "D",
    },
}
print("[SIMULADO] Respuesta del modelo:")
print(f"  {respuesta_ia['texto']}\n")

print("Ahora la parte que casi nadie hace: comprobar cada cifra con tu propio codigo.")
ventas_norte = df.loc[df["region"] == "NORTE", "ventas"].sum()
pct_norte = 100 * ventas_norte / df["ventas"].sum()
producto_top = df.groupby("producto")["ventas"].sum().idxmax()

comprobaciones = [
    ("ventas_norte", respuesta_ia["afirmaciones"]["ventas_norte"], round(ventas_norte, 2)),
    ("porcentaje_norte", respuesta_ia["afirmaciones"]["porcentaje_norte"], round(pct_norte, 1)),
    ("producto_top", respuesta_ia["afirmaciones"]["producto_top"], producto_top),
]
print(f"  {'afirmacion':<20} {'dice la IA':>12}   {'dice tu codigo':>15}   veredicto")
for nombre, dice_ia, real in comprobaciones:
    ok = (abs(dice_ia - real) < 0.15) if isinstance(real, float) else (dice_ia == real)
    print(f"  {nombre:<20} {str(dice_ia):>12}   {str(real):>15}   {'OK' if ok else '<-- FALSO'}")

print("\nDos de tres. La cifra del Norte es correcta, pero el porcentaje esta")
print("inflado y el producto lider es C, no D. Todo dicho con el mismo tono de")
print("seguridad. Eso es una alucinacion: no suena a error, suena a informe.")
print("\n  Regla: si un numero va a salir de tu pantalla, lo has recalculado tu.")

# ── PASO 4: CLASIFICAR CON LA API (8.6) ───────────────────────────
titulo(4, "Meter el LLM DENTRO del pipeline: clasificar resenas (8.6)")


def clasificar_con_api(texto, cliente):
    """Una llamada, una etiqueta. Formato cerrado = salida parseable."""
    msg = cliente.messages.create(
        model=MODELO,
        max_tokens=8,                     # una palabra: no necesita mas
        system="Eres un clasificador de sentimiento. Respondes UNA sola palabra.",
        messages=[{
            "role": "user",
            "content": "Clasifica el sentimiento de esta resena como POSITIVO, "
                       f"NEUTRO o NEGATIVO. Responde solo la palabra.\n\n{texto}",
        }],
    )
    return msg.content[0].text.strip().upper()


def clasificar_simulado(texto):
    """Sustituto offline: reglas tontas, para que el demo corra sin clave."""
    t = texto.lower()
    negativas = ("rompio", "decepcion", "desastre", "no recomiendo", "nadie contesta",
                 "sin llegar", "roto")
    positivas = ("perfecto", "contento", "excelente", "repetire", "calidad")
    if any(p in t for p in negativas):
        return "NEGATIVO"
    if any(p in t for p in positivas):
        return "POSITIVO"
    return "NEUTRO"


cliente = None
if os.environ.get("ANTHROPIC_API_KEY"):
    try:
        import anthropic
        cliente = anthropic.Anthropic()
        print(f"Clave detectada: clasificando de verdad con {MODELO}.")
    except ImportError:
        print("Tienes clave pero falta la libreria. Instalala con:  uv add anthropic")
if cliente is None:
    print("[SIMULADO] Sin clave de API: uso un clasificador de reglas para que el")
    print("demo corra igual. Todo lo demas (la validacion) es identico.")

RESENAS["prediccion"] = [
    clasificar_con_api(t, cliente) if cliente else clasificar_simulado(t)
    for t in RESENAS["resena"]
]

print("\nY AHORA LO IMPORTANTE: validar contra las etiquetas de una persona.")
RESENAS["acierta"] = RESENAS["prediccion"] == RESENAS["humano"]
print(RESENAS[["producto", "humano", "prediccion", "acierta"]].to_string(index=False))
exactitud = RESENAS["acierta"].mean()
print(f"\n  Exactitud: {RESENAS['acierta'].sum()}/{len(RESENAS)} = {exactitud:.0%}")
print("\n  Matriz de confusion (filas = humano, columnas = modelo):")
print(pd.crosstab(RESENAS["humano"], RESENAS["prediccion"]).to_string())
fallos = RESENAS[~RESENAS["acierta"]]
if len(fallos):
    print("\n  Donde falla (leelo, aqui esta la mejora del prompt):")
    for _, r in fallos.iterrows():
        print(f"    humano={r['humano']:<9} modelo={r['prediccion']:<9} {r['resena'][:60]}")
print("\n  Nunca pongas un clasificador en produccion sin este numero. 'Parece que")
print("  funciona' no es una metrica; 90% sobre 100 casos etiquetados a mano si.")

# ── PASO 5: TEXT-TO-SQL Y SU AUDITORIA (8.7) ──────────────────────
titulo(5, "Text-to-SQL: el SQL que parece bien y devuelve otra cosa (8.7)")
pregunta = "Cuanto vendio cada region en junio?"
sql_generado = """
    SELECT region, SUM(ventas) AS total
    FROM ventas
    WHERE fecha > '2026-06-01'
    GROUP BY region
    ORDER BY total DESC
"""
print(f"Pregunta en lenguaje natural: '{pregunta}'")
print("[SIMULADO] SQL que devuelve el modelo:")
print(sql_generado)

con = duckdb.connect()
con.register("ventas", df)
resultado_ia = con.execute(sql_generado).fetchdf()
correcto = (
    df[df["fecha"].dt.month == 6]
    .groupby("region")["ventas"].sum()
    .sort_values(ascending=False)
    .reset_index()
)
print("Lo que devuelve el SQL de la IA:      | Lo que es correcto:")
for (_, a), (_, b) in zip(resultado_ia.iterrows(), correcto.iterrows()):
    print(f"  {a['region']:<8} {a['total']:>9.1f}            |   {b['region']:<8} {b['ventas']:>9.1f}")
dif = correcto["ventas"].sum() - resultado_ia["total"].sum()
print(f"\n  Faltan {dif:.1f} USD. El bug: `fecha > '2026-06-01'` excluye el propio")
print("  dia 1 de junio. Deberia ser >= , o mejor, un BETWEEN explicito.")
print("\n  El SQL compilaba, corria, devolvia una tabla con pinta perfecta y estaba")
print("  mal. Por eso Text-to-SQL se audita SIEMPRE contra un calculo de referencia.")
con.close()

# ── PASO 6: PRIVACIDAD (8.8) ──────────────────────────────────────
titulo(6, "Lo que sale de tu maquina: anonimiza ANTES de enviar (8.8)")


def anonimizar(texto):
    """Redacta lo obvio antes de que salga de tu red. Minimo indispensable."""
    texto = re.sub(r"[\w\.-]+@[\w\.-]+\.\w+", "[EMAIL]", texto)
    texto = re.sub(r"\b\d{3}[\s-]?\d{3}[\s-]?\d{3}\b", "[TELEFONO]", texto)
    texto = re.sub(r"\bpedido\s+\d+\b", "pedido [ID]", texto, flags=re.IGNORECASE)
    return texto


original = RESENAS.loc[RESENAS.index[-1], "resena"]
print("Lo que hay en tu base de datos:")
print(f"  {original}")
print("\nLo que puede salir hacia un servicio externo:")
print(f"  {anonimizar(original)}")
print("\n  Tres reglas que un profesional no rompe:")
print("   1. Datos personales de clientes: nunca en un chat publico de IA.")
print("   2. Credenciales, claves, connection strings: nunca, ni 'de ejemplo'.")
print("   3. Si tu empresa lo exige, di que el analisis fue asistido por IA.")
print("\n  Y ojo: anonimizar con regex es el MINIMO, no la garantia. Un nombre")
print("  propio o un caso unico ('el cliente de Cadiz que compro 900 unidades')")
print("  siguen identificando a alguien.")

# ── PASO 7: COSTE Y VOLUMEN (8.6) ─────────────────────────────────
titulo(7, "Antes de clasificar 200 000 filas: haz la cuenta (8.6)")
n_filas = 200_000
tok_entrada, tok_salida = 120, 5          # por resena, aproximado
precio_in, precio_out = 3.0, 15.0         # USD por millon de tokens (Sonnet 5)
coste = (n_filas * tok_entrada / 1e6) * precio_in + (n_filas * tok_salida / 1e6) * precio_out
print(f"  {n_filas:,} resenas x ({tok_entrada} tokens entrada + {tok_salida} salida)")
print(f"  = {coste:,.2f} USD por pasada completa")
print("\n  Como bajarlo sin perder calidad:")
print("   - cachea: si la resena no cambio, no la vuelvas a clasificar")
print("   - procesa por lotes (Batch API): la mitad de precio")
print("   - usa el modelo mas pequeno que pase tu validacion (mide, no supongas)")
print("   - clasifica una muestra primero y decide si el resultado vale el gasto")

# ── PASO 8: EL FLUJO REALISTA (8.9) ───────────────────────────────
titulo(8, "El flujo completo, y quien firma cada paso (8.9)")
print("""
  1. TU     defines la pregunta y decides el enfoque.
  2. IA     te da un borrador de codigo, SQL o prompt.
  3. TU     lo ejecutas y lo VERIFICAS con un caso de resultado conocido.
  4. IA     te ayuda a depurar lo que falla.
  5. TU     interpretas los resultados. Esto no se delega jamas.
  6. IA     te ayuda a redactar el resumen ejecutivo.
  7. TU     lo revisas, lo corriges y lo firmas. Eres responsable.

  Fijate en el patron: la IA hace lo mecanico, tu pones el criterio.
  Un analista que solo sabe pegar la respuesta del modelo es reemplazable
  por el modelo. Uno que sabe cuando la respuesta esta mal, no.
""")

print("=" * 68)
print("LO QUE TE LLEVAS")
print("=" * 68)
print("  1. Un prompt sin formato de salida no sirve para un pipeline.")
print("  2. Toda cifra que da un LLM se recalcula antes de publicarla.")
print("  3. Un clasificador sin conjunto etiquetado a mano no esta validado.")
print("  4. El SQL generado se audita contra un calculo de referencia.")
print("  5. Anonimiza antes de enviar; asume que lo enviado ya no es tuyo.")
print("\nAhora hazlo tu:  uv run actividad_01.py")
