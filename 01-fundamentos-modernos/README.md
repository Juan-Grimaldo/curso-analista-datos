# Módulo 01 — Fundamentos modernos del análisis de datos

> **Objetivo:** entender el rol del analista hoy, el ciclo de vida del dato y los tipos
> de análisis, con el vocabulario y las herramientas actuales.

---

## 1.1 El rol del analista de datos en 2026

El analista de datos convierte **datos en decisiones**. Lo que ha cambiado es el *cómo*:

| Antes | Ahora |
|-------|-------|
| Excel para todo | Excel para exploración rápida; **Python/SQL** para lo repetible y a escala |
| Datos en archivos locales | Datos en **la nube** (warehouses, lakes) |
| Reportes estáticos | **Dashboards** interactivos y análisis reproducible |
| Trabajo manual | **Automatización** + **IA como copiloto** |
| "Sacar un número" | **Contar una historia** que impulse una acción |

### Roles vecinos (para ubicarte)

- **Data Analyst** — analiza y comunica. *(este curso)*
- **Analytics Engineer** — modela y transforma datos (dbt, SQL) — muy demandado.
- **Data Scientist** — modelado estadístico/ML, experimentación.
- **Data Engineer** — construye pipelines e infraestructura.
- **BI Developer** — especializado en dashboards y semántica de negocio.

> 💡 La frontera más "caliente" hoy es el **Analytics Engineer**: un analista que también
> sabe modelar datos con SQL + dbt. Este curso te lleva en esa dirección.

---

## 1.2 El ciclo de vida del dato

```
Captura → Ingesta → Almacenamiento → Transformación → Análisis → Visualización → Decisión
                                          │
                                     Gobernanza / Calidad (transversal)
```

- **Captura:** eventos, formularios, transacciones, sensores, APIs.
- **Ingesta:** mover datos al sistema (batch o streaming).
- **Almacenamiento:** bases de datos, **data warehouse** (BigQuery, Snowflake), **data lake**.
- **Transformación:** limpiar, unir, agregar (pandas, **dbt**).
- **Análisis:** estadística, EDA, modelos.
- **Visualización/Comunicación:** dashboards, informes, storytelling.
- **Gobernanza:** calidad, seguridad, privacidad, documentación — **transversal**.

---

## 1.3 ELT vs ETL — el cambio clave

El *modern data stack* invirtió el orden clásico:

- **ETL** (Extract → Transform → Load): transformabas *antes* de cargar. Rígido.
- **ELT** (Extract → Load → Transform): cargas los datos crudos al warehouse y
  **transformas dentro** con SQL. Flexible y escalable.

Este cambio es la razón de ser de herramientas como **dbt** (Módulo 07).

---

## 1.4 Los cuatro tipos de análisis

| Tipo | Pregunta | Ejemplo |
|------|----------|---------|
| **Descriptivo** | ¿Qué pasó? | "Las ventas cayeron 8% en junio." |
| **Diagnóstico** | ¿Por qué pasó? | "Cayeron por la baja de un canal." |
| **Predictivo** | ¿Qué pasará? | "Julio caerá otro 5% si no actuamos." |
| **Prescriptivo** | ¿Qué hacer? | "Reactivar el canal X con campaña Y." |

El analista vive sobre todo en **descriptivo y diagnóstico**, y colabora en predictivo.

---

## 1.5 Tipos y estructura de datos

- **Estructurados:** tablas (SQL, CSV). La mayoría de tu trabajo.
- **Semiestructurados:** JSON, XML, logs. Cada vez más comunes (APIs).
- **No estructurados:** texto libre, imágenes, audio. La IA los volvió analizables.

### Datos *tidy* (ordenados) — un principio fundamental

Un dataset está **tidy** cuando:
1. Cada **variable** es una columna.
2. Cada **observación** es una fila.
3. Cada **tipo de unidad observacional** es una tabla.

```
❌ NO tidy (ancho, valores en cabeceras)
| producto | ene | feb | mar |
|----------|-----|-----|-----|
| A        | 10  | 12  | 9   |

✅ Tidy (largo)
| producto | mes | ventas |
|----------|-----|--------|
| A        | ene | 10     |
| A        | feb | 12     |
| A        | mar | 9      |
```

El formato *tidy* hace que agrupar, filtrar y graficar sea trivial. Lo usaremos siempre.

---

## 1.6 Métricas, KPIs y dimensiones

- **Métrica:** un número medible (ventas, usuarios, tiempo).
- **KPI:** una métrica *clave* atada a un objetivo de negocio.
- **Dimensión:** el "por qué/dónde/cuándo" con el que cortas una métrica (región, mes, canal).

> Una buena métrica es **específica, comparable y accionable**. Cuidado con las
> *vanity metrics* (métricas de vanidad) que se ven bien pero no guían decisiones.

---

## 1.7 Calidad y gobernanza de datos

Antes de analizar, pregunta por la **calidad**:

- **Completitud:** ¿faltan valores?
- **Exactitud:** ¿los valores son correctos?
- **Consistencia:** ¿el mismo dato coincide en distintas fuentes?
- **Puntualidad:** ¿está actualizado?
- **Unicidad:** ¿hay duplicados?

Y por la **gobernanza / ética**:

- **Privacidad:** GDPR, datos personales (PII). No analices lo que no debes.
- **Sesgo:** los datos reflejan sesgos del mundo real; cuestiónalos.
- **Trazabilidad:** documenta de dónde viene cada número (*data lineage*).

---

## Ejercicios

1. Para tu trabajo o un negocio que conozcas, escribe **una pregunta de negocio** de cada
   tipo (descriptiva, diagnóstica, predictiva, prescriptiva).
2. Toma esta tabla ancha y descríbela en formato **tidy** (en papel o texto):
   `| tienda | q1_2025 | q2_2025 | q3_2025 |`
3. Lista **3 KPIs** de un e-commerce y, para cada uno, **2 dimensiones** con las que lo cortarías.
4. Identifica un caso donde un dato "correcto" podría llevar a una conclusión **sesgada**.

## Reto del módulo

Elige un dominio que te interese (deportes, salud, retail, música...). Escribe una página
que incluya: la pregunta de negocio principal, los datos que necesitarías, dónde vivirían
(fuente/almacenamiento), y qué decisión buscarías impulsar. Guárdalo: será candidato a tu
**proyecto final**.

➡️ Siguiente: [Módulo 02 — Entorno y Git](../02-entorno-y-git/README.md)
