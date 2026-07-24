# Módulo 08 — El Modern Data Stack

> **Objetivo:** entender cómo se organizan los datos en empresas modernas y aprender los
> fundamentos de **dbt**, la herramienta que convirtió a los analistas en *analytics
> engineers*. Foco conceptual + práctica local con DuckDB.
>
> 🧭 **Formato:** cada bloque va seguido de un **▶️ Practica ahora**. Los primeros son de
> reflexión; a partir de dbt, son prácticos. Al final, un **Reto** de cierre.

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

## 7.3 dbt: transformación como código

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

## 7.4 Pruebas y documentación (lo que hace a dbt especial)

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

## 7.5 Practicar dbt localmente (sin cloud)

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

## 7.6 Orquestación (visión general)

Los pipelines deben correr solos, en orden y a tiempo. Herramientas: **Airflow** (el
estándar), **Dagster/Prefect** (modernas), **dbt Cloud** (programa dbt sin infraestructura).

Como analista, al principio basta con **entender el concepto**: un orquestador asegura que
"primero se cargan los datos, luego corre dbt, luego se refresca el dashboard" todos los
días a las 6am, y te avisa si algo falla.

> ### ▶️ Practica ahora
> Escribe la secuencia ordenada de pasos que un orquestador ejecutaría cada mañana para tu
> e-commerce imaginario (mínimo 3 pasos, en orden).

---

## 7.7 Conceptos que oirás

- **Parquet:** formato columnar comprimido, estándar analítico.
- **Iceberg / Delta / Hudi:** formatos de "table" para lakehouses (versionado, transacciones).
- **Data contract:** acuerdo de esquema/calidad entre productor y consumidor de datos.
- **Data catalog:** inventario de datasets (dónde está qué, quién es dueño, qué significa).
- **Reverse ETL:** enviar datos del warehouse de vuelta a herramientas operativas (CRM, ads).

> ### ▶️ Practica ahora
> Elige 2 de estos términos y explícalos con tus palabras en una frase cada uno, como si se
> lo contaras a un compañero.

---

## 7.8 Dónde encaja el analista

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
