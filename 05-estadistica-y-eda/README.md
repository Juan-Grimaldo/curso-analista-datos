# Módulo 05 — Estadística aplicada y análisis exploratorio (EDA)

> **Objetivo:** desarrollar criterio estadístico para no engañarte (ni engañar). Aprenderás
> EDA sistemático, estadística descriptiva e inferencial, y a distinguir correlación de
> causalidad. Sin matemáticas de más: intuición + código.

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
df = pd.read_csv("data/raw/datos.csv")

df.shape
df.info()
df.describe(include="all")   # numéricas y categóricas
df.isna().mean().sort_values(ascending=False)   # % de nulos
```

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
- **Varianza / Desviación estándar:** cuánto se alejan los datos de la media.
- **IQR (rango intercuartílico):** Q3 − Q1. Robusto. Base para detectar *outliers*.

```python
df["ventas"].mean(), df["ventas"].median(), df["ventas"].std()
df["ventas"].quantile([0.25, 0.5, 0.75])
```

### Detección de outliers (regla IQR)

```python
q1, q3 = df["ventas"].quantile([0.25, 0.75])
iqr = q3 - q1
lim_inf, lim_sup = q1 - 1.5 * iqr, q3 + 1.5 * iqr
outliers = df[(df["ventas"] < lim_inf) | (df["ventas"] > lim_sup)]
```

> ⚠️ Un *outlier* no siempre es un error. Puede ser el dato más importante (fraude, un
> cliente enorme). Investígalo, no lo borres por reflejo.

---

## 5.3 Distribuciones

Formas que verás a menudo:

- **Normal (campana):** simétrica. Muchos fenómenos naturales.
- **Sesgada a la derecha:** cola larga a la derecha (ingresos, precios). La más común en negocio.
- **Uniforme:** todos los valores igual de probables.
- **Bimodal:** dos "picos" → puede indicar dos subgrupos mezclados.

```python
import matplotlib.pyplot as plt
df["ventas"].hist(bins=30)
plt.show()
```

---

## 5.4 Relaciones entre variables

### Correlación

Mide la relación **lineal** entre dos variables numéricas (−1 a +1).

```python
df[["ventas", "descuento", "trafico"]].corr()

import seaborn as sns
sns.heatmap(df.corr(numeric_only=True), annot=True, cmap="coolwarm")
```

- **+1:** relación positiva perfecta. **−1:** negativa perfecta. **0:** sin relación lineal.

> ⚠️ **Correlación ≠ causalidad.** Que dos cosas suban juntas no significa que una cause la
> otra (puede haber una tercera variable, o pura casualidad). Más en 5.7.

### Categórica vs numérica

```python
df.groupby("region")["ventas"].agg(["mean", "median", "std"])
sns.boxplot(data=df, x="region", y="ventas")
```

---

## 5.5 Estadística inferencial: de la muestra a la población

Casi nunca tienes *todos* los datos; tienes una **muestra**. La inferencia te dice cuánto
puedes confiar en generalizar.

### Conceptos clave

- **Población vs muestra:** el todo vs lo que observaste.
- **Intervalo de confianza:** rango probable del valor real. "La media está entre 95 y 105
  con 95% de confianza."
- **Error estándar:** cuánto varía tu estimación entre muestras.

---

## 5.6 Pruebas de hipótesis y test A/B

El pan de cada día del analista de producto/marketing.

### La lógica

1. **H₀ (hipótesis nula):** "no hay diferencia" (la versión B no cambia nada).
2. **H₁ (alternativa):** "sí hay diferencia".
3. Calculas un **p-valor:** probabilidad de ver este resultado (o más extremo) si H₀ fuera cierta.
4. Si **p < 0.05** (umbral típico), rechazas H₀: la diferencia es *estadísticamente significativa*.

```python
from scipy import stats

grupo_a = df.loc[df["variante"] == "A", "conversion"]
grupo_b = df.loc[df["variante"] == "B", "conversion"]

t_stat, p_valor = stats.ttest_ind(grupo_a, grupo_b)
print(f"p-valor: {p_valor:.4f}")
```

### Errores frecuentes (¡evítalos!)

- **Confundir significancia con importancia:** un resultado puede ser significativo pero
  con un efecto minúsculo e irrelevante para el negocio. Reporta también el **tamaño del efecto**.
- **p-hacking:** probar mil cosas hasta que algo dé p < 0.05. Define tu hipótesis *antes*.
- **Muestra insuficiente:** sin suficientes datos, no concluyas. Calcula el tamaño de muestra
  necesario antes del test.
- **Detener el test al primer resultado bueno:** invalida la estadística. Fija la duración
  de antemano.

---

## 5.7 Correlación, causalidad y sesgos

Para afirmar **causalidad** necesitas más que correlación:

- **Experimento controlado (A/B test):** el estándar de oro. Asignación aleatoria.
- **Cuidado con variables de confusión:** una tercera variable que causa ambas.
- **Sesgo de supervivencia:** solo miras a los que "sobrevivieron" (ej. analizar solo
  clientes activos ignora a los que se fueron).
- **Sesgo de selección:** tu muestra no representa a la población.
- **Paradoja de Simpson:** una tendencia se invierte al agrupar/desagrupar. Siempre revisa
  por subgrupos.

> 💡 Frase para recordar: *"¿Qué más podría explicar esto?"*. Un buen analista busca
> activamente explicaciones alternativas antes de afirmar una causa.

---

## 5.8 Un flujo de EDA reproducible

```python
def resumen_eda(df):
    print("Forma:", df.shape)
    print("\nTipos:\n", df.dtypes)
    print("\n% Nulos:\n", (df.isna().mean() * 100).round(1))
    print("\nDuplicados:", df.duplicated().sum())
    print("\nNuméricas:\n", df.describe().T)
    cats = df.select_dtypes("object").columns
    for c in cats[:5]:
        print(f"\n{c}:\n", df[c].value_counts().head())

resumen_eda(df)
```

Guarda esta función; la usarás en cada proyecto.

---

## Ejercicios

1. Sobre tu dataset, calcula media, mediana y std de una variable numérica. ¿Hay asimetría?
2. Detecta *outliers* con la regla IQR y **investiga** 2 de ellos: ¿error o dato real?
3. Haz un `heatmap` de correlaciones y describe la relación más fuerte que encuentres.
4. Plantea una pregunta de causalidad sobre tus datos y lista 2 posibles variables de confusión.
5. Simula un test A/B con `scipy` y explica en una frase qué significa tu p-valor.

## Reto del módulo

Escribe un **informe de EDA** (notebook) sobre tu dataset: forma, calidad, distribuciones de
3 variables, matriz de correlación, 2 outliers investigados y 3 hallazgos con su implicación.
Termina con una sección "qué NO puedo concluir y por qué".

➡️ Siguiente: [Módulo 06 — Visualización y storytelling](../06-visualizacion-y-storytelling/README.md)
