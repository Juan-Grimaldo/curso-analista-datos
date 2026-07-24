# Módulo 06 — Estadística aplicada y análisis exploratorio (EDA)

> **Objetivo:** desarrollar criterio estadístico para no engañarte (ni engañar). Aprenderás
> EDA sistemático, estadística descriptiva e inferencial, y a distinguir correlación de
> causalidad. Sin matemáticas de más: intuición + código.
>
> 🧭 **Formato:** cada bloque va seguido de un **▶️ Practica ahora** sobre tu dataset limpio.
> Ejecútalo en el momento. Al final, un **Reto** de cierre.

---

## 5.1 El EDA: análisis exploratorio de datos

El EDA es lo primero que haces con un dataset nuevo. Objetivo: **entender** los datos antes
de sacar conclusiones. Un flujo confiable:

1. **Forma:** ¿cuántas filas/columnas? ¿qué tipos?
2. **Calidad:** nulos, duplicados, valores imposibles.
3. **Distribuciones:** ¿cómo se reparte cada variable?
4. **Relaciones:** ¿cómo se relacionan las variables entre sí?
5. **Anomalías:** *outliers*, patrones raros.

```python
import pandas as pd
df = pd.read_csv("data/processed/ventas_limpio.parquet")  # o tu CSV limpio
df.shape
df.info()
df.describe(include="all")
df.isna().mean().sort_values(ascending=False)   # % de nulos
```

> ### ▶️ Practica ahora
> Sobre tu dataset limpio del Módulo 03, ejecuta los 5 pasos del flujo. Escribe en una celda
> de texto (Markdown) 2 observaciones iniciales que notes.

---

## 5.2 Estadística descriptiva

### Tendencia central
- **Media:** promedio. Sensible a valores extremos.
- **Mediana:** valor central. Robusta frente a *outliers*.
- **Moda:** valor más frecuente.

> 💡 Si media y mediana difieren mucho, hay **asimetría** (*skew*) u *outliers*. En ingresos
> o precios, casi siempre reporta la **mediana**.

### Dispersión
- **Rango:** max − min.
- **Desviación estándar:** cuánto se alejan los datos de la media.
- **IQR (rango intercuartílico):** Q3 − Q1. Robusto. Base para detectar *outliers*.

```python
df["ventas"].mean(), df["ventas"].median(), df["ventas"].std()
df["ventas"].quantile([0.25, 0.5, 0.75])
```

> ### ▶️ Practica ahora
> Calcula media, mediana y std de `ventas`. ¿La media es mayor que la mediana? Si sí, tienes
> asimetría a la derecha (cola de valores altos). Explica en una frase qué la causa.

---

## 5.3 Detección de outliers (regla IQR)

```python
q1, q3 = df["ventas"].quantile([0.25, 0.75])
iqr = q3 - q1
lim_inf, lim_sup = q1 - 1.5 * iqr, q3 + 1.5 * iqr
outliers = df[(df["ventas"] < lim_inf) | (df["ventas"] > lim_sup)]
```

> ⚠️ Un *outlier* no siempre es un error. Puede ser el dato más importante (fraude, un
> cliente enorme). Investígalo, no lo borres por reflejo.

> ### ▶️ Practica ahora
> Detecta los outliers de `ventas` con la regla IQR. **Investiga 2**: ¿son los outliers que
> inyectamos a propósito (ventas ~8× lo normal), un error, o datos reales? Justifica qué harías.

---

## 5.4 Distribuciones

Formas que verás a menudo:
- **Normal (campana):** simétrica.
- **Sesgada a la derecha:** cola larga a la derecha (ingresos, precios). Muy común en negocio.
- **Uniforme:** todos los valores igual de probables.
- **Bimodal:** dos "picos" → puede indicar dos subgrupos mezclados.

```python
import matplotlib.pyplot as plt
df["ventas"].hist(bins=30)
plt.show()
```

> ### ▶️ Practica ahora
> Haz un histograma de `ventas`. ¿Qué forma tiene? Ahora haz uno **por producto**
> (`df.groupby("producto")["ventas"].hist()` o un boxplot). ¿Cambia la distribución entre productos?

---

## 5.5 Relaciones entre variables

### Correlación
Mide la relación **lineal** entre dos variables numéricas (−1 a +1).

```python
df[["ventas", "descuento", "trafico"]].corr()

import seaborn as sns
sns.heatmap(df.corr(numeric_only=True), annot=True, cmap="coolwarm")
```

- **+1:** positiva perfecta. **−1:** negativa perfecta. **0:** sin relación lineal.

> ⚠️ **Correlación ≠ causalidad.** Que dos cosas suban juntas no significa que una cause la
> otra. Más en 5.8.

> ### ▶️ Practica ahora
> Haz el `heatmap` de correlaciones entre `ventas`, `descuento` y `trafico`. ¿Cuál es la
> relación más fuerte? ¿Te sorprende su signo (positivo/negativo)?

---

## 5.6 Estadística inferencial: de la muestra a la población

Casi nunca tienes *todos* los datos; tienes una **muestra**. La inferencia te dice cuánto
puedes confiar en generalizar.

- **Población vs muestra:** el todo vs lo que observaste.
- **Intervalo de confianza:** rango probable del valor real ("la media está entre 95 y 105
  con 95% de confianza").
- **Error estándar:** cuánto varía tu estimación entre muestras.

> ### ▶️ Practica ahora
> Imagina que `ventas_ejemplo.csv` es solo una muestra de todas las ventas del año. En una
> frase, explica por qué no puedes afirmar que "la venta media exacta del año es X".

---

## 5.7 Pruebas de hipótesis y test A/B

El pan de cada día del analista de producto/marketing.

**La lógica:**
1. **H₀ (nula):** "no hay diferencia".
2. **H₁ (alternativa):** "sí hay diferencia".
3. **p-valor:** probabilidad de ver este resultado (o más extremo) si H₀ fuera cierta.
4. Si **p < 0.05**, rechazas H₀: la diferencia es *estadísticamente significativa*.

```python
from scipy import stats
grupo_a = df.loc[df["canal"] == "Web", "ventas"]
grupo_b = df.loc[df["canal"] == "Movil", "ventas"]
t_stat, p_valor = stats.ttest_ind(grupo_a, grupo_b, nan_policy="omit")
print(f"p-valor: {p_valor:.4f}")
```

**Errores frecuentes (¡evítalos!):**
- Confundir **significancia** con **importancia** (reporta también el tamaño del efecto).
- **p-hacking:** probar mil cosas hasta que algo dé p < 0.05.
- **Muestra insuficiente** o **detener el test** al primer resultado bueno.

> ### ▶️ Practica ahora
> Compara las ventas medias entre dos canales con `ttest_ind`. Interpreta tu p-valor en una
> frase: ¿la diferencia es significativa o podría deberse al azar?

---

## 5.8 Correlación, causalidad y sesgos

Para afirmar **causalidad** necesitas más que correlación:

- **Experimento controlado (A/B test):** el estándar de oro (asignación aleatoria).
- **Variables de confusión:** una tercera variable que causa ambas.
- **Sesgo de supervivencia:** solo miras a los que "sobrevivieron".
- **Sesgo de selección:** tu muestra no representa a la población.
- **Paradoja de Simpson:** una tendencia se invierte al agrupar/desagrupar. Revisa por subgrupos.

> 💡 Frase para recordar: *"¿Qué más podría explicar esto?"*.

> ### ▶️ Practica ahora
> Si encontraste correlación entre `descuento` y `ventas`, plantea 2 **explicaciones
> alternativas** a "el descuento causa más ventas" (ej. los productos populares se descuentan más).

---

## 5.9 Un flujo de EDA reproducible

```python
def resumen_eda(df):
    print("Forma:", df.shape)
    print("\n% Nulos:\n", (df.isna().mean() * 100).round(1))
    print("\nDuplicados:", df.duplicated().sum())
    print("\nNuméricas:\n", df.describe().T)
    for c in df.select_dtypes("object").columns[:5]:
        print(f"\n{c}:\n", df[c].value_counts().head())

resumen_eda(df)
```

> ### ▶️ Practica ahora
> Copia esta función a tu proyecto (`src/`), ejecútala sobre tu dataset y guárdala: la
> reutilizarás en cada proyecto futuro.

---

## Reto del módulo (cierre)

Escribe un **informe de EDA** (notebook) sobre tu dataset: forma, calidad, distribuciones de
3 variables, matriz de correlación, 2 outliers investigados y 3 hallazgos con su implicación.
Termina con una sección **"qué NO puedo concluir y por qué"**. Commit y push.

➡️ Siguiente: [Módulo 07 — Visualización y storytelling](../07-visualizacion-y-storytelling/README.md)
