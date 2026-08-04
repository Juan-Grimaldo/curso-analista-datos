# Módulo 08 — El Modern Data Stack

> **Objetivo:** entender cómo se organizan los datos en empresas modernas: las plataformas
> cloud (**Snowflake, BigQuery, Databricks**), las herramientas de transformación y
> orquestación (**dbt, Airflow, KNIME, Alteryx**) y, sobre todo, los fundamentos de **dbt**,
> la herramienta que convirtió a los analistas en *analytics engineers*. Foco conceptual +
> práctica local con DuckDB.
>
> 🔗 El pipeline ELT que construiste con SQL en el [Módulo 05](../05-sql-moderno/README.md)
> es exactamente lo que aquí automatizarás con dbt: mismo patrón `raw → staging → marts`,
> mismos tests, pero declarado y versionado.
>
> 🧭 **Formato:** cada bloque va seguido de un **▶️ Practica ahora**. Los primeros son de
> reflexión; a partir de dbt, son prácticos. Al final, un **Reto** de cierre.
>
> 📂 **Dónde practicas:** este README es solo la **teoría**. Todo lo que hagas (el proyecto
> dbt, los modelos SQL) va en tu **repo de práctica** `curso-datos`.

---

## 7.1 ¿Qué es el "modern data stack"?

Es el conjunto de herramientas cloud, modulares y basadas en SQL que reemplazó a los
sistemas monolíticos. Su columna vertebral es el **ELT** (Módulo 01):

```
   FUENTES              INGESTA         WAREHOUSE          TRANSFORMACIÓN      CONSUMO
┌───────────┐        ┌──────────┐   ┌───────────────┐   ┌───────────┐   ┌──────────────┐
│ Apps, DBs │        │ Fivetran │   │  BigQuery /   │   │           │   │ Power BI /   │
│ SaaS, APIs│ ─────► │ Airbyte  │─► │  Snowflake /  │─► │    dbt    │─► │ Tableau /    │
│ Archivos  │        │ (EL)     │   │  Databricks   │   │   (T)     │   │ notebooks    │
└───────────┘        └──────────┘   └───────────────┘   └───────────┘   └──────────────┘
                                            │
                                     Orquestación (Airflow / Dagster / dbt Cloud)
```

- **Extract + Load (EL):** herramientas como Fivetran/Airbyte copian datos crudos al warehouse.
- **Transform (T):** **dbt** transforma esos datos crudos con SQL.
- **Orquestación:** programa y encadena los procesos.

> ### ▶️ Practica ahora
> Dibuja (a mano o en texto) el flujo fuentes → warehouse → dbt → BI para un **e-commerce
> imaginario**. Nombra al menos una fuente concreta (ej. Shopify) y una herramienta de BI.

---

## 7.2 El Data Warehouse

Un **data warehouse** es una base de datos optimizada para **análisis** (no para
transacciones).

| Warehouse | Nota |
|-----------|------|
| **BigQuery** (Google) | Serverless, pago por consulta. |
| **Snowflake** | Multi-cloud, separa cómputo y almacenamiento. |
| **Databricks** | Fuerte en datos + ML (lakehouse). |
| **Redshift** (AWS) | El clásico de Amazon. |

**Lake vs Warehouse vs Lakehouse:**
- **Data Lake:** datos crudos de cualquier tipo (barato, flexible).
- **Data Warehouse:** datos estructurados y modelados (rápido para consultas).
- **Lakehouse:** híbrido (Databricks; formatos Delta/Iceberg).

> 💡 Como analista no administras el warehouse, pero **consultas** y **modelas** dentro con
> dbt. Practicaremos la lógica con **DuckDB** — el SQL es transferible.

> ### ▶️ Practica ahora
> En una frase, explica cuándo usarías un **data lake** y cuándo un **data warehouse** para
> guardar: (a) logs crudos de una app, (b) la tabla final de ventas para el dashboard.

---

## 7.3 Las tres plataformas cloud que verás en las ofertas

"Se valorará experiencia en Snowflake, BigQuery y/o Databricks" aparece en casi todas las
ofertas de analista. Esto es lo que necesitas saber para entenderlas — y para hablar de
ellas con criterio en una entrevista.

| | **Snowflake** | **BigQuery** (Google Cloud) | **Databricks** |
|---|---|---|---|
| Qué es | Data warehouse en la nube, funciona igual sobre AWS, Azure o GCP | Warehouse *serverless*: no administras nada, solo consultas | *Lakehouse*: datos + ingeniería + ML en el mismo sitio |
| Cómo pagas | Por **segundos de cómputo** del *warehouse* encendido (se escala a mano: XS, S, M…) | Por **bytes leídos** en cada consulta (o por capacidad reservada) | Por cómputo del clúster (DBUs) + almacenamiento |
| Optimizar significa | Consultas cortas, aprovechar la caché de resultados, *cluster keys* en tablas grandes | Particionar por fecha, *clustering*, y **jamás** `SELECT *` sobre una tabla enorme | `OPTIMIZE` y `Z-ORDER` sobre tablas Delta, evitar millones de ficheros pequeños |
| Formato de datos | Micro-particiones propias | Almacenamiento columnar propio | **Delta Lake** (Parquet + un log de transacciones) |
| Su gracia | *Time travel* (consultar la tabla como estaba hace 3 días), clonado sin copiar datos | Cero administración; datasets públicos gigantes; integración nativa con el ecosistema Google | SQL, Python y Spark conviven; es la opción cuando hay ML de por medio |
| Lo típico del analista | Escribir SQL y modelos dbt sobre esquemas ya cargados | Consultar tablas particionadas y alimentar Looker Studio | Usar *SQL warehouses* y notebooks sobre tablas Delta |

**Lo que de verdad cambia para ti:** casi nada del SQL. Cambian el **modelo de coste** (y
por tanto qué es "una consulta bien escrita"), los nombres de las tablas y algunas
funciones de fecha. El Módulo 05 (sección 4.20) tiene la tabla de equivalencias de
dialecto.

**Los tres conceptos que sí debes entender de cualquier plataforma cloud:**

1. **Separación de cómputo y almacenamiento.** Los datos viven en un sitio barato; la
   potencia de cálculo se enciende cuando la necesitas. Por eso puedes tener 10 años de
   histórico sin arruinarte, y por eso una consulta descuidada sí cuesta dinero.
2. **Elasticidad.** Si mañana necesitas 10× potencia, la pides. No hay que comprar
   servidores.
3. **Gobernanza.** Permisos por esquema/tabla/columna, enmascarado de datos personales y
   registro de quién consultó qué. En una empresa, tú serás un *rol* con permisos de
   lectura sobre unos esquemas concretos.

> ### ▶️ Practica ahora
> Entra en la [consola de BigQuery](https://console.cloud.google.com/bigquery) (capa
> gratuita: 1 TB de consultas al mes) y ejecuta una consulta sobre un **dataset público**
> (por ejemplo `bigquery-public-data.london_bicycles`). Antes de darle a "Ejecutar", mira
> el estimador de **bytes procesados** que muestra arriba a la derecha; luego quita
> columnas del `SELECT` y observa cómo baja. Eso es tu factura, en directo.

---

## 7.4 dbt: transformación como código

**[dbt](https://www.getdbt.com/)** te deja construir tus tablas de análisis con **SQL +
ingeniería de software**: versionado, pruebas, documentación y dependencias.

Escribes modelos como archivos `.sql` que son un `SELECT`. dbt crea las tablas/vistas y
resuelve el orden de dependencias.

```sql
-- models/staging/stg_ventas.sql  (limpia y estandariza el crudo)
SELECT
    venta_id,
    CAST(fecha AS DATE)  AS fecha,
    UPPER(TRIM(region))  AS region,
    producto,
    ventas
FROM {{ source('raw', 'ventas') }}
WHERE ventas IS NOT NULL
```

```sql
-- models/marts/ventas_mensuales.sql  (modelo de negocio sobre staging)
WITH ventas AS ( SELECT * FROM {{ ref('stg_ventas') }} )
SELECT
    DATE_TRUNC('month', fecha) AS mes,
    region,
    SUM(ventas) AS ventas_total,
    COUNT(*)    AS n_ventas
FROM ventas
GROUP BY 1, 2
```

- `{{ source(...) }}` → datos crudos. `{{ ref('stg_ventas') }}` → otro modelo.
  dbt construye el **grafo de dependencias** (DAG) automáticamente.

**Capas de modelado (convención):**
```
raw → staging (limpio, 1:1 con fuente) → intermediate → marts (negocio)
```

> ### ▶️ Practica ahora
> Sin instalar nada aún: escribe en papel qué haría un modelo `stg_ventas` para tu dataset
> (qué columnas renombrarías/castearías/limpiarías). Es el paso previo a programarlo.

---

## 7.5 Pruebas y documentación (lo que hace a dbt especial)

```yaml
# models/staging/stg_ventas.yml
models:
  - name: stg_ventas
    columns:
      - name: venta_id
        tests: [unique, not_null]
      - name: region
        tests:
          - accepted_values:
              values: ['NORTE', 'SUR', 'ESTE', 'OESTE']
```

Con `dbt test` verificas la **calidad de los datos automáticamente**. Con `dbt docs generate`
obtienes documentación navegable con el **linaje** de cada tabla.

**Comandos clave:** `dbt run` (construye), `dbt test` (prueba), `dbt build` (ambos),
`dbt docs generate && dbt docs serve` (documentación + linaje).

> ### ▶️ Practica ahora
> Piensa 2 pruebas de calidad para tu dataset (ej. `venta_id` es `unique` y `not_null`;
> `region` solo tiene valores válidos). Escríbelas mentalmente en el formato YAML de arriba.

---

## 7.6 Practicar dbt localmente (sin cloud)

Puedes aprender dbt en tu máquina con **DuckDB**:

```bash
uv add dbt-core dbt-duckdb
dbt init mi_proyecto_dbt   # crea la estructura
```

Configura DuckDB como destino en `profiles.yml` y ya puedes escribir modelos y correr
`dbt build`. Todo el SQL de los Módulos 04 y 05 aplica directo.

> 💡 Esta es la mejor forma de poner **dbt en tu portafolio** sin pagar un warehouse.

> ### ▶️ Practica ahora
> Instala `dbt-duckdb`, ejecuta `dbt init`, y crea tu primer modelo `stg_ventas.sql` que
> limpie `ventas_ejemplo.csv`. Corre `dbt run` y verifica que se crea la tabla.

---

## 7.7 Orquestación: que el pipeline corra solo

Los pipelines deben correr solos, en orden y a tiempo. Un orquestador ejecuta un **DAG**
(grafo de tareas con dependencias): "primero carga los datos, luego corre dbt, luego
refresca el dashboard", todos los días a las 6am — y te avisa si algo falla.

| Herramienta | Cómo es | Nota |
|-------------|---------|------|
| **Apache Airflow** | El estándar de la industria. DAGs escritos en Python | Si una oferta menciona orquestación, casi seguro es Airflow |
| **Dagster** | Moderno, orientado a *assets* (piensa en tablas, no en tareas) | Muy buena integración con dbt |
| **Prefect** | Ligero, se parece a escribir Python normal | Curva de entrada más suave |
| **dbt Cloud** | Programa tus `dbt build` sin montar infraestructura | Suficiente para muchos equipos de analítica |

```python
# Un DAG de Airflow, en esencia: tareas + el orden entre ellas
extraer >> cargar_raw >> dbt_build >> tests_calidad >> refrescar_dashboard
```

Lo que un orquestador te da (y un `cron` no): **reintentos** automáticos, **alertas**
cuando algo falla, ejecución de tareas en paralelo, *backfills* (recalcular el pasado) y un
historial de qué corrió, cuándo y en cuánto tiempo.

Como analista no vas a administrarlo, pero sí verás su interfaz para responder a la
pregunta más habitual del mundo: *"¿por qué el dashboard tiene los datos de ayer?"*.

> ### ▶️ Practica ahora
> Escribe la secuencia ordenada de pasos que un orquestador ejecutaría cada mañana para tu
> e-commerce imaginario (mínimo 3 pasos, en orden) e indica **qué debería pasar si el paso
> 2 falla**: ¿se ejecutan los siguientes? ¿a quién se avisa?

---

## 7.8 El mapa de herramientas de preparación y transformación

Las ofertas piden "familiaridad con herramientas de transformación o preparación de datos"
y luego enumeran cosas que hacen trabajos muy distintos. Este es el mapa:

| Fase | Herramientas | Qué son |
|------|--------------|---------|
| **Ingesta (EL)** | Fivetran, Airbyte, **Snowflake Openflow** | Conectores ya hechos que copian datos de un origen (Salesforce, Postgres, S3, APIs) al warehouse. Openflow es el servicio de ingesta de Snowflake, construido sobre Apache NiFi, para mover datos —incluidos los no estructurados— hacia Snowflake |
| **Transformación con código** | **dbt**, SQLMesh | SQL + Git + pruebas + linaje. El estándar del ELT moderno |
| **Transformación visual (low-code)** | **KNIME**, **Alteryx**, Power Query, Talend | Construyes el flujo arrastrando **nodos** en un lienzo, sin escribir código |
| **Orquestación** | Airflow, Dagster, Prefect, dbt Cloud | Ejecutan lo anterior en orden y a su hora |
| **Calidad de datos** | dbt tests, Great Expectations, Soda | Comprueban que el dato cumple lo que promete |

**KNIME vs Alteryx vs dbt** — la comparación que de verdad importa:

| | KNIME | Alteryx | dbt |
|---|-------|---------|-----|
| Cómo trabajas | Nodos en un lienzo | Nodos en un lienzo | Archivos `.sql` en Git |
| Licencia | Gratuito (Analytics Platform) | Comercial, caro | Open source (dbt Core) |
| Filosofía | **ETL**: transformas fuera y cargas el resultado | **ETL** | **ELT**: transformas dentro del warehouse |
| Fuerte en | Prototipar rápido, análisis de negocio, algo de ML | Equipos de negocio con procesos complejos y sin programadores | Equipos de datos que quieren versionado, pruebas y linaje |
| Su límite | El flujo visual crece y se vuelve difícil de revisar y versionar | Lo mismo, más el coste de licencia | Requiere saber SQL y Git |

> 💡 Cómo elegir en la vida real: si el dato ya está (o puede estar) en un warehouse,
> **dbt**. Si el proceso lo mantiene gente de negocio que no programa, o hay que tocar
> archivos locales, Excel y sistemas sueltos, una herramienta visual tipo **KNIME** o
> **Alteryx** hace el trabajo antes.

**Lo que aprendes en este curso te vale para las tres.** Un nodo "Joiner" de KNIME es un
`JOIN`; un nodo "Filter" es un `WHERE`; un "GroupBy" es un `GROUP BY`. Y el problema del
*fan-out* del Módulo 05 te muerde exactamente igual en un lienzo visual que en SQL. Por eso
el orden correcto es aprender **los conceptos y SQL primero**, y la herramienta después: la
herramienta se aprende en una semana.

> ### ▶️ Practica ahora
> Coge el pipeline que montaste en el Módulo 05 (`raw → staging → marts` + tests) y
> **dibújalo como un flujo de nodos**: una caja por paso y flechas entre ellas. Etiqueta
> cada caja con la operación SQL que hace. Acabas de traducir tu pipeline al lenguaje de
> KNIME/Alteryx — y esa misma imagen es lo que enseñarás en una entrevista.

---

## 7.9 Conceptos que oirás

- **Parquet:** formato columnar comprimido, estándar analítico.
- **Iceberg / Delta / Hudi:** formatos de "table" para lakehouses (versionado, transacciones).
- **Data contract:** acuerdo de esquema/calidad entre productor y consumidor de datos.
- **Data catalog:** inventario de datasets (dónde está qué, quién es dueño, qué significa).
- **Reverse ETL:** enviar datos del warehouse de vuelta a herramientas operativas (CRM, ads).

> ### ▶️ Practica ahora
> Elige 2 de estos términos y explícalos con tus palabras en una frase cada uno, como si se
> lo contaras a un compañero.

---

## 7.10 Dónde encaja el analista

```
Data Engineer        → construye ingesta e infraestructura
Analytics Engineer   → modela con dbt/SQL (staging → marts)   ← tu crecimiento
Data Analyst         → analiza los marts, dashboards e informes  ← tú
```

Aprender dbt te mueve de "consumidor de tablas" a "creador de las tablas confiables". Es la
habilidad con mejor relación esfuerzo/impacto en tu carrera ahora mismo.

---

## Reto del módulo (cierre)

Monta un mini-proyecto **dbt + DuckDB** con tu dataset: al menos 1 modelo de staging y 1
mart, con 2 pruebas y descripciones en el `.yml`. Genera la documentación (`dbt docs`) y
captura el **diagrama de linaje**. Súbelo a tu repo: es oro puro en un portafolio.

➡️ Siguiente: [Módulo 09 — IA generativa aplicada](../09-ia-generativa-aplicada/README.md)
