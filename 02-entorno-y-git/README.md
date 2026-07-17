# Módulo 02 — Entorno moderno y control de versiones

> **Objetivo:** montar un entorno de análisis profesional, reproducible y versionado.
> Terminarás con Python instalado, un entorno aislado, Jupyter funcionando y tu primer
> repositorio en GitHub.

---

## 2.1 Por qué esto importa

El 80% de la frustración de quien empieza viene del **entorno**, no del análisis.
Un entorno bien montado te da tres superpoderes:

- **Reproducibilidad:** que tu análisis corra igual hoy y en otra máquina.
- **Aislamiento:** que un proyecto no rompa a otro (dependencias).
- **Versionado:** poder volver atrás y colaborar sin pisar el trabajo de nadie.

---

## 2.2 Instalar Python moderno con `uv`

En 2026 la forma recomendada de gestionar Python y dependencias es **[uv](https://docs.astral.sh/uv/)**
(de Astral): rapidísimo y reemplaza a `pip`, `venv`, `pyenv` y `poetry` a la vez.

### Instalación

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Verifica:
```bash
uv --version
```

### Crear tu primer proyecto

```bash
uv init curso-datos
cd curso-datos
uv add pandas polars numpy matplotlib seaborn plotly jupyter scikit-learn statsmodels duckdb
```

`uv` crea automáticamente:
- Un entorno virtual aislado (`.venv`).
- Un `pyproject.toml` con tus dependencias.
- Un `uv.lock` que **fija versiones exactas** (reproducibilidad).

Para ejecutar algo dentro del entorno:
```bash
uv run python mi_script.py
uv run jupyter lab
```

> 💡 Alternativa clásica: `python -m venv .venv` + `pip install`. Funciona, pero `uv` es
> más rápido y fiable. Si tu empresa usa Anaconda/conda, también es válido.

---

## 2.3 El editor: VS Code

Descarga **[Visual Studio Code](https://code.visualstudio.com/)** e instala estas extensiones:

- **Python** (Microsoft)
- **Jupyter**
- **Ruff** (linter/formateador rápido)
- **GitLens** (Git visual)
- Opcional: un asistente de IA (Copilot, Claude, etc.)

Abre la carpeta del proyecto con `code .`.

---

## 2.4 Notebooks vs scripts

- **Jupyter Notebook (`.ipynb`):** ideal para **explorar** — ejecutas celda a celda y ves
  resultados al instante. Perfecto para EDA.
- **Scripts (`.py`):** ideal para **producción** — código reutilizable, automatizable, testeable.

Regla práctica: **explora en notebook, consolida en script**.

Lanza Jupyter:
```bash
uv run jupyter lab
```

### Tu primera celda

```python
import pandas as pd
import numpy as np

print(f"pandas {pd.__version__}")
df = pd.DataFrame({"ciudad": ["Madrid", "Lima", "Bogotá"], "ventas": [120, 95, 140]})
df
```

---

## 2.5 Git: control de versiones

**Git** es un sistema que guarda el historial de tus cambios. **GitHub** es la nube donde
lo publicas y colaboras. Es una habilidad **no negociable** para un analista moderno.

### Configuración inicial (una sola vez)

```bash
git config --global user.name "Tu Nombre"
git config --global user.email "tu@email.com"
git config --global init.defaultBranch main
```

### El flujo básico

```bash
git init                      # inicializa el repo
git add .                     # prepara los cambios (staging)
git commit -m "Primer commit" # guarda una foto del proyecto
git log --oneline             # ve el historial
```

Piensa en `commit` como un **punto de guardado** de un videojuego.

### Conceptos clave

| Concepto | Qué es |
|----------|--------|
| **Repositorio** | La carpeta del proyecto con su historial |
| **Commit** | Una instantánea guardada con un mensaje |
| **Branch** | Una línea de trabajo paralela (`main`, `feature-x`) |
| **Remote** | La copia en la nube (GitHub) |
| **Push / Pull** | Subir / bajar cambios al remoto |

### El archivo `.gitignore`

Nunca subas datos sensibles, entornos ni credenciales. Crea `.gitignore`:

```gitignore
.venv/
__pycache__/
.ipynb_checkpoints/
*.env
.DS_Store
data/raw/        # datos grandes o privados
credentials.json
```

> ⚠️ **Nunca** subas contraseñas, tokens ni API keys a GitHub. Usa variables de entorno
> (`.env`) y añádelas al `.gitignore`.

---

## 2.6 Subir a GitHub

1. Crea una cuenta en [github.com](https://github.com).
2. Crea un repositorio nuevo (ej. `curso-analista-datos`).
3. Conéctalo y sube:

```bash
git remote add origin https://github.com/TU_USUARIO/curso-analista-datos.git
git branch -M main
git push -u origin main
```

A partir de ahora, tu flujo diario es:
```bash
git add .
git commit -m "Descripción clara de qué cambiaste"
git push
```

### Buenos mensajes de commit

- ✅ `Añade limpieza de nulos en dataset de ventas`
- ❌ `cambios`, `asdf`, `arreglos varios`

---

## 2.7 Estructura recomendada de un proyecto de datos

```
mi-proyecto/
├── data/
│   ├── raw/          ← datos originales (nunca los edites)
│   └── processed/    ← datos limpios generados por tu código
├── notebooks/        ← exploración (.ipynb)
├── src/              ← código reutilizable (.py)
├── reports/          ← gráficos y entregables
├── .gitignore
├── pyproject.toml
└── README.md         ← qué hace el proyecto y cómo correrlo
```

> 💡 Trata `data/raw/` como **solo lectura**. Toda transformación se hace por código,
> nunca a mano. Así tu análisis es reproducible.

---

## Ejercicios

1. Instala `uv`, crea el proyecto `curso-datos` y añade las librerías del módulo.
2. Lanza Jupyter Lab y ejecuta la celda de ejemplo (2.4).
3. Inicializa Git, crea un `.gitignore` y haz tu primer commit.
4. Crea el repo en GitHub y haz `push`.
5. Modifica el `README.md`, haz commit y push. Verifica el cambio en GitHub.

## Reto del módulo

Crea la estructura de carpetas recomendada (2.7), añade un `README.md` que explique el
proyecto, súbelo a GitHub y comparte el enlace contigo mismo/a. Este será el repositorio
donde vivirá **todo el curso**.

➡️ Siguiente: [Módulo 03 — Python: pandas y Polars](../03-python-pandas-polars/README.md)
