# Editar video con Claude, sin CapCut — brief para la sesión que lo tome

> Escrito el 2026-09-04 desde la sesión del tablero (cero-agent), a pedido de Fernando:
> *«genera lo necesario para que otra sesión se encargue de los videos, quiero editar con
> Claude todo en vez de usar CapCut, basta con dar ciertos parámetros de cómo lo quiero,
> iterar sobre los videos y listo»*. Todo lo medido aquí viene del cajón de las tareas
> luna #290 y #291 (medido el 31-ago) y de esta Mac el 4-sep. Lo que no se midió está marcado.

## Qué quiere Fernando

Un flujo donde **él da parámetros** (qué clip, de qué segundo a qué segundo, dónde encuadrar,
qué color, logo sí/no) y **Claude renderiza con ffmpeg**, él mira, corrige el parámetro,
se vuelve a renderizar. Sin abrir CapCut. Dos lotes:

| Lote | luna | Material | Lo que hay que hacer |
|---|---|---|---|
| **Red Bull** | #290 | `~/Downloads/redbull` · 29 videos + 3 HEIC · 7.7 GB · ~76 min · 1920×1080 horizontal · tomas de 2–5 min · `IMG_9979.MOV` a 120 fps (cámara lenta, sirve de hook) | elegir el momento (**sólo él**), cortar a ≤ 90 s, reencuadrar a 9:16, color, subir **a mano** a @fercreek |
| **Social / Dance Leveling** | #291 | `~/Downloads/social` · 17 videos · 1.1 GB · ~11 min · 1920×1080 30 fps · 13 de 17 duran < 40 s · `IMG_0038` 82 s · `IMG_0039` 4:26 (ésa sí se corta) | reencuadrar a 9:16, color, **logo de Dance Leveling**, publicar en dance.leveling **por API** |

Verificado el 4-sep: las dos carpetas siguen ahí (32 y 17 archivos). Empezar por **#291**:
es más barato (casi no hay que elegir momentos) y deja el pipeline listo para #290.

## Paso 0 — lo único que Fernando tiene que hacer antes

**Exportar su preset de color de CapCut como `.cube`** y dejarlo en `assets/luts/fernando.cube`.
No hay un solo LUT propio en el disco (medido: los únicos `.cube` son de CapCut mismo). Con el
`.cube`, el color es EL SUYO y se aplica con `lut3d`; sin él, Claude inventaría un look, que es
justo lo que no quiere. `ffmpeg` 8.1.2 de esta Mac SÍ tiene `lut3d` (verificado con `-filters`).

## Lo que ya existe (≈35 %) — reusar, no reescribir

- `scripts/batch_render.py` — runner de lote con anti-duplicado y resume.
- `scripts/qa_short.py --batch` — mide audio, movimiento y duración de MP4 por carpeta (no mide color).
- `scripts/render_sleep.py:512-524` — sintaxis de grading ffmpeg ya probada en esta Mac.
- `scripts/render_sleep.py:526` — overlay RGBA por ffmpeg (el logo entra por aquí).
- Logo: `~/Documents/context/assets/dance-leveling/logos/dl-logo-galaxy-transparent.png`
  (1536×1024 RGBA, 82.9 % transparente). **Recortar al alfa real antes de componer**
  (`im.crop(im.getchannel("A").getbbox())`, trae ~24 px de margen muerto).
  NUNCA `dl-logo-galaxy-official.png` (fondo horneado) ni los `bl-*` (son Bachata Leveling).

## Lo que falta de verdad — es lo que esta sesión construye

1. **Ingesta:** nada en el ecosistema toma un video existente y lo transforma; todo genera
   video desde imágenes. Un `scripts/edit_clip.py` que lea un archivo de parámetros y arme
   la cadena ffmpeg: `trim → crop 9:16 (con pan por keyframes) → lut3d → overlay logo → encode`.
2. **Reencuadre 9:16 con seguimiento del bailarín:** lo más caro. Empezar SIN tracking: un
   `crop` fijo o un pan lineal entre dos keyframes que Fernando da a ojo (`x` al segundo A, `x`
   al segundo B). Tracking automático sólo si el pan manual no alcanza — y decidirlo viendo un
   render, no antes.
3. **Preview barato para iterar:** render a 540×960 y 2 Mbps para revisar; el final a 1080×1920.
   Iterar sobre el preview, no sobre el final.

⚠️ `ffmpeg` de esta Mac **no tiene `libfreetype`**: `drawtext` no sirve. Texto va por Pillow a
PNG y entra como overlay, igual que el logo.

## La interfaz: un archivo de parámetros por clip

Lo que Fernando dicta y Claude escribe. Un YAML por salida, en `data/edits/<nombre>.yaml`:

```yaml
in: ~/Downloads/social/IMG_0039.MOV
out: out/dl-0039-a.mp4
trim: {start: "1:12", end: "1:58"}      # ≤ 90 s si es Reel
frame: {ratio: "9:16", pan: [{t: 0, x: 620}, {t: 46, x: 880}]}   # x = borde izq del recorte en el original 1920
lut: assets/luts/fernando.cube           # paso 0
logo: {file: dl-logo-galaxy-transparent.png, pos: bottom-right, width_pct: 18, margin_px: 48}
speed: 1.0                               # 0.5 para el clip de 120 fps
audio: keep                              # keep | mute
preview: true                            # 540×960; false = final 1080×1920
```

Cambiar un número y volver a correr es la iteración. Lo que Fernando NO va a dar: el momento
exacto lo da él (sí), pero el ffmpeg, el crop y el encode los arma Claude.

## Definición de terminado

- **#291:** los 17 clips reencuadrados con el LUT de Fernando y el logo, revisados por él en
  preview, y los finales publicados en dance.leveling por el publicador que YA existe
  (`cero/cero-content/scripts/dance-leveling_publish.py:78-79`, ig_id `17841438322438397`,
  launchd `com.dance-leveling.ig-daily-publisher` 12:00 MTY). Metricool NO la toca.
- **#290:** los momentos que él elija, cortados a ≤ 90 s, con el mismo LUT. **La subida a
  @fercreek es a mano siempre** (cuenta personal, la API de Meta no publica ahí); su pool
  `cero-agent/pools/fercreek-feed.json` es un recordatorio por Telegram, no autopublicación.

## Prompt para abrir la sesión (pegar tal cual)

```
Abre ~/Documents/loop-video-maker. Lee specs/video-edit/BRIEF.md completo. Voy a editar
video con Claude en vez de CapCut: yo doy parámetros por clip (YAML), tú renderizas con
ffmpeg, yo reviso el preview y corregimos. Empieza por luna #291 (~/Downloads/social).
Antes de escribir código: confirma que existe assets/luts/fernando.cube; si no, pídemelo y
no inventes un look. Primer entregable: UN clip corto (el más corto de la carpeta) en
preview 540×960 con reencuadre 9:16 fijo, LUT y logo — lo veo y de ahí seguimos.
```

## Lo que esta sesión no decide

- Qué momento de cada toma de Red Bull vale — es de Fernando.
- Si se necesita tracking automático — se decide con un render en la mano.
- Si el look final es el del `.cube` o hay que ajustarlo — es de Fernando, viendo el preview.
