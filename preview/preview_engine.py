from __future__ import annotations
"""
Motor de preview HTML para versículos bíblicos.
Genera HTML autocontenido con imagen y audio en base64.
"""

import base64
import os
from typing import Optional


def _file_to_base64(path: str) -> str:
    """Convierte un archivo a string base64."""
    if not path or not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def _get_audio_mime(path: str) -> str:
    """Detecta el tipo MIME del audio."""
    if path.endswith(".mp3"):
        return "audio/mpeg"
    elif path.endswith(".wav"):
        return "audio/wav"
    elif path.endswith(".ogg"):
        return "audio/ogg"
    return "audio/wav"


def generar_preview_html(
    imagen_path: str,
    musica_path: str,
    versiculos: list[dict],
    segundos_por_versiculo: int = 12,
    config_texto: Optional[dict] = None,
) -> str:
    """
    Genera HTML completo autocontenido con preview del video.

    Args:
        imagen_path: Path a la imagen de fondo
        musica_path: Path al archivo de audio
        versiculos: Lista de dicts con keys 'texto' y 'referencia'
        segundos_por_versiculo: Duración de cada versículo en segundos
        config_texto: Dict con configuración de texto (posicion, tamano, color, etc.)

    Returns:
        String HTML completo
    """
    if config_texto is None:
        config_texto = {}

    posicion = config_texto.get("posicion", "bottom")
    tamano_versiculo = config_texto.get("tamano", 52)
    color_texto = config_texto.get("color_texto", "#FFFFFF")
    color_referencia = config_texto.get("color_referencia", "#E8D5A3")
    mostrar_referencia = config_texto.get("mostrar_referencia", True)
    fade_duration = config_texto.get("fade_duration", 1.5)

    # Convertir archivos a base64
    img_b64 = _file_to_base64(imagen_path)
    audio_b64 = _file_to_base64(musica_path)
    audio_mime = _get_audio_mime(musica_path) if musica_path else "audio/wav"

    # Posición vertical del texto
    if posicion == "top":
        text_align_css = "top: 8%;"
    elif posicion == "center":
        text_align_css = "top: 50%; transform: translateY(-50%);"
    else:
        text_align_css = "bottom: 8%;"

    # Serializar versículos para JS
    verses_js = "[\n"
    for v in versiculos:
        texto = v.get("texto", "").replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
        ref = v.get("referencia", "").replace("\\", "\\\\").replace('"', '\\"')
        verses_js += f'  {{"texto": "{texto}", "referencia": "{ref}"}},\n'
    verses_js += "]"

    img_bg = f"data:image/jpeg;base64,{img_b64}" if img_b64 else ""
    audio_src = f"data:{audio_mime};base64,{audio_b64}" if audio_b64 else ""

    # Fix: audio tag y sync en JS
    audio_src_attr = f'src="{audio_src}"' if audio_src else ""
    has_audio_js = "true" if audio_src else "false"

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=EB+Garamond:ital@1&family=Cinzel&display=swap');

  * {{ margin: 0; padding: 0; box-sizing: border-box; }}

  .preview-root {{
    width: 100%;
    max-width: 960px;
    margin: 0 auto;
    font-family: sans-serif;
    color: #e0e0e0;
    background: #111;
    border-radius: 12px;
    overflow: hidden;
  }}

  .canvas-wrapper {{
    position: relative;
    width: 100%;
    padding-top: 56.25%; /* 16:9 */
    background: #000;
    overflow: hidden;
  }}

  .canvas-bg {{
    position: absolute;
    top: 0; left: 0; width: 100%; height: 100%;
    background-image: url('{img_bg}');
    background-size: cover;
    background-position: center;
    background-color: #0a0a2e;
  }}

  .verse-overlay {{
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
    {text_align_css}
    width: 75%;
    text-align: center;
    z-index: 10;
  }}

  .verse-bg {{
    background: rgba(0, 0, 0, 0.4);
    padding: 24px 32px;
    border-radius: 8px;
    display: inline-block;
    max-width: 100%;
    opacity: 0;
    transition: opacity {fade_duration}s ease-in-out;
  }}

  .verse-bg.visible {{
    opacity: 1;
  }}

  .verse-text {{
    font-family: 'EB Garamond', 'Georgia', serif;
    font-style: italic;
    font-size: {tamano_versiculo * 0.55}px;
    color: {color_texto};
    line-height: 1.5;
    text-shadow: 1px 2px 4px rgba(0,0,0,0.8);
    margin-bottom: 12px;
  }}

  .verse-separator {{
    width: 60px;
    height: 1px;
    background: {color_referencia};
    margin: 12px auto;
    opacity: 0.7;
  }}

  .verse-ref {{
    font-family: 'Cinzel', 'Times New Roman', serif;
    font-size: {28 * 0.55}px;
    color: {color_referencia};
    letter-spacing: 2px;
    text-shadow: 1px 1px 3px rgba(0,0,0,0.8);
  }}

  .controls {{
    padding: 12px 16px;
    background: #1a1a1a;
  }}

  .timeline {{
    width: 100%;
    height: 6px;
    background: #333;
    border-radius: 3px;
    cursor: pointer;
    position: relative;
    margin-bottom: 10px;
  }}

  .timeline-fill {{
    height: 100%;
    background: linear-gradient(90deg, #E8D5A3, #FFD700);
    border-radius: 3px;
    width: 0%;
    transition: width 0.3s linear;
    pointer-events: none;
  }}

  .timeline-handle {{
    position: absolute;
    top: 50%;
    transform: translate(-50%, -50%);
    width: 14px;
    height: 14px;
    background: #FFD700;
    border-radius: 50%;
    cursor: grab;
    left: 0%;
    transition: left 0.3s linear;
    box-shadow: 0 0 4px rgba(0,0,0,0.5);
  }}

  .timeline:hover .timeline-handle {{
    transform: translate(-50%, -50%) scale(1.3);
  }}

  .controls-row {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
  }}

  .btn {{
    background: none;
    border: 1px solid #555;
    color: #e0e0e0;
    padding: 6px 12px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 13px;
    transition: all 0.2s;
  }}

  .btn:hover {{
    background: #333;
    border-color: #E8D5A3;
    color: #E8D5A3;
  }}

  .btn.active {{
    background: #E8D5A3;
    color: #111;
    border-color: #E8D5A3;
  }}

  .info-text {{
    font-size: 13px;
    color: #aaa;
    white-space: nowrap;
  }}

  .speed-group {{
    display: flex;
    gap: 4px;
  }}
</style>
</head>
<body>
<div class="preview-root" id="previewRoot">
  <div class="canvas-wrapper">
    <div class="canvas-bg"></div>
    <div class="verse-overlay">
      <div class="verse-bg" id="verseBg">
        <div class="verse-text" id="verseText"></div>
        {"" if not mostrar_referencia else '<div class="verse-separator" id="verseSep"></div><div class="verse-ref" id="verseRef"></div>'}
      </div>
    </div>
  </div>

  <div class="controls">
    <div class="timeline" id="timeline">
      <div class="timeline-fill" id="timelineFill"></div>
      <div class="timeline-handle" id="timelineHandle"></div>
    </div>
    <div class="controls-row">
      <div style="display:flex; gap:4px; align-items:center;">
        <button class="btn" id="btnPrev" title="Anterior">&#9664;&#9664;</button>
        <button class="btn" id="btnPlay" title="Play/Pause">&#9654; Play</button>
        <button class="btn" id="btnNext" title="Siguiente">&#9654;&#9654;</button>
      </div>
      <span class="info-text" id="verseCounter">0 / 0</span>
      <span class="info-text" id="timeDisplay">0:00 / 0:00</span>
      <div class="speed-group">
        <button class="btn active" data-speed="1">1x</button>
        <button class="btn" data-speed="2">2x</button>
        <button class="btn" data-speed="4">4x</button>
      </div>
    </div>
  </div>
</div>

<audio id="audioPlayer" preload="auto" {audio_src_attr}></audio>

<script>
(function() {{
  const verses = {verses_js};
  const secPerVerse = {segundos_por_versiculo};
  const fadeDur = {fade_duration};
  const showRef = {'true' if mostrar_referencia else 'false'};
  const hasAudio = {has_audio_js};

  const totalDuration = verses.length * secPerVerse;

  const verseBg = document.getElementById('verseBg');
  const verseText = document.getElementById('verseText');
  const verseRef = document.getElementById('verseRef');
  const btnPlay = document.getElementById('btnPlay');
  const btnPrev = document.getElementById('btnPrev');
  const btnNext = document.getElementById('btnNext');
  const verseCounter = document.getElementById('verseCounter');
  const timeDisplay = document.getElementById('timeDisplay');
  const timeline = document.getElementById('timeline');
  const timelineFill = document.getElementById('timelineFill');
  const timelineHandle = document.getElementById('timelineHandle');
  const audio = document.getElementById('audioPlayer');
  const speedBtns = document.querySelectorAll('[data-speed]');

  let playing = false;
  let currentTime = 0;
  let speed = 1;
  let lastTimestamp = null;
  let currentVerseIdx = -1;
  let dragging = false;

  function formatTime(s) {{
    const m = Math.floor(s / 60);
    const sec = Math.floor(s % 60);
    return m + ':' + (sec < 10 ? '0' : '') + sec;
  }}

  function updateVerse() {{
    if (verses.length === 0) return;

    const idx = Math.min(Math.floor(currentTime / secPerVerse), verses.length - 1);
    const timeInVerse = currentTime - (idx * secPerVerse);

    // Update counter
    verseCounter.textContent = (idx + 1) + ' / ' + verses.length;
    timeDisplay.textContent = formatTime(currentTime) + ' / ' + formatTime(totalDuration);

    // Timeline
    const pct = totalDuration > 0 ? (currentTime / totalDuration) * 100 : 0;
    timelineFill.style.width = pct + '%';
    timelineHandle.style.left = pct + '%';

    if (idx !== currentVerseIdx) {{
      // Fade out old
      verseBg.classList.remove('visible');

      setTimeout(function() {{
        verseText.textContent = verses[idx].texto;
        if (showRef && verseRef) {{
          verseRef.textContent = '— ' + verses[idx].referencia + ' —';
        }}
        // Fade in new
        verseBg.classList.add('visible');
      }}, fadeDur * 500); // half the fade duration for transition

      currentVerseIdx = idx;
    }} else {{
      // Handle fade at boundaries
      if (timeInVerse < fadeDur) {{
        verseBg.classList.add('visible');
      }} else if (timeInVerse > secPerVerse - fadeDur) {{
        verseBg.classList.remove('visible');
      }} else {{
        verseBg.classList.add('visible');
      }}
    }}
  }}

  function tick(timestamp) {{
    if (!playing) return;

    if (lastTimestamp === null) lastTimestamp = timestamp;
    const delta = (timestamp - lastTimestamp) / 1000;
    lastTimestamp = timestamp;

    currentTime += delta * speed;

    if (currentTime >= totalDuration) {{
      currentTime = 0;
      currentVerseIdx = -1;
    }}

    // Sync audio
    if (hasAudio && audio.readyState >= 2) {{
      if (Math.abs(audio.currentTime - currentTime) > 1) {{
        audio.currentTime = currentTime;
      }}
    }}

    updateVerse();
    requestAnimationFrame(tick);
  }}

  function play() {{
    playing = true;
    lastTimestamp = null;
    btnPlay.innerHTML = '&#9646;&#9646; Pausa';

    if (hasAudio && audio.readyState >= 2) {{
      audio.playbackRate = speed;
      audio.currentTime = currentTime;
      audio.play().catch(function() {{}});
    }}

    requestAnimationFrame(tick);
  }}

  function pause() {{
    playing = false;
    btnPlay.innerHTML = '&#9654; Play';
    if (hasAudio) audio.pause();
  }}

  btnPlay.addEventListener('click', function() {{
    if (playing) pause(); else play();
  }});

  btnPrev.addEventListener('click', function() {{
    const idx = Math.floor(currentTime / secPerVerse);
    currentTime = Math.max(0, (idx - 1)) * secPerVerse;
    currentVerseIdx = -1;
    updateVerse();
    if (hasAudio && audio.readyState >= 2) audio.currentTime = currentTime;
  }});

  btnNext.addEventListener('click', function() {{
    const idx = Math.floor(currentTime / secPerVerse);
    const nextIdx = (idx + 1) >= verses.length ? 0 : idx + 1;
    currentTime = nextIdx * secPerVerse;
    currentVerseIdx = -1;
    updateVerse();
    if (hasAudio && audio.readyState >= 2) audio.currentTime = currentTime;
  }});

  // Speed buttons
  speedBtns.forEach(function(btn) {{
    btn.addEventListener('click', function() {{
      speed = parseInt(btn.dataset.speed);
      speedBtns.forEach(function(b) {{ b.classList.remove('active'); }});
      btn.classList.add('active');
      if (audio.src && audio.readyState >= 2) audio.playbackRate = speed;
    }});
  }});

  // Timeline drag
  function seekFromEvent(e) {{
    const rect = timeline.getBoundingClientRect();
    const x = Math.max(0, Math.min(e.clientX - rect.left, rect.width));
    const pct = x / rect.width;
    currentTime = pct * totalDuration;
    currentVerseIdx = -1;
    updateVerse();
    if (hasAudio && audio.readyState >= 2) audio.currentTime = currentTime;
  }}

  timeline.addEventListener('mousedown', function(e) {{
    dragging = true;
    seekFromEvent(e);
  }});

  document.addEventListener('mousemove', function(e) {{
    if (dragging) seekFromEvent(e);
  }});

  document.addEventListener('mouseup', function() {{
    dragging = false;
  }});

  // Init: show first verse
  if (verses.length > 0) {{
    verseText.textContent = verses[0].texto;
    if (showRef && verseRef) {{
      verseRef.textContent = '— ' + verses[0].referencia + ' —';
    }}
    verseBg.classList.add('visible');
    currentVerseIdx = 0;
    verseCounter.textContent = '1 / ' + verses.length;
    timeDisplay.textContent = '0:00 / ' + formatTime(totalDuration);
  }}
}})();
</script>
</body>
</html>"""

    return html
