"""
ACTIVIDAD 01 - Modulo 09 (IA generativa aplicada)
=================================================
Mismo tipo de trabajo que demo_guiado.py, pero ahora lo escribes TU.

Ojo a lo que se corrige aqui: NO se evalua si sabes hablar con un modelo, sino
si sabes CONTROLARLO. Escribiras un prompt con estructura, un verificador de
cifras, un anonimizador, un auditor de SQL y una medida de calidad. Todo esto
funciona sin clave de API: es tu codigo el que trabaja.

Este archivo se trabaja en tu repo de practica `curso-datos`. Copialo ahi y
ejecutalo desde la raiz del repo con:  uv run actividad_01.py

Como funciona:
  - Completa cada funcion donde dice TODO.
  - NO cambies los nombres de las funciones ni lo que devuelven.
  - El corrector del final las ejecuta y te dice que esta bien y que no.

Requisitos (en curso-datos):  uv add pandas duckdb
y copiar ventas_ejemplo.csv del material a  data/raw/

Pistas: README secciones 8.3 a 8.8. No mires demo_guiado.py hasta haberlo
intentado al menos dos veces.
"""

import re
import sys

import duckdb
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CSV = "data/raw/ventas_ejemplo.csv"


def cargar():
    """Dataset limpio del Modulo 03: 720 filas. No modifiques esta funcion."""
    return (
        pd.read_csv(CSV, parse_dates=["fecha"])
        .drop_duplicates()
        .assign(
            ventas=lambda d: d["ventas"].fillna(d["ventas"].median()),
            region=lambda d: d["region"].str.strip().str.upper(),
        )
    )


# ── EJERCICIO 1: un prompt que sirva en un pipeline ───────────────
# Devuelve (como STRING) el prompt que usarias para que un LLM clasifique
# comentarios de clientes en tres categorias de motivo:
#   ENVIO, PRODUCTO, ATENCION
# Tu prompt debe contener, escrito de forma explicita:
#   - un ROL para el modelo               (la palabra "eres" o "actua")
#   - las tres categorias, en mayusculas
#   - un FORMATO de salida maquina-legible (menciona JSON o CSV)
#   - una instruccion de brevedad          ("solo", "unicamente" o "sin explicaciones")
#   - una REGLA para los casos dudosos     (la palabra "si no" / "en caso de duda")
# (El corrector busca esos elementos: no es un test de estilo, es la checklist
#  minima de un prompt que otro programa va a parsear.)
def ej1_prompt_clasificador():
    # TODO: return """Eres ... CATEGORIAS: ... FORMATO: ... """
    ...


# ── EJERCICIO 2: verificar lo que afirma la IA ────────────────────
# Un LLM te ha entregado este parrafo sobre el dataset:
#   "El canal Movil facturo 25288.5 USD, el ticket medio global es de 100.45 USD
#    y el mes con mas ventas fue mayo."
# Escribe la funcion que COMPRUEBA cada afirmacion con pandas y devuelve un
# diccionario {afirmacion: True/False}, con estas tres claves exactas:
#   {"ventas_movil": ..., "ticket_medio": ..., "mejor_mes": ...}
# Compara con tolerancia 0.1 en los numeros. El mes lo comparas como numero (5).
def ej2_verificar(df):
    afirmaciones = {"ventas_movil": 25288.5, "ticket_medio": 100.45, "mejor_mes": 5}
    # TODO: calcula cada valor real con pandas y compara
    ...


# ── EJERCICIO 3: anonimizar antes de enviar ───────────────────────
# Devuelve el texto con los datos personales sustituidos:
#   - cualquier email            -> [EMAIL]
#   - un DNI espanol (8 digitos + letra, p.ej. 12345678Z) -> [DNI]
#   - un IBAN que empiece por ES seguido de 22 digitos    -> [IBAN]
# El resto del texto no se toca. Usa re.sub.
def ej3_anonimizar(texto):
    # TODO
    ...


# ── EJERCICIO 4: auditar el SQL que genero la IA ──────────────────
# Un asistente Text-to-SQL respondio a "ventas medias por canal" con el SQL de
# abajo (ya escrito, no lo cambies). Tiene un fallo silencioso.
# Devuelve una TUPLA (valor_sql, valor_correcto, coinciden) para el canal 'Movil':
#   - valor_sql:      el promedio de Movil que devuelve ESE SQL (redondea a 2)
#   - valor_correcto: el promedio de Movil calculado con pandas sobre TODO el df
#   - coinciden:      True/False comparando con tolerancia 0.01
# Pista: registra el DataFrame en duckdb con  con.register("ventas", df)
SQL_SOSPECHOSO = """
    SELECT canal, ROUND(AVG(ventas), 2) AS ticket_medio
    FROM ventas
    WHERE ventas > 0
    GROUP BY canal
"""


def ej4_auditar_sql(df):
    # TODO: ejecuta SQL_SOSPECHOSO en duckdb, calcula lo correcto con pandas, compara
    ...


# ── EJERCICIO 5: medir un clasificador ────────────────────────────
# Recibes las etiquetas de una persona y las que predijo un modelo.
# Devuelve un diccionario con:
#   {"exactitud": <proporcion de aciertos, redondeada a 2>,
#    "n_fallos": <int>,
#    "peor_clase": <la clase HUMANA con mas fallos, como string>}
# Sin esta medida no puedes decir que un clasificador "funciona".
def ej5_medir(humano, prediccion):
    # TODO: usa pandas (Series) o listas; devuelve las 3 claves
    ...


# ── EJERCICIO 6: la cuenta antes de gastar ────────────────────────
# Calcula el coste en USD de clasificar `n_filas` textos, sabiendo que cada uno
# consume `tok_in` tokens de entrada y `tok_out` de salida, y que el modelo
# cuesta `precio_in` y `precio_out` USD por MILLON de tokens.
# Devuelve el coste redondeado a 2 decimales.
def ej6_coste(n_filas, tok_in, tok_out, precio_in, precio_out):
    # TODO
    ...


# ══════════════════════════════════════════════════════════════════
#  CORRECTOR - no toques nada de aqui abajo
# ══════════════════════════════════════════════════════════════════
def _seguro(fn, *args):
    try:
        return fn(*args)
    except Exception as e:
        return e


def corregir():
    df = cargar()
    humano = pd.Series(["POSITIVO", "NEUTRO", "NEGATIVO", "NEUTRO", "NEGATIVO",
                        "POSITIVO", "NEGATIVO", "NEUTRO"])
    prediccion = pd.Series(["POSITIVO", "NEGATIVO", "NEGATIVO", "NEGATIVO", "NEGATIVO",
                            "POSITIVO", "NEUTRO", "NEUTRO"])
    texto = ("Soy Ana (ana.ruiz@correo.com), DNI 12345678Z, "
             "devolvedme el importe a ES9121000418450200051332 por favor.")

    r1 = _seguro(ej1_prompt_clasificador)
    r2 = _seguro(ej2_verificar, df)
    r3 = _seguro(ej3_anonimizar, texto)
    r4 = _seguro(ej4_auditar_sql, df)
    r5 = _seguro(ej5_medir, humano, prediccion)
    r6 = _seguro(ej6_coste, 200_000, 120, 5, 3.0, 15.0)

    def c1():
        p = r1.lower()
        return (isinstance(r1, str) and len(r1) > 120
                and ("eres" in p or "actua" in p)
                and all(cat in r1 for cat in ("ENVIO", "PRODUCTO", "ATENCION"))
                and ("json" in p or "csv" in p)
                and any(w in p for w in ("solo", "unicamente", "sin explicaciones", "sólo"))
                and any(w in p for w in ("si no", "en caso de duda", "duda")))

    def c2():
        claves = ("ventas_movil", "ticket_medio", "mejor_mes")
        return (isinstance(r2, dict) and all(k in r2 for k in claves)
                and all(bool(r2[k]) for k in claves))

    def c3():
        return (isinstance(r3, str) and "[EMAIL]" in r3 and "[DNI]" in r3
                and "[IBAN]" in r3 and "ana.ruiz" not in r3
                and "12345678Z" not in r3 and "ES9121000418450200051332" not in r3
                and "Soy Ana" in r3)

    def c4():
        return (isinstance(r4, (tuple, list)) and len(r4) == 3
                and abs(float(r4[0]) - 109.95) < 0.02
                and abs(float(r4[1]) - 109.47) < 0.02
                and bool(r4[2]) is False)

    def c5():
        return (isinstance(r5, dict) and abs(float(r5.get("exactitud", -1)) - 0.62) < 0.02
                and int(r5.get("n_fallos", -1)) == 3
                and str(r5.get("peor_clase", "")).upper() == "NEUTRO")

    def c6():
        return not isinstance(r6, Exception) and abs(float(r6) - 87.0) < 0.01

    checks = [
        ("1. El prompt trae rol, categorias, formato, brevedad y regla de duda", c1),
        ("2. Las tres afirmaciones de la IA se verifican como ciertas", c2),
        ("3. Email, DNI e IBAN redactados; el resto del texto intacto", c3),
        ("4. Auditoria del SQL: 109.95 (SQL) vs 109.47 (real) -> no coinciden", c4),
        ("5. Exactitud 0.62, 3 fallos, peor clase NEUTRO", c5),
        ("6. Coste de 200 000 clasificaciones = 87.00 USD", c6),
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

    for i, r in enumerate([r1, r2, r3, r4, r5, r6], start=1):
        if isinstance(r, Exception):
            print(f"  [ej{i}] lanzo una excepcion: {type(r).__name__}: {r}")

    if aciertos == len(checks):
        print("\n  Perfecto. Fijate en lo que acabas de demostrar: sabes comprobar")
        print("  a la IA. Eso es lo que te separa de quien solo copia respuestas.")
        print("\n  Cierre (escribelo en tu repo, en POLITICA_IA.md): tus 5 reglas")
        print("  personales de uso de IA. Que SI haras siempre y que NUNCA haras.")
        print("\n  Listo para el Modulo 10.")
    else:
        print("\n  Revisa los FALLA. En el ejercicio 4, el fallo del SQL esta en el")
        print("  WHERE: piensa que filas del dataset se estan quedando fuera.")


if __name__ == "__main__":
    corregir()
