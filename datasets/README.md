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

## Las fuentes crudas del bloque ETL/ELT (Módulo 05)

El bloque de ETL/ELT, modelado y optimización del [Módulo 05](../05-sql-moderno/README.md)
necesita datos **a escala** y **sucios de verdad**, así que no se guardan aquí: los
**genera** el script [`crear_fuentes.py`](../05-sql-moderno/crear_fuentes.py) dentro de tu
repo `curso-datos`:

```bash
uv run crear_fuentes.py      # ~4 segundos, escribe en data/raw/
```

| Archivo generado | Contenido |
|------------------|-----------|
| `ventas_crudas.csv` | **201.000 filas** (18 meses de ventas, 2025-01 a 2026-06) tal como saldrían de un sistema real |
| `ventas_crudas_lote2.csv` | El lote de julio de 2026 (~10.000 filas), para practicar carga incremental |
| `clientes.csv` | 2.000 clientes (+ fichas repetidas), segunda fuente |
| `productos.json` | Catálogo de 12 productos en JSON, tercera fuente |

> ⚠️ **A propósito**, el crudo llega roto: todo como texto, fechas en dos formatos
> (`2026-03-16` y `16/04/2026`), importes tipo `"$1,450.00"`, nulos escritos como `N/A` o
> vacío, regiones sin normalizar (`"  Este "`, `"ESTE"`), ~1.000 filas duplicadas, outliers,
> importes incoherentes y, en el lote 2, un producto que **no existe** en el catálogo.

Los datos son **deterministas**: el script usa un generador propio, así que obtienes los
mismos números en cualquier máquina — de eso dependen los correctores de las actividades.
Ocupan ~25 MB: añade `data/` a tu `.gitignore`.

## Otros datasets recomendados (reales)

Para el proyecto final, usa datos reales de:

- [Kaggle Datasets](https://www.kaggle.com/datasets)
- [datos.gob.es](https://datos.gob.es/) (España) · [datos.gob](https://www.datos.gov) (varios países)
- [Google Dataset Search](https://datasetsearch.research.google.com/)
- [Our World in Data](https://ourworldindata.org/)
- APIs públicas: [public-apis](https://github.com/public-apis/public-apis)

> 💡 Guarda siempre los datos descargados en `data/raw/` y trátalos como solo lectura.
