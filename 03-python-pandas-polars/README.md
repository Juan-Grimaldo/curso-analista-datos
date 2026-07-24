# Módulo 03 — Python para análisis: pandas y Polars

> **Objetivo:** dominar la manipulación de datos en Python. pandas es el estándar; Polars
> es la alternativa moderna para grandes volúmenes. Aprenderás ambos y cuándo usar cada uno.
>
> 🧭 **Formato:** cada bloque de teoría va seguido de un **▶️ Practica ahora** con el dataset
> [`ventas_ejemplo.csv`](../datasets/ventas_ejemplo.csv). Ejecuta cada práctica antes de seguir.
> Al final, un **Reto**.
>
> 📂 **Dónde practicas:** este README es solo la **teoría**. Todo lo que escribas va en tu
> **repo de práctica** `curso-datos`. Crea ahí tu notebook
> (`notebooks/03-python-pandas-polars/practica.ipynb`) y copia el
> [`ventas_ejemplo.csv`](../datasets/ventas_ejemplo.csv) a tu `data/raw/` (como viste en el Módulo 02).

---

## 3.1 Repaso rápido de Python para datos

Solo necesitas cuatro cosas para empezar:

```python
# Variables y tipos
nombre = "ventas"          # str
total = 1250.5             # float
activo = True             # bool
meses = ["ene", "feb"]    # list
config = {"pais": "PE"}   # dict

# Funciones
def iva(precio, tasa=0.18):
    return precio * (1 + tasa)

# Comprensión de listas (muy usada)
cuadrados = [x**2 for x in range(5)]   # [0, 1, 4, 9, 16]
```

El resto lo aprenderás con la práctica de pandas.

> ### ▶️ Practica ahora
> En una celda, crea la función `iva(precio, tasa=0.18)` y calcula el precio con IVA de
> `[100, 250, 99.9]` usando una comprensión de listas. Debe devolver 3 valores.

---

## 3.2 pandas: la Series y el DataFrame

- **Series:** una columna (array 1D con índice).
- **DataFrame:** una tabla (varias Series con índice común).

### Cargar datos reales

```python
import pandas as pd

df = pd.read_csv("data/raw/ventas_ejemplo.csv", parse_dates=["fecha"])
# otras fuentes:
# pd.read_excel("archivo.xlsx", sheet_name="2026")
# pd.read_parquet("archivo.parquet")   # columnar, rápido
# pd.read_json("api.json")
```

> 💡 **Parquet** es el formato preferido en el mundo moderno: comprimido, tipado y mucho
> más rápido que CSV. Úsalo para datos intermedios.

> ### ▶️ Practica ahora
> Carga `ventas_ejemplo.csv` con `parse_dates=["fecha"]`. Comprueba que `df` tiene 735 filas
> y que la columna `fecha` es de tipo `datetime` (revisa con `df.dtypes`).

---

## 3.3 Inspeccionar: lo primero que haces SIEMPRE

```python
df.head()          # primeras 5 filas
df.tail(3)         # últimas 3
df.shape           # (filas, columnas)
df.info()          # tipos y nulos
df.describe()      # estadísticas de columnas numéricas
df.dtypes          # tipos de cada columna
df.isna().sum()    # nulos por columna
df.nunique()       # valores únicos por columna
df["region"].value_counts()   # frecuencia de categorías
```

> ### ▶️ Practica ahora
> Ejecuta `info()`, `describe()`, `isna().sum()` y `df["region"].value_counts()`.
> Responde: ¿cuántos nulos tiene `ventas`? ¿cuántas regiones distintas hay?

---

## 3.4 Seleccionar y filtrar

```python
# Columnas
df["ventas"]                    # una columna (Series)
df[["producto", "ventas"]]      # varias (DataFrame)

# Filas por condición (booleana)
df[df["ventas"] > 100]
df[(df["ventas"] > 100) & (df["region"] == "Norte")]   # AND: &   OR: |
df[df["producto"].isin(["A", "B"])]

# .loc (por etiqueta) y .iloc (por posición) — la forma recomendada
df.loc[df["ventas"] > 100, ["producto", "ventas"]]
df.iloc[0:3, 0:2]               # primeras 3 filas, 2 columnas
```

> ⚠️ Evita el *chained indexing* (`df[...][...]`). Usa `.loc` para evitar el
> `SettingWithCopyWarning`.

> ### ▶️ Practica ahora
> Filtra las ventas de la región `Norte` con monto mayor a 120, mostrando solo las columnas
> `fecha`, `producto` y `ventas`. ¿Cuántas filas salen?

---

## 3.5 Limpiar datos (el 70% del trabajo real)

### Valores nulos

```python
df.isna().sum()                       # cuántos nulos
df.dropna(subset=["ventas"])          # elimina filas sin 'ventas'
df["ventas"] = df["ventas"].fillna(df["ventas"].median())   # rellena con la mediana
```

### Duplicados

```python
df.duplicated().sum()
df = df.drop_duplicates()
```

### Tipos y texto

```python
df["region"] = df["region"].str.strip().str.upper()
df["fecha"] = pd.to_datetime(df["fecha"])
df["categoria"] = df["region"].astype("category")   # ahorra memoria
```

### Crear columnas

```python
import numpy as np
df["ventas_con_iva"] = df["ventas"] * 1.18
df["mes"] = df["fecha"].dt.month
df["nivel"] = np.where(df["ventas"] > 100, "Alto", "Bajo")
df["tramo"] = pd.cut(df["ventas"], bins=[0, 90, 120, 9999],
                     labels=["Bajo", "Medio", "Alto"])
```

> ### ▶️ Practica ahora
> Limpia el dataset paso a paso: (1) cuenta duplicados y elimínalos, (2) rellena los nulos
> de `ventas` con la mediana, (3) normaliza `region` a mayúsculas, (4) crea la columna `mes`.
> Al terminar, `df.isna().sum()` debe dar 0 en `ventas` y `df.duplicated().sum()` debe dar 0.

---

## 3.6 Agrupar y agregar (el corazón del análisis)

```python
# Total de ventas por región
df.groupby("region")["ventas"].sum()

# Varias métricas a la vez
df.groupby("region").agg(
    ventas_total=("ventas", "sum"),
    ventas_media=("ventas", "mean"),
    n_ventas=("ventas", "count"),
)

# Tabla dinámica (pivot)
df.pivot_table(index="region", columns="producto",
               values="ventas", aggfunc="sum", fill_value=0)
```

> ### ▶️ Practica ahora
> 1. Calcula las ventas **totales por región**, ordenadas de mayor a menor.
> 2. Crea una `pivot_table` de ventas por `region` (filas) y `producto` (columnas).
> 3. Responde: ¿qué región vende más? ¿qué producto domina en cada región?

---

## 3.7 Combinar tablas: merge y concat

```python
# JOIN entre dos tablas (como en SQL)
ventas.merge(productos, on="producto_id", how="left")
# how: "inner", "left", "right", "outer"

# Apilar tablas (mismas columnas)
pd.concat([df_enero, df_febrero], ignore_index=True)
```

```
INNER  → solo coincidencias en ambas       LEFT → todas las de la izquierda + coincidencias
RIGHT  → todas las de la derecha + coinc.   OUTER → todas de ambas
```

> ### ▶️ Practica ahora
> Crea una pequeña tabla de referencia con el nombre completo de cada producto
> (`pd.DataFrame({"producto": ["A","B","C","D"], "nombre": [...]})`) y haz un `merge`
> `how="left"` con tu `df`. Verifica que la nueva columna `nombre` se llenó en todas las filas.

---

## 3.8 Datos de tiempo

```python
serie = df.set_index("fecha").sort_index()["ventas"]
serie.resample("MS").sum()      # ventas mensuales (MS = inicio de mes)
serie.rolling(7).mean()         # media móvil de 7 días
serie.pct_change()              # cambio respecto al periodo anterior
```

> ### ▶️ Practica ahora
> Calcula las ventas **totales por mes** con `resample("MS")`. ¿En qué mes se vendió más?

---

## 3.9 Reshape: wide ↔ long (formato tidy)

```python
# Ancho → largo (melt)
df_long = df.melt(id_vars="producto", value_vars=["ene", "feb", "mar"],
                  var_name="mes", value_name="ventas")

# Largo → ancho (pivot)
df_wide = df_long.pivot(index="producto", columns="mes", values="ventas")
```

> ### ▶️ Practica ahora
> Toma tu `pivot_table` de la sección 3.6 (ancha) y vuélvela a formato **largo** con
> `.melt()` o `.stack()`. Confirma que recuperas una tabla `region | producto | ventas`.

---

## 3.10 El método chaining (código limpio, nivel pro)

En vez de reasignar `df` diez veces, encadena transformaciones:

```python
resultado = (
    df
    .dropna(subset=["ventas"])
    .assign(mes=lambda d: d["fecha"].dt.to_period("M"))
    .query("ventas > 50")
    .groupby("mes", as_index=False)["ventas"].sum()
    .sort_values("ventas", ascending=False)
)
```

Este estilo (*method chaining*) es más legible y es la forma profesional de escribir pandas.

> ### ▶️ Practica ahora
> Reescribe tu análisis de "ventas totales por región" (sección 3.6) como **una sola
> cadena** encadenada con `.groupby().sort_values()`. Compara: ¿se lee mejor?

---

## 3.11 Polars: el pandas moderno para escala

**[Polars](https://pola.rs/)** está escrito en Rust, es **mucho más rápido** que pandas y
maneja mejor la memoria. Ideal cuando pandas se queda corto (millones de filas).

```python
import polars as pl

df = pl.read_csv("data/raw/ventas_ejemplo.csv")

resultado = (
    df
    .filter(pl.col("ventas") > 50)
    .group_by("region")
    .agg(
        pl.col("ventas").sum().alias("total"),
        pl.col("ventas").mean().alias("media"),
    )
    .sort("total", descending=True)
)
```

### ¿cuándo cada uno?

| Situación | Elige |
|-----------|-------|
| Aprender, datasets pequeños/medianos, máximo ecosistema | **pandas** |
| Millones de filas, rendimiento, pipelines | **Polars** |
| Datos más grandes que la RAM | **Polars (lazy)** o DuckDB |

**Modo lazy** (evaluación diferida): `pl.scan_csv(...)` planifica y solo lee lo necesario;
ejecutas con `.collect()`. Muy eficiente.

> 💡 Convierte entre ambos: `df.to_pandas()` / `pl.from_pandas(df)`. No eliges uno para siempre.

> ### ▶️ Practica ahora
> Repite el "total de ventas por región" **en Polars** y compáralo con tu versión de pandas.
> ¿En qué se parece la sintaxis? ¿En qué cambia?

---

## 3.12 Errores comunes (y cómo evitarlos)

- **`SettingWithCopyWarning`** → usa `.loc[fila, col] = valor`, no encadenes.
- **Comparar con `==` para nulos** → usa `.isna()`, no `== None`.
- **Fechas como texto** → convierte siempre con `pd.to_datetime()`.
- **Modificar `data/raw/`** → nunca; genera `data/processed/`.
- **Bucles `for` sobre filas** → casi siempre hay una operación vectorizada más rápida.

---

## Reto del módulo (cierre)

Con lo que practicaste, haz una **limpieza completa documentada** en un notebook sobre
`ventas_ejemplo.csv` (o un dataset real que te guste): carga → inspección → limpieza →
responde 3 preguntas con `groupby`. Guarda el resultado limpio en `data/processed/` como
**Parquet** (`df.to_parquet(...)`). Haz commit y push a tu repo `curso-datos`.

➡️ Siguiente: [Módulo 04 — SQL: fundamentos](../04-sql-fundamentos/README.md)
