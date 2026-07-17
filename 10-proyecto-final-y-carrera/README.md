# Módulo 10 — Proyecto final, portafolio y carrera

> **Objetivo:** integrar todo el curso en un proyecto de punta a punta, construir un
> portafolio que consiga entrevistas y trazar tu plan de crecimiento profesional.

---

## 10.1 El proyecto final (capstone)

Un proyecto completo que demuestra **todo el ciclo** del Módulo 01. Debe recorrer:

```
Pregunta de negocio → Datos → SQL/limpieza → EDA/estadística
    → Modelado (dbt) → Visualización/storytelling → App desplegada → IA como apoyo
```

### Requisitos del proyecto

- [ ] Una **pregunta de negocio** clara y relevante.
- [ ] Datos **reales** (Kaggle, datos abiertos, una API pública).
- [ ] Limpieza documentada en un notebook (pandas/Polars).
- [ ] Consultas **SQL** con CTEs y window functions (DuckDB).
- [ ] Un **EDA** con estadística e insights, incluyendo qué NO se puede concluir.
- [ ] (Deseable) Modelado con **dbt** (staging → mart + pruebas).
- [ ] **Visualizaciones** con títulos-conclusión y buen diseño.
- [ ] Un **dashboard/app en Streamlit** desplegado.
- [ ] Uso **documentado y verificado** de IA como apoyo.
- [ ] Un **README** excelente que lo explique todo.

### Ideas de proyecto por interés

| Interés | Idea |
|---------|------|
| Retail / e-commerce | Análisis de ventas, cohortes de clientes, churn |
| Deportes | Rendimiento de equipos/jugadores, predicción de resultados |
| Salud pública | Tendencias de indicadores, comparación entre regiones |
| Finanzas personales | Análisis de gastos, presupuesto, categorización |
| Música / cine | Tendencias de Spotify/streaming, éxito por género |
| Movilidad | Bicis públicas, tráfico, transporte (muchos datos abiertos) |

> 💡 Elige un tema que te **apasione**. Se nota en la calidad del análisis y en la
> entrevista hablarás con entusiasmo genuino.

---

## 10.2 El portafolio: tu mejor CV

Los reclutadores de datos valoran **evidencia** por encima de certificados. Un buen portafolio:

- **GitHub** ordenado, con 2–4 proyectos de calidad (no 20 mediocres).
- Cada proyecto con **README de primera**: problema, datos, método, hallazgos, cómo correrlo,
  y **una imagen o GIF** del resultado.
- Al menos un **dashboard desplegado** (URL viva).
- Opcional pero potente: un blog corto explicando un proyecto (Medium, dev.to, tu web).

### Anatomía de un README de proyecto que impresiona

```markdown
# Título del proyecto — [una línea con el resultado clave]

## 🎯 Problema
Qué pregunta de negocio respondes y por qué importa.

## 📊 Datos
Fuente, tamaño, periodo, cómo se obtuvieron.

## 🔧 Método
Herramientas y pasos: limpieza → SQL → EDA → modelado → viz.

## 💡 Hallazgos clave
- Hallazgo 1 (con número y su implicación).
- Hallazgo 2.
- Hallazgo 3.

## 🚀 Demo
[Enlace al dashboard desplegado] + captura de pantalla.

## ▶️ Cómo ejecutarlo
Pasos con uv. Reproducible de principio a fin.
```

> ⚠️ El error #1 de los portafolios: proyectos que **no se pueden ejecutar** o sin README.
> Un proyecto que nadie puede correr no cuenta.

---

## 10.3 Preparación para entrevistas

Las entrevistas de analista suelen tener 4 partes:

### 1. SQL (casi siempre)
Practica: JOINs, agregaciones, **CTEs y window functions**, encontrar el "2º más alto",
variación periodo a periodo. Plataformas: **StrataScratch**, **DataLemur**, **LeetCode (SQL)**.

### 2. Python / manipulación de datos
Limpieza con pandas, `groupby`, merge, transformaciones. A veces un caso con dataset.

### 3. Caso de negocio / analítico
"Las ventas cayeron 20%, ¿cómo lo investigarías?" Buscan tu **estructura de pensamiento**:
segmentar, formular hipótesis, pedir datos, descartar causas. (Repasa Módulo 05 y 01.)

### 4. Comunicación / comportamiento
"Cuéntame un análisis que hiciste." Usa la estructura **STAR** (Situación, Tarea, Acción,
Resultado) y enfatiza el **impacto** en la decisión.

### Métricas y producto (para roles de producto)
Define una métrica, diseña un A/B test, detecta una métrica engañosa. (Módulo 05.)

---

## 10.4 Cómo hablar de tus proyectos

Estructura de 30 segundos por proyecto:

> "Quise entender **[pregunta]**. Usé **[datos]** y con **[SQL/pandas]** descubrí que
> **[hallazgo con número]**. Lo comuniqué en **[dashboard]** y la recomendación fue
> **[acción]**, con un impacto potencial de **[resultado]**."

Practica esto en voz alta para cada proyecto de tu portafolio.

---

## 10.5 Plan de crecimiento continuo

El campo evoluciona rápido. Rutas típicas desde analista:

```
Data Analyst ─┬─► Senior Analyst ──► Analytics Manager / Head of Data
              ├─► Analytics Engineer (dbt, modelado)   ← muy demandado
              ├─► Data Scientist (ML, experimentación)
              └─► Product Analyst / BI specialist
```

### Cómo seguir aprendiendo

- **Profundiza en 1 área** cada trimestre (ej. dbt, luego estadística avanzada, luego DAX).
- Sigue a la comunidad: newsletters de datos, blogs de ingeniería de empresas.
- Contribuye o replica proyectos open source.
- Enseña lo que aprendes (escribir/explicar consolida el conocimiento).
- Mantén tu portafolio **vivo**: un proyecto nuevo cada pocos meses.

### Habilidades "blandas" que multiplican tu valor

- **Comunicación:** traducir datos a decisiones (Módulo 06).
- **Curiosidad de negocio:** entender *por qué* importa la pregunta.
- **Rigor:** verificar, dudar, documentar.
- **Colaboración:** trabajar con Git, con stakeholders, con feedback.

---

## 10.6 Checklist final del curso

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
