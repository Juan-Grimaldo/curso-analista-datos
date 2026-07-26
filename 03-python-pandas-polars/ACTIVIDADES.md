# Módulo 03 — Actividades: pon a prueba lo aprendido

> **Reglas del juego:**
> 1. Trabaja en un notebook nuevo (`notebooks/actividades_m03.ipynb`).
> 2. Dataset: [`ventas_ejemplo.csv`](../datasets/ventas_ejemplo.csv) en tu `data/raw/`.
> 3. Intenta cada actividad **sin mirar la solución**. Cada una trae una
>    **verificación** (el resultado exacto) para que compruebes tú si lo lograste.
> 4. Las soluciones están plegadas en `▸ Ver solución` — úsalas solo después de intentarlo.
>
> ⏱️ Tiempo estimado: 2–3 horas en total. Puedes hacerlas en varias sesiones.

---

## 🟢 Nivel 1 — Cargar, inspeccionar, filtrar (secciones 3.2–3.4)

### Actividad 1 — Radiografía del dataset

Carga el CSV con las fechas parseadas y responde **sin limpiar nada**:

1. ¿Cuántas filas y columnas tiene?
2. ¿Qué columna tiene nulos y cuántos?
3. ¿Cuántas filas duplicadas hay?
4. ¿Qué rango de fechas cubre el dataset?

**Verificación:** (735, 8) · 19 nulos en `ventas` · 15 duplicados · del 2026-01-01 al 2026-06-29.

<details><summary>▸ Ver solución</summary>

```python
import pandas as pd

df = pd.read_csv("data/raw/ventas_ejemplo.csv", parse_dates=["fecha"])
df.shape                    # (735, 8)
df.isna().sum()             # ventas → 19
df.duplicated().sum()       # 15
df["fecha"].min(), df["fecha"].max()
```
</details>

---

### Actividad 2 — Filtros combinados

¿Cuántas ventas del canal **Web** tuvieron **descuento mayor a 0**?
Muestra solo las columnas `fecha`, `producto`, `ventas` y `descuento`.

**Verificación:** 127 filas.

<details><summary>▸ Ver solución</summary>

```python
web_desc = df.loc[
    (df["canal"] == "Web") & (df["descuento"] > 0),
    ["fecha", "producto", "ventas", "descuento"],
]
len(web_desc)   # 127
```
</details>

---

### Actividad 3 — La trampa del más frecuente

1. ¿Qué producto aparece en **más filas** (más transacciones)?
2. ¿Es también el que **más vende en monto**? Calcula el total de `ventas` por producto y compara.

**Verificación:** el producto **D** es el más frecuente (199 filas)… pero es el que
**menos** vende en monto. Frecuencia ≠ facturación: primera lección de analista.

<details><summary>▸ Ver solución</summary>

```python
df["producto"].value_counts()            # D: 199 ← más transacciones
df.groupby("producto")["ventas"].sum().sort_values(ascending=False)
# A y C lideran en monto; D es el último
```
</details>

---

## 🟡 Nivel 2 — Limpiar y crear columnas (sección 3.5)

### Actividad 4 — Pipeline de limpieza con verificación automática

Limpia el dataset y demuestra con `assert` que quedó bien:

1. Elimina los duplicados.
2. Rellena los nulos de `ventas` con la **mediana**.
3. Normaliza `region` (sin espacios, en mayúsculas).
4. Convierte `canal` a tipo `category`.

**Verificación:** el bloque de `assert` debe ejecutarse sin errores y `df.shape`
debe ser `(720, 8)`.

<details><summary>▸ Ver solución</summary>

```python
df = df.drop_duplicates()
df["ventas"] = df["ventas"].fillna(df["ventas"].median())   # mediana = 90.5
df["region"] = df["region"].str.strip().str.upper()
df["canal"] = df["canal"].astype("category")

assert df.shape == (720, 8)
assert df["ventas"].isna().sum() == 0
assert df.duplicated().sum() == 0
assert df["canal"].dtype == "category"
print("Limpieza OK ✓")
```
</details>

> ⚠️ Las actividades siguientes parten de este dataset **ya limpio**.

---

### Actividad 5 — Ingreso neto

El descuento reduce el ingreso real. Crea la columna
`ingreso_neto = ventas × (1 − descuento)` y calcula el **total del semestre**.

**Verificación:** 67 163.9.

<details><summary>▸ Ver solución</summary>

```python
df["ingreso_neto"] = df["ventas"] * (1 - df["descuento"])
round(df["ingreso_neto"].sum(), 1)   # 67163.9
```
</details>

---

### Actividad 6 — Clasificar con condiciones

Crea la columna `tramo` con `pd.cut` usando los cortes `[0, 90, 120, 9999]` y las
etiquetas `["Bajo", "Medio", "Alto"]`. ¿Cuántas ventas hay en cada tramo?

<details><summary>▸ Ver solución</summary>

```python
df["tramo"] = pd.cut(df["ventas"], bins=[0, 90, 120, 9999],
                     labels=["Bajo", "Medio", "Alto"])
df["tramo"].value_counts()
```
</details>

---

## 🟠 Nivel 3 — Agrupar, combinar, tiempo (secciones 3.6–3.9)

### Actividad 7 — Ticket medio por producto

Calcula el **ticket medio** (`mean` de `ventas`) por producto, ordenado de mayor
a menor. ¿Qué producto tiene el ticket más alto?

**Verificación:** C (142.0) > A (109.2) > B (90.9) > D (69.1).

<details><summary>▸ Ver solución</summary>

```python
df.groupby("producto")["ventas"].mean().round(1).sort_values(ascending=False)
```
</details>

---

### Actividad 8 — Pivot región × canal

Crea una `pivot_table` con la **suma de ventas** por `region` (filas) y `canal`
(columnas). Responde: ¿en qué región gana el canal **Web**?

**Verificación:** solo en **OESTE** (6 637) el canal Web supera a Tienda y Movil.

<details><summary>▸ Ver solución</summary>

```python
pivot = df.pivot_table(index="region", columns="canal",
                       values="ventas", aggfunc="sum", fill_value=0).round(0)
pivot.idxmax(axis=1)   # OESTE → Web; el resto → Movil o Tienda
```
</details>

---

### Actividad 9 — Merge con costos y margen

1. Crea este catálogo y únelo a `df` con un `merge` `how="left"`:

```python
catalogo = pd.DataFrame({
    "producto": ["A", "B", "C", "D"],
    "costo":    [40, 25, 30, 55],
})
```

2. Crea `margen = ventas − costo` y calcula el **margen total por producto**.
3. ¿Qué producto deja el peor margen? ¿Coincide con lo que viste en la Actividad 3?

**Verificación:** C (16 798) > A (13 142) > B (12 184) > **D (2 750)**. El producto D
es el más vendido en transacciones, pero con costo 55 casi no deja margen.

<details><summary>▸ Ver solución</summary>

```python
df = df.merge(catalogo, on="producto", how="left")
df["margen"] = df["ventas"] - df["costo"]
df.groupby("producto")["margen"].sum().round(0).sort_values(ascending=False)
```
</details>

---

### Actividad 10 — Series de tiempo: crecimiento mensual

1. Calcula las ventas totales por mes con `resample("MS")`.
2. Con `.pct_change()`, calcula el **% de cambio** mes a mes.
3. ¿Cuál fue el mejor crecimiento y cuál la peor caída?

**Verificación:** mayo creció **+11.2%**; junio cayó **−21.4%**.

<details><summary>▸ Ver solución</summary>

```python
mensual = df.set_index("fecha").sort_index()["ventas"].resample("MS").sum()
(mensual.pct_change() * 100).round(1)
# feb -0.1 · mar -2.7 · abr +3.6 · may +11.2 · jun -21.4
```
</details>

---

### Actividad 11 — Wide → long

Toma la pivot de la Actividad 8 y conviértela a formato **largo** (tidy) con
`melt`, quedando con las columnas `region | canal | ventas`.

**Verificación:** 12 filas (4 regiones × 3 canales).

<details><summary>▸ Ver solución</summary>

```python
largo = (
    pivot
    .reset_index()
    .melt(id_vars="region", var_name="canal", value_name="ventas")
)
largo.shape   # (12, 3)
```
</details>

---

## 🔴 Nivel 4 — Chaining y Polars (secciones 3.10–3.11)

### Actividad 12 — Todo en una cadena

Escribe **una sola expresión encadenada** que, partiendo del CSV crudo:
elimine duplicados → rellene nulos con la mediana → filtre `ventas > 50` →
calcule el ticket medio por `canal` → ordene de mayor a menor.

Reto extra: ninguna reasignación intermedia de `df`.

<details><summary>▸ Ver solución</summary>

```python
resultado = (
    pd.read_csv("data/raw/ventas_ejemplo.csv", parse_dates=["fecha"])
    .drop_duplicates()
    .assign(ventas=lambda d: d["ventas"].fillna(d["ventas"].median()))
    .query("ventas > 50")
    .groupby("canal", as_index=False)["ventas"].mean()
    .sort_values("ventas", ascending=False)
)
```
</details>

---

### Actividad 13 — Tradúcelo a Polars

Repite la Actividad 12 en **Polars** (modo eager con `pl.read_csv`).
Reto extra: hazlo en modo **lazy** con `pl.scan_csv(...)` + `.collect()`.

<details><summary>▸ Ver solución</summary>

```python
import polars as pl

resultado = (
    pl.scan_csv("data/raw/ventas_ejemplo.csv")          # lazy: aún no lee nada
    .unique()
    .with_columns(pl.col("ventas").fill_null(pl.col("ventas").median()))
    .filter(pl.col("ventas") > 50)
    .group_by("canal")
    .agg(pl.col("ventas").mean().alias("ticket_medio"))
    .sort("ticket_medio", descending=True)
    .collect()                                          # aquí se ejecuta el plan
)
```
</details>

---

## 🏆 Actividad final — Mini-informe: "¿el tráfico impulsa las ventas?"

Integra todo el módulo en un notebook con conclusiones escritas:

1. Carga y limpia el dataset (Actividad 4).
2. Calcula la **correlación** entre `trafico` y `ventas` (`df["ventas"].corr(df["trafico"])`).
   ¿Hay relación?
3. Crea la columna `dia_semana` (`df["fecha"].dt.day_name()`) y calcula el ticket
   medio por día. ¿Qué día se vende mejor?
4. Escribe en una celda Markdown **3 conclusiones** con números concretos
   (estilo: "El producto D concentra el 27% de las transacciones pero solo el 4% del margen").
5. Guarda el dataset limpio en `data/processed/ventas_limpio.parquet`,
   haz commit y push a tu repo `curso-datos`.

**Verificación:** correlación ≈ **−0.035** (prácticamente nula: ¡más tráfico no
significa más ventas en estos datos!) · el mejor día es el **sábado** (ticket medio 109.2).

<details><summary>▸ Ver pistas</summary>

```python
df["ventas"].corr(df["trafico"])          # -0.035 → sin relación lineal
(
    df.assign(dia=df["fecha"].dt.day_name())
    .groupby("dia")["ventas"].mean()
    .round(1)
    .sort_values(ascending=False)
)                                          # Saturday 109.2
df.to_parquet("data/processed/ventas_limpio.parquet", index=False)
```

Una correlación cercana a 0 **también es un hallazgo**: reportar "no hay relación"
con evidencia es trabajo de analista de verdad.
</details>

---

### ✅ Checklist de dominio del módulo

Marca lo que ya sabes hacer sin mirar apuntes:

- [ ] Cargar CSV con fechas parseadas e inspeccionar (shape, nulos, duplicados)
- [ ] Filtrar con condiciones combinadas usando `.loc`
- [ ] Limpiar: duplicados, nulos con mediana, normalizar texto
- [ ] Crear columnas con `assign`, `np.where` y `pd.cut`
- [ ] `groupby` con varias métricas y `pivot_table`
- [ ] `merge` entre tablas y verificar el resultado
- [ ] `resample`, `rolling` y `pct_change` en series de tiempo
- [ ] Convertir wide ↔ long con `melt` / `pivot`
- [ ] Escribir un pipeline completo con method chaining
- [ ] Traducir un análisis de pandas a Polars (eager y lazy)

Si marcaste todo → estás listo para el [Módulo 04 — SQL moderno](../04-sql-moderno/README.md).
