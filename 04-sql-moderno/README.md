# Módulo 04 — SQL moderno para analistas

> **Objetivo:** escribir SQL analítico profesional: desde consultas sólidas hasta CTEs,
> *window functions* y buenas prácticas de modelado. Practicaremos con **DuckDB**, que
> corre en tu máquina sin instalar un servidor.
>
> 🧭 **Formato:** cada concepto va seguido de un **▶️ Practica ahora** sobre
> [`ventas_ejemplo.csv`](../datasets/ventas_ejemplo.csv) usando DuckDB. Ejecútalo en el
> momento. Al final, un **Reto** de cierre.

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
duckdb.sql("SELECT * FROM 'data/raw/ventas_ejemplo.csv' LIMIT 5").show()
```

> ### ▶️ Practica ahora
> En un notebook, ejecuta ese `SELECT ... LIMIT 5` sobre `ventas_ejemplo.csv`. Confirma que
> ves las 8 columnas. A partir de aquí, todas las prácticas serán consultas SQL sobre este archivo.

---

## 4.3 La consulta fundamental y su orden

```sql
SELECT   region, SUM(ventas) AS ventas_total
FROM     'data/raw/ventas_ejemplo.csv'
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

> ### ▶️ Practica ahora
> Escribe una consulta que devuelva las ventas totales por `canal`, solo de la región
> `Norte`, ordenadas de mayor a menor. (Filtra por región en `WHERE`, agrupa por canal.)

---

## 4.4 Filtrar bien

```sql
WHERE precio BETWEEN 10 AND 50
WHERE region IN ('Norte', 'Sur')
WHERE producto LIKE 'A%'          -- empieza por A
WHERE ventas IS NOT NULL
WHERE (region = 'Norte' AND ventas > 100) OR canal = 'Web'
```

`WHERE` filtra **filas** antes de agrupar; `HAVING` filtra **grupos** después.

> ### ▶️ Practica ahora
> Cuenta cuántas ventas hay en los canales `Web` y `Movil` (usa `IN`) con monto no nulo
> y superior a 90.

---

## 4.5 Agregaciones

```sql
SELECT
    region,
    COUNT(*)                   AS n_ventas,
    COUNT(DISTINCT producto)   AS productos_distintos,
    SUM(ventas)                AS total,
    AVG(ventas)                AS promedio,
    MEDIAN(ventas)             AS mediana      -- disponible en DuckDB
FROM 'data/raw/ventas_ejemplo.csv'
GROUP BY region;
```

> ### ▶️ Practica ahora
> Para cada `producto`, calcula el número de ventas, el total y el promedio. ¿Qué producto
> tiene el promedio de venta más alto?

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

> ### ▶️ Practica ahora
> Crea una tabla de referencia en SQL con los nombres de producto y haz un JOIN. Puedes
> usar una CTE: `WITH ref(producto, nombre) AS (VALUES ('A','Alfa'),('B','Beta'),('C','Cesar'),('D','Delta'))`
> y únela con el CSV por `producto`.

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
    FROM 'data/raw/ventas_ejemplo.csv'
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

Lee de arriba a abajo como pasos. **Prefiere siempre CTEs a subconsultas anidadas.**

> ### ▶️ Practica ahora
> Escribe una consulta con **dos CTEs**: la primera agrega ventas por `mes` y `region`; la
> segunda selecciona solo el mes con más ventas totales. Lee tu consulta en voz alta como pasos.

---

## 4.8 Window functions (funciones de ventana) — nivel pro

Calculan valores **entre filas relacionadas sin colapsar** el resultado (a diferencia de
`GROUP BY`). Es lo que separa a un analista junior de uno senior.

```sql
SELECT
    fecha, region, ventas,
    -- Total acumulado por región a lo largo del tiempo
    SUM(ventas) OVER (PARTITION BY region ORDER BY fecha) AS acumulado,
    -- Ranking de ventas dentro de cada región
    ROW_NUMBER() OVER (PARTITION BY region ORDER BY ventas DESC) AS puesto,
    -- Valor de la fila anterior (para calcular variación)
    LAG(ventas) OVER (PARTITION BY region ORDER BY fecha) AS ventas_previas
FROM 'data/raw/ventas_ejemplo.csv';
```

**Anatomía:** `FUNCION() OVER (PARTITION BY <grupo> ORDER BY <orden> <marco>)`.
Funciones comunes: `ROW_NUMBER`, `RANK`, `DENSE_RANK`, `LAG`, `LEAD`, `SUM`, `AVG`, `NTILE`.

### Caso típico: variación mes a mes

```sql
WITH mensual AS (
    SELECT DATE_TRUNC('month', fecha) AS mes, SUM(ventas) AS total
    FROM 'data/raw/ventas_ejemplo.csv' GROUP BY 1
)
SELECT
    mes, total,
    LAG(total) OVER (ORDER BY mes) AS mes_anterior,
    ROUND(100.0 * (total - LAG(total) OVER (ORDER BY mes))
          / LAG(total) OVER (ORDER BY mes), 1) AS variacion_pct
FROM mensual;
```

> ### ▶️ Practica ahora
> 1. Saca el **Top 3 productos** por ventas totales usando `RANK()`.
> 2. Calcula la **variación porcentual** de ventas mes a mes (adapta el ejemplo de arriba).
> ¿Qué mes tuvo la mayor caída?

---

## 4.9 CASE: lógica condicional

```sql
SELECT
    producto, ventas,
    CASE
        WHEN ventas >= 120 THEN 'Alto'
        WHEN ventas >= 90  THEN 'Medio'
        ELSE 'Bajo'
    END AS segmento
FROM 'data/raw/ventas_ejemplo.csv';
```

> ### ▶️ Practica ahora
> Segmenta cada venta en Alto/Medio/Bajo con `CASE` y luego **cuenta cuántas hay de cada
> segmento** (envuélvelo en una CTE y agrupa por el segmento).

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

> ### ▶️ Practica ahora
> Mira `ventas_ejemplo.csv` e identifica: ¿cuál sería la **tabla de hechos**? ¿qué columnas
> serían **dimensiones**? ¿cuáles son las **métricas**? Escríbelo en 3 líneas.

---

## 4.11 Buenas prácticas

- Palabras clave en MAYÚSCULAS y sangría consistente.
- Usa **CTEs** en vez de subconsultas anidadas.
- Nombra columnas de forma clara (`ventas_total`, no `col1`).
- Evita `SELECT *` en producción.
- Comenta el *por qué*, no el *qué*.
- Filtra pronto (`WHERE`) para procesar menos datos.

---

## Reto del módulo (cierre)

Escribe **una** consulta (con al menos una CTE y una window function) que produzca una tabla
lista para un dashboard: una métrica clave cortada por 2 dimensiones (ej. región y mes) con
su **variación temporal**. Documenta qué pregunta de negocio responde. Guárdala en tu repo.

➡️ Siguiente: [Módulo 05 — Estadística y EDA](../05-estadistica-y-eda/README.md)
