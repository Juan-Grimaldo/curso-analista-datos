# Módulo 03 — Ejemplo completo: análisis de ventas del 1er semestre 2026

> Este ejemplo recorre **todo el módulo de principio a fin** sobre el dataset
> [`ventas_ejemplo.csv`](../datasets/ventas_ejemplo.csv). Cópialo a tu carpeta
> `data/raw/` y ejecuta cada celda en un notebook. Los resultados mostrados son
> los reales del dataset, así puedes verificar que vas bien.
>
> **Pregunta de negocio:** *¿Qué región, producto y canal impulsan las ventas del
> semestre, y cómo evolucionan mes a mes?*

---

## Paso 0 — Preparación (3.1)

```python
import pandas as pd
import numpy as np

# Función auxiliar que usaremos más adelante (repaso de Python)
def con_iva(precio, tasa=0.18):
    return precio * (1 + tasa)

# Comprensión de listas: rápida prueba
[con_iva(p) for p in [100, 250, 99.9]]
# → [118.0, 295.0, 117.882]
```

---

## Paso 1 — Cargar (3.2)

```python
df = pd.read_csv("data/raw/ventas_ejemplo.csv", parse_dates=["fecha"])
df.shape
# → (735, 8)
```

Columnas del dataset:

| columna | tipo | significado |
|---|---|---|
| `venta_id` | int | identificador de la venta |
| `fecha` | datetime | día de la venta (ene–jun 2026) |
| `region` | str | Norte, Sur, Este, Oeste |
| `producto` | str | A, B, C, D |
| `canal` | str | Tienda, Web, Movil |
| `ventas` | float | monto vendido |
| `descuento` | float | descuento aplicado (0 a 1) |
| `trafico` | int | visitas del día |

---

## Paso 2 — Inspeccionar SIEMPRE antes de tocar nada (3.3)

```python
df.info()          # 735 filas; 'ventas' tiene nulos
df.describe()      # rangos razonables, sin negativos
df.isna().sum()
```

```
venta_id      0
fecha         0
region        0
producto      0
canal         0
ventas       19   ← ¡19 nulos!
descuento     0
trafico       0
```

```python
df.duplicated().sum()
# → 15   ← ¡15 filas duplicadas!

df["region"].value_counts()
# Norte    194
# Sur      182
# Oeste    180
# Este     179
```

**Diagnóstico:** 19 nulos en `ventas` y 15 duplicados. Hay que limpiar antes de analizar.

---

## Paso 3 — Seleccionar y filtrar (3.4)

Antes de limpiar, exploremos con filtros:

```python
# Ventas altas del Norte, solo las columnas que interesan
df.loc[
    (df["region"] == "Norte") & (df["ventas"] > 120),
    ["fecha", "producto", "ventas"],
].head()

# ¿Cuántas son?
len(df.loc[(df["region"] == "Norte") & (df["ventas"] > 120)])
# → 44
```

> Nota el uso de `.loc[filas, columnas]` en un solo paso: sin *chained indexing*,
> sin `SettingWithCopyWarning`.

---

## Paso 4 — Limpiar (3.5)

```python
# 1) Eliminar duplicados
df = df.drop_duplicates()
df.shape
# → (720, 8)    735 - 15 = 720 ✓

# 2) Rellenar nulos de 'ventas' con la mediana
mediana = df["ventas"].median()   # → 90.5
df["ventas"] = df["ventas"].fillna(mediana)

# 3) Normalizar texto
df["region"] = df["region"].str.strip().str.upper()

# 4) Crear columnas derivadas
df["mes"] = df["fecha"].dt.month
df["ventas_con_iva"] = con_iva(df["ventas"])          # ¡reutilizamos la función!
df["nivel"] = np.where(df["ventas"] > 100, "Alto", "Bajo")

# Verificación final de la limpieza
assert df["ventas"].isna().sum() == 0
assert df.duplicated().sum() == 0
df["nivel"].value_counts()
# Bajo    437
# Alto    283
```

---

## Paso 5 — Agrupar y agregar (3.6)

**¿Qué región vende más?**

```python
df.groupby("region")["ventas"].sum().sort_values(ascending=False)
```

```
NORTE    21367.5   ← líder del semestre
ESTE     17672.5
OESTE    16904.5
SUR      16379.5
```

**¿Y por canal, con varias métricas a la vez?**

```python
df.groupby("canal").agg(
    total=("ventas", "sum"),
    media=("ventas", "mean"),
    n_ventas=("ventas", "count"),
).round(1)
```

```
        total   media  n_ventas
Movil   25288.5  109.5      231
Tienda  23319.5   99.2      235
Web     23716.0   93.4      254
```

> 💡 Insight: **Movil** tiene menos transacciones pero el ticket medio más alto (109.5).

**Tabla dinámica región × producto:**

```python
pivot = df.pivot_table(index="region", columns="producto",
                       values="ventas", aggfunc="sum", fill_value=0).round(0)
```

```
producto       A       B       C       D
ESTE      5183.0  3952.0  4854.0  3684.0
NORTE     6720.0  5066.0  6136.0  3445.0
OESTE     4137.0  3594.0  5726.0  3448.0
SUR       4702.0  4197.0  4582.0  2899.0
```

> 💡 El producto **A** domina en Norte, Este y Sur; en Oeste gana **C**. El **D** es
> el más débil en todas las regiones.

---

## Paso 6 — Enriquecer con merge (3.7)

```python
catalogo = pd.DataFrame({
    "producto": ["A", "B", "C", "D"],
    "nombre":   ["Auriculares", "Batería", "Cargador", "Dock"],
    "costo":    [40, 25, 30, 55],
})

df = df.merge(catalogo, on="producto", how="left")
df["nombre"].isna().sum()
# → 0   ✓ todas las filas encontraron su producto
```

---

## Paso 7 — Series de tiempo (3.8)

```python
serie = df.set_index("fecha").sort_index()["ventas"]

serie.resample("MS").sum()
```

```
2026-01-01    12089.5
2026-02-01    12082.0
2026-03-01    11758.5
2026-04-01    12185.0
2026-05-01    13554.5   ← mejor mes
2026-06-01    10654.5   ← caída en junio
```

```python
serie.resample("D").sum().rolling(7).mean()   # media móvil semanal, suaviza el ruido
```

> 💡 Insight: mayo es el pico del semestre y junio cae ~21%. Esa caída es la
> pregunta que llevarías a negocio.

---

## Paso 8 — Reshape: de ancho a largo (3.9)

La `pivot` del paso 5 es **ancha** (un producto por columna). Para graficar o
guardar en base de datos conviene el formato **largo** (tidy):

```python
pivot_largo = (
    pivot
    .reset_index()
    .melt(id_vars="region", var_name="producto", value_name="ventas")
)
pivot_largo.head(3)
```

```
  region producto  ventas
0   ESTE        A  5183.0
1  NORTE        A  6720.0
2  OESTE        A  4137.0
```

---

## Paso 9 — Todo junto con method chaining (3.10)

El análisis completo del paso 5, escrito como lo haría un profesional — **una sola
expresión, desde el CSV crudo**:

```python
resumen = (
    pd.read_csv("data/raw/ventas_ejemplo.csv", parse_dates=["fecha"])
    .drop_duplicates()
    .assign(
        ventas=lambda d: d["ventas"].fillna(d["ventas"].median()),
        region=lambda d: d["region"].str.strip().str.upper(),
        mes=lambda d: d["fecha"].dt.to_period("M"),
    )
    .groupby("region", as_index=False)["ventas"].sum()
    .sort_values("ventas", ascending=False)
)
```

Mismo resultado que el paso 5, pero legible de arriba a abajo como una receta.

---

## Paso 10 — Lo mismo en Polars (3.11)

```python
import polars as pl

resumen_pl = (
    pl.read_csv("data/raw/ventas_ejemplo.csv")
    .unique()                                        # ~ drop_duplicates
    .with_columns(
        pl.col("ventas").fill_null(pl.col("ventas").median()),
        pl.col("region").str.strip_chars().str.to_uppercase(),
    )
    .group_by("region")
    .agg(pl.col("ventas").sum().alias("total"))
    .sort("total", descending=True)
)
```

Compara: la lógica es idéntica; cambia la sintaxis (`pl.col(...)` en vez de
`lambda`, `group_by` con guion bajo). En este dataset no notarás diferencia de
velocidad — con millones de filas, sí.

---

## Paso 11 — Guardar el resultado (Reto del módulo)

```python
# Nunca sobrescribas data/raw/ — guarda en processed/ y en Parquet
df.to_parquet("data/processed/ventas_limpio.parquet", index=False)
```

### Respuestas a la pregunta de negocio

1. **Región líder:** Norte (21 367.5), ~30% por encima de Sur, la última.
2. **Producto estrella:** A en casi todas las regiones; D es el más débil.
3. **Canal:** Movil tiene el mejor ticket medio; Web mueve más transacciones.
4. **Tendencia:** pico en mayo, caída fuerte en junio → investigar causa.

---

➡️ Ahora ponte a prueba con las [Actividades del módulo](ACTIVIDADES.md).
