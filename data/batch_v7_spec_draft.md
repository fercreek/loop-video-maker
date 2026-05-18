# Spec Draft Batch v7 — Shorts @VersiculoDeDios
> Fecha: 2026-05-22 | Estado: BORRADOR — refinar con métricas reales de v6
> Período objetivo: Jun 2–11 2026 (10 días, 1 video/día, 6am MTY)

---

## Resumen ejecutivo

| Campo | v6 | v7 (propuesto) |
|-------|-----|----------------|
| Videos | 10 | 10 |
| Período | May 12–21 | Jun 2–11 |
| Horario | 5am MTY | **6am MTY** ← experimento |
| Hook style | Pregunta (¿...?) | Mixto: pregunta + 2da persona directa |
| CTA | Escribe AMÉN | Escribe AMÉN (mantener) |
| Subtítulos | 6 palabras/chunk | 6 palabras/chunk (mantener) |
| Hook duration | 3.5s | 3.5s (mantener) |
| Fondos | Únicos por Short | Únicos por Short (mantener) |
| Experimento nuevo | — | Slide versículo final (5s) |

> **Esperar métricas v6 antes de confirmar este spec.** Si dormir_001 y ansiedad_001
> lideran con amplio margen, mantener el enfoque en necesidades urgentes/nocturnas.

---

## Quick wins heredados de v6 (todos se mantienen)

- [x] Subtítulos 6 palabras por chunk
- [x] CTA: 'Escribe AMÉN si esto te llegó al corazón'
- [x] Hook duration: 3.5s
- [x] Fondos únicos por Short (sin repetición dentro del batch)
- [x] Voz ElevenLabs ES-MX (Daniel/Antonio)
- [x] Música: YT Audio Library / Kevin MacLeod CC-BY / MusicGen local

---

## Experimento nuevo — Slide versículo final

**Qué:** Agregar un slide final (5 segundos) con el versículo clave en texto grande centrado,
sobre fondo oscuro con leve vignette, antes del fade out.

**Por qué:** Los Shorts con retención >100% en el canal tienen loop natural. Un slide de versículo
claro al final puede:
1. Invitar al viewer a volver a ver desde el inicio (boost retención)
2. Servir como screenshot compartible (boost orgánico en WhatsApp/IG)
3. Reforzar la identidad de marca

**Cómo medir éxito:**
- Comparar retención promedio v7 vs v6 (mismo tema, mismo tipo de hook)
- Comparar compartidos/guardados v7 vs v6 en Facebook

**Implementación:** Agregar en `render_short.py`:
```python
# Slide final: versículo key, 5s, texto centrado, fondo oscuro
# Parámetro: --final-slide True/False (default True para v7)
```

---

## 10 oraciones propuestas para v7

Temas distintos a los 10 de v6 (v6 cubrió: tiempos difíciles, dormir, ansiedad, milagro,
mañana, soledad, hijos, corazón roto, tristeza, trabajo).

| # | ID propuesto | Hook | Tema | Tipo hook | Banco versículos |
|---|-------------|------|------|-----------|-----------------|
| 1 | sanacion_001 | 'Dios quiere sanarte hoy — recíbelo' | Sanación física/emocional | 2da persona | `data/versiculos/sanacion.json` |
| 2 | prosperidad_001 | '¿Sientes que nada te alcanza?' | Provisión/prosperidad | Pregunta | `data/versiculos/provision.json` |
| 3 | gratitud_001 | 'Gracias, Señor, aunque no lo entiendo' | Gratitud en la prueba | Afirmación | `data/versiculos/gratitud.json` |
| 4 | perdon_001 | '¿Hay alguien a quien no puedes perdonar?' | Perdón/liberación | Pregunta | (nuevo JSON pendiente) |
| 5 | paz_001 | 'Dios tiene paz para ti ahora mismo' | Paz interior | 2da persona | `data/versiculos/paz.json` |
| 6 | familia_001 | 'Esta oración es por toda tu familia' | Familia/protección | Afirmación | `data/versiculos/amor.json` |
| 7 | fe_001 | '¿Estás perdiendo la fe?' | Fe en la oscuridad | Pregunta | `data/versiculos/fe.json` |
| 8 | victoria_001 | 'Eres más que vencedor — créelo' | Victoria espiritual | 2da persona | `data/versiculos/victoria.json` |
| 9 | manana_002 | 'Que este día sea diferente' | Oración del amanecer v2 | Afirmación | `data/versiculos/esperanza.json` |
| 10 | proteccion_001 | '¿Sientes que el enemigo te ataca?' | Protección/guerra espiritual | Pregunta | `data/versiculos/fuerza.json` |

### Notas sobre la selección
- **sanacion_001** como apertura: nicho alto, banco de versículos ya listo en repo
- **prosperidad_001** cubre el ángulo económico que faltó en v6 (trabajo_001 fue milagro genérico)
- **manana_002** replica manana_001 de v6 con hook diferente — si v6 tiene buen resultado, vale duplicar el tema
- **perdon_001** requiere crear `data/versiculos/perdon.json` antes del render
- Mezcla 4 hooks pregunta + 3 afirmación + 3 segunda persona → distribuye para probar H1 de v6

---

## Orden estratégico de publicación

| Día | ID | Lógica |
|-----|-----|--------|
| Jun 2 (mar) | sanacion_001 | Tema fuerte para abrir — alta intención de búsqueda |
| Jun 3 (mié) | prosperidad_001 | Inicio de semana laboral → necesidad financiera activa |
| Jun 4 (jue) | paz_001 | Mid-week stress → paz como respuesta |
| Jun 5 (vie) | fe_001 | Viernes de reflexión espiritual |
| Jun 6 (sáb) | gratitud_001 | Sábado devocional / congregacional |
| Jun 7 (dom) | familia_001 | Domingo → familia y culto |
| Jun 8 (lun) | victoria_001 | Lunes motivacional — inicio de semana |
| Jun 9 (mar) | manana_002 | Martes rutina devocional matutina |
| Jun 10 (mié) | perdon_001 | Mid-week emocional pesado |
| Jun 11 (jue) | proteccion_001 | Cierre del batch — tema de alto impacto |

---

## Checklist pre-producción

- [ ] Confirmar métricas v6 y ajustar este spec si hay sorpresas
- [ ] Crear `data/versiculos/perdon.json` (versículos de perdón — pendiente)
- [ ] Seleccionar fondos únicos (10 fondos distintos a los usados en v6)
  - Ver output mflux disponibles en `output/fondos_mflux/`
  - Generar fondos faltantes: `python3 scripts/generate_fondos_mflux.py --count 2 --format 9:16`
- [ ] Revisar que `render_short.py` soporte `--final-slide` para el experimento
- [ ] Programar publicación: 6am MTY (verificar offset UTC en scheduler)
- [ ] Verificar ElevenLabs créditos disponibles (10 oraciones × ~300 palabras ≈ 3,000 chars)
- [ ] Anti-strike: confirmar música libre de derechos para los 10 fondos de audio

---

## Versículos clave sugeridos por oración

| ID | Versículo principal | Referencia |
|----|---------------------|-----------|
| sanacion_001 | "Yo soy Jehová tu sanador" | Éxodo 15:26 |
| prosperidad_001 | "Mi Dios suplirá todo lo que os falta" | Filipenses 4:19 |
| gratitud_001 | "Dad gracias en todo" | 1 Tesalonicenses 5:18 |
| perdon_001 | "Antes sed benignos unos con otros... perdonándoos" | Efesios 4:32 |
| paz_001 | "La paz de Dios que sobrepasa todo entendimiento" | Filipenses 4:7 |
| familia_001 | "En cuanto a mí y a mi casa, serviremos a Jehová" | Josué 24:15 |
| fe_001 | "La fe es la certeza de lo que se espera" | Hebreos 11:1 |
| victoria_001 | "Somos más que vencedores" | Romanos 8:37 |
| manana_002 | "Este es el día que hizo Jehová; nos gozaremos" | Salmos 118:24 |
| proteccion_001 | "Jehová es mi luz y mi salvación; ¿a quién temeré?" | Salmos 27:1 |

---

## Proyección YPP — impacto de Shorts v6+v7

> Referencia: canal necesita 3,000,000 vistas Shorts en 90 días para YPP por Shorts.
> Actual (Apr 27): ~159K vistas en 90 días → muy lejos del objetivo.
> **Foco real:** Long-form watch time sigue siendo el camino más realista (ver CLAUDE.md).

Los Shorts siguen siendo valiosos para:
- Crecer suscriptores (funnel hacia long-form)
- Mantener engagement del algoritmo
- Canalization a videos de 60/120min via end screens

Considerar agregar end screen en v7 apuntando al video long-form del mismo tema.
Ej: sanacion_001 → fin → "Ver oración completa de 60 min →" (link a sanacion_60min cuando exista)
