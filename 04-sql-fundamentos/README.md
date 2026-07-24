# Módulo 04 — SQL: fundamentos

> **Objetivo:** escribir tus primeras consultas SQL con seguridad. Aquí no hay nada avanzado:
> aprendes a **pedirle datos a una tabla** paso a paso — elegir columnas, filtrar filas,
> ordenar, contar y agrupar. Cuando esto te salga solo, el Módulo 05 (SQL moderno) te resultará fácil.
>
> 🧭 **Formato:** cada concepto va seguido de un **▶️ Practica ahora** sobre
> [`ventas_ejemplo.csv`](../datasets/ventas_ejemplo.csv) usando DuckDB. Ejecuta cada práctica
> antes de seguir. Al final, un **Reto** de cierre.
>
> ⚙️ **Prepara todo una vez:** `py -m pip install duckdb` y luego `py crear_db.py`
> (esto genera `data/tienda.duckdb`, la base con varias tablas que usarás para los JOINs de 4.11).
>
> 🎬 **Ver el proceso completo:** `py demo_guiado.py` — todas las consultas de este módulo
> ejecutadas de principio a fin sobre el dataset.
> ✍️ **Hacerlo tú:** `py actividad_01.py` — tú escribes el SQL, con corrector automático
> que ejecuta tus consultas y te dice qué falta.

---

## 4.1 ¿Qué es SQL? (en una frase)

SQL es el idioma para **hacerle preguntas a una tabla de datos**. Le dices *qué* quieres
(columnas), *de dónde* (tabla), *con qué condición* (filtro) y *cómo ordenarlo*. La base de
datos hace el trabajo y te devuelve una tabla de respuesta.

Piensa en una hoja de cálculo enorme: SQL es la forma profesional de filtrarla, sumarla y
resumirla sin ratón, con instrucciones que se leen casi como inglés.

---

## 4.2 Practicar sin instalar nada: DuckDB

**[DuckDB](https://duckdb.org/)** es "el SQLite del análisis": una base de datos que corre
dentro de tu propio Python y **lee un CSV directamente**, sin servidores ni configuración.

```python
import duckdb

# Consultar un CSV como si fuera una tabla
duckdb.sql("SELECT * FROM 'ruta/ventas_ejemplo.csv' LIMIT 5").show()
```

> 💡 `.show()` imprime la tabla bonita. `.fetchall()` te la devuelve como lista de Python.

> ### ▶️ Practica ahora
> Ejecuta ese `SELECT ... LIMIT 5` sobre `ventas_ejemplo.csv`. Confirma que ves las 8
> columnas: `venta_id, fecha, region, producto, canal, ventas, descuento, trafico`.

---

## 4.3 SELECT: elegir columnas

`SELECT` dice **qué columnas** quieres. `FROM` dice **de qué tabla**.

```sql
SELECT *                      -- todas las columnas
FROM 'ventas_ejemplo.csv';

SELECT region, producto, ventas   -- solo estas tres
FROM 'ventas_ejemplo.csv';
```

> ⚠️ El `*` es cómodo para explorar, pero en un análisis real **pide solo las columnas que
> necesitas**. Es más claro y más rápido.

> ### ▶️ Practica ahora
> Escribe una consulta que devuelva solo `fecha`, `region` y `ventas`. Añade `LIMIT 10` al
> final para ver únicamente las 10 primeras filas.

---

## 4.4 WHERE: filtrar filas

`WHERE` se queda solo con las filas que **cumplen una condición**.

```sql
SELECT region, ventas
FROM 'ventas_ejemplo.csv'
WHERE ventas > 100;
```

Operadores que usarás todo el tiempo:

```sql
WHERE region = 'Norte'            -- igual (texto entre comillas simples)
WHERE ventas >= 100               -- mayor o igual
WHERE ventas <> 0                 -- distinto de
WHERE region = 'Norte' AND ventas > 100    -- las dos condiciones
WHERE region = 'Norte' OR region = 'Sur'   -- cualquiera de las dos
```

> 💡 El texto va entre **comillas simples** (`'Norte'`), los números van sin comillas (`100`).

> ### ▶️ Practica ahora
> Devuelve las ventas de la región `Norte` con monto mayor a 150. ¿Salen muchas o pocas filas?

---

## 4.5 ORDER BY y LIMIT: ordenar y recortar

```sql
SELECT region, producto, ventas
FROM 'ventas_ejemplo.csv'
ORDER BY ventas DESC       -- DESC = de mayor a menor (ASC = menor a mayor, por defecto)
LIMIT 5;                   -- solo las 5 primeras filas del resultado
```

`ORDER BY ... DESC` + `LIMIT` es la receta clásica del **"top N"**: las 5 ventas más altas,
los 10 productos más vendidos, etc.

> ### ▶️ Practica ahora
> Muestra las **10 ventas más altas** del dataset (todas las columnas), ordenadas de mayor
> a menor. Pista: `ORDER BY ventas DESC LIMIT 10`.

---

## 4.6 Contar, sumar, promediar: funciones de agregación

Estas funciones **resumen muchas filas en un solo número**:

```sql
SELECT
    COUNT(*)      AS n_filas,      -- cuántas filas hay
    SUM(ventas)   AS total,        -- suma de todas las ventas
    AVG(ventas)   AS promedio,     -- promedio
    MIN(ventas)   AS minimo,
    MAX(ventas)   AS maximo
FROM 'ventas_ejemplo.csv';
```

> 💡 `COUNT(*)` cuenta filas; `COUNT(ventas)` cuenta solo las que **no son nulas**. Útil para
> detectar datos faltantes.

> ### ▶️ Practica ahora
> En una sola consulta, saca el **número de filas**, el **total** de ventas y el **promedio**.
> Redondea el promedio con `ROUND(AVG(ventas), 2)`.

---

## 4.7 GROUP BY: resumir por categoría

`GROUP BY` es el corazón del análisis: aplica las funciones de arriba **a cada grupo** por
separado. "Ventas totales **por región**", "promedio **por producto**"...

```sql
SELECT region, SUM(ventas) AS total
FROM 'ventas_ejemplo.csv'
GROUP BY region
ORDER BY total DESC;
```

**Regla de oro:** cada columna del `SELECT` que **no** esté dentro de una función de
agregación tiene que estar en el `GROUP BY`.

> ### ▶️ Practica ahora
> Calcula el **total de ventas por región**, ordenado de mayor a menor. ¿Qué región vende más?

---

## 4.8 HAVING: filtrar los grupos

`WHERE` filtra **filas** (antes de agrupar). `HAVING` filtra **grupos** (después de agrupar).

```sql
SELECT region, SUM(ventas) AS total
FROM 'ventas_ejemplo.csv'
GROUP BY region
HAVING SUM(ventas) > 17000;      -- solo las regiones que superan ese total
```

> 💡 No puedes usar `SUM(ventas) > 17000` en el `WHERE`: cuando `WHERE` corre, los grupos aún
> no existen. Para eso está `HAVING`.

> ### ▶️ Practica ahora
> Muestra solo los **canales** cuyo total de ventas supere `23500`. (Agrupa por `canal`,
> filtra con `HAVING`.) ¿Cuántos canales quedan?

---

## 4.9 Alias y columnas calculadas

`AS` le pone **nombre** a una columna del resultado. También puedes calcular columnas nuevas:

```sql
SELECT
    producto,
    ventas,
    ventas * 1.18            AS ventas_con_iva,    -- columna calculada
    descuento * 100          AS descuento_pct
FROM 'ventas_ejemplo.csv';
```

> ### ▶️ Practica ahora
> Crea una columna `ventas_con_iva` (= `ventas * 1.18`) redondeada a 2 decimales y muestra
> `producto`, `ventas` y esa columna nueva para las 5 primeras filas.

---

## 4.10 DISTINCT: valores únicos

```sql
SELECT DISTINCT region FROM 'ventas_ejemplo.csv';          -- las regiones que existen
SELECT COUNT(DISTINCT canal) FROM 'ventas_ejemplo.csv';    -- cuántos canales distintos hay
```

> ### ▶️ Practica ahora
> Averigua **cuántos productos distintos** hay y **cuáles son**. (Dos consultas: una con
> `COUNT(DISTINCT ...)` y otra con `SELECT DISTINCT ...`.)

---

## 4.11 JOIN: combinar tablas de una base de datos

Hasta aquí consultábamos **un solo CSV**. Pero en el mundo real los datos viven repartidos en
**varias tablas** dentro de una base de datos, y `JOIN` es lo que las une. Para practicarlo
con tablas de verdad, crea una pequeña base DuckDB:

```
py crear_db.py        # genera data/tienda.duckdb con 3 tablas
```

Contiene un mini **esquema estrella** (lo verás formalmente en el Módulo 05):

```
   dim_producto            dim_region
   (nombre, categoría)     (zona, responsable)
        \                      /
         \                    /
            ventas   ← tabla de HECHOS (una fila por venta)
```

- **`ventas`** — los hechos: `venta_id, fecha, region, producto, canal, ventas, ...`
- **`dim_producto`** — describe cada producto: `producto, nombre, categoria`
- **`dim_region`** — describe cada región: `region, zona, responsable`

`ventas.producto` (una letra: `A`, `B`...) se conecta con `dim_producto.producto`. Eso es una
**clave común**: la columna por la que unimos.

### Conectarse a la base desde Python

```python
import duckdb
con = duckdb.connect("data/tienda.duckdb")     # abre la base
con.sql("SELECT * FROM ventas LIMIT 5").show()  # ahora las tablas tienen NOMBRE, sin comillas
```

### INNER JOIN: filas que coinciden en ambas tablas

```sql
SELECT v.fecha, v.ventas, p.nombre, p.categoria
FROM ventas v
JOIN dim_producto p ON v.producto = p.producto   -- une donde el producto coincide
LIMIT 10;
```

- `JOIN ... ON <col_izquierda> = <col_derecha>` pega cada venta con su fila de producto.
- `v` y `p` son **alias** (apodos cortos) de cada tabla; `p.nombre` dice "la columna `nombre`
  de la tabla `p`". Con JOINs, **cualifica** siempre las columnas así.
- `JOIN` a secas es un **INNER JOIN**: solo deja las filas con coincidencia en ambos lados.

### LEFT JOIN: conserva todas las filas de la izquierda

```sql
SELECT v.fecha, v.ventas, p.nombre
FROM ventas v
LEFT JOIN dim_producto p ON v.producto = p.producto;
```

`LEFT JOIN` mantiene **todas** las ventas aunque un producto no tenga fila en `dim_producto`
(en ese caso `p.nombre` saldría `NULL`). Es la opción segura cuando no quieres perder filas.

> 💡 Combinas JOIN con todo lo anterior: una vez unidas las tablas, puedes `GROUP BY p.categoria`,
> filtrar con `WHERE`, ordenar... como si fuera una sola tabla.

> ### ▶️ Practica ahora
> Sobre `tienda.duckdb`, une `ventas` con `dim_producto` y calcula el **total de ventas por
> categoría** (`GROUP BY p.categoria`, ordenado de mayor a menor). ¿Vende más `Bebidas` o `Snacks`?

---

## 4.12 El orden de una consulta

Escribes las cláusulas siempre en este orden (memorízalo):

```sql
SELECT   columnas
FROM     tabla
WHERE    condición de filas
GROUP BY categoría
HAVING   condición de grupos
ORDER BY columna
LIMIT    n;
```

No siempre las usas todas, pero cuando aparecen, **van en ese orden**. En el Módulo 05
verás que SQL las *ejecuta* en un orden distinto — pero eso es tema del siguiente módulo.

---

## Reto del módulo (cierre)

Con solo lo de este módulo, responde estas 3 preguntas de negocio, **una consulta cada una**:

1. ¿Cuál es la **región con más ventas** totales?
2. ¿Cuántas ventas superan los **200**?
3. ¿Cuál es el **promedio de ventas por canal**, ordenado de mayor a menor?
4. Con un **JOIN** sobre `tienda.duckdb`: ¿qué **zona** (`dim_region`) vende más en total?

Guarda las 4 consultas en un archivo `.sql` o en tu notebook y haz commit a tu repo.

➡️ Siguiente: [Módulo 05 — SQL moderno](../05-sql-moderno/README.md)
