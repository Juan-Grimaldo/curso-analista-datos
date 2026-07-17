# Módulo 03 — Python para análisis: pandas y Polars

> **Objetivo:** dominar la manipulación de datos en Python. pandas es el estándar; Polars
> es la alternativa moderna para grandes volúmenes. Aprenderás ambos y cuándo usar cada uno.

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

---

## 3.2 pandas: la Series y el DataFrame

- **Series:** una columna (array 1D con índice).
- **DataFrame:** una tabla (varias Series con índice común).

```python
import pandas as pd

df = pd.DataFrame({
    "producto": ["A", "B", "C", "A"],
    "region":   ["Norte", "Sur", "Norte", "Sur"],
    "ventas":   [120, 95, 140, 80],
    "fecha":    pd.to_datetime(["2026-01-05", "2026-01-06", "2026-02-01", "2026-02-03"]),
})
```

### Cargar datos reales

```python
df = pd.read_csv("data/raw/ventas.csv")
df = pd.read_excel("data/raw/ventas.xlsx", sheet_name="2026")
df = pd.read_parquet("data/raw/ventas.parquet")   # formato columnar, rápido
df = pd.read_json("data/raw/api.json")
```

> 💡 **Parquet** es el formato preferido en el mundo moderno: comprimido, tipado y mucho
> más rápido que CSV. Úsalo para datos intermedios.

---

## 3.3 Inspeccionar: lo primero que haces SIEMPRE

```python
df.head()          # primeras 5 filas
df.tail(3)         # últimas 3
df.shape           # (filas, columnas)
df.info()          # tipos y nulos
df.describe()      # estadísticas de columnas numéricas
df.dtypes          # tipos de cada columna
df.columns         # nombres de columnas
df.isna().sum()    # nulos por columna
df.nunique()       # valores únicos por columna
df["region"].value_counts()   # frecuencia de categorías
```

---

## 3.4 Seleccionar y filtrar

```python
# Columnas
df["ventas"]                    # una columna (Series)
df[["producto", "ventas"]]      # varias (DataFrame)

# Filas por condición (booleana)
df[df["ventas"] > 100]
df[(df["ventas"] > 100) & (df["region"] == "Norte")]   # AND: &  |  OR: |
df[df["producto"].isin(["A", "B"])]
df[df["producto"].str.startswith("A")]

# .loc (por etiqueta) y .iloc (por posición) — la forma recomendada
df.loc[df["ventas"] > 100, ["producto", "ventas"]]
df.iloc[0:3, 0:2]               # primeras 3 filas, 2 columnas
```

> ⚠️ Evita el *chained indexing* (`df[...][...]`). Usa `.loc` para evitar el
> `SettingWithCopyWarning`.

---

## 3.5 Limpiar datos (el 70% del trabajo real)

### Valores nulos

```python
df.isna().sum()                       # cuántos nulos
df.dropna()                           # elimina filas con nulos
df.dropna(subset=["ventas"])          # solo si falta 'ventas'
df["ventas"].fillna(0)                # rellena con 0
df["ventas"].fillna(df["ventas"].median())   # con la mediana
df["region"] = df["region"].fillna("Desconocido")
```

### Duplicados

```python
df.duplicated().sum()
df = df.drop_duplicates()
df = df.drop_duplicates(subset=["producto", "fecha"], keep="last")
```

### Tipos y texto

```python
df["ventas"] = df["ventas"].astype(float)
df["categoria"] = df["categoria"].astype("category")   # ahorra memoria
df["producto"] = df["producto"].str.strip().str.upper()
df["fecha"] = pd.to_datetime(df["fecha"])
```

### Renombrar y crear columnas

```python
df = df.rename(columns={"ventas": "ventas_usd"})
df["ventas_con_iva"] = df["ventas_usd"] * 1.18
df["mes"] = df["fecha"].dt.month
df["dia_semana"] = df["fecha"].dt.day_name()

# Categorizar con condiciones
import numpy as np
df["nivel"] = np.where(df["ventas_usd"] > 100, "Alto", "Bajo")

# Múltiples condiciones
df["tramo"] = pd.cut(df["ventas_usd"], bins=[0, 90, 120, 999],
                     labels=["Bajo", "Medio", "Alto"])
```

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

# Agrupar por varias dimensiones
df.groupby(["region", "producto"])["ventas"].sum().reset_index()

# Tabla dinámica (pivot)
df.pivot_table(index="region", columns="producto",
               values="ventas", aggfunc="sum", fill_value=0)
```

---

## 3.7 Combinar tablas: merge y concat

```python
# JOIN entre dos tablas (como en SQL)
ventas.merge(productos, on="producto_id", how="left")
# how: "inner", "left", "right", "outer"

# Apilar tablas (mismas columnas)
pd.concat([df_enero, df_febrero], ignore_index=True)
```

### Los tipos de JOIN, visualmente

```
INNER  → solo coincidencias en ambas
LEFT   → todas las de la izquierda + coincidencias
RIGHT  → todas las de la derecha + coincidencias
OUTER  → todas de ambas
```

---

## 3.8 Datos de tiempo

```python
df = df.set_index("fecha").sort_index()

# Remuestreo: ventas mensuales
df["ventas"].resample("MS").sum()      # MS = inicio de mes

# Media móvil de 7 días
df["ventas"].rolling(7).mean()

# Cambio respecto al periodo anterior
df["ventas"].pct_change()
```

---

## 3.9 Reshape: wide ↔ long (formato tidy)

```python
# Ancho → largo (melt)
df_long = df.melt(id_vars="producto", value_vars=["ene", "feb", "mar"],
                  var_name="mes", value_name="ventas")

# Largo → ancho (pivot)
df_wide = df_long.pivot(index="producto", columns="mes", values="ventas")
```

---

## 3.10 El método `.pipe()` y encadenar (código limpio)

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

---

## 3.11 Polars: el pandas moderno para escala

**[Polars](https://pola.rs/)** es una librería escrita en Rust, **mucho más rápida** que
pandas y con mejor manejo de memoria. Ideal cuando pandas se queda corto (millones de filas).

```python
import polars as pl

df = pl.read_csv("data/raw/ventas.csv")

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

### pandas vs Polars — ¿cuándo cada uno?

| Situación | Elige |
|-----------|-------|
| Aprender, datasets pequeños/medianos, máximo ecosistema | **pandas** |
| Millones de filas, rendimiento, pipelines | **Polars** |
| Datos más grandes que la RAM | **Polars (lazy)** o DuckDB |

### Modo *lazy* (evaluación diferida) — el superpoder de Polars

```python
resultado = (
    pl.scan_csv("data/raw/ventas.csv")   # no lee aún
    .filter(pl.col("ventas") > 50)
    .group_by("region")
    .agg(pl.col("ventas").sum())
    .collect()                            # ahora sí ejecuta, optimizado
)
```

Polars planifica toda la consulta y solo lee lo necesario. Muy eficiente.

> 💡 Puedes convertir entre ambos: `df.to_pandas()` / `pl.from_pandas(df)`. No tienes que
> elegir uno para siempre.

---

## 3.12 Errores comunes (y cómo evitarlos)

- **`SettingWithCopyWarning`** → usa `.loc[fila, col] = valor`, no encadenes.
- **Comparar con `==` para nulos** → usa `.isna()`, no `== None`.
- **Fechas como texto** → convierte siempre con `pd.to_datetime()`.
- **Modificar `data/raw/`** → nunca; genera `data/processed/`.
- **Bucles `for` sobre filas** → casi siempre hay una operación vectorizada más rápida.

---

## Ejercicios

Usa el dataset [`datasets/ventas_ejemplo.csv`](../datasets/ventas_ejemplo.csv) (o descarga uno público de tu interés).

1. Carga el CSV, muestra `info()`, `describe()` y los nulos por columna.
2. Limpia: elimina duplicados, rellena nulos numéricos con la mediana y normaliza el texto.
3. Crea una columna `mes` a partir de la fecha y una columna `nivel` (Alto/Bajo por ventas).
4. Calcula ventas totales por región y por mes (usando `groupby` y `pivot_table`).
5. Reescribe el ejercicio 4 con **method chaining** (`.pipe`/encadenado).
6. Repite el ejercicio 4 en **Polars** y compara el código.

## Reto del módulo

Toma un dataset real de [Kaggle](https://www.kaggle.com/datasets) o
[datos.gob](https://datos.gob.es/) sobre un tema que te interese. Haz una **limpieza
completa** documentada en un notebook: carga → inspección → limpieza → 3 preguntas
respondidas con `groupby`. Guarda el resultado limpio en `data/processed/` como Parquet.

➡️ Siguiente: [Módulo 04 — SQL moderno](../04-sql-moderno/README.md)
