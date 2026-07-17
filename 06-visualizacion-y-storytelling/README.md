# Módulo 06 — Visualización de datos y storytelling

> **Objetivo:** convertir análisis en **comunicación que mueve decisiones**. Aprenderás a
> elegir el gráfico correcto, a hacerlos con Python (matplotlib/seaborn/plotly), y los
> principios de dashboards (Power BI/Tableau) y narrativa de datos.

---

## 6.1 El principio central

> Un gráfico no existe para "verse bonito", sino para **comunicar una idea con el mínimo
> esfuerzo cognitivo** del lector.

Antes de graficar, responde: **¿cuál es el UN mensaje que quiero transmitir?**

---

## 6.2 Elegir el gráfico correcto

| Quieres mostrar... | Usa | Evita |
|--------------------|-----|-------|
| Comparar categorías | Barras | 3D, pastel con muchas categorías |
| Evolución en el tiempo | Líneas | Barras para series largas |
| Relación entre 2 variables | Dispersión (scatter) | — |
| Distribución de una variable | Histograma / boxplot | — |
| Parte de un todo (pocas partes) | Barras apiladas / donut simple | Pastel con >5 trozos |
| Composición en el tiempo | Área apilada | — |
| Datos geográficos | Mapa (choropleth) | — |
| Correlaciones múltiples | Heatmap | — |

> ⚠️ **Los gráficos de pastel** casi siempre son peores que unas barras. El ojo humano
> compara longitudes mucho mejor que ángulos.

---

## 6.3 Visualización con Python

### matplotlib — la base

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(8, 5))
ax.bar(ventas_region.index, ventas_region.values, color="#2563eb")
ax.set_title("Ventas por región — 2026")
ax.set_ylabel("Ventas (USD)")
ax.spines[["top", "right"]].set_visible(False)   # limpia el marco
plt.tight_layout()
plt.savefig("reports/ventas_region.png", dpi=150)
```

### seaborn — estadístico y elegante

```python
import seaborn as sns
sns.set_theme(style="whitegrid")

sns.barplot(data=df, x="region", y="ventas", estimator="sum")
sns.lineplot(data=df, x="fecha", y="ventas", hue="region")
sns.boxplot(data=df, x="region", y="ventas")
sns.scatterplot(data=df, x="trafico", y="ventas", hue="region", size="descuento")
sns.histplot(data=df, x="ventas", bins=30, kde=True)
```

### plotly — interactivo (para apps y dashboards)

```python
import plotly.express as px

fig = px.line(df, x="fecha", y="ventas", color="region",
              title="Ventas mensuales por región")
fig.show()
fig.write_html("reports/ventas.html")   # interactivo, compartible
```

Con plotly el usuario puede hacer zoom, hover y filtrar. Ideal para Streamlit (Módulo 09).

---

## 6.4 Principios de diseño (pre-attentive attributes)

Nuestro cerebro procesa ciertas señales **antes** de pensar. Úsalas a tu favor:

- **Color:** resérvalo para destacar lo importante. Todo en color = nada destaca.
- **Posición:** lo más alto/izquierda se lee primero.
- **Tamaño:** lo grande se percibe como importante.

### Reglas de oro (data-ink ratio, de Tufte)

1. **Elimina lo que no informa:** rejillas pesadas, bordes, fondos, 3D, sombras.
2. **Ordena** las barras por valor (salvo orden natural como meses).
3. **Etiqueta directamente** en vez de obligar a mirar una leyenda lejana.
4. **Empieza los ejes de barras en 0** (si no, exageras diferencias — engañoso).
5. **Un color de acento** + grises para el contexto.
6. **Título que dice la conclusión:** "Las ventas del Norte cayeron 15%", no "Ventas por región".

---

## 6.5 Accesibilidad del color

- ~8% de los hombres tiene daltonismo. Evita depender solo de rojo/verde.
- Usa paletas seguras (`viridis`, `cividis`) o combina color + forma/etiqueta.
- Asegura contraste suficiente entre texto y fondo.

```python
sns.set_palette("colorblind")
```

---

## 6.6 Dashboards y BI (Power BI / Tableau)

Cuando el público necesita **explorar** los datos por sí mismo (no solo leer un informe),
usas un **dashboard**.

### Herramientas

- **Power BI** — estándar corporativo (Microsoft), fuerte con Excel/Azure. Lenguaje **DAX**.
- **Tableau** — muy potente en visualización, popular en análisis.
- **Looker Studio** — gratuito, integra con Google.
- **Streamlit** — cuando quieres hacerlo con Python (Módulo 09).

### Anatomía de un buen dashboard

```
┌─────────────────────────────────────────┐
│  TÍTULO + filtros (fecha, región)        │  ← contexto arriba
├───────────┬───────────┬─────────────────┤
│  KPI 1    │  KPI 2    │  KPI 3          │  ← números clave (big numbers)
├───────────┴───────────┴─────────────────┤
│  Tendencia principal (línea)             │  ← el gráfico "héroe"
├──────────────────┬───────────────────────┤
│  Desglose 1      │  Desglose 2           │  ← detalle secundario
└──────────────────┴───────────────────────┘
```

Principios: **lo más importante arriba-izquierda**, máximo 5–7 elementos, filtros claros,
y cada gráfico responde una pregunta concreta.

### Conceptos de Power BI que debes conocer

- **Modelo de datos:** relaciones entre tablas (esquema estrella, Módulo 04).
- **Medidas (DAX):** cálculos como `Ventas Totales = SUM(Ventas[Monto])`.
- **Columnas calculadas** vs **medidas** (las medidas se calculan según el contexto del filtro).

---

## 6.7 Storytelling con datos

Un análisis sin narrativa se ignora. Estructura tu comunicación como una historia:

### El arco narrativo

1. **Contexto:** ¿de qué hablamos y por qué importa ahora?
2. **Conflicto/hallazgo:** ¿qué descubriste? (el "¡ajá!")
3. **Resolución:** ¿qué recomiendas hacer?

### El framework SCR (Situación – Complicación – Resolución)

- **Situación:** "Las ventas crecían 5% mensual."
- **Complicación:** "En junio cayeron 15%, concentrado en el canal móvil."
- **Resolución:** "Recomiendo auditar el checkout móvil; impacto estimado: recuperar ~200k."

### Consejos

- **Empieza por la conclusión** (estilo ejecutivo), luego el detalle.
- **Un mensaje por diapositiva/gráfico.**
- Anticipa el *"¿y qué?"*: cada dato debe conectar con una **acción o decisión**.
- Conoce a tu audiencia: un CEO quiere el "qué hacer"; un analista quiere el "cómo lo sabes".

---

## 6.8 Errores que gritan "novato"

- Gráficos de pastel con 8 categorías.
- Ejes que no empiezan en 0 en gráficos de barras.
- Demasiados colores sin significado.
- Títulos genéricos ("Gráfico 1") en vez de la conclusión.
- Tablas gigantes cuando un gráfico bastaría (o al revés).
- No indicar unidades, fechas ni fuente de los datos.

---

## Ejercicios

1. Toma un hallazgo de tu EDA (Módulo 05) y elige el **gráfico correcto** para comunicarlo.
   Justifica por qué ese y no otro.
2. Créalo en seaborn aplicando las reglas de oro (título-conclusión, sin *chartjunk*, un acento).
3. Haz una versión **interactiva** con plotly y expórtala a HTML.
4. Diseña (en papel o herramienta) el *layout* de un dashboard de 4 elementos para tu tema.
5. Escribe el mensaje de tu análisis con el framework **SCR** en 3 frases.

## Reto del módulo

Crea un mini-informe visual (1 página o 3 slides) que cuente una historia con datos:
contexto → hallazgo → recomendación, con 2–3 gráficos bien diseñados. El título de cada
gráfico debe ser su conclusión. Este material va directo a tu portafolio.

➡️ Siguiente: [Módulo 07 — Modern data stack](../07-stack-datos-moderno/README.md)
