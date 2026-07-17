# Módulo 02 — Entorno moderno y control de versiones

> **Objetivo:** montar un entorno de análisis profesional, reproducible y versionado.
> Terminarás con Python instalado, un entorno aislado, Jupyter funcionando y tu primer
> repositorio en GitHub.
>
> 🧭 **Formato del módulo:** cada concepto viene seguido de un bloque **▶️ Practica ahora**.
> Hazlo *en el momento*, antes de seguir leyendo. Al final solo hay un **Reto** de cierre.

---

## 0. Antes de nada: las DOS carpetas (no las confundas)

En este curso trabajarás con **dos carpetas distintas** con propósitos diferentes:

| Carpeta | Qué es | ¿Es tu repo de Git? |
|---------|--------|---------------------|
| **`Curso Analista de datos`** | El **material** del curso (estas lecciones, el glosario, el dataset de ejemplo). Solo lo **lees**. | ❌ No |
| **`curso-datos`** | **Tu proyecto de práctica**, donde TÚ escribes el código y haces los ejercicios. | ✅ Sí (este va a GitHub) |

⚠️ **Nunca metas un repo de Git dentro de otro.** Crea `curso-datos` **fuera** de la carpeta
del material, como carpetas hermanas:

```
Documents/
├── Curso Analista de datos/    ← MATERIAL (solo lees)
└── curso-datos/                ← TU trabajo (tu repo de GitHub)
```

> Cuando más abajo hagas `uv init curso-datos`, ejecútalo desde `Documents/`, **no** dentro
> de "Curso Analista de datos".

---

## 1. Por qué esto importa

El 80% de la frustración de quien empieza viene del **entorno**, no del análisis.
Un entorno bien montado te da tres superpoderes:

- **Reproducibilidad:** que tu análisis corra igual hoy y en otra máquina.
- **Aislamiento:** que un proyecto no rompa a otro (dependencias).
- **Versionado:** poder volver atrás y colaborar sin pisar el trabajo de nadie.

---

## 2. Instalar Python moderno con `uv`

En 2026 la forma recomendada de gestionar Python y dependencias es **[uv](https://docs.astral.sh/uv/)**
(de Astral): rapidísimo y reemplaza a `pip`, `venv`, `pyenv` y `poetry` a la vez.

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

> ### ▶️ Practica ahora
> 1. Instala `uv` con el comando de tu sistema.
> 2. Cierra y reabre la terminal, y verifica: `uv --version`.
>
> Si te muestra un número de versión, ✅ listo. Si no, revisa que reabriste la terminal.

---

## 3. Crear tu proyecto de práctica

Ubícate **fuera** del material (por ejemplo en `Documents/`) y crea tu proyecto:

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

> ### ▶️ Practica ahora
> 1. Desde `Documents/` (no dentro del material) ejecuta `uv init curso-datos`.
> 2. Entra con `cd curso-datos` y añade las librerías de arriba.
> 3. Confirma que existen los archivos `pyproject.toml` y `uv.lock`, y la carpeta `.venv`.

> 💡 Alternativa clásica: `python -m venv .venv` + `pip install`. Funciona, pero `uv` es
> más rápido y fiable. Si tu empresa usa Anaconda/conda, también es válido.

---

## 4. El editor: VS Code

Descarga **[Visual Studio Code](https://code.visualstudio.com/)** e instala estas extensiones:

- **Python** (Microsoft)
- **Jupyter**
- **Ruff** (linter/formateador rápido)
- **GitLens** (Git visual)
- Opcional: un asistente de IA (Copilot, Claude, etc.)

> ### ▶️ Practica ahora
> Desde la carpeta `curso-datos`, ábrela en el editor con `code .` e instala las cuatro
> extensiones. Comprueba que abajo a la derecha VS Code detecta el intérprete de `.venv`.

---

## 5. Notebooks vs scripts + tu primera celda

- **Jupyter Notebook (`.ipynb`):** ideal para **explorar** — ejecutas celda a celda y ves
  resultados al instante. Perfecto para EDA.
- **Scripts (`.py`):** ideal para **producción** — código reutilizable, automatizable, testeable.

Regla práctica: **explora en notebook, consolida en script**.

> ### ▶️ Practica ahora
> 1. Lanza Jupyter: `uv run jupyter lab`.
> 2. Crea un notebook nuevo dentro de `curso-datos` y ejecuta esta celda:
>
> ```python
> import pandas as pd
> import numpy as np
>
> print(f"pandas {pd.__version__}")
> df = pd.DataFrame({"ciudad": ["Madrid", "Lima", "Bogotá"], "ventas": [120, 95, 140]})
> df
> ```
>
> Si ves la tabla con las tres ciudades, ✅ tu entorno funciona de punta a punta.

---

## 6. Git: control de versiones

**Git** es un sistema que guarda el historial de tus cambios. **GitHub** es la nube donde
lo publicas y colaboras. Es una habilidad **no negociable** para un analista moderno.

Configuración inicial (una sola vez):

```bash
git config --global user.name "Tu Nombre"
git config --global user.email "tu@email.com"
git config --global init.defaultBranch main
```

El flujo básico (piensa en `commit` como un **punto de guardado** de un videojuego):

```bash
git init                      # inicializa el repo
git add .                     # prepara los cambios (staging)
git commit -m "Primer commit" # guarda una foto del proyecto
git log --oneline             # ve el historial
```

| Concepto | Qué es |
|----------|--------|
| **Repositorio** | La carpeta del proyecto con su historial |
| **Commit** | Una instantánea guardada con un mensaje |
| **Branch** | Una línea de trabajo paralela (`main`, `feature-x`) |
| **Remote** | La copia en la nube (GitHub) |
| **Push / Pull** | Subir / bajar cambios al remoto |

> ### ▶️ Practica ahora
> Dentro de `curso-datos` (¡recuerda: aquí sí es tu repo!):
> 1. Configura tu nombre y email (los tres comandos de arriba).
> 2. Ejecuta `git init`.
> 3. Aún **no** hagas commit — primero necesitas el `.gitignore` del siguiente paso.

---

## 7. El archivo `.gitignore`

Nunca subas datos sensibles, entornos ni credenciales. Crea un archivo `.gitignore` en
`curso-datos` con:

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

> ### ▶️ Practica ahora
> 1. Crea el archivo `.gitignore` con ese contenido.
> 2. Ahora sí, tu primer commit:
>    ```bash
>    git add .
>    git commit -m "Configura entorno inicial del proyecto"
>    git log --oneline
>    ```
> 3. Verifica en el `git log` que aparece tu commit.

---

## 8. Subir a GitHub

1. Crea una cuenta en [github.com](https://github.com).
2. Crea un repositorio nuevo (ej. `curso-analista-datos`) **vacío** (sin README).
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

**Buenos mensajes de commit:**
- ✅ `Añade limpieza de nulos en dataset de ventas`
- ❌ `cambios`, `asdf`, `arreglos varios`

> ### ▶️ Practica ahora
> 1. Crea el repo en GitHub y conéctalo con los comandos de arriba.
> 2. Haz `push` y comprueba en el navegador que tus archivos aparecen en GitHub.
> 3. Cambia algo pequeño (crea un `README.md` con una línea), y haz
>    `git add . && git commit -m "Añade README" && git push`. Verifica el cambio en GitHub.

---

## 9. Estructura recomendada del proyecto

Organiza `curso-datos` así:

```
curso-datos/
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

Para practicar con el dataset del curso, **cópialo** desde el material a tu proyecto:

```powershell
Copy-Item "..\Curso Analista de datos\datasets\ventas_ejemplo.csv" "data\raw\"
```

> ### ▶️ Practica ahora
> 1. Crea las carpetas `data/raw`, `data/processed`, `notebooks`, `src` y `reports`.
> 2. Copia `ventas_ejemplo.csv` a `data/raw/`.
> 3. Escribe un `README.md` que explique en 3 líneas qué es este proyecto.
> 4. Haz commit y push de la nueva estructura.

---

## Reto del módulo (cierre)

Ya tienes casi todo hecho por las prácticas. Para cerrar, confirma que tu repositorio
`curso-datos` en GitHub tiene: la estructura de carpetas, el `.gitignore`, el `README.md`
y al menos 3 commits con mensajes claros. Comparte contigo mismo/a el enlace del repo:
**aquí vivirá todo tu trabajo del curso**.

➡️ Siguiente: [Módulo 03 — Python: pandas y Polars](../03-python-pandas-polars/README.md)
