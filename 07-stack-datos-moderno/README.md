# Módulo 07 — El Modern Data Stack

> **Objetivo:** entender cómo se organizan los datos en empresas modernas y aprender los
> fundamentos de **dbt**, la herramienta que convirtió a los analistas en *analytics
> engineers*. Foco conceptual + práctica local.

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
- **Transform (T):** **dbt** transforma esos datos crudos en tablas limpias y modeladas, con SQL.
- **Orquestación:** programa y encadena los procesos (Airflow, Dagster, dbt Cloud).

---

## 7.2 El Data Warehouse

Un **data warehouse** es una base de datos optimizada para **análisis** (no para
transacciones). Los principales:

| Warehouse | Nota |
|-----------|------|
| **BigQuery** (Google) | Serverless, pago por consulta. Muy popular. |
| **Snowflake** | Multi-cloud, separa cómputo y almacenamiento. Estándar empresarial. |
| **Databricks** | Fuerte en datos + ML (lakehouse). |
| **Redshift** (AWS) | El clásico de Amazon. |

### Data Lake vs Warehouse vs Lakehouse

- **Data Lake:** almacena datos crudos de cualquier tipo (barato, flexible, menos estructura).
- **Data Warehouse:** datos estructurados y modelados para análisis (rápido para consultas).
- **Lakehouse:** híbrido que combina ambos (Databricks, formatos como Delta/Iceberg).

> 💡 Como analista no administras el warehouse, pero **consultas** en él y **modelas** dentro
> con dbt. Practicaremos la lógica con **DuckDB** localmente — el SQL es transferible.

---

## 7.3 dbt: transformación como código

**[dbt](https://www.getdbt.com/)** (data build tool) te deja construir tus tablas de análisis
con **SQL + ingeniería de software**: versionado, pruebas, documentación y dependencias.

### La idea central

Escribes modelos como archivos `.sql` que son simplemente un `SELECT`. dbt se encarga de
crear las tablas/vistas y de resolver el orden de dependencias.

```sql
-- models/staging/stg_ventas.sql
-- Limpia y estandariza los datos crudos
SELECT
    id            AS venta_id,
    CAST(fecha AS DATE) AS fecha,
    UPPER(TRIM(region)) AS region,
    producto_id,
    monto
FROM {{ source('raw', 'ventas') }}
WHERE monto IS NOT NULL
```

```sql
-- models/marts/ventas_mensuales.sql
-- Modelo de negocio, construido SOBRE el de staging
WITH ventas AS (
    SELECT * FROM {{ ref('stg_ventas') }}
)
SELECT
    DATE_TRUNC('month', fecha) AS mes,
    region,
    SUM(monto) AS ventas_total,
    COUNT(*)   AS n_ventas
FROM ventas
GROUP BY 1, 2
```

- `{{ source(...) }}` → referencia a datos crudos.
- `{{ ref('stg_ventas') }}` → referencia a otro modelo. dbt construye el **grafo de
  dependencias** automáticamente (DAG).

### Capas de modelado (convención estándar)

```
raw (crudo)  →  staging (limpio, 1:1 con fuente)  →  intermediate  →  marts (negocio)
```

- **staging:** renombrar, castear tipos, limpiar. Un modelo por tabla fuente.
- **marts:** tablas finales orientadas al negocio (ej. `ventas_mensuales`, `dim_clientes`).

### Pruebas y documentación (lo que hace a dbt especial)

```yaml
# models/staging/stg_ventas.yml
models:
  - name: stg_ventas
    columns:
      - name: venta_id
        tests:
          - unique
          - not_null
      - name: region
        tests:
          - accepted_values:
              values: ['NORTE', 'SUR', 'ESTE', 'OESTE']
```

Con `dbt test` verificas la **calidad de los datos automáticamente** en cada ejecución.
Con `dbt docs generate` obtienes documentación navegable con el linaje (*lineage*) de cada tabla.

### Comandos clave

```bash
dbt run      # construye todos los modelos
dbt test     # ejecuta las pruebas de calidad
dbt build    # run + test juntos
dbt docs generate && dbt docs serve   # documentación + linaje
```

---

## 7.4 Practicar dbt localmente (sin cloud)

Puedes aprender dbt en tu máquina con **DuckDB**:

```bash
uv add dbt-core dbt-duckdb
dbt init mi_proyecto_dbt   # crea la estructura
```

Configura DuckDB como destino en `profiles.yml` y ya puedes escribir modelos y correr
`dbt build`. Todo el SQL que aprendiste en el Módulo 04 aplica directo.

> 💡 Esta es la mejor forma de poner **dbt en tu portafolio** sin pagar un warehouse.

---

## 7.5 Orquestación (visión general)

Los pipelines de datos deben correr solos, en orden y a tiempo. Herramientas:

- **Airflow** — el estándar, define pipelines como DAGs en Python.
- **Dagster** / **Prefect** — alternativas modernas, más centradas en datos.
- **dbt Cloud** — programa ejecuciones de dbt sin infraestructura.

Como analista, al principio basta con **entender el concepto**: un orquestador se asegura de
que "primero se cargan los datos, luego corre dbt, luego se refresca el dashboard", todos
los días a las 6am, y te avisa si algo falla.

---

## 7.6 Formatos y conceptos que oirás

- **Parquet:** formato columnar comprimido. El estándar para datos analíticos.
- **Iceberg / Delta / Hudi:** formatos de "table" para lakehouses (versionado, transacciones).
- **Data contract:** acuerdo sobre el esquema y calidad entre quien produce y quien consume datos.
- **Data catalog:** inventario de datasets (dónde está qué, quién lo dueño, qué significa).
- **Reverse ETL:** enviar datos del warehouse de vuelta a herramientas operativas (CRM, ads).

---

## 7.7 Dónde encaja el analista

```
Data Engineer        → construye ingesta e infraestructura
Analytics Engineer   → modela con dbt/SQL (staging → marts)   ← tu crecimiento
Data Analyst         → analiza los marts, hace dashboards e informes  ← tú
```

Aprender dbt te mueve de "consumidor de tablas" a "creador de las tablas confiables de la
empresa". Es la habilidad con mejor relación esfuerzo/impacto en tu carrera ahora mismo.

---

## Ejercicios

1. Explica con tus palabras la diferencia entre **ETL y ELT** y por qué el modern data stack
   prefiere ELT.
2. Dibuja el flujo fuentes → warehouse → dbt → BI para un e-commerce imaginario.
3. Instala `dbt-duckdb`, inicializa un proyecto y crea un modelo `stg_` que limpie tu dataset.
4. Crea un modelo `mart_` que agregue tu `stg_` por una dimensión y un periodo de tiempo.
5. Añade 2 pruebas (`unique`, `not_null`) y ejecuta `dbt build`. Corrige si algo falla.

## Reto del módulo

Monta un mini-proyecto dbt+DuckDB con tu dataset: al menos 1 modelo de staging y 1 mart,
con pruebas y descripciones en el `.yml`. Genera la documentación (`dbt docs`) y captura el
**diagrama de linaje**. Súbelo a tu repo: es oro puro en un portafolio.

➡️ Siguiente: [Módulo 08 — IA generativa aplicada](../08-ia-generativa-aplicada/README.md)
