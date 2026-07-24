"""
Construye la base de datos de práctica del Módulo 04:  data/tienda.duckdb
Ejecútalo UNA vez con:  py crear_db.py

Crea 3 tablas relacionadas (un mini "esquema estrella"):
  - ventas        → tabla de HECHOS (cada venta), leída del CSV del curso
  - dim_producto  → dimensión: nombre y categoría de cada producto
  - dim_region    → dimensión: zona y responsable de cada región

Con esto puedes practicar JOINs de verdad, uniendo tablas por su columna común.

Requisito único:  py -m pip install duckdb
"""

import pathlib
import duckdb

CSV = "../datasets/ventas_ejemplo.csv"
DB = "data/tienda.duckdb"

pathlib.Path("data").mkdir(exist_ok=True)
pathlib.Path(DB).unlink(missing_ok=True)  # empezar de cero cada vez

con = duckdb.connect(DB)

# ── Tabla de HECHOS: una fila por venta ───────────────────────────
con.execute(f"CREATE TABLE ventas AS SELECT * FROM '{CSV}'")

# ── Dimensión PRODUCTO: describe cada código A/B/C/D ──────────────
con.execute("""
    CREATE TABLE dim_producto (
        producto  VARCHAR,   -- clave que une con ventas.producto
        nombre    VARCHAR,
        categoria VARCHAR
    )
""")
con.execute("""
    INSERT INTO dim_producto VALUES
        ('A', 'Alfa',  'Bebidas'),
        ('B', 'Beta',  'Snacks'),
        ('C', 'Cesar', 'Bebidas'),
        ('D', 'Delta', 'Snacks')
""")

# ── Dimensión REGION: describe cada región ────────────────────────
con.execute("""
    CREATE TABLE dim_region (
        region      VARCHAR,   -- clave que une con ventas.region
        zona        VARCHAR,
        responsable VARCHAR
    )
""")
con.execute("""
    INSERT INTO dim_region VALUES
        ('Norte', 'Continental', 'Ana Ruiz'),
        ('Sur',   'Continental', 'Luis Paz'),
        ('Este',  'Costa',       'Marta Sol'),
        ('Oeste', 'Costa',       'Beto Lima')
""")

# ── Comprobación ──────────────────────────────────────────────────
for t in ("ventas", "dim_producto", "dim_region"):
    n = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    print(f"  {t:<14} {n} filas")

con.close()
print(f"\nBase creada en {DB}. Ya puedes hacer JOINs sobre ella.")
