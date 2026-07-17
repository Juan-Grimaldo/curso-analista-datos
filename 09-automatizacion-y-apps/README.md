# Módulo 09 — Automatización y apps de datos

> **Objetivo:** dejar de hacer análisis "de una sola vez" y empezar a construir cosas que
> **corren solas** y que otros pueden usar: scripts reutilizables, pipelines y apps con Streamlit.
>
> 🧭 **Formato:** cada bloque va seguido de un **▶️ Practica ahora**. Al final, un **Reto** de cierre.

---

## 9.1 De notebook a producto

Un notebook demuestra un análisis. El valor real aparece cuando ese análisis:
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
        df.drop_duplicates()
          .dropna(subset=["ventas"])
          .assign(region=lambda d: d["region"].str.upper().str.strip())
    )

def agregar_mensual(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.assign(mes=lambda d: d["fecha"].dt.to_period("M"))
          .groupby(["mes", "region"], as_index=False)["ventas"].sum()
    )

def main():
    df = limpiar(cargar("data/raw/ventas_ejemplo.csv"))
    resultado = agregar_mensual(df)
    resultado.to_parquet("data/processed/ventas_mensuales.parquet")
    print(f"✅ Procesadas {len(df)} filas → {len(resultado)} agregadas")

if __name__ == "__main__":
    main()
```

> 💡 Buenas prácticas: funciones pequeñas con un solo propósito, *type hints*, separar
> "cargar / transformar / guardar". Usa `logging` en vez de `print` para procesos serios.

> ### ▶️ Practica ahora
> Convierte tu limpieza del Módulo 03 en un script `src/pipeline.py` con funciones y `main()`.
> Ejecútalo con `uv run python src/pipeline.py` y confirma que genera el Parquet en `data/processed/`.

---

## 9.3 Automatizar la ejecución

- **Windows:** Programador de tareas (Task Scheduler).
- **macOS/Linux:** `cron`.
- **En la nube:** GitHub Actions (gratis para tareas ligeras), Airflow/Dagster (Módulo 07).

```yaml
# .github/workflows/pipeline.yml — corre el pipeline cada día a las 6am
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
      - run: uv run python src/pipeline.py
```

> ### ▶️ Practica ahora
> (Conceptual/opcional) Escribe el `cron` que ejecutaría tu pipeline **todos los lunes a las
> 8am**. Pista: `min hora * * dia_semana`. Verifícalo en [crontab.guru](https://crontab.guru).

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

@st.cache_data
def cargar_datos():
    return pd.read_parquet("data/processed/ventas_mensuales.parquet")

df = cargar_datos()

regiones = st.sidebar.multiselect(
    "Región", options=df["region"].unique(), default=list(df["region"].unique())
)
d = df[df["region"].isin(regiones)]

c1, c2, c3 = st.columns(3)
c1.metric("Ventas totales", f"${d['ventas'].sum():,.0f}")
c2.metric("Regiones", d["region"].nunique())
c3.metric("Ticket promedio", f"${d['ventas'].mean():,.0f}")

fig = px.line(d, x="mes", y="ventas", color="region", title="Evolución por región")
st.plotly_chart(fig, use_container_width=True)
st.dataframe(d, use_container_width=True)
```

Ejecuta: `uv add streamlit plotly` y luego `uv run streamlit run app.py`.

**Componentes útiles:** `st.metric` (KPIs), `st.selectbox`/`st.multiselect`/`st.slider`
(filtros), `st.columns`/`st.tabs` (layout), `st.plotly_chart`/`st.dataframe`/`st.map`
(mostrar), `@st.cache_data` (rendimiento).

> ### ▶️ Practica ahora
> Crea `app.py` con al menos: 1 filtro (multiselect), 2 KPIs (`st.metric`) y 1 gráfico
> interactivo. Lánzala con `uv run streamlit run app.py` y pruébala en el navegador.

---

## 9.5 Compartir tu app

- **Streamlit Community Cloud** — despliegue gratis conectando tu repo de GitHub.
- **Hugging Face Spaces** — otra opción gratuita.

La app queda en una URL pública para tu **portafolio y CV**.

> 💡 Un dashboard desplegado y enlazado en tu CV vale más que diez notebooks que nadie puede ejecutar.

> ### ▶️ Practica ahora
> (Opcional pero recomendado) Sube tu app a Streamlit Community Cloud y obtén su URL pública.
> Añádela al `README.md` de tu proyecto.

---

## 9.6 Otras vías útiles

- **`papermill`** — ejecuta notebooks parametrizados programados.
- **`nbconvert`** — convierte notebooks a HTML/PDF para informes automáticos.
- **`gspread`** — leer/escribir Google Sheets desde Python.
- **`schedule`** — tareas periódicas simples dentro de un script.
- **Email/Slack automáticos** — enviar el informe a un canal (webhooks).

> ### ▶️ Practica ahora
> Elige una de estas herramientas que resolvería una tarea repetitiva tuya (real o
> imaginaria) y describe en 2 frases cómo la usarías.

---

## 9.7 Reproducibilidad: el sello profesional

1. **`pyproject.toml` + `uv.lock`** → dependencias fijas.
2. **`README.md`** → qué hace y cómo ejecutarlo, paso a paso.
3. **Datos por código**, nunca ediciones manuales.
4. **Semillas fijas** (`random_state=42`) donde haya aleatoriedad.
5. **Rutas relativas**, no `C:\Users\tu_nombre\...`.

> ### ▶️ Practica ahora
> Revisa tu proyecto contra estos 5 puntos. ¿Alguna ruta absoluta escondida? ¿El README
> explica cómo correrlo? Corrige lo que falte.

---

## Reto del módulo (cierre)

Convierte tu proyecto del curso en una **app de datos desplegada**: un dashboard de Streamlit
que lea tus datos procesados, con filtros, KPIs y 2–3 gráficos que cuenten la historia del
Módulo 06. Despliégalo y añade la URL a tu README. Entregable de portafolio de primer nivel.

➡️ Siguiente: [Módulo 10 — Proyecto final y carrera](../10-proyecto-final-y-carrera/README.md)
