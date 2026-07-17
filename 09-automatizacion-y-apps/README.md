# Módulo 09 — Automatización y apps de datos

> **Objetivo:** dejar de hacer análisis "de una sola vez" y empezar a construir cosas que
> **corren solas** y que otros pueden usar: scripts reutilizables, pipelines y apps
> interactivas con Streamlit.

---

## 9.1 De notebook a producto

Un notebook demuestra un análisis. Pero el valor real aparece cuando ese análisis:

- **Se repite solo** (cada día/semana) → automatización.
- **Lo usan otros** sin saber programar → una app/dashboard.

Este módulo te lleva de "hice un análisis" a "construí algo que se usa".

---

## 9.2 De notebook a script reutilizable

Refactoriza tu notebook en funciones dentro de un `.py`:

```python
# src/pipeline_ventas.py
import pandas as pd

def cargar(ruta: str) -> pd.DataFrame:
    return pd.read_csv(ruta, parse_dates=["fecha"])

def limpiar(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df
        .drop_duplicates()
        .dropna(subset=["ventas"])
        .assign(region=lambda d: d["region"].str.upper().str.strip())
    )

def agregar_mensual(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.assign(mes=lambda d: d["fecha"].dt.to_period("M"))
          .groupby(["mes", "region"], as_index=False)["ventas"].sum()
    )

def main():
    df = cargar("data/raw/ventas.csv")
    df = limpiar(df)
    resultado = agregar_mensual(df)
    resultado.to_parquet("data/processed/ventas_mensuales.parquet")
    print(f"✅ Procesadas {len(df)} filas → {len(resultado)} agregadas")

if __name__ == "__main__":
    main()
```

Ejecútalo con `uv run python src/pipeline_ventas.py`. Ahora es **reproducible y automatizable**.

> 💡 Buenas prácticas: funciones pequeñas con un solo propósito, *type hints*, y separar
> "cargar / transformar / guardar". Añade `logging` en vez de `print` para procesos serios.

---

## 9.3 Automatizar la ejecución

- **Windows:** Programador de tareas (Task Scheduler).
- **macOS/Linux:** `cron` (`crontab -e`).
- **En la nube:** GitHub Actions (gratis para tareas ligeras), Airflow/Dagster (Módulo 07).

Ejemplo de GitHub Actions (corre el pipeline cada día a las 6am):

```yaml
# .github/workflows/pipeline.yml
name: Pipeline diario
on:
  schedule:
    - cron: "0 6 * * *"
  workflow_dispatch:          # permite ejecutarlo a mano
jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - run: uv run python src/pipeline_ventas.py
```

---

## 9.4 Streamlit: apps de datos con solo Python

**[Streamlit](https://streamlit.io/)** convierte un script de Python en una app web
interactiva. Ideal para dashboards y prototipos sin saber front-end.

```python
# app.py
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard de Ventas", layout="wide")
st.title("📊 Dashboard de Ventas 2026")

@st.cache_data                      # cachea la carga (rápido)
def cargar_datos():
    return pd.read_parquet("data/processed/ventas_mensuales.parquet")

df = cargar_datos()

# --- Filtros en la barra lateral ---
regiones = st.sidebar.multiselect(
    "Región", options=df["region"].unique(), default=list(df["region"].unique())
)
df_filtrado = df[df["region"].isin(regiones)]

# --- KPIs ---
col1, col2, col3 = st.columns(3)
col1.metric("Ventas totales", f"${df_filtrado['ventas'].sum():,.0f}")
col2.metric("Regiones", df_filtrado["region"].nunique())
col3.metric("Ticket promedio", f"${df_filtrado['ventas'].mean():,.0f}")

# --- Gráfico ---
fig = px.line(df_filtrado, x="mes", y="ventas", color="region",
              title="Evolución de ventas por región")
st.plotly_chart(fig, use_container_width=True)

# --- Tabla ---
st.dataframe(df_filtrado, use_container_width=True)
```

Ejecuta:
```bash
uv add streamlit plotly
uv run streamlit run app.py
```

En segundos tienes un dashboard con filtros, KPIs y gráficos interactivos. Los conceptos de
diseño del **Módulo 06** aplican igual.

### Componentes útiles de Streamlit

- `st.metric` → KPIs (big numbers).
- `st.selectbox` / `st.multiselect` / `st.slider` / `st.date_input` → filtros.
- `st.columns` / `st.tabs` → layout.
- `st.dataframe` / `st.plotly_chart` / `st.map` → mostrar datos.
- `@st.cache_data` → rendimiento.

---

## 9.5 Compartir tu app

- **Streamlit Community Cloud** — despliegue gratis conectando tu repo de GitHub.
- **Hugging Face Spaces** — otra opción gratuita.
- La app queda en una URL pública que puedes poner en tu **portafolio y CV**.

> 💡 Un dashboard de Streamlit desplegado y enlazado en tu CV vale más que diez notebooks
> que nadie puede ejecutar.

---

## 9.6 Otras vías de automatización útiles

- **`papermill`** — ejecuta notebooks parametrizados de forma programada.
- **`nbconvert`** — convierte notebooks a HTML/PDF para informes automáticos.
- **Google Sheets API / `gspread`** — leer/escribir hojas de cálculo desde Python.
- **`schedule` (librería)** — tareas periódicas simples dentro de un script Python.
- **Email/Slack automáticos** — enviar el informe generado a un canal (con webhooks).

---

## 9.7 Reproducibilidad: el sello profesional

Para que cualquiera (incluido tu yo futuro) pueda correr tu proyecto:

1. **`pyproject.toml` + `uv.lock`** → dependencias fijas.
2. **`README.md`** → qué hace y cómo ejecutarlo, paso a paso.
3. **Datos por código**, nunca ediciones manuales.
4. **Semillas fijas** (`random_state=42`) donde haya aleatoriedad.
5. **Rutas relativas**, no `C:\Users\tu_nombre\...`.

---

## Ejercicios

1. Refactoriza un notebook previo en un script `src/pipeline.py` con funciones y `main()`.
2. Ejecútalo con `uv run` y verifica que genera el Parquet en `data/processed/`.
3. Crea una app de Streamlit con al menos: 1 filtro, 2 KPIs y 1 gráfico interactivo.
4. Añade `@st.cache_data` y comprueba la mejora de velocidad.
5. (Opcional) Despliega la app en Streamlit Community Cloud y obtén su URL.

## Reto del módulo

Convierte tu proyecto del curso en una **app de datos desplegada**: un dashboard de Streamlit
que lea tus datos procesados, con filtros, KPIs y 2–3 gráficos que cuenten la historia del
Módulo 06. Despliégalo y añade la URL a tu README. Esto es un entregable de portafolio de
primer nivel.

➡️ Siguiente: [Módulo 10 — Proyecto final y carrera](../10-proyecto-final-y-carrera/README.md)
