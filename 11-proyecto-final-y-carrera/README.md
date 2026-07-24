# Módulo 11 — Proyecto final, portafolio y carrera

> **Objetivo:** integrar todo el curso en un proyecto de punta a punta, construir un
> portafolio que consiga entrevistas y trazar tu plan de crecimiento profesional.
>
> 🧭 **Formato:** este módulo es práctico por naturaleza. Cada bloque va seguido de un
> **▶️ Practica ahora** que construye una pieza de tu entregable final.

---

## 10.1 El proyecto final (capstone)

Un proyecto completo que demuestra **todo el ciclo** del Módulo 01:

```
Pregunta de negocio → Datos → SQL/limpieza → EDA/estadística
    → Modelado (dbt) → Visualización/storytelling → App desplegada → IA como apoyo
```

**Requisitos:**
- [ ] Pregunta de negocio clara y relevante.
- [ ] Datos **reales** (Kaggle, datos abiertos, una API).
- [ ] Limpieza documentada (pandas/Polars).
- [ ] Consultas **SQL** con CTEs y window functions (DuckDB).
- [ ] Un **EDA** con estadística, incluyendo qué NO se puede concluir.
- [ ] (Deseable) Modelado con **dbt** (staging → mart + pruebas).
- [ ] **Visualizaciones** con títulos-conclusión y buen diseño.
- [ ] Un **dashboard/app en Streamlit** desplegado.
- [ ] Uso **documentado y verificado** de IA.
- [ ] Un **README** excelente.

> ### ▶️ Practica ahora
> Elige el **tema y la pregunta de negocio** de tu proyecto final (puedes retomar el reto del
> Módulo 01). Consigue el dataset real y guárdalo en `data/raw/`. Escribe la pregunta en el README.

---

## 10.2 Ideas de proyecto por interés

| Interés | Idea |
|---------|------|
| Retail / e-commerce | Ventas, cohortes de clientes, churn |
| Deportes | Rendimiento de equipos/jugadores |
| Salud pública | Tendencias de indicadores por región |
| Finanzas personales | Análisis de gastos, presupuesto |
| Música / cine | Tendencias de streaming, éxito por género |
| Movilidad | Bicis públicas, tráfico (muchos datos abiertos) |

> 💡 Elige un tema que te **apasione**. Se nota en la calidad y en la entrevista hablarás con
> entusiasmo genuino.

> ### ▶️ Practica ahora
> Ejecuta el ciclo completo sobre tu tema: limpieza → SQL → EDA → visualización → app.
> (Reutiliza todo lo que hiciste en los módulos 03–09 sobre tu propio dataset.)

---

## 10.3 El portafolio: tu mejor CV

Los reclutadores valoran **evidencia** por encima de certificados:
- **GitHub** ordenado, con 2–4 proyectos de calidad (no 20 mediocres).
- Cada proyecto con **README de primera**: problema, datos, método, hallazgos, cómo correrlo,
  y **una imagen/GIF** del resultado.
- Al menos un **dashboard desplegado** (URL viva).
- Opcional potente: un blog corto explicando un proyecto.

**README que impresiona:**
```markdown
# Título — [una línea con el resultado clave]
## 🎯 Problema      ## 📊 Datos       ## 🔧 Método
## 💡 Hallazgos     ## 🚀 Demo (URL)  ## ▶️ Cómo ejecutarlo
```

> ⚠️ Error #1 de los portafolios: proyectos que **no se pueden ejecutar** o sin README. Un
> proyecto que nadie puede correr no cuenta.

> ### ▶️ Practica ahora
> Escribe el README de tu proyecto final usando la [plantilla de proyecto](../recursos/plantilla-proyecto.md).
> Incluye una captura de tu dashboard. Verifica tú mismo/a que alguien podría clonarlo y correrlo.

---

## 10.4 Preparación para entrevistas

Las entrevistas de analista suelen tener 4 partes:

1. **SQL** (casi siempre): JOINs, agregaciones, **CTEs y window functions**, "2º más alto",
   variación periodo a periodo. Practica en **StrataScratch**, **DataLemur**, **LeetCode (SQL)**.
2. **Python / datos:** limpieza con pandas, `groupby`, merge.
3. **Caso de negocio:** "Las ventas cayeron 20%, ¿cómo lo investigarías?" Buscan tu
   **estructura de pensamiento** (segmentar, hipótesis, descartar causas).
4. **Comunicación/comportamiento:** "Cuéntame un análisis que hiciste." Usa **STAR**
   (Situación, Tarea, Acción, Resultado) y enfatiza el **impacto**.

> ### ▶️ Practica ahora
> Resuelve **3 ejercicios de SQL** en DataLemur o StrataScratch (nivel medio, con window
> functions). Anota cuáles te costaron para repasarlos.

---

## 10.5 Cómo hablar de tus proyectos

Estructura de 30 segundos:
> "Quise entender **[pregunta]**. Usé **[datos]** y con **[SQL/pandas]** descubrí que
> **[hallazgo con número]**. Lo comuniqué en **[dashboard]** y recomendé **[acción]**, con
> impacto potencial de **[resultado]**."

> ### ▶️ Practica ahora
> Escribe y **di en voz alta** este pitch de 30 segundos para tu proyecto final. Grábate si
> puedes. ¿Suena claro y con impacto?

---

## 10.6 Plan de crecimiento continuo

```
Data Analyst ─┬─► Senior Analyst ──► Analytics Manager / Head of Data
              ├─► Analytics Engineer (dbt, modelado)   ← muy demandado
              ├─► Data Scientist (ML, experimentación)
              └─► Product Analyst / BI specialist
```

**Cómo seguir aprendiendo:** profundiza en 1 área por trimestre, sigue a la comunidad,
replica proyectos open source, enseña lo que aprendes, mantén tu portafolio **vivo**.

**Habilidades blandas que multiplican tu valor:** comunicación, curiosidad de negocio,
rigor (verificar/documentar), colaboración (Git, stakeholders).

> ### ▶️ Practica ahora
> Elige **la próxima habilidad** que profundizarás tras el curso (ej. dbt avanzado, DAX,
> estadística) y define un mini-objetivo para los próximos 3 meses.

---

## 10.7 Checklist final del curso

- [ ] Entorno moderno con uv + Git + GitHub funcionando.
- [ ] Dominio de pandas y nociones de Polars.
- [ ] SQL analítico con CTEs y window functions.
- [ ] EDA y criterio estadístico (correlación ≠ causalidad, A/B, sesgos).
- [ ] Visualización con principios de diseño + storytelling.
- [ ] Entiendo el modern data stack y he tocado dbt.
- [ ] Uso IA con criterio y verificación.
- [ ] Tengo una app de datos desplegada.
- [ ] Portafolio con 2–4 proyectos ejecutables y buenos README.
- [ ] Preparación de entrevistas iniciada.

> ### ▶️ Practica ahora
> Marca honestamente esta checklist. Por cada casilla sin marcar, agenda cuándo la cerrarás.

---

## 🎓 Cierre

Completaste una actualización que te pone en el mapa del análisis de datos moderno: no solo
sabes *sacar números*, sabes construir procesos reproducibles, modelar datos, comunicar con
impacto y apalancarte en la IA sin perder el criterio.

El siguiente paso es simple y difícil a la vez: **construye, publica y comparte**. Tu
portafolio hablará por ti.

¡Éxitos! 🚀

---

*Recursos complementarios: ver la carpeta [`recursos/`](../recursos/).*
