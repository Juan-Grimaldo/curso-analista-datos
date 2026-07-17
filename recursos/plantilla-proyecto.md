# 📋 Plantilla de proyecto de análisis

Copia este archivo como `README.md` de tu proyecto y complétalo.

---

# [Título del proyecto] — [una línea con el resultado clave]

> Ejemplo: "Análisis de churn en e-commerce — identifico el 20% de clientes que genera el 80% de las bajas."

## 🎯 Problema / Pregunta de negocio
Describe qué pregunta respondes y por qué importa. ¿Qué decisión ayuda a tomar?

## 📊 Datos
- **Fuente:** (Kaggle / API / datos abiertos / …) con enlace.
- **Tamaño:** N filas × M columnas.
- **Periodo:** fechas cubiertas.
- **Diccionario de datos:** breve descripción de las columnas clave.

## 🔧 Método
1. **Obtención / carga** — cómo llegaron los datos.
2. **Limpieza** — decisiones principales (nulos, duplicados, tipos).
3. **Transformación / SQL** — modelado, agregaciones, window functions.
4. **Análisis / EDA** — estadística, relaciones, hallazgos.
5. **Visualización** — qué gráficos y por qué.

## 💡 Hallazgos clave
- **Hallazgo 1:** [con número]. Implicación: […].
- **Hallazgo 2:** […].
- **Hallazgo 3:** […].

## ⚠️ Limitaciones
Qué NO se puede concluir con estos datos y por qué (sesgos, tamaño de muestra, causalidad).

## 🚀 Demo
[Enlace al dashboard desplegado] · Captura de pantalla:

![captura](reports/dashboard.png)

## ▶️ Cómo ejecutarlo
```bash
git clone <repo>
cd <proyecto>
uv sync
uv run python src/pipeline.py
uv run streamlit run app.py
```

## 🧰 Stack usado
Python · pandas/Polars · DuckDB/SQL · dbt · seaborn/plotly · Streamlit · Git

## 📁 Estructura
```
proyecto/
├── data/{raw,processed}/
├── notebooks/
├── src/
├── reports/
├── app.py
└── README.md
```

---

## Rúbrica de autoevaluación (0–3 cada una)
- [ ] Pregunta de negocio clara y relevante
- [ ] Limpieza documentada y reproducible
- [ ] SQL con CTEs / window functions
- [ ] EDA con criterio estadístico
- [ ] Visualizaciones bien diseñadas (título-conclusión)
- [ ] Storytelling: contexto → hallazgo → recomendación
- [ ] App/dashboard desplegado
- [ ] README excelente y proyecto ejecutable

**Objetivo:** ≥ 20/24 para nivel portafolio.
