from __future__ import annotations
"""
Motor de preview HTML para versículos bíblicos.

Cambios vs. versión anterior:
- Audio: usa URL /file= de Gradio en lugar de base64 (evita cuelgue con WAVs grandes)
- Audio trim: genera musica_preview.wav de 90s máx para carga rápida
- Play button: usa oncanplaythrough en lugar de readyState >= 2 (fix autoplay)
- Ken Burns: animación CSS en el fondo para simular el efecto del video real
- Badge "Vista previa · Baja calidad" en esquina superior derecha
"""

import os
import shutil
import wave
from typing import Optional


def _file_to_base64(path: str) -> str:
    """Convierte un archivo a string base64 (solo para imagen — audio usa URL)."""
    import base64
    if not path or not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def _get_audio_mime(path: str) -> str:
    """Detecta el tipo MIME del audio."""
    if not path:
        return "audio/wav"
    lp = path.lower()
    if lp.endswith(".mp3"):
        return "audio/mpeg"
    elif lp.endswith(".ogg"):
        return "audio/ogg"
    return "audio/wav"


def _trim_audio_for_preview(audio_path: str, max_sec: int = 90) -> str:
    """
    Crea un WAV recortado de max_sec segundos en el mismo directorio.
    Retorna la ruta del archivo recortado (o el original si ya es corto).
    Llama desde generar_preview_html(); nunca falla — si hay error devuelve original.
    """
    if not audio_path or not os.path.exists(audio_path):
        return audio_path

    out_dir = os.path.dirname(audio_path)
    preview_path = os.path.join(out_dir, "musica_preview.wav")

    try:
        with wave.open(audio_path, "r") as src:
            sr = src.getframerate()
            channels = src.getnchannels()
            sampwidth = src.getsampwidth()
            frames_total = src.getnframes()
            frames_max = sr * max_sec

            if frames_total <= frames_max:
                # Already short enough — copy as-is
                shutil.copy2(audio_path, preview_path)
                return preview_path

            data = src.readframes(frames_max)

        with wave.open(preview_path, "w") as dst:
            dst.setnchannels(channels)
            dst.setsampwidth(sampwidth)
            dst.setframerate(sr)
            dst.writeframes(data)

        return preview_path
    except Exception:
        return audio_path


def generar_preview_html(
    imagen_path: str,
    musica_path: str,
    versiculos: list[dict],
    segundos_por_versiculo: int = 12,
    config_texto: Optional[dict] = None,
) -> str:
    """
    Genera HTML completo con preview del video.

    Audio: usa /file= URL de Gradio (no base64) + clip recortado a 90s.
    Imagen: embebida como base64 (imágenes son pequeñas ~100-200KB).
    """
    if config_texto is None:
        config_texto = {}

    posicion = config_texto.get("posicion", "bottom")
    tamano_versiculo = config_texto.get("tamano", 52)
    color_texto = config_texto.get("color_texto", "#FFFFFF")
    color_referencia = config_texto.get("color_referencia", "#E8D5A3")
    mostrar_referencia = config_texto.get("mostrar_referencia", True)
    fade_duration = config_texto.get("fade_duration", 1.5)

    # Imagen: base64 (pequeña, siempre funciona)
    img_b64 = _file_to_base64(imagen_path)
    img_bg = f"data:image/jpeg;base64,{img_b64}" if img_b64 else ""

    # Audio: trim a 90s + usar URL /file= de Gradio (no base64)
    audio_url = ""
    has_audio_js = "false"
    if musica_path and os.path.exists(musica_path):
        preview_audio = _trim_audio_for_preview(musica_path, max_sec=90)
        # Gradio sirve archivos del output_dir via /file=<absolute_path>
        audio_url = f"/file={preview_audio}"
        has_audio_js = "true"

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

  /* Ken Burns: simula el zoom-in lento del video real */
  @keyframes kenburns {{
    0%   {{ transform: scale(1.0); }}
    100% {{ transform: scale(1.08); }}
  }}

  .canvas-bg {{
    position: absolute;
    top: 0; left: 0; width: 100%; height: 100%;
    background-image: url('{img_bg}');
    background-size: cover;
    background-position: center;
    background-color: #0a0a2e;
    /* Animación activa solo cuando el preview está reproduciendo */
    transform-origin: center center;
  }}

  .canvas-bg.playing {{
    animation: kenburns 30s linear infinite alternate;
  }}

  /* Badge de calidad */
  .quality-badge {{
    position: absolute;
    top: 8px;
    right: 8px;
    background: rgba(0,0,0,0.65);
    color: #999;
    font-size: 11px;
    padding: 3px 8px;
    border-radius: 4px;
    z-index: 20;
    pointer-events: none;
    letter-spacing: 0.3px;
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

  /* Audio status hint */
  .audio-hint {{
    font-size: 11px;
    color: #666;
    text-align: center;
    padding: 4px 0 0;
  }}
</style>
</head>
<body>
<div class="preview-root" id="previewRoot">
  <div class="canvas-wrapper">
    <div class="canvas-bg" id="canvasBg"></div>
    <div class="quality-badge">Vista previa · Baja calidad</div>
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
      <span class="info-text" id="verseCounter">1 / {len(versiculos)}</span>
      <span class="info-text" id="timeDisplay">0:00 / 0:00</span>
      <div class="speed-group">
        <button class="btn active" data-speed="1">1x</button>
        <button class="btn" data-speed="2">2x</button>
        <button class="btn" data-speed="4">4x</button>
      </div>
    </div>
    {"<p class='audio-hint' id='audioHint'>&#9654; Haz clic en Play para escuchar la música</p>" if has_audio_js == 'true' else ""}
  </div>
</div>

<!-- Audio: URL directa de Gradio, clip de 90s máx para carga rápida -->
{"<audio id='audioPlayer' preload='auto' src='" + audio_url + "'></audio>" if audio_url else "<audio id='audioPlayer'></audio>"}

<script>
(function() {{
  var verses = {verses_js};
  var secPerVerse = {segundos_por_versiculo};
  var fadeDur = {fade_duration};
  var showRef = {'true' if mostrar_referencia else 'false'};
  var hasAudio = {has_audio_js};

  var totalDuration = verses.length * secPerVerse;

  var canvasBg = document.getElementById('canvasBg');
  var verseBg = document.getElementById('verseBg');
  var verseText = document.getElementById('verseText');
  var verseRef = document.getElementById('verseRef');
  var btnPlay = document.getElementById('btnPlay');
  var btnPrev = document.getElementById('btnPrev');
  var btnNext = document.getElementById('btnNext');
  var verseCounter = document.getElementById('verseCounter');
  var timeDisplay = document.getElementById('timeDisplay');
  var timeline = document.getElementById('timeline');
  var timelineFill = document.getElementById('timelineFill');
  var timelineHandle = document.getElementById('timelineHandle');
  var audio = document.getElementById('audioPlayer');
  var speedBtns = document.querySelectorAll('[data-speed]');
  var audioHint = document.getElementById('audioHint');

  var playing = false;
  var currentTime = 0;
  var speed = 1;
  var lastTimestamp = null;
  var currentVerseIdx = -1;
  var dragging = false;
  var audioReady = false;

  // Audio ready detection — handles both cached and streamed audio
  if (hasAudio && audio) {{
    audio.addEventListener('canplaythrough', function() {{
      audioReady = true;
      if (audioHint) audioHint.style.display = 'none';
    }});
    audio.addEventListener('error', function(e) {{
      console.warn('Preview audio error:', e);
      audioReady = false;
    }});
    // Some browsers fire canplay not canplaythrough — accept either
    audio.addEventListener('canplay', function() {{
      audioReady = true;
    }});
  }}

  function formatTime(s) {{
    var m = Math.floor(s / 60);
    var sec = Math.floor(s % 60);
    return m + ':' + (sec < 10 ? '0' : '') + sec;
  }}

  function updateVerse() {{
    if (verses.length === 0) return;

    var idx = Math.min(Math.floor(currentTime / secPerVerse), verses.length - 1);
    var timeInVerse = currentTime - (idx * secPerVerse);

    verseCounter.textContent = (idx + 1) + ' / ' + verses.length;
    timeDisplay.textContent = formatTime(currentTime) + ' / ' + formatTime(totalDuration);

    var pct = totalDuration > 0 ? (currentTime / totalDuration) * 100 : 0;
    timelineFill.style.width = pct + '%';
    timelineHandle.style.left = pct + '%';

    if (idx !== currentVerseIdx) {{
      verseBg.classList.remove('visible');
      var capturedIdx = idx;
      setTimeout(function() {{
        verseText.textContent = verses[capturedIdx].texto;
        if (showRef && verseRef) {{
          verseRef.textContent = '— ' + verses[capturedIdx].referencia + ' —';
        }}
        verseBg.classList.add('visible');
      }}, fadeDur * 500);
      currentVerseIdx = idx;
    }} else {{
      if (timeInVerse < fadeDur || timeInVerse <= secPerVerse - fadeDur) {{
        verseBg.classList.add('visible');
      }} else {{
        verseBg.classList.remove('visible');
      }}
    }}
  }}

  function tryPlayAudio() {{
    if (!hasAudio || !audio) return;
    audio.playbackRate = speed;
    audio.currentTime = currentTime % (audio.duration || secPerVerse * verses.length);
    var promise = audio.play();
    if (promise !== undefined) {{
      promise.catch(function(e) {{
        // Autoplay blocked — user already clicked, so this usually succeeds
        console.warn('Audio play blocked:', e.message);
      }});
    }}
  }}

  function tick(timestamp) {{
    if (!playing) return;

    if (lastTimestamp === null) lastTimestamp = timestamp;
    var delta = (timestamp - lastTimestamp) / 1000;
    lastTimestamp = timestamp;

    currentTime += delta * speed;

    if (currentTime >= totalDuration) {{
      currentTime = 0;
      currentVerseIdx = -1;
    }}

    // Sync audio drift (> 1.5s off)
    if (hasAudio && audio && audioReady) {{
      var audioClamped = currentTime % (audio.duration || totalDuration);
      if (Math.abs(audio.currentTime - audioClamped) > 1.5) {{
        audio.currentTime = audioClamped;
      }}
    }}

    updateVerse();
    requestAnimationFrame(tick);
  }}

  function play() {{
    playing = true;
    lastTimestamp = null;
    btnPlay.innerHTML = '&#9646;&#9646; Pausa';
    canvasBg.classList.add('playing');
    tryPlayAudio();
    requestAnimationFrame(tick);
  }}

  function pause() {{
    playing = false;
    btnPlay.innerHTML = '&#9654; Play';
    canvasBg.classList.remove('playing');
    if (hasAudio && audio) audio.pause();
  }}

  btnPlay.addEventListener('click', function() {{
    if (playing) {{ pause(); }} else {{ play(); }}
  }});

  btnPrev.addEventListener('click', function() {{
    var idx = Math.floor(currentTime / secPerVerse);
    currentTime = Math.max(0, (idx - 1)) * secPerVerse;
    currentVerseIdx = -1;
    updateVerse();
    if (hasAudio && audio && audioReady) {{
      audio.currentTime = currentTime % (audio.duration || totalDuration);
    }}
  }});

  btnNext.addEventListener('click', function() {{
    var idx = Math.floor(currentTime / secPerVerse);
    var nextIdx = (idx + 1) >= verses.length ? 0 : idx + 1;
    currentTime = nextIdx * secPerVerse;
    currentVerseIdx = -1;
    updateVerse();
    if (hasAudio && audio && audioReady) {{
      audio.currentTime = currentTime % (audio.duration || totalDuration);
    }}
  }});

  speedBtns.forEach(function(btn) {{
    btn.addEventListener('click', function() {{
      speed = parseFloat(btn.dataset.speed);
      speedBtns.forEach(function(b) {{ b.classList.remove('active'); }});
      btn.classList.add('active');
      if (hasAudio && audio && audioReady) audio.playbackRate = speed;
    }});
  }});

  function seekFromEvent(e) {{
    var rect = timeline.getBoundingClientRect();
    var x = Math.max(0, Math.min(e.clientX - rect.left, rect.width));
    var pct = x / rect.width;
    currentTime = pct * totalDuration;
    currentVerseIdx = -1;
    updateVerse();
    if (hasAudio && audio && audioReady) {{
      audio.currentTime = currentTime % (audio.duration || totalDuration);
    }}
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
