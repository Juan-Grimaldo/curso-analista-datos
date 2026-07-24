# Módulo 07 — Visualización de datos y storytelling

> **Objetivo:** convertir análisis en **comunicación que mueve decisiones**. Aprenderás a
> elegir el gráfico correcto, a hacerlos con Python (matplotlib/seaborn/plotly), y los
> principios de dashboards (Power BI/Tableau) y narrativa de datos.
>
> 🧭 **Formato:** cada bloque va seguido de un **▶️ Practica ahora** con tu dataset. Al final,
> un **Reto** de cierre.

---

## 6.1 El principio central

> Un gráfico no existe para "verse bonito", sino para **comunicar una idea con el mínimo
> esfuerzo cognitivo** del lector.

Antes de graficar, responde: **¿cuál es el UN mensaje que quiero transmitir?**

> ### ▶️ Practica ahora
> Toma un hallazgo de tu EDA (Módulo 06) y escríbelo como **una frase** (el mensaje).
> Ejemplo: "El canal Móvil vende menos pero con menos descuento". Ese será el mensaje a graficar.

---

## 6.2 Elegir el gráfico correcto

| Quieres mostrar... | Usa | Evita |
|--------------------|-----|-------|
| Comparar categorías | Barras | 3D, pastel con muchas categorías |
| Evolución en el tiempo | Líneas | Barras para series largas |
| Relación entre 2 variables | Dispersión (scatter) | — |
| Distribución de una variable | Histograma / boxplot | — |
| Parte de un todo (pocas partes) | Barras / donut simple | Pastel con >5 trozos |
| Datos geográficos | Mapa (choropleth) | — |
| Correlaciones múltiples | Heatmap | — |

> ⚠️ **Los gráficos de pastel** casi siempre son peores que unas barras. El ojo compara
> longitudes mucho mejor que ángulos.

> ### ▶️ Practica ahora
> Para el mensaje que escribiste en 6.1, decide **qué gráfico** es el correcto y por qué.
> Justifícalo en una frase antes de programar nada.

---

## 6.3 Visualización con Python

### matplotlib — la base
```python
import matplotlib.pyplot as plt
ventas_region = df.groupby("region")["ventas"].sum().sort_values()

fig, ax = plt.subplots(figsize=(8, 5))
ax.bar(ventas_region.index, ventas_region.values, color="#2563eb")
ax.set_title("El Norte lidera las ventas del semestre")   # título = conclusión
ax.set_ylabel("Ventas (USD)")
ax.spines[["top", "right"]].set_visible(False)
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
sns.scatterplot(data=df, x="trafico", y="ventas", hue="region")
```

### plotly — interactivo (para apps y dashboards)
```python
import plotly.express as px
fig = px.line(df, x="fecha", y="ventas", color="region", title="Ventas por región")
fig.write_html("reports/ventas.html")   # interactivo, compartible
```

> ### ▶️ Practica ahora
> Crea el gráfico que elegiste en 6.2 con seaborn. Guárdalo en `reports/`. Ponle un
> **título que sea la conclusión**, no una etiqueta genérica.

---

## 6.4 Principios de diseño

Nuestro cerebro procesa ciertas señales **antes** de pensar (*pre-attentive*): color,
posición, tamaño. Úsalas a tu favor.

**Reglas de oro (data-ink ratio, de Tufte):**
1. **Elimina lo que no informa:** rejillas pesadas, bordes, fondos, 3D, sombras.
2. **Ordena** las barras por valor (salvo orden natural como meses).
3. **Etiqueta directamente** en vez de obligar a mirar una leyenda lejana.
4. **Empieza los ejes de barras en 0** (si no, exageras diferencias — engañoso).
5. **Un color de acento** + grises para el contexto.
6. **Título que dice la conclusión.**

> ### ▶️ Practica ahora
> Revisa tu gráfico de 6.3 con esta checklist. Aplica al menos 3 mejoras (quita chartjunk,
> ordena, usa un solo acento). Compara el antes y el después.

---

## 6.5 Accesibilidad del color

- ~8% de los hombres tiene daltonismo. Evita depender solo de rojo/verde.
- Usa paletas seguras (`viridis`, `cividis`, `colorblind`) o combina color + forma/etiqueta.
- Asegura contraste suficiente entre texto y fondo.

```python
sns.set_palette("colorblind")
```

> ### ▶️ Practica ahora
> Aplica `sns.set_palette("colorblind")` a un gráfico con varias series. Verifica que las
> categorías siguen distinguiéndose bien.

---

## 6.6 Dashboards y BI (Power BI / Tableau)

Cuando el público necesita **explorar** los datos por sí mismo, usas un **dashboard**.

**Herramientas:** Power BI (estándar corporativo, lenguaje **DAX**), Tableau, Looker Studio
(gratis), o **Streamlit** con Python (Módulo 10).

**Anatomía de un buen dashboard:**
```
┌─────────────────────────────────────────┐
│  TÍTULO + filtros (fecha, región)        │  ← contexto arriba
├───────────┬───────────┬─────────────────┤
│  KPI 1    │  KPI 2    │  KPI 3          │  ← números clave
├───────────┴───────────┴─────────────────┤
│  Tendencia principal (línea)             │  ← gráfico "héroe"
├──────────────────┬───────────────────────┤
│  Desglose 1      │  Desglose 2           │  ← detalle
└──────────────────┴───────────────────────┘
```

Principios: **lo más importante arriba-izquierda**, máximo 5–7 elementos, filtros claros.
En Power BI conocerás el **modelo de datos** (esquema estrella), las **medidas (DAX)** y la
diferencia entre columnas calculadas y medidas.

> ### ▶️ Practica ahora
> Diseña (en papel o en una herramienta) el *layout* de un dashboard de 4 elementos para tu
> dataset: 2 KPIs + 1 gráfico héroe + 1 desglose. Indica qué pregunta responde cada uno.

---

## 6.7 Storytelling con datos

Un análisis sin narrativa se ignora. Estructura como una historia:

**Arco narrativo:** Contexto → Conflicto/hallazgo → Resolución.

**Framework SCR:**
- **Situación:** "Las ventas crecían 5% mensual."
- **Complicación:** "En junio cayeron 15%, concentrado en el canal móvil."
- **Resolución:** "Recomiendo auditar el checkout móvil; impacto: recuperar ~200k."

**Consejos:** empieza por la conclusión (estilo ejecutivo), un mensaje por gráfico, anticipa
el *"¿y qué?"* (cada dato → una acción), y conoce a tu audiencia.

> ### ▶️ Practica ahora
> Escribe el mensaje de tu análisis con el framework **SCR** en 3 frases (Situación,
> Complicación, Resolución). Debe terminar en una **recomendación accionable**.

---

## 6.8 Errores que gritan "novato"

- Gráficos de pastel con 8 categorías.
- Ejes que no empiezan en 0 en barras.
- Demasiados colores sin significado.
- Títulos genéricos ("Gráfico 1").
- Tablas gigantes cuando un gráfico bastaría.
- No indicar unidades, fechas ni fuente.

> ### ▶️ Practica ahora
> Revisa todos los gráficos que hiciste en este módulo contra esta lista. ¿Cometiste alguno?
> Corrígelo.

---

## Reto del módulo (cierre)

Crea un mini-informe visual (1 página o 3 slides) que cuente una historia con datos:
**contexto → hallazgo → recomendación**, con 2–3 gráficos bien diseñados (título = conclusión,
sin chartjunk, paleta accesible). Este material va directo a tu portafolio. Commit y push.

➡️ Siguiente: [Módulo 08 — Modern data stack](../08-stack-datos-moderno/README.md)
