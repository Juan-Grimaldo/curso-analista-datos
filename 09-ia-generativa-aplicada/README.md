# Módulo 09 — IA generativa aplicada al análisis de datos

> **Objetivo:** usar LLMs (Claude, ChatGPT, Copilot…) como **acelerador profesional** del
> análisis, con criterio: prompting efectivo, verificación, límites y ética.
>
> 🧭 **Formato:** cada bloque va seguido de un **▶️ Practica ahora** (usa tu asistente de IA
> preferido). Al final, un **Reto** de cierre.
>
> 📂 **Dónde practicas:** este README es solo la **teoría**. Lo que generes o escribas
> (política de uso de IA, prompts, código) guárdalo en tu **repo de práctica** `curso-datos`.

---

## 8.1 El nuevo perfil: analista + IA

En 2026, un analista que usa IA con criterio es dramáticamente más productivo. Pero hay una
regla que no cambia:

> ⚠️ **Tú eres responsable del resultado.** La IA se equivoca con seguridad ("alucina").
> Nunca entregues un número o código que no hayas **verificado**.

La IA es excelente **acelerando**, pésima **garantizando**. Tu valor está en el criterio.

> ### ▶️ Practica ahora
> Pídele a un LLM que calcule algo que ya sabes de tu dataset (ej. "¿cuántas regiones hay?").
> Dale el contexto justo. Observa: ¿acertó? Esto te entrena a **verificar siempre**.

---

## 8.2 Dónde la IA ayuda de verdad

| Tarea | Cómo ayuda |
|-------|------------|
| **Escribir código** | Genera pandas/SQL desde una descripción |
| **Explicar código** | Te explica una consulta heredada o un error |
| **Depurar** | Diagnostica un traceback o un resultado raro |
| **Regex y transformaciones** | Genera expresiones regulares complejas |
| **Ideas de EDA** | Sugiere preguntas y análisis para un dataset |
| **Documentar** | Redacta README, docstrings, descripciones |
| **Redactar hallazgos** | Convierte resultados en resumen ejecutivo |
| **Texto no estructurado** | Clasifica, resume o extrae info |

> ### ▶️ Practica ahora
> Toma un error (traceback) que hayas tenido en un módulo anterior (o provócalo). Pégaselo a
> un LLM y pídele que lo **explique y lo arregle**. ¿Entendiste la causa?

---

## 8.3 Prompting efectivo

Un buen prompt tiene **contexto + tarea + formato + restricciones**.

**❌ Pobre:** "dame código de pandas para ventas"

**✅ Efectivo:**
> "Tengo un DataFrame `df` con columnas: `fecha` (datetime), `region` (str), `producto`
> (str), `ventas` (float). Quiero la variación porcentual de ventas mensuales por región
> respecto al mes anterior. Dame el código con method chaining, comentado, y explica la
> lógica en 2 frases."

**Técnicas clave:** da contexto real (esquema, `df.head().to_dict()`), sé específico con el
formato ("en Polars", "como función"), pide que razone, itera con el error exacto, pide
alternativas ("¿hay una forma más eficiente?").

> ### ▶️ Practica ahora
> Escribe **dos** prompts para la misma tarea de tu dataset: uno pobre y uno efectivo (con
> contexto + tarea + formato). Compara las dos respuestas. ¿Cuánto mejora?

---

## 8.4 La IA como tutor (no como muleta)

En vez de "resuélveme esto", prueba:
> "Explícame por qué mi `groupby` devuelve NaN aquí y qué concepto debo entender para
> evitarlo la próxima vez."

Así aprendes en lugar de crear dependencia.

> ### ▶️ Practica ahora
> Elige un concepto del curso que no dominaste (window functions, p-valor, ELT…). Pídele al
> LLM que te lo explique **con una analogía** y resúmelo luego **con tus palabras**.

---

## 8.5 Verificación: la habilidad más importante

Nunca confíes a ciegas. Protocolo:
- **Código:** ejecútalo con un caso cuya respuesta **ya conoces**.
- **Números:** revisa órdenes de magnitud, totales, que sumen 100%, bordes (nulos, ceros).
- **SQL generado:** léelo. ¿El JOIN duplica filas? ¿el filtro va antes o después de agrupar?
- **Afirmaciones:** pide fuentes; los LLMs inventan funciones y citas.

> 💡 Truco: pide a la IA que **verifique su propio resultado por otro método**.

> ### ▶️ Practica ahora
> Pídele a la IA un total de tu dataset y luego pídele que lo **compruebe de otra forma**.
> Después verifícalo tú mismo/a en pandas. ¿Coinciden los tres?

---

## 8.6 Analizar datos con LLMs vía código (API)

Los LLMs sirven **dentro** de tu pipeline para datos no estructurados: clasificar tickets,
extraer entidades, analizar sentimiento, resumir reseñas.

```python
import anthropic
client = anthropic.Anthropic()   # API key en variable de entorno

def clasificar_sentimiento(texto):
    msg = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=10,
        messages=[{"role": "user",
                   "content": f"Clasifica el sentimiento como POSITIVO, NEUTRO o NEGATIVO. "
                              f"Responde solo una palabra.\n\nReseña: {texto}"}],
    )
    return msg.content[0].text.strip()

df["sentimiento"] = df["reseña"].apply(clasificar_sentimiento)
```

> 💡 Para muchas filas: procesa por lotes, controla costos, cachea y valida una muestra a mano.

> ### ▶️ Practica ahora
> (Conceptual) Diseña el prompt que usarías para **clasificar el sentimiento** de reseñas de
> producto en 3 categorías. ¿Qué instrucción evita que el modelo se explaye de más?

---

## 8.7 RAG y Text-to-SQL (para que sepas qué son)

- **RAG** (Retrieval-Augmented Generation): darle al LLM tus documentos como contexto para
  que responda basándose en ellos. Base de los "chatea con tus datos".
- **Text-to-SQL:** herramientas que generan SQL desde lenguaje natural. Útil, pero
  **verifica el SQL** y funciona mejor sobre datos bien modelados y documentados (¡otra
  razón para dbt!).

> ### ▶️ Practica ahora
> Pídele a un LLM que traduzca a SQL una pregunta en lenguaje natural sobre tu dataset (ej.
> "ventas por región el último mes"). **Audita** el SQL: ¿es correcto? ¿duplica filas?

---

## 8.8 Riesgos, ética y privacidad

Reglas que un profesional **no rompe**:
- 🔒 **Nunca pegues datos sensibles/PII** en herramientas públicas de IA.
- 🔒 **No subas credenciales** ni datos de clientes a un chat.
- 🧠 **Cuidado con alucinaciones:** funciones inventadas, cifras falsas.
- ⚖️ **Sesgo:** los modelos heredan sesgos; audita en decisiones que afectan personas.
- 📉 **No delegues el juicio:** la IA no conoce tu negocio ni las consecuencias.
- 📝 **Transparencia:** indica cuándo un análisis fue asistido por IA si tu organización lo requiere.

> ### ▶️ Practica ahora
> Escribe tu **política personal de uso de IA** en 5 reglas (qué SÍ harás, qué NUNCA harás).
> Guárdala en tu repo.

---

## 8.9 Un flujo de trabajo realista con IA

```
1. TÚ defines la pregunta y el enfoque.
2. IA → borrador de código/SQL con tu contexto.
3. TÚ ejecutas, VERIFICAS con un caso conocido y ajustas.
4. IA → te ayuda a depurar y optimizar.
5. TÚ interpretas los resultados (no se delega).
6. IA → te ayuda a redactar el resumen ejecutivo.
7. TÚ revisas, corriges y firmas. Eres responsable.
```

El patrón: **la IA acelera lo mecánico; tú aportas el criterio en las decisiones.**

---

## Reto del módulo (cierre)

Reescribe el resumen ejecutivo de tu informe de EDA (Módulo 06) con ayuda de IA: dale tus
hallazgos **verificados** y pídele un texto claro para un directivo. Luego **corrígelo tú**
(la IA no conoce tu negocio). Documenta qué cambiaste y por qué: esa diferencia es tu valor.

➡️ Siguiente: [Módulo 10 — Automatización y apps](../10-automatizacion-y-apps/README.md)
