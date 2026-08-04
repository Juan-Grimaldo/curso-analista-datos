# Módulo 05 — SQL moderno para analistas

> **Objetivo:** escribir SQL analítico profesional y usarlo para lo que se usa en una
> empresa de verdad: **extraer** datos de cualquier fuente, **transformarlos** (ETL/ELT),
> **modelarlos** para un almacén de datos y **optimizar** las consultas. Practicaremos con
> **DuckDB**, que corre en tu máquina sin instalar un servidor, pero todo lo que aprendas
> vale igual en BigQuery, Snowflake o Databricks.
>
> 🧭 **Formato:** cada concepto va seguido de un **▶️ Practica ahora**. Ejecútalo en el
> momento. Al final, un **Reto** de cierre.
>
> 📂 **Dónde practicas:** este README es solo la **teoría**. Todo lo que escribas va en tu
> **repo de práctica** `curso-datos`. Prepáralo una sola vez:
>
> ```bash
> cd curso-datos
> uv add duckdb                       # añade DuckDB a tu entorno
> mkdir -p notebooks/05-sql-moderno
> echo "data/" >> .gitignore          # los datos NO se suben al repo
> ```
>
> Crea ahí tu notebook (`notebooks/05-sql-moderno/practica.ipynb`) y escribe cada
> **▶️ Practica ahora** tú mismo. Copia el
> [`ventas_ejemplo.csv`](../datasets/ventas_ejemplo.csv) a la carpeta `data/raw/` de tu repo.
>
> 🧰 **Los scripts del módulo.** Cópialos a la raíz de tu repo `curso-datos` y ejecútalos
> con `uv run` **en este orden**. Los cuatro primeros usan `tienda.duckdb` (Módulo 04); el
> bloque de datos trabaja con un dataset propio de **200.000 filas sucias**:
>
> | # | Script | Qué hace |
> |---|--------|----------|
> | 1 | `demo_guiado.py` | SQL analítico paso a paso (secciones 4.2 – 4.10) |
> | 2 | `actividad_01.py` | Lo escribes tú, con corrector automático |
> | 3 | `crear_fuentes.py` | Genera las fuentes crudas: CSV de 200.000 ventas, clientes y catálogo JSON |
> | 4 | `demo_etl_elt.py` | Extracción, ETL vs ELT, capas raw → staging → marts, tests, carga incremental |
> | 5 | `actividad_etl.py` | Construyes tú el pipeline ELT completo (corrector automático) |
> | 6 | `demo_modelado.py` | Grano, fan-out, claves, `dim_fecha`, SCD tipo 2, estrella vs copo |
> | 7 | `demo_optimizacion.py` | EXPLAIN, Parquet, particionado, índices, materialización — con cronómetro |
> | 8 | `actividad_modelado_opt.py` | Modelas y optimizas tú (corrector automático) |

---

## 4.1 Por qué SQL sigue siendo el rey

Aunque uses Python, **SQL es el lenguaje de los datos**: los warehouses (BigQuery,
Snowflake, Redshift) hablan SQL, y dbt (Módulo 08) es SQL con superpoderes. Un analista
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
y lo construirás con dbt en el Módulo 08.

> ### ▶️ Practica ahora
> Mira `ventas_ejemplo.csv` e identifica: ¿cuál sería la **tabla de hechos**? ¿qué columnas
> serían **dimensiones**? ¿cuáles son las **métricas**? Escríbelo en 3 líneas.

---

## 4.11 Extracción: traer el dato desde donde esté

Hasta aquí has consultado lo que ya tenías. En el trabajo real, el primer paso es
**extraer**: los datos viven en archivos, en otras bases de datos y en APIs. Con SQL
moderno puedes leerlos **sin cargarlos** primero.

```sql
-- Archivos, con el formato que sea
SELECT * FROM 'data/raw/ventas_crudas.csv';
SELECT * FROM read_csv('data/raw/ventas_crudas.csv', all_varchar=true);  -- todo como texto
SELECT * FROM read_parquet('data/raw/ventas.parquet');
SELECT * FROM read_json_auto('data/raw/productos.json');

-- Varios archivos de golpe (un patrón, como en un data lake)
SELECT * FROM read_parquet('data/lake/ventas/**/*.parquet', hive_partitioning=true);

-- Otra base de datos, como si fuera local
ATTACH 'otra.duckdb' AS otra;          -- también PostgreSQL, MySQL o SQLite
SELECT * FROM otra.ventas;

-- Y el camino de vuelta: exportar el resultado
COPY (SELECT * FROM marts.fct_ventas) TO 'salida.parquet' (FORMAT PARQUET);
```

Antes de transformar nada, **mira la fuente**. Dos consultas que deberías hacer siempre:

```sql
DESCRIBE   SELECT * FROM 'data/raw/ventas_crudas.csv';   -- qué columnas y de qué tipo
SUMMARIZE  SELECT * FROM 'data/raw/ventas_crudas.csv';   -- nulos, mín, máx, distintos
```

> 💡 `all_varchar=true` parece un capricho, pero es la clave del ELT: si dejas que el
> lector adivine tipos, una fila rara te tumba la carga entera. Cargas todo como texto y
> **decides tú** los tipos después, con SQL.

> ### ▶️ Practica ahora
> Copia `crear_fuentes.py` a tu repo y ejecútalo (`uv run crear_fuentes.py`): genera
> 200.000 filas crudas. Luego lanza `DESCRIBE` y `SUMMARIZE` sobre `ventas_crudas.csv` y
> responde: ¿cuántas columnas llegan como texto que deberían ser números o fechas?

---

## 4.12 Manipulación: crear y modificar datos (DDL y DML)

Consultar es la mitad del trabajo; la otra mitad es **crear las tablas** del almacén.

| Familia | Sentencias | Para qué |
|---------|-----------|----------|
| **DDL** (estructura) | `CREATE`, `ALTER`, `DROP` | crear tablas, vistas, esquemas |
| **DML** (datos) | `INSERT`, `UPDATE`, `DELETE`, `MERGE` | mover filas |
| **DQL** (consulta) | `SELECT` | lo que ya sabes |

```sql
CREATE SCHEMA IF NOT EXISTS marts;             -- un "cajón" con nombre para agrupar tablas

-- CTAS: crear una tabla A PARTIR de una consulta. El caballo de batalla del ELT.
CREATE OR REPLACE TABLE marts.fct_ventas AS
SELECT venta_id, fecha, region, monto FROM staging.stg_ventas WHERE monto IS NOT NULL;

-- Una VISTA no guarda datos: guarda la consulta y la recalcula al usarla
CREATE OR REPLACE VIEW staging.stg_ventas AS SELECT ... FROM raw.ventas;

INSERT INTO marts.fct_ventas SELECT ... ;      -- añadir filas
UPDATE marts.fct_ventas SET region = 'Norte' WHERE region = 'NORTE';
DELETE FROM marts.fct_ventas WHERE fecha < DATE '2025-01-01';
```

**Tabla o vista**, la decisión que más se repite:

| | Vista | Tabla |
|---|-------|-------|
| Ocupa espacio | No | Sí |
| Siempre al día | Sí | Solo tras recargarla |
| Coste al consultar | Recalcula cada vez | Ya está calculado |
| Úsala en | staging, lógica que cambia | marts, agregados que se consultan mucho |

`CREATE OR REPLACE` es tu mejor amigo: hace el proceso **idempotente** — ejecutarlo dos
veces deja exactamente el mismo resultado. Y cuando varias sentencias deben ir juntas:

```sql
BEGIN TRANSACTION;
  DELETE FROM marts.fct_ventas WHERE mes = DATE '2026-07-01';
  INSERT INTO marts.fct_ventas SELECT ... WHERE mes = DATE '2026-07-01';
COMMIT;                    -- o ROLLBACK si algo falla: o entra todo, o no entra nada
```

> ### ▶️ Practica ahora
> En tu notebook: crea un esquema `pruebas`, dentro una tabla con `CREATE TABLE ... AS
> SELECT` (las 100 primeras ventas), añade una fila con `INSERT`, bórrala con `DELETE` y
> tira la tabla con `DROP TABLE`. Cinco líneas, pero son el 80% del DDL/DML que usarás.

---

## 4.13 ETL vs ELT: los dos caminos

Ya viste la definición en el [Módulo 01](../01-fundamentos-modernos/README.md). Aquí la
ejecutas.

```
ETL (clásico)     Extraer ──► Transformar (fuera) ──► Cargar ya limpio
ELT (moderno)     Extraer ──► Cargar el CRUDO ──► Transformar DENTRO con SQL
```

| | ETL | ELT |
|---|-----|-----|
| Dónde transformas | Fuera: Python, Alteryx, KNIME… | Dentro del warehouse, con SQL |
| El dato crudo | Se pierde por el camino | Se guarda en la capa `raw` |
| Cambiar una regla | Reprocesar el archivo original | Cambias una vista y listo |
| Quién lo mantiene | Quien sepa la herramienta | Cualquiera que sepa SQL |
| Escala | La RAM de tu máquina | El motor del warehouse |
| Cuándo elegirlo | Datos sensibles que hay que filtrar **antes** de cargar; orígenes enormes que no quieres almacenar | El resto de casos: es el estándar actual |

El ELT ganó porque **almacenar salió barato y el cómputo se volvió elástico**. Y porque
guardar el crudo te permite responder mañana preguntas que hoy no sabías que tenías.

> ### ▶️ Practica ahora
> Ejecuta `uv run demo_etl_elt.py` y compara los **pasos 2 y 3**. Escribe en 3 líneas:
> ¿qué información se pierde en el camino ETL que el camino ELT conserva?

---

## 4.14 El patrón de capas: `raw` → `staging` → `marts`

Es la arquitectura estándar (y exactamente la que organiza dbt en el Módulo 08):

```
   FUENTES          raw                staging              marts
  CSV / JSON  ──►  copia fiel   ──►   limpio y tipado  ──►  modelo de negocio
   API / BD        (sin tocar)         (1:1 con la fuente)   (hechos + dimensiones)
```

| Capa | Contiene | Regla de oro | Vista o tabla |
|------|----------|--------------|---------------|
| `raw` | El crudo tal cual llegó, más metadatos de ingesta (`_cargado_en`, `_lote`) | **Nunca** se edita ni se limpia | Tabla |
| `staging` | Tipos correctos, nombres estándar, sin duplicados. Sigue habiendo una fila por fila de origen | Nada de lógica de negocio aquí | Vista |
| `marts` | `fct_*` (hechos) y `dim_*` (dimensiones), agregados listos para el dashboard | Aquí sí vive la lógica de negocio | Tabla |

Convención de nombres que verás en cualquier empresa: `stg_ventas`, `fct_ventas`,
`dim_cliente`, `mart_ventas_mensuales`.

> 💡 ¿Por qué tres capas y no una consulta gigante? Porque cuando un número sale mal, puedes
> bajar capa a capa hasta encontrar dónde se rompió. Eso es **trazabilidad**, y es lo que te
> permite decir "confío en este dato".

> ### ▶️ Practica ahora
> Mira los pasos 3, 4 y 5 de `demo_etl_elt.py` y escribe, para cada capa, **una frase** que
> explique qué transformación ocurre ahí. Si no puedes, es que esa capa está haciendo de más.

---

## 4.15 Limpiar con SQL (la capa staging por dentro)

El dato sucio siempre trae los mismos problemas. Y SQL tiene una respuesta para cada uno:

| Problema en el crudo | Solución en SQL |
|----------------------|-----------------|
| `'123'` que debería ser número | `CAST(x AS INTEGER)` |
| …y a veces trae `'N/A'` y revienta | `TRY_CAST(x AS INTEGER)` → devuelve `NULL` en vez de fallar |
| `'$1,450.00'` | `TRY_CAST(REPLACE(REPLACE(x,'$',''),',','') AS DECIMAL(12,2))` |
| Fechas en dos formatos | `COALESCE(TRY_CAST(f AS DATE), TRY_STRPTIME(f,'%d/%m/%Y')::DATE)` |
| `'  ESTE '`, `'este'`, `'Este'` | `TRIM`, `UPPER`, `LOWER`, `SUBSTR` |
| Cadenas vacías que deberían ser nulos | `NULLIF(x, '')` |
| Texto con basura variable | `REGEXP_REPLACE(x, '[^0-9.]', '', 'g')` |
| Filas duplicadas | `QUALIFY ROW_NUMBER() OVER (PARTITION BY id ORDER BY _cargado_en DESC) = 1` |

`QUALIFY` es el filtro de las *window functions*: `WHERE` filtra filas, `HAVING` filtra
grupos, **`QUALIFY` filtra por el resultado de una ventana**. Es la forma más limpia de
deduplicar que existe.

```sql
CREATE OR REPLACE VIEW staging.stg_ventas AS
SELECT
    CAST(venta_id AS INTEGER)                                            AS venta_id,
    COALESCE(TRY_CAST(fecha AS DATE), TRY_STRPTIME(fecha,'%d/%m/%Y')::DATE) AS fecha,
    UPPER(SUBSTR(TRIM(region),1,1)) || LOWER(SUBSTR(TRIM(region),2))     AS region,
    TRY_CAST(REPLACE(REPLACE(monto,'$',''),',','') AS DECIMAL(12,2))     AS monto
FROM raw.ventas
QUALIFY ROW_NUMBER() OVER (PARTITION BY venta_id ORDER BY _cargado_en DESC) = 1;
```

> ⚠️ Usa `TRY_CAST` en staging, siempre. Un `CAST` normal detiene todo el pipeline por una
> fila mala; `TRY_CAST` la deja en `NULL` y luego un test te dice cuántas fueron.

> ### ▶️ Practica ahora
> Ejecuta `uv run actividad_etl.py` y resuelve los **ejercicios 1 a 4**: cargar el crudo,
> cargar el JSON y escribir la vista de staging completa. El corrector te dice si tu
> limpieza dejó 200.000 filas, 5 regiones y 0 fechas sin parsear.

---

## 4.16 Carga incremental e idempotencia

Recargar 18 meses de datos cada noche funciona… hasta que son 500 millones de filas.

| Estrategia | Cómo | Cuándo |
|------------|------|--------|
| **Full refresh** | `CREATE OR REPLACE TABLE ... AS SELECT` | Tablas pequeñas o lógica que cambia mucho |
| **Delete + insert** | Borras el período y lo vuelves a insertar | El caso más común: recargar el mes en curso |
| **Append** | `INSERT INTO ... SELECT` del lote nuevo | Datos que solo crecen (logs, eventos) |
| **Upsert / MERGE** | Actualiza si existe, inserta si no | Cuando el origen corrige filas viejas |

```sql
-- Delete + insert: idempotente por definición. Ejecútalo 10 veces: mismo resultado.
DELETE FROM marts.fct_ventas WHERE fecha >= DATE '2026-07-01';
INSERT INTO marts.fct_ventas
SELECT ... FROM staging.stg_ventas WHERE fecha >= DATE '2026-07-01';
```

**Idempotente** = ejecutarlo dos veces deja el mismo estado que ejecutarlo una. Es el
requisito número uno de un pipeline: los procesos fallan a medias y se reintentan, y si tu
carga no es idempotente, cada reintento duplica datos.

Para saber *desde dónde* cargar se usa una **marca de agua** (*watermark*): la fecha máxima
ya cargada.

```sql
SELECT MAX(fecha) FROM marts.fct_ventas;   -- cargo solo lo posterior a esto
```

> ### ▶️ Practica ahora
> En `demo_etl_elt.py`, el **paso 7** hace una carga incremental. Ejecútalo **dos veces
> seguidas** y comprueba que el número de filas no cambia. Después, resuelve el
> **ejercicio 8** de `actividad_etl.py`.

---

## 4.17 Tests de calidad: SQL que vigila tus datos

Un test de datos es simplemente **una consulta que debe devolver 0 filas**. Si devuelve
algo, hay un problema.

```sql
-- Unicidad: no puede haber dos ventas con el mismo id
SELECT venta_id FROM staging.stg_ventas GROUP BY 1 HAVING COUNT(*) > 1;

-- No nulos: ninguna fecha se quedó sin parsear
SELECT venta_id FROM staging.stg_ventas WHERE fecha IS NULL;

-- Valores aceptados: solo existen estas regiones
SELECT DISTINCT region FROM staging.stg_ventas
WHERE region NOT IN ('Norte','Sur','Este','Oeste','Centro');

-- Integridad referencial: todo producto vendido existe en el catálogo (claves huérfanas)
SELECT DISTINCT f.producto_id FROM marts.fct_ventas f
LEFT JOIN marts.dim_producto d ON f.producto_id = d.producto_id
WHERE d.producto_id IS NULL;

-- Coherencia de negocio: el importe cuadra con unidades x precio x descuento
SELECT venta_id FROM marts.fct_ventas
WHERE ABS(monto - ROUND(unidades * precio_unitario * (1 - descuento), 2)) > 0.05;
```

Cuando un test falla tienes tres opciones honestas: **parar** el pipeline, mandar esas filas
a **cuarentena** (una tabla aparte) o **avisar** y seguir. Lo que nunca debes hacer es
descartarlas en silencio.

> 💡 Estos cinco tests son exactamente los que dbt trae de serie (`unique`, `not_null`,
> `accepted_values`, `relationships`) y que declararás en YAML en el Módulo 08. Escribirlos
> a mano ahora hace que allí entiendas qué está pasando por debajo.

> ### ▶️ Practica ahora
> Ejecuta el **paso 6** de `demo_etl_elt.py`. Uno de los tests falla a propósito: averigua
> **cuántas filas** están mal y **por qué**. Luego escribe tú un sexto test: que ninguna
> venta tenga fecha futura.

---

## 4.18 Modelado para el almacén de datos

La sección 4.10 te dio el esquema estrella. Estos son los cinco detalles que separan un
modelo que aguanta de uno que da números raros.

**1. El grano.** ¿Qué representa UNA fila? Defínelo en una frase *antes* de escribir nada:
"una línea de venta de un producto a un cliente en una fecha". Si no puedes, el modelo
está mal.

**2. El fan-out: el error más caro del análisis.** Unir una tabla que tiene varias filas
por clave **multiplica** tus hechos:

```sql
-- MAL: si cada producto participó en 3 campañas, los ingresos salen x3
SELECT SUM(f.monto) FROM fct_ventas f JOIN campanas c ON f.producto_id = c.producto_id;

-- BIEN: llevas cada fuente a su grano ANTES de unir
WITH ventas AS (SELECT producto_id, SUM(monto) AS ingresos FROM fct_ventas GROUP BY 1),
     inversion AS (SELECT producto_id, SUM(inversion) AS inv FROM campanas GROUP BY 1)
SELECT * FROM ventas JOIN inversion USING (producto_id);
```

**3. Claves naturales y subrogadas.** La **natural** es la del origen (`'P01'`); la
**subrogada** es un entero que controlas tú (`1, 2, 3…`, con `ROW_NUMBER()`). Los hechos
apuntan a la subrogada: es estable, ocupa menos y permite guardar varias versiones de la
misma entidad.

**4. `dim_fecha`.** Una tabla con un día por fila y sus atributos (año, trimestre, mes,
fin de semana, festivo). Se genera una vez:

```sql
CREATE TABLE dim_fecha AS
SELECT d::DATE AS fecha, YEAR(d) AS anio, QUARTER(d) AS trimestre,
       MONTHNAME(d) AS mes_nombre, DAYOFWEEK(d) IN (0,6) AS es_fin_de_semana
FROM generate_series(DATE '2025-01-01', DATE '2026-12-31', INTERVAL 1 DAY) AS t(d);
```

Sin ella, los días sin ventas **desaparecen** de tus gráficos (no existen en la tabla de
hechos) y las series temporales mienten.

**5. Dimensiones que cambian (SCD).** Un cliente pasa de "Retail" a "Corporativo":

| Tipo | Qué hace | Consecuencia |
|------|----------|--------------|
| **SCD 1** | Machaca el valor viejo | El histórico se reescribe: sus compras de 2025 pasan a contarse como Corporativo |
| **SCD 2** | Añade una fila nueva con `valido_desde` / `valido_hasta` / `es_actual` | Puedes responder "¿qué era este cliente **cuando compró**?" |

```sql
-- Ingresos por el segmento VIGENTE EN LA FECHA DE LA VENTA
SELECT d.segmento, SUM(f.monto)
FROM fct_ventas f
JOIN dim_cliente_scd2 d
  ON f.cliente_id = d.cliente_id
 AND f.fecha BETWEEN d.valido_desde AND d.valido_hasta
GROUP BY 1;
```

Y una decisión de fondo: en analítica **desnormaliza** (esquema estrella, pocas uniones,
fácil de usar); en una base transaccional (OLTP) se **normaliza** para evitar
inconsistencias al escribir. Modela según el uso, no por dogma.

> ### ▶️ Practica ahora
> Ejecuta `uv run demo_modelado.py` y quédate con el **paso 2**: verás los ingresos
> triplicarse por un JOIN inocente. Luego resuelve los **ejercicios 1 a 4** de
> `actividad_modelado_opt.py` (dim_fecha, claves subrogadas, fan-out y SCD 2).

---

## 4.19 Optimización de consultas

Una consulta lenta en tu portátil es una consulta **cara** en la nube. Estas son las
palancas, ordenadas por impacto real.

**1. Lee menos datos.** Es el 80% de la optimización.

```sql
SELECT *                        FROM ventas;   -- lee las 14 columnas
SELECT region, monto            FROM ventas;   -- lee 2: hasta 6x más rápido
```

En un formato **columnar** (Parquet, o cualquier warehouse moderno), las columnas que no
pides ni se leen del disco: *projection pushdown*. En BigQuery eso es literalmente tu
factura.

**2. Filtra pronto y de forma "aprovechable".**

```sql
WHERE YEAR(fecha) = 2026                                   -- ❌ la columna va envuelta
WHERE fecha >= DATE '2026-01-01' AND fecha < DATE '2027-01-01'   -- ✅ rango directo
```

Al envolver la columna en una función, el motor no puede usar índices, estadísticas de
bloque ni particiones: tiene que calcularla fila a fila. Deja la columna **desnuda** a un
lado del operador.

**3. Mide, no adivines: `EXPLAIN`.**

```sql
EXPLAIN         SELECT ... ;   -- el plan que piensa ejecutar
EXPLAIN ANALYZE SELECT ... ;   -- lo ejecuta y añade tiempo y filas reales por operador
```

El plan se lee **de abajo hacia arriba**. Busca tres cosas: qué columnas y filtros llegan
al `SCAN` (¿bajó el filtro?), el tipo de `JOIN` (un `NESTED LOOP` sobre millones de filas
es una alarma) y en qué operador se dispara el tiempo.

**4. Particiona por lo que filtras.** Si guardas los datos en carpetas `anio=2026/mes=7/`,
el motor descarta los archivos que no cumplen el filtro sin abrirlos (*partition pruning*).
Es la optimización que más dinero ahorra en la nube.

**5. Materializa lo que repites.** ¿La misma agregación pesada mil veces al día? Guárdala
como tabla una vez por carga (staging → vistas, marts → tablas).

**6. Índices: para buscar, no para agregar.** Un índice acelera consultas **selectivas**
(una fila entre millones). Una agregación que recorre toda la tabla no lo necesita: por eso
los warehouses columnares casi no usan índices y confían en particiones, *clustering* y
estadísticas.

**Checklist rápido** — ante una consulta lenta, en este orden:

1. ¿Pido columnas que no uso? 2. ¿Puedo filtrar antes? 3. ¿El filtro envuelve la columna?
4. ¿Está particionado por lo que filtro? 5. ¿Estoy leyendo CSV en vez de Parquet/tabla?
6. ¿Repito un cálculo caro que podría materializar? 7. ¿Qué dice `EXPLAIN ANALYZE`?

> ### ▶️ Practica ahora
> Ejecuta `uv run demo_optimizacion.py`: trae cronómetro. Anota las dos proporciones que
> más te sorprendan. Luego resuelve los **ejercicios 5 a 8** de `actividad_modelado_opt.py`
> (filtro aprovechable, materialización, particionado y lectura con *pruning*).

---

## 4.20 El mismo SQL en la nube: Snowflake, BigQuery, Databricks

Todo lo anterior lo has hecho en DuckDB, en tu portátil. En una empresa lo harás sobre un
warehouse cloud — y el 90% de tu SQL se copia y pega tal cual.

| | **Snowflake** | **BigQuery** (Google) | **Databricks** |
|---|---|---|---|
| Qué es | Warehouse multi-cloud | Warehouse *serverless* | Lakehouse (datos + ML) |
| Cómo pagas | Por **segundos de cómputo** encendido | Por **bytes leídos** en cada consulta | Por cómputo del clúster (DBUs) |
| Optimizar es… | Consultas cortas, aprovechar la caché, *cluster keys* | Particionar, *clustering*, pedir solo columnas | `OPTIMIZE` + `Z-ORDER`, evitar ficheros pequeños |
| Formato interno | Micro-particiones propias | Almacenamiento columnar propio | Delta Lake (Parquet + log) |
| Peculiaridad | *Time travel*, clonado sin copiar, `WAREHOUSE` que escalas a mano | `SELECT *` de una tabla grande puede costar dinero de verdad | SQL y Python/Spark conviven en el mismo sitio |

**Diferencias de dialecto** que te encontrarás (nada dramático):

| Idea | DuckDB / Postgres | BigQuery | Snowflake |
|------|-------------------|----------|-----------|
| Truncar a mes | `DATE_TRUNC('month', f)` | `DATE_TRUNC(f, MONTH)` | `DATE_TRUNC('month', f)` |
| Cast | `CAST(x AS INT)` / `x::INT` | `CAST(x AS INT64)` / `SAFE_CAST` | `CAST(x AS NUMBER)` / `TRY_CAST` |
| Cast seguro | `TRY_CAST` | `SAFE_CAST` | `TRY_CAST` |
| Filtrar ventanas | `QUALIFY` | `QUALIFY` | `QUALIFY` |
| Nombres | sensibles a comillas dobles | backticks `` `proyecto.dataset.tabla` `` | MAYÚSCULAS por defecto |

> 💡 No memorices dialectos: memoriza **conceptos**. Cuando sepas que existe "el cast que no
> revienta", buscar cómo se llama en cada motor te lleva diez segundos.

**Para practicar sin tarjeta de crédito:** BigQuery tiene una capa gratuita (1 TB de
consultas al mes) con datasets públicos enormes; Snowflake y Databricks dan pruebas
gratuitas con crédito. Una consulta tuya sobre un dataset público de BigQuery, capturada en
el portafolio, vale mucho en una entrevista.

> ### ▶️ Practica ahora
> Coge la consulta del mart mensual que escribiste en `actividad_etl.py` y **tradúcela a
> BigQuery**: cambia `DATE_TRUNC('month', fecha)` por `DATE_TRUNC(fecha, MONTH)` y los
> nombres de tabla al formato `` `proyecto.dataset.tabla` ``. Fíjate en lo poco que cambia.

---

## 4.21 Buenas prácticas

**Escribiendo consultas:**

- Palabras clave en MAYÚSCULAS y sangría consistente.
- Usa **CTEs** en vez de subconsultas anidadas.
- Nombra columnas de forma clara (`ventas_total`, no `col1`).
- Evita `SELECT *` en producción.
- Comenta el *por qué*, no el *qué*.
- Filtra pronto (`WHERE`) para procesar menos datos.

**Construyendo pipelines:**

- El crudo (`raw`) **no se toca jamás**: es tu única fuente de verdad.
- Todo proceso debe ser **idempotente** (`CREATE OR REPLACE`, `DELETE` + `INSERT`).
- Un `TRY_CAST` en staging por cada `CAST` que podría fallar.
- Cada tabla del mart, con al menos un test de unicidad y uno de no nulos.
- Nada de descartar filas en silencio: **cuarentena** y avisa.
- El SQL de transformación vive en **archivos versionados en Git**, no en un notebook suelto.

---

## Reto del módulo (cierre)

**Reto 1 — la consulta de dashboard.** Escribe **una** consulta (con al menos una CTE y una
window function) que produzca una tabla lista para un dashboard: una métrica clave cortada
por 2 dimensiones (ej. región y mes) con su **variación temporal**. Documenta qué pregunta
de negocio responde.

**Reto 2 — tu propio pipeline ELT.** Monta, en un solo script `.sql` o `.py`, el camino
completo sobre las fuentes crudas:

1. **Extrae y carga** el CSV y el JSON en un esquema `raw`, sin transformar nada.
2. **Staging:** una vista limpia y deduplicada por cada fuente.
3. **Marts:** una tabla de hechos y al menos dos dimensiones (una de ellas, `dim_fecha`).
4. **Tests:** tres consultas de calidad que devuelvan 0 filas.
5. **Incremental:** que volver a ejecutarlo entero **no cambie ni una fila** (idempotencia).
6. **Optimiza:** exporta el mart a Parquet particionado y compara con `EXPLAIN ANALYZE` una
   consulta antes y después. Anota la mejora.

Escribe al final un `README.md` de 10 líneas explicando el flujo y qué preguntas de negocio
responde el mart. Guárdalo todo en tu repo `curso-datos` y haz commit a **ese** repo: este
proyecto, con su diagrama de capas, es material de portafolio de primera.

➡️ Siguiente: [Módulo 06 — Estadística y EDA](../06-estadistica-y-eda/README.md)
