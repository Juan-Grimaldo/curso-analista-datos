# ✅ Checklist del analista de datos

Una lista práctica para no saltarte pasos en cualquier análisis.

## Antes de empezar
- [ ] ¿Cuál es la **pregunta de negocio** exacta? ¿Quién la usará y para qué decisión?
- [ ] ¿Qué datos necesito y de dónde vienen? ¿Tengo permiso para usarlos?
- [ ] ¿Cuál sería una respuesta "buena"? ¿Qué haría cambiar la decisión?

## Al recibir los datos
- [ ] Revisar forma (`shape`), tipos (`info`), primeras filas (`head`).
- [ ] Contar nulos y duplicados.
- [ ] Buscar valores imposibles (negativos, fechas futuras, categorías raras).
- [ ] Entender qué significa cada columna (diccionario de datos).
- [ ] Guardar los datos crudos como **solo lectura** (`data/raw/`).

## Durante la limpieza
- [ ] Documentar cada decisión (por qué relleno/elimino/transformo).
- [ ] No modificar los datos a mano: todo por código.
- [ ] Verificar tipos (fechas como datetime, números como número).
- [ ] Guardar el resultado limpio aparte (`data/processed/`).

## Durante el análisis
- [ ] Empezar con EDA antes de conclusiones.
- [ ] Comparar media vs mediana (asimetría, outliers).
- [ ] Investigar outliers en vez de borrarlos por reflejo.
- [ ] Preguntar "¿qué más podría explicar esto?" antes de afirmar causa.
- [ ] Revisar por subgrupos (paradoja de Simpson).

## Al comunicar
- [ ] Un mensaje claro por gráfico; título = conclusión.
- [ ] Gráfico correcto para el tipo de dato.
- [ ] Ejes de barras empiezan en 0; unidades y fuente visibles.
- [ ] Estructura narrativa: contexto → hallazgo → recomendación.
- [ ] Incluir "qué NO puedo concluir y por qué".

## Al usar IA
- [ ] Dar contexto real (esquema, tipos) en el prompt.
- [ ] **Verificar** todo código y número con un caso conocido.
- [ ] No pegar datos sensibles/PII en herramientas públicas.
- [ ] Yo soy responsable del resultado final.

## Antes de entregar
- [ ] ¿Es reproducible? (dependencias fijas, rutas relativas, README).
- [ ] ¿Está en Git con commits claros?
- [ ] ¿El README explica qué hace y cómo ejecutarlo?
- [ ] ¿Los números cuadran? (totales, porcentajes que suman 100%).
