# Módulo 08 — IA generativa aplicada al análisis de datos

> **Objetivo:** usar LLMs (Claude, ChatGPT, Copilot…) como **acelerador profesional** del
> análisis, con criterio: prompting efectivo, verificación, límites y ética. La IA no
> reemplaza al analista; **potencia** al que sabe usarla.

---

## 8.1 El nuevo perfil: analista + IA

En 2026, un analista que usa IA con criterio es dramáticamente más productivo. Pero hay una
regla que no cambia:

> ⚠️ **Tú eres responsable del resultado.** La IA se equivoca con seguridad ("alucina").
> Nunca entregues un número o código que no hayas **verificado**.

La IA es excelente **acelerando**, pésima **garantizando**. Tu valor está en el criterio.

---

## 8.2 Dónde la IA ayuda de verdad en el flujo del analista

| Tarea | Cómo ayuda la IA |
|-------|------------------|
| **Escribir código** | Genera pandas/SQL a partir de una descripción |
| **Explicar código** | Te explica una consulta heredada o un error |
| **Depurar** | Diagnostica un traceback o un resultado raro |
| **Regex y transformaciones** | Genera expresiones regulares y limpiezas complejas |
| **Generar ideas de EDA** | Sugiere preguntas y análisis para un dataset |
| **Documentar** | Redacta README, docstrings, descripciones de columnas |
| **Redactar hallazgos** | Convierte resultados en un resumen ejecutivo |
| **Análisis de texto** | Clasifica, resume o extrae info de datos no estructurados |

---

## 8.3 Prompting efectivo para análisis

Un buen prompt tiene **contexto + tarea + formato + restricciones**.

### ❌ Prompt pobre
> "dame código de pandas para ventas"

### ✅ Prompt efectivo
> "Tengo un DataFrame de pandas `df` con columnas: `fecha` (datetime), `region` (str),
> `producto` (str), `ventas` (float). Quiero calcular la variación porcentual de ventas
> mensuales por región respecto al mes anterior. Devuélveme el código con method chaining,
> comentado, y explica la lógica en 2 frases."

### Técnicas clave

1. **Da contexto real:** esquema, tipos, una muestra de datos (`df.head().to_dict()`).
2. **Sé específico con el formato:** "en Polars", "con seaborn", "como función".
3. **Pide que razone:** "explica por qué" reduce errores.
4. **Itera:** si algo no cuadra, corrige con el error exacto pegado.
5. **Pide alternativas:** "¿hay una forma más eficiente/legible?".

### La IA como tutor (no como muleta)

En vez de "resuélveme esto", prueba:
> "Explícame por qué mi `groupby` devuelve NaN aquí y qué concepto debo entender para
> evitarlo la próxima vez."

Así aprendes en lugar de crear dependencia.

---

## 8.4 Verificación: la habilidad más importante

Nunca confíes a ciegas. Protocolo de verificación:

- **Código:** ejecútalo y revisa el resultado en un caso que **conozcas la respuesta**.
- **Números:** comprueba órdenes de magnitud, totales, que sumen 100%, bordes (nulos, ceros).
- **SQL generado:** léelo. ¿El JOIN duplica filas? ¿El filtro está antes o después de agrupar?
- **Afirmaciones:** pide las fuentes; los LLMs inventan citas y funciones que no existen.

> 💡 Truco: pídele a la IA que **escriba un test** o que verifique su propio resultado con
> un método distinto. "Comprueba este total de otra forma."

---

## 8.5 Analizar datos con LLMs vía código (API)

Los LLMs también sirven **dentro** de tu pipeline para datos no estructurados: clasificar
tickets, extraer entidades, analizar sentimiento, resumir reseñas.

```python
# Ejemplo conceptual: clasificar el sentimiento de reseñas
import anthropic

client = anthropic.Anthropic()   # requiere API key en variable de entorno

def clasificar_sentimiento(texto):
    msg = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=10,
        messages=[{
            "role": "user",
            "content": f"Clasifica el sentimiento como POSITIVO, NEUTRO o NEGATIVO. "
                       f"Responde solo con una palabra.\n\nReseña: {texto}"
        }],
    )
    return msg.content[0].text.strip()

df["sentimiento"] = df["reseña"].apply(clasificar_sentimiento)
```

> 💡 Para muchas filas: procesa por lotes, controla costos, cachea resultados y valida una
> muestra a mano. Para tareas simples y masivas, a veces un modelo clásico es más barato.

---

## 8.6 RAG en una frase (para que sepas qué es)

**RAG** (Retrieval-Augmented Generation) = darle al LLM tus documentos como contexto para
que responda basándose en ellos, no en su memoria. Es la base de los "chatea con tus datos".
Como analista te lo cruzarás; no necesitas construirlo aún, pero entiende el concepto:
*recuperar información relevante → pasársela al modelo → generar respuesta fundamentada*.

---

## 8.7 "Text-to-SQL" y asistentes de BI

Cada vez más herramientas dejan preguntar en lenguaje natural ("¿ventas por región el mes
pasado?") y generan el SQL. Útil, pero:

- **Verifica el SQL generado** — puede malinterpretar la pregunta.
- Funciona mejor sobre datos **bien modelados y documentados** (¡otra razón para dbt!).
- No sustituye entender el modelo de datos; lo acelera.

---

## 8.8 Riesgos, ética y privacidad

Reglas que un profesional **no rompe**:

- 🔒 **Nunca pegues datos sensibles/PII** en herramientas públicas de IA. Usa datos
  anonimizados o instancias empresariales aprobadas.
- 🔒 **No subas credenciales** ni datos de clientes a un chat.
- 🧠 **Cuidado con las alucinaciones:** funciones inventadas, cifras falsas, fuentes ficticias.
- ⚖️ **Sesgo:** los modelos heredan sesgos; en clasificaciones que afectan personas, audita.
- 📉 **No delegues el juicio:** la IA no conoce el contexto de tu negocio ni las consecuencias.
- 📝 **Transparencia:** indica cuándo un análisis o texto fue asistido por IA si tu organización lo requiere.

---

## 8.9 Un flujo de trabajo realista con IA

```
1. TÚ defines la pregunta de negocio y el enfoque.
2. IA → borrador de código/SQL a partir de tu descripción con contexto.
3. TÚ ejecutas, VERIFICAS con un caso conocido y ajustas.
4. IA → te ayuda a depurar errores y a optimizar.
5. TÚ interpretas los resultados (esto no se delega).
6. IA → te ayuda a redactar el resumen ejecutivo.
7. TÚ revisas, corriges y firmas. Eres responsable.
```

El patrón: **la IA acelera las partes mecánicas; tú aportas el criterio en las decisiones.**

---

## Ejercicios

1. Toma un problema real de un módulo anterior y escribe un **prompt efectivo** (contexto +
   tarea + formato). Compara la respuesta con un prompt pobre.
2. Pídele a un LLM que genere una consulta SQL con un JOIN; **audítala**: ¿duplica filas?
   ¿el filtro está bien? Documenta qué encontraste.
3. Usa la IA como **tutor**: haz que te explique un concepto que no dominaste (window
   functions, p-valor…) y resume la explicación con tus palabras.
4. Pídele que **verifique un total** de dos formas distintas sobre tu dataset.
5. Escribe tu propia "política personal de uso de IA" en 5 reglas (qué sí, qué nunca).

## Reto del módulo

Reescribe el resumen ejecutivo de tu informe de EDA (Módulo 05) con ayuda de IA: dale tus
hallazgos verificados y pídele un texto claro para un directivo. Luego **corrígelo tú**
(la IA no conoce tu negocio). Documenta qué cambiaste y por qué: esa diferencia es tu valor.

➡️ Siguiente: [Módulo 09 — Automatización y apps](../09-automatizacion-y-apps/README.md)
