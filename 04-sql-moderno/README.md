# Módulo 04 — SQL moderno para analistas

> **Objetivo:** escribir SQL analítico profesional: desde consultas sólidas hasta CTEs,
> *window functions* y buenas prácticas de modelado. Practicaremos con **DuckDB**, que
> corre en tu máquina sin instalar un servidor.

---

## 4.1 Por qué SQL sigue siendo el rey

Aunque uses Python, **SQL es el lenguaje de los datos**: los warehouses (BigQuery,
Snowflake, Redshift) hablan SQL, y dbt (Módulo 07) es SQL con superpoderes. Un analista
que domina SQL es infinitamente más empleable.

> 💡 Regla práctica: **transforma cerca del dato**. Si el dato vive en un warehouse,
> agrégalo con SQL *antes* de traerlo a Python. Es más rápido y escala mejor.

---

## 4.2 Practicar sin instalar nada: DuckDB

**[DuckDB](https://duckdb.org/)** es "el SQLite del análisis": una base de datos analítica
que corre en tu proceso y lee CSV/Parquet directamente.

```python
import duckdb

# Consultar un CSV directamente, sin cargarlo
duckdb.sql("SELECT * FROM 'data/raw/ventas.csv' LIMIT 5").show()

# Consultar un DataFrame de pandas
import pandas as pd
df = pd.read_csv("data/raw/ventas.csv")
duckdb.sql("SELECT region, SUM(ventas) FROM df GROUP BY region").df()
```

Esto te deja practicar SQL **sobre tus propios archivos**. Lo usaremos en todo el módulo.

---

## 4.3 La consulta fundamental y su orden

```sql
SELECT   region, SUM(ventas) AS ventas_total
FROM     ventas
WHERE    fecha >= '2026-01-01'
GROUP BY region
HAVING   SUM(ventas) > 1000
ORDER BY ventas_total DESC
LIMIT    10;
```

**Orden de escritura ≠ orden de ejecución.** SQL ejecuta así:

```
FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT
```

Entender esto explica muchos errores (ej. por qué no puedes usar un alias del `SELECT`
en el `WHERE`).

---

## 4.4 Filtrar bien

```sql
WHERE precio BETWEEN 10 AND 50
WHERE region IN ('Norte', 'Sur')
WHERE producto LIKE 'A%'          -- empieza por A
WHERE fecha IS NOT NULL
WHERE (region = 'Norte' AND ventas > 100) OR prioridad = 'Alta'
```

`WHERE` filtra **filas** antes de agrupar; `HAVING` filtra **grupos** después.

---

## 4.5 Agregaciones

```sql
SELECT
    region,
    COUNT(*)            AS n_ventas,
    COUNT(DISTINCT cliente_id) AS clientes_unicos,
    SUM(ventas)         AS total,
    AVG(ventas)         AS promedio,
    MIN(ventas)         AS minimo,
    MAX(ventas)         AS maximo,
    MEDIAN(ventas)      AS mediana      -- disponible en DuckDB
FROM ventas
GROUP BY region;
```

---

## 4.6 JOINs

```sql
SELECT v.fecha, v.ventas, p.nombre, p.categoria
FROM ventas v
LEFT JOIN productos p ON v.producto_id = p.id;
```

| JOIN | Devuelve |
|------|----------|
| `INNER JOIN` | Solo filas con coincidencia en ambas tablas |
| `LEFT JOIN` | Todas las de la izquierda + las que coincidan |
| `RIGHT JOIN` | Todas las de la derecha + las que coincidan |
| `FULL OUTER JOIN` | Todas las filas de ambas |

> 💡 Usa **alias** cortos (`v`, `p`) y **cualifica** las columnas (`v.fecha`) cuando hay
> JOINs. Evita `SELECT *` en producción.

---

## 4.7 CTEs: consultas legibles (Common Table Expressions)

Las CTEs (`WITH`) descomponen una consulta compleja en pasos con nombre. Son la base del
SQL profesional y de dbt.

```sql
WITH ventas_mes AS (
    SELECT
        DATE_TRUNC('month', fecha) AS mes,
        region,
        SUM(ventas) AS total
    FROM ventas
    GROUP BY 1, 2
),
ranking AS (
    SELECT
        mes, region, total,
        RANK() OVER (PARTITION BY mes ORDER BY total DESC) AS puesto
    FROM ventas_mes
)
SELECT * FROM ranking WHERE puesto <= 3;
```

Lee de arriba a abajo como pasos: "primero agrego por mes, luego rankeo, luego filtro top 3".
**Prefiere siempre CTEs a subconsultas anidadas.**

---

## 4.8 Window functions (funciones de ventana) — nivel pro

Calculan valores **entre filas relacionadas sin colapsar** el resultado (a diferencia de
`GROUP BY`). Son lo que separa a un analista junior de uno senior.

```sql
SELECT
    fecha,
    region,
    ventas,

    -- Total acumulado por región a lo largo del tiempo
    SUM(ventas) OVER (PARTITION BY region ORDER BY fecha) AS acumulado,

    -- Ranking de ventas dentro de cada región
    ROW_NUMBER() OVER (PARTITION BY region ORDER BY ventas DESC) AS puesto,

    -- Valor de la fila anterior (para calcular variación)
    LAG(ventas) OVER (PARTITION BY region ORDER BY fecha) AS ventas_previas,

    -- Media móvil de 3 periodos
    AVG(ventas) OVER (PARTITION BY region ORDER BY fecha
                      ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS media_movil
FROM ventas;
```

### Anatomía de una window function

```
FUNCION() OVER (PARTITION BY <grupo> ORDER BY <orden> <marco>)
              └ opcional      └ opcional            └ opcional (ROWS BETWEEN...)
```

**Funciones comunes:** `ROW_NUMBER`, `RANK`, `DENSE_RANK`, `LAG`, `LEAD`, `SUM`, `AVG`,
`FIRST_VALUE`, `NTILE`.

### Caso típico: variación respecto al mes anterior

```sql
WITH mensual AS (
    SELECT DATE_TRUNC('month', fecha) AS mes, SUM(ventas) AS total
    FROM ventas GROUP BY 1
)
SELECT
    mes,
    total,
    LAG(total) OVER (ORDER BY mes) AS mes_anterior,
    ROUND(100.0 * (total - LAG(total) OVER (ORDER BY mes))
          / LAG(total) OVER (ORDER BY mes), 1) AS variacion_pct
FROM mensual;
```

---

## 4.9 CASE: lógica condicional

```sql
SELECT
    producto,
    ventas,
    CASE
        WHEN ventas >= 120 THEN 'Alto'
        WHEN ventas >= 90  THEN 'Medio'
        ELSE 'Bajo'
    END AS segmento
FROM ventas;
```

---

## 4.10 Modelado dimensional (para BI)

Los datos para análisis se suelen modelar en **esquema estrella**:

```
          dim_tiempo
              │
dim_producto ─┼─ FACT_ventas ─┬─ dim_cliente
              │               │
          dim_region      (métricas: cantidad, monto)
```

- **Tabla de hechos (fact):** los eventos medibles (ventas, clics). Muchas filas, métricas.
- **Tablas de dimensiones (dim):** el contexto (producto, cliente, tiempo, región).

Este modelo hace los dashboards rápidos e intuitivos. Es el estándar en Power BI/Tableau
y lo construirás con dbt en el Módulo 07.

---

## 4.11 Buenas prácticas

- Escribe las palabras clave en MAYÚSCULAS y usa sangría consistente.
- Usa **CTEs** en vez de subconsultas anidadas.
- Nombra columnas de forma clara (`ventas_total`, no `col1`).
- Evita `SELECT *` en producción; pide solo lo que necesitas.
- Comenta el *por qué*, no el *qué*.
- Filtra pronto (`WHERE`) para procesar menos datos.

---

## Ejercicios

Usa DuckDB sobre [`datasets/ventas_ejemplo.csv`](../datasets/ventas_ejemplo.csv).

1. Ventas totales y promedio por región, ordenadas de mayor a menor.
2. Top 3 productos por ventas usando `RANK()` con una window function.
3. Ventas mensuales con su **variación porcentual** respecto al mes anterior (`LAG`).
4. Total acumulado de ventas por región a lo largo del tiempo.
5. Segmenta cada venta en Alto/Medio/Bajo con `CASE` y cuenta cuántas hay de cada una.
6. Escribe una consulta con **dos CTEs** encadenadas que responda una pregunta tuya.

## Reto del módulo

Toma tu dataset del reto anterior. Escribe una consulta SQL (con CTEs y al menos una
window function) que produzca una tabla lista para un dashboard: una métrica clave cortada
por 2 dimensiones y con su variación temporal. Documenta qué pregunta responde.

➡️ Siguiente: [Módulo 05 — Estadística y EDA](../05-estadistica-y-eda/README.md)
