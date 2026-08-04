"""
Crea las FUENTES CRUDAS del bloque ETL/ELT del Módulo 05.

En el mundo real los datos no llegan limpios ni en un solo archivo: llegan como los
escupe cada sistema de origen (texto, formatos mezclados, duplicados, nulos raros) y
repartidos en varias fuentes. Este script fabrica esa realidad, a lo grande.

Este script se ejecuta en tu repo de práctica `curso-datos`. Cópialo ahí y, desde la
raíz del repo, ejecútalo UNA vez con:  uv run crear_fuentes.py

Genera en data/raw/:
  ventas_crudas.csv        ~200.000 filas SUCIAS (18 meses de ventas, todo texto:
                           fechas mezcladas, importes con "$", regiones desalineadas,
                           nulos "N/A", duplicados y outliers)
  ventas_crudas_lote2.csv  el lote de julio 2026 → para practicar carga INCREMENTAL
  clientes.csv             dimensión de clientes (segunda fuente, también sucia)
  productos.json           catálogo de productos en JSON (tercera fuente)

No necesita ningún dato previo: lo genera todo. Los números salen de un generador
determinista propio, así que el resultado es IDÉNTICO en cualquier máquina y versión
de Python (los correctores de las actividades dependen de eso).

Si tu equipo va justo de memoria o disco, baja N_VENTAS a 50_000: todo sigue
funcionando, solo cambian los números que reporta el corrector.
"""

import csv
import datetime as dt
import json
import pathlib

N_VENTAS = 200_000            # filas del lote histórico
N_CLIENTES = 2_000
INICIO = dt.date(2025, 1, 1)  # el histórico cubre 18 meses
FIN = dt.date(2026, 6, 30)
DESTINO = pathlib.Path("data/raw")


# ── Generador determinista (no usa `random`, para que nunca cambie) ─
class Rng:
    """Generador congruencial lineal: misma semilla → misma secuencia, siempre."""

    def __init__(self, semilla=20260701):
        self.s = semilla

    def _bits(self):
        self.s = (self.s * 6364136223846793005 + 1442695040888963407) % 2**64
        return self.s >> 33

    def entero(self, a, b):
        """Entero entre a y b, ambos incluidos."""
        return a + self._bits() % (b - a + 1)

    def elegir(self, opciones):
        return opciones[self._bits() % len(opciones)]

    def ocurre(self, porcentaje):
        """True el `porcentaje` % de las veces."""
        return self._bits() % 1000 < porcentaje * 10


rng = Rng()

# ── Catálogos de referencia ───────────────────────────────────────
REGIONES = ["Norte", "Sur", "Este", "Oeste", "Centro"]
CANALES = ["Web", "Tienda", "Movil", "Marketplace"]
SEGMENTOS = ["Retail", "Mayorista", "Corporativo"]

PRODUCTOS = [
    {"producto": "P01", "nombre": "Agua Alfa 1L",      "categoria": "Bebidas",   "precio_lista": 1.20,  "activo": True},
    {"producto": "P02", "nombre": "Jugo Beta 500ml",   "categoria": "Bebidas",   "precio_lista": 2.40,  "activo": True},
    {"producto": "P03", "nombre": "Cola Cesar 2L",     "categoria": "Bebidas",   "precio_lista": 3.10,  "activo": True},
    {"producto": "P04", "nombre": "Cafe Delta 250g",   "categoria": "Bebidas",   "precio_lista": 7.90,  "activo": True},
    {"producto": "P05", "nombre": "Galleta Eco",       "categoria": "Snacks",    "precio_lista": 1.75,  "activo": True},
    {"producto": "P06", "nombre": "Papas Fenix 150g",  "categoria": "Snacks",    "precio_lista": 2.30,  "activo": True},
    {"producto": "P07", "nombre": "Barra Gamma",       "categoria": "Snacks",    "precio_lista": 1.10,  "activo": True},
    {"producto": "P08", "nombre": "Mix Helio 300g",    "categoria": "Snacks",    "precio_lista": 4.60,  "activo": False},
    {"producto": "P09", "nombre": "Detergente Iris",   "categoria": "Limpieza",  "precio_lista": 5.40,  "activo": True},
    {"producto": "P10", "nombre": "Jabon Kappa",       "categoria": "Limpieza",  "precio_lista": 2.95,  "activo": True},
    {"producto": "P11", "nombre": "Suavizante Luna",   "categoria": "Limpieza",  "precio_lista": 6.20,  "activo": True},
    {"producto": "P12", "nombre": "Esponja Mega",      "categoria": "Limpieza",  "precio_lista": 0.95,  "activo": False},
]
PRECIOS = {p["producto"]: p["precio_lista"] for p in PRODUCTOS}
CODIGOS = [p["producto"] for p in PRODUCTOS]

# Estacionalidad: la demanda no es plana durante el año (noviembre y diciembre mandan)
FACTOR_MES = {1: 0.85, 2: 0.80, 3: 0.95, 4: 1.00, 5: 1.05, 6: 1.10,
              7: 1.15, 8: 1.05, 9: 0.95, 10: 1.05, 11: 1.30, 12: 1.45}
FACTOR_ANIO = {2025: 1.00, 2026: 1.18}          # el negocio crece un 18% en 2026
FACTOR_CANAL = {"Web": 1.10, "Tienda": 1.00, "Movil": 0.95, "Marketplace": 1.25}

COLUMNAS = ["venta_id", "fecha", "cliente_id", "region", "producto", "canal",
            "unidades", "precio_unitario", "descuento", "monto", "trafico", "ingestado_en"]


# ── Cómo se "ensucia" cada campo (igual en los dos lotes) ─────────
def texto_fecha(fecha):
    """1 de cada 5 fechas llega en formato europeo DD/MM/YYYY."""
    if rng.ocurre(20):
        return fecha.strftime("%d/%m/%Y")
    return fecha.isoformat()


def texto_region(region):
    """La región llega sin normalizar: MAYÚSCULAS, con espacios, o correcta."""
    r = rng.entero(1, 3)
    if r == 1:
        return region.upper()
    if r == 2:
        return f"  {region} "
    return region


def texto_monto(monto):
    """El importe llega como TEXTO con moneda y separador de miles; los nulos, como
    "N/A" o cadena vacía (los dos casos clásicos de un export mal hecho)."""
    if monto is None:
        return "N/A" if rng.ocurre(50) else ""
    return f"${monto:,.2f}"


def fila_venta(venta_id, fecha):
    """Genera una venta con patrones reales (estacionalidad, canal, precio promocional)."""
    producto = rng.elegir(CODIGOS)
    canal = rng.elegir(CANALES)
    region = rng.elegir(REGIONES)
    cliente = rng.entero(1, N_CLIENTES)

    # Demanda base modulada por mes, año y canal
    demanda = FACTOR_MES[fecha.month] * FACTOR_ANIO[fecha.year] * FACTOR_CANAL[canal]
    unidades = max(1, int(rng.entero(1, 12) * demanda))
    if rng.ocurre(0.3):                      # outlier: pedido mayorista enorme
        unidades *= rng.entero(20, 60)

    # Precio real = precio de lista con promoción o recargo
    precio = round(PRECIOS[producto] * rng.elegir([0.90, 0.95, 1.00, 1.00, 1.05]), 2)
    descuento = rng.elegir([0, 0, 0, 0.05, 0.10, 0.15, 0.20])
    monto = round(unidades * precio * (1 - descuento), 2)

    if rng.ocurre(2):                        # 2% de importes perdidos por el origen
        monto_txt = texto_monto(None)
    elif rng.ocurre(0.4):                    # 0.4%: importe incoherente (error de carga)
        monto_txt = texto_monto(round(monto * 10, 2))
    else:
        monto_txt = texto_monto(monto)

    canal_txt = canal.lower() if rng.ocurre(15) else canal
    cliente_txt = f"C{cliente:05d}" if rng.ocurre(85) else f"c{cliente:05d}"

    return [str(venta_id), texto_fecha(fecha), cliente_txt, texto_region(region),
            producto, canal_txt, str(unidades), f"{precio:.2f}", str(descuento),
            monto_txt, str(rng.entero(50, 900)), "2026-07-01 03:15:00"]


def escribir_csv(ruta, columnas, filas):
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        # Entrecomillar TODO, como hacen muchos exports reales (y así los espacios sobreviven)
        w = csv.writer(f, quoting=csv.QUOTE_ALL)
        w.writerow(columnas)
        w.writerows(filas)


DESTINO.mkdir(parents=True, exist_ok=True)

# ── 1. Lote histórico: 18 meses de ventas ─────────────────────────
dias = (FIN - INICIO).days + 1
ventas = [fila_venta(i, INICIO + dt.timedelta(days=rng.entero(0, dias - 1)))
          for i in range(1, N_VENTAS + 1)]
ventas.sort(key=lambda f: int(f[0]))

# Duplicados: el 0.5% de las filas llega dos veces (reintento del sistema origen)
duplicados = [ventas[rng.entero(0, N_VENTAS - 1)] for _ in range(N_VENTAS // 200)]
escribir_csv(DESTINO / "ventas_crudas.csv", COLUMNAS, ventas + duplicados)

# ── 2. Lote de julio 2026: llega después → carga incremental ──────
JULIO_INI = dt.date(2026, 7, 1)
n_lote2 = N_VENTAS // 20
lote2 = [fila_venta(N_VENTAS + i, JULIO_INI + dt.timedelta(days=rng.entero(0, 30)))
         for i in range(1, n_lote2 + 1)]
# A propósito: 5 filas de un producto que NO está en el catálogo (clave huérfana) y
# 20 filas duplicadas. Los tests de calidad del demo los detectarán.
for i in range(5):
    lote2[i * 7][4] = "P99"
lote2 += [lote2[rng.entero(0, n_lote2 - 1)] for _ in range(20)]
for fila in lote2:
    fila[11] = "2026-08-01 03:15:00"
escribir_csv(DESTINO / "ventas_crudas_lote2.csv", COLUMNAS, lote2)

# ── 3. Segunda fuente: dimensión de clientes (CSV, también sucio) ──
NOMBRES = ["Ana", "Luis", "Marta", "Beto", "Sofia", "Carlos", "Elena", "Diego", "Rosa", "Ivan"]
APELLIDOS = ["Ruiz", "Paz", "Sol", "Lima", "Vega", "Mora", "Cano", "Duarte", "Prado", "Nieto"]

clientes = []
for i in range(1, N_CLIENTES + 1):
    alta = dt.date(2023, 1, 1) + dt.timedelta(days=rng.entero(0, 1000))
    nombre = f"{rng.elegir(NOMBRES)} {rng.elegir(APELLIDOS)}"
    if rng.ocurre(20):
        nombre = f"  {nombre.upper()} "                    # nombre sin normalizar
    correo = f"cliente{i}@ejemplo.com"
    clientes.append([f"C{i:05d}", nombre, rng.elegir(SEGMENTOS), rng.elegir(REGIONES),
                     texto_fecha(alta), correo.upper() if rng.ocurre(30) else correo])

# 30 clientes llegan repetidos (el CRM exportó dos veces algunas fichas)
clientes += [clientes[rng.entero(0, N_CLIENTES - 1)] for _ in range(30)]
escribir_csv(DESTINO / "clientes.csv",
             ["cliente_id", "nombre", "segmento", "region", "fecha_alta", "email"], clientes)

# ── 4. Tercera fuente: catálogo de productos en JSON ──────────────
with open(DESTINO / "productos.json", "w", encoding="utf-8") as f:
    json.dump(PRODUCTOS, f, indent=2, ensure_ascii=False)

# ── Comprobación ──────────────────────────────────────────────────
mb = (DESTINO / "ventas_crudas.csv").stat().st_size / 1024 / 1024
print(f"  ventas_crudas.csv        {len(ventas) + len(duplicados):,} filas  ({mb:.1f} MB, con duplicados y outliers)")
print(f"  ventas_crudas_lote2.csv  {len(lote2):,} filas  (julio 2026, con claves huérfanas)")
print(f"  clientes.csv             {len(clientes):,} filas  ({N_CLIENTES} clientes + repetidos)")
print(f"  productos.json           {len(PRODUCTOS)} productos")
print("\nFuentes creadas en data/raw/. Ahora ejecuta:  uv run demo_etl_elt.py")
print("Añade data/ a tu .gitignore: estos archivos NO se suben al repo.")
