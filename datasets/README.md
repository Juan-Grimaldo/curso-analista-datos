# 📂 Datasets de práctica

## `ventas_ejemplo.csv`

Dataset sintético de ventas para los ejercicios de los módulos 03–06 y 09.
**735 filas**, primer semestre de 2026.

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `venta_id` | int | Identificador único de la venta |
| `fecha` | date | Fecha de la venta (2026-01-01 a 2026-06-29) |
| `region` | str | Norte / Sur / Este / Oeste |
| `producto` | str | A / B / C / D |
| `canal` | str | Web / Tienda / Movil |
| `ventas` | float | Monto de la venta en USD |
| `descuento` | float | Descuento aplicado (0 a 0.20) |
| `trafico` | int | Visitas asociadas ese día |

> ⚠️ **A propósito** contiene imperfecciones para que practiques limpieza:
> - **Valores nulos** en `ventas` (~3%).
> - **Outliers** (algunas ventas ~8× lo normal).
> - **Filas duplicadas** (15 al final).

Este es tu campo de entrenamiento: aplica todo lo del Módulo 03 (limpieza) y Módulo 06 (EDA).

## Otros datasets recomendados (reales)

Para el proyecto final, usa datos reales de:

- [Kaggle Datasets](https://www.kaggle.com/datasets)
- [datos.gob.es](https://datos.gob.es/) (España) · [datos.gob](https://www.datos.gov) (varios países)
- [Google Dataset Search](https://datasetsearch.research.google.com/)
- [Our World in Data](https://ourworldindata.org/)
- APIs públicas: [public-apis](https://github.com/public-apis/public-apis)

> 💡 Guarda siempre los datos descargados en `data/raw/` y trátalos como solo lectura.
