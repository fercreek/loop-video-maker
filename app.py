"""
Loop Video Maker — Generador de Videos Bíblicos para YouTube
Entry point: lanza la interfaz Gradio en localhost.
"""

import json
import os
import subprocess
import platform

import gradio as gr

from core.verse_gen import (
    cargar_temas,
    cargar_versiculos,
    generar_mas_versiculos,
    guardar_versiculos_extra,
    versiculos_a_lista,
)
from core.image_gen import generar_imagen, generar_imagen_rapida, PRESET_LABELS
from core.music_gen import generar_musica, MOODS
from preview.preview_engine import generar_preview_html

# ─── Configuración ──────────────────────────────────────────────

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
OUTPUT_DIR = "output"


def cargar_config() -> dict:
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "gemini_api_key": "",
        "claude_api_key": "",
        "output_dir": "output",
        "default_font_size": 52,
        "default_seconds_per_verse": 12,
        "default_fade_duration": 1.5,
        "default_video_duration_minutes": 60,
        "default_resolution": [1920, 1080],
        "default_fps": 24,
        "default_text_position": "bottom",
    }


def guardar_config(cfg: dict) -> None:
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


config = cargar_config()
os.makedirs(config.get("output_dir", OUTPUT_DIR), exist_ok=True)

# ─── Estado global ──────────────────────────────────────────────

estado = {
    "imagen_path": None,
    "musica_path": None,
    "tema_actual": None,
    "versiculos": [],
    "datos_tema": None,
}


# ─── Funciones de la UI ────────────────────────────────────────

def obtener_temas():
    return cargar_temas()


def al_cargar_tema(tema):
    if not tema:
        return [], "", "", "", gr.update()

    try:
        datos = cargar_versiculos(tema)
    except FileNotFoundError as e:
        gr.Warning(str(e))
        return [], "", "", "", gr.update()

    estado["datos_tema"] = datos
    estado["tema_actual"] = tema

    versiculos = versiculos_a_lista(datos)
    estado["versiculos"] = versiculos

    tabla = [[v.get("referencia", ""), v.get("texto", "")] for v in versiculos]
    prompt_img = datos.get("prompt_imagen", "")

    mood_seleccionado = list(MOODS.keys())[0]
    mood_tema = datos.get("mood_mubert", "")
    for nombre, valor in MOODS.items():
        if valor == mood_tema or nombre.lower() in tema.lower():
            mood_seleccionado = nombre
            break

    info = f"✓ {len(versiculos)} versículos — tema «{tema}»"
    return tabla, prompt_img, mood_seleccionado, info, gr.update()


def generar_mas_con_ia(tema, cantidad, tabla_actual):
    api_key = config.get("claude_api_key", "")
    if not api_key:
        gr.Warning("Configura tu API key de Claude en la pestaña Configuración.")
        return tabla_actual, "❌ API key de Claude no configurada"

    try:
        nuevos = generar_mas_versiculos(tema, int(cantidad), api_key)
        guardar_versiculos_extra(tema, nuevos)
        nuevas_filas = [[v.get("referencia", ""), v.get("texto", "")] for v in nuevos]
        tabla_actualizada = tabla_actual + nuevas_filas
        estado["versiculos"] = estado["versiculos"] + nuevos
        return tabla_actualizada, f"✓ {len(nuevos)} versículos generados"
    except Exception as e:
        return tabla_actual, f"❌ Error: {str(e)}"


def listar_imagenes_guardadas():
    out_dir = config.get("output_dir", OUTPUT_DIR)
    if not os.path.exists(out_dir):
        return [], "Sin imágenes guardadas"
    exts = {".jpg", ".jpeg", ".png", ".webp"}
    imgs = sorted(
        [os.path.join(out_dir, f) for f in os.listdir(out_dir)
         if os.path.splitext(f)[1].lower() in exts],
        key=os.path.getmtime, reverse=True,
    )
    label = f"{len(imgs)} imagen{'es' if len(imgs) != 1 else ''} guardada{'s' if len(imgs) != 1 else ''}"
    return imgs, label


def al_seleccionar_imagen_guardada(evt: gr.SelectData):
    # evt.value es el item seleccionado en Gradio 4.x Gallery
    item = evt.value
    if isinstance(item, dict):
        path = item.get("name") or item.get("url") or item.get("path") or str(item)
    else:
        path = str(item)
    if not os.path.exists(path):
        return None, f"❌ No encontrado: {path}"
    estado["imagen_path"] = path
    return path, f"✓ {os.path.basename(path)}"


def al_generar_imagen(prompt, estilo):
    api_key = config.get("gemini_api_key", "")
    out_dir = config.get("output_dir", OUTPUT_DIR)
    preset_key = PRESET_LABELS.get(estilo)

    try:
        path = generar_imagen(prompt, api_key, out_dir, preset_key=preset_key)
        estado["imagen_path"] = path
        return path, f"✓ Imagen generada — {estilo}"
    except Exception as e:
        gr.Warning(f"Error al generar imagen: {str(e)}")
        return None, f"❌ Error: {str(e)}"


def al_generar_musica(mood, duracion_min):
    out_dir = config.get("output_dir", OUTPUT_DIR)
    duracion_seg = int(duracion_min) * 60

    try:
        path = generar_musica(mood, duracion_seg, "", out_dir)
        estado["musica_path"] = path
        return path, f"✓ Audio generado ({duracion_min} min)"
    except Exception as e:
        gr.Warning(f"Error al generar música: {str(e)}")
        return None, f"❌ Error: {str(e)}"


def al_generar_musica_ia(mood, duracion_min):
    out_dir = config.get("output_dir", OUTPUT_DIR)
    duracion_seg = int(duracion_min) * 60

    try:
        from core.music_gen import generar_musica_musicgen
    except ImportError:
        return None, "❌ MusicGen requiere: pip install torch transformers soundfile"

    try:
        prompt = MOODS.get(mood, "peaceful ambient meditation")
        path = generar_musica_musicgen(
            prompt=prompt, duracion_clip=15,
            duracion_total=duracion_seg, output_dir=out_dir,
        )
        estado["musica_path"] = path
        return path, f"✓ Música IA generada ({duracion_min} min)"
    except Exception as e:
        return None, f"❌ Error: {str(e)}"


def al_subir_audio(archivo):
    if archivo is None:
        return None, "❌ No se seleccionó archivo"
    estado["musica_path"] = archivo
    return archivo, "✓ Audio cargado"


def subir_imagen(archivo):
    if archivo is None:
        return None, "❌ No se seleccionó archivo"
    estado["imagen_path"] = archivo
    return archivo, "✓ Imagen cargada"


def al_actualizar_preview(tabla, seg_por_verso, fade_dur, posicion, tamano,
                          color_texto, color_ref, mostrar_ref):
    versiculos = []
    if tabla is not None:
        for fila in tabla:
            if len(fila) >= 2 and fila[0] and fila[1]:
                versiculos.append({"referencia": fila[0], "texto": fila[1]})

    if not versiculos:
        return "<div style='color:#888;text-align:center;padding:40px;background:#111;border-radius:12px;'>Carga un tema primero (Paso 1)</div>"

    img_path = estado.get("imagen_path")
    mus_path = estado.get("musica_path")

    if not img_path or not os.path.exists(str(img_path)):
        out_dir = config.get("output_dir", OUTPUT_DIR)
        color_acento = "#1a1a3e"
        if estado.get("datos_tema"):
            color_acento = estado["datos_tema"].get("color_acento", "#1a1a3e")
        img_path = generar_imagen_rapida(color_acento, out_dir)
        estado["imagen_path"] = img_path

    config_texto = {
        "posicion": posicion,
        "tamano": tamano,
        "color_texto": color_texto,
        "color_referencia": color_ref,
        "mostrar_referencia": mostrar_ref,
        "fade_duration": fade_dur,
    }

    return generar_preview_html(img_path, mus_path, versiculos, int(seg_por_verso), config_texto)


def al_generar_video(tabla, seg_por_verso, duracion_min, posicion, tamano,
                     color_texto, color_ref, mostrar_ref, fade_dur, efecto_imagen,
                     nombre_archivo, progress=gr.Progress()):
    from core.video_render import renderizar_video

    versiculos = []
    if tabla is not None:
        for fila in tabla:
            if len(fila) >= 2 and fila[0] and fila[1]:
                versiculos.append({"referencia": fila[0], "texto": fila[1]})

    if not versiculos:
        return "❌ Carga versículos primero (Paso 1)"

    img_path = estado.get("imagen_path")
    mus_path = estado.get("musica_path")

    if not img_path or not os.path.exists(str(img_path)):
        return "❌ Genera o sube una imagen primero (Paso 2)"

    out_dir = config.get("output_dir", OUTPUT_DIR)
    os.makedirs(out_dir, exist_ok=True)

    if not nombre_archivo:
        nombre_archivo = f"versiculos_{estado.get('tema_actual', 'video')}_{duracion_min}min.mp4"
    if not nombre_archivo.endswith(".mp4"):
        nombre_archivo += ".mp4"

    output_path = os.path.join(out_dir, nombre_archivo)
    config_texto = {
        "posicion": posicion,
        "tamano": tamano,
        "color_texto": color_texto,
        "color_referencia": color_ref,
        "mostrar_referencia": mostrar_ref,
        "fade_duration": fade_dur,
    }

    try:
        def progress_cb(pct, msg=""):
            progress(pct, desc=msg)

        path = renderizar_video(
            imagen_path=img_path,
            musica_path=mus_path,
            versiculos=versiculos,
            duracion_total_segundos=int(duracion_min) * 60,
            segundos_por_versiculo=int(seg_por_verso),
            config_texto=config_texto,
            output_path=output_path,
            efecto_imagen=efecto_imagen or "Sin efecto",
            progress_callback=progress_cb,
        )
        return f"✓ Video listo: {path}"
    except Exception as e:
        return f"❌ Error: {str(e)}"


def abrir_carpeta_salida():
    out_dir = os.path.abspath(config.get("output_dir", OUTPUT_DIR))
    os.makedirs(out_dir, exist_ok=True)
    try:
        if platform.system() == "Darwin":
            subprocess.Popen(["open", out_dir])
        elif platform.system() == "Windows":
            os.startfile(out_dir)
        else:
            subprocess.Popen(["xdg-open", out_dir])
        return f"✓ Carpeta abierta: {out_dir}"
    except Exception as e:
        return f"Error: {str(e)}"


def guardar_configuracion(gemini_key, claude_key):
    config["gemini_api_key"] = gemini_key
    config["claude_api_key"] = claude_key
    guardar_config(config)
    estados = []
    for nombre, key in [("Gemini", gemini_key), ("Claude", claude_key)]:
        if key:
            estados.append(f"✓ {nombre}: configurada")
        else:
            estados.append(f"✗ {nombre}: no configurada")
    return "✓ Guardado", "\n".join(estados)


# ─── UI Gradio ──────────────────────────────────────────────────

temas_disponibles = obtener_temas()

CSS = """
/* ── Contenedor general ─────────────────────────────────── */
.gradio-container { max-width: 1400px !important; }

/* ── Título y subtítulo ─────────────────────────────────── */
.main-title {
    text-align:center; color:#E8D5A3;
    margin-bottom:4px; font-size:32px; font-weight:700;
    letter-spacing:1px;
}
.sub-title {
    text-align:center; color:#aaa;
    font-size:16px; margin-bottom:24px;
}

/* ── Cabeceras de pasos ──────────────────────────────────── */
.step-header {
    display:flex; align-items:center; gap:12px;
    padding:8px 0 12px 0; border-bottom:2px solid #2a2a2a; margin-bottom:16px;
}
.step-num {
    width:34px; height:34px; border-radius:50%;
    background:#E8D5A3; color:#111; font-weight:800; font-size:16px;
    display:flex; align-items:center; justify-content:center; flex-shrink:0;
    box-shadow: 0 2px 6px rgba(232,213,163,0.3);
}
.step-title { color:#F5F5F5; font-size:18px; font-weight:700; }
.step-hint  { color:#999; font-size:13px; margin-top:-10px; margin-bottom:12px; padding-left:46px; }

/* ── Todos los labels de inputs ─────────────────────────── */
.gradio-container label span {
    font-size: 15px !important;
    font-weight: 500 !important;
    color: #D0D0D0 !important;
}

/* ── Status textboxes ────────────────────────────────────── */
.status-box textarea {
    font-size: 14px !important;
    color: #7ecb85 !important;
    background: #1e1e1e !important;
    border: 1px solid #2d3d2d !important;
    border-radius: 6px !important;
    padding: 6px 10px !important;
    min-height: 36px !important;
}

/* ── Botones primarios más altos ─────────────────────────── */
.gradio-container button.lg {
    min-height: 48px !important;
    font-size: 15px !important;
}
.gradio-container button.sm {
    min-height: 38px !important;
    font-size: 14px !important;
}

/* ── Botón secundario con borde visible ──────────────────── */
.gradio-container button.secondary {
    border: 1px solid #444 !important;
    color: #ccc !important;
}

/* ── Botón render (dorado prominente) ────────────────────── */
.render-btn > .lg {
    background: linear-gradient(135deg, #E8D5A3, #c9a84c) !important;
    color: #111 !important;
    font-weight: 800 !important;
    font-size: 17px !important;
    border: none !important;
    letter-spacing: 0.5px !important;
    min-height: 56px !important;
}

/* ── Botón vista previa ───────────────────────────────────── */
.preview-btn > .lg {
    background: #1e3a5f !important;
    color: #fff !important;
    font-weight: 700 !important;
    font-size: 15px !important;
    border: 1px solid #2a5a8f !important;
    min-height: 48px !important;
}

/* ── Sliders — etiquetas más grandes ─────────────────────── */
.gradio-container .wrap input[type=range] { height: 6px !important; }

/* ── Dropdowns / Radio ────────────────────────────────────── */
.gradio-container .wrap span { font-size: 14px !important; }

/* ── Texto readonly de estado ────────────────────────────── */
textarea[readonly], input[readonly] {
    font-size: 13px !important; color: #bbb !important;
}
"""

with gr.Blocks(
    title="Loop Video Maker",
    theme=gr.themes.Soft(
        primary_hue="amber",
        secondary_hue="blue",
        neutral_hue="slate",
    ).set(
        body_background_fill="#0f0f0f",
        body_background_fill_dark="#0f0f0f",
        block_background_fill="#1a1a1a",
        block_background_fill_dark="#1a1a1a",
        block_border_color="#2a2a2a",
        block_border_color_dark="#2a2a2a",
        button_primary_background_fill="#E8D5A3",
        button_primary_background_fill_dark="#E8D5A3",
        button_primary_text_color="#111",
        button_primary_text_color_dark="#111",
    ),
    css=CSS,
) as app:

    gr.HTML("<h1 class='main-title'>✝ Creador de Videos Bíblicos</h1>")
    gr.HTML("<p class='sub-title'>Crea videos con versículos, música e imagen para compartir en YouTube</p>")

    with gr.Tabs():

        # ═══ TAB EDITOR ═══════════════════════════════════════════
        with gr.Tab("Editor"):
            with gr.Row():

                # ── COLUMNA IZQUIERDA — Pasos 1, 2, 3 ──────────────
                with gr.Column(scale=2):

                    # ── PASO 1: TEMA ────────────────────────────────
                    gr.HTML("<div class='step-header'><div class='step-num'>1</div><div class='step-title'>Elige el Tema Bíblico</div></div>")
                    gr.HTML("<p class='step-hint'>Selecciona un tema y carga los versículos que aparecerán en el video.</p>")

                    tema_dropdown = gr.Dropdown(
                        choices=temas_disponibles,
                        label="Tema bíblico",
                        value=temas_disponibles[0] if temas_disponibles else None,
                    )
                    btn_cargar = gr.Button("📖  Cargar versículos", variant="primary")
                    info_versiculos = gr.Textbox(
                        label="", interactive=False, lines=1,
                        placeholder="Aquí verás cuántos versículos se cargaron...",
                        elem_classes=["status-box"],
                    )

                    with gr.Accordion("Ver y editar los versículos", open=False):
                        tabla_versiculos = gr.Dataframe(
                            headers=["Referencia", "Texto"],
                            datatype=["str", "str"],
                            label="Versículos",
                            interactive=True,
                            wrap=True,
                            row_count=(5, "dynamic"),
                            col_count=(2, "fixed"),
                        )
                        seg_por_verso = gr.Slider(
                            minimum=5, maximum=30,
                            value=config.get("default_seconds_per_verse", 12),
                            step=1, label="Segundos que aparece cada versículo",
                        )
                        with gr.Row():
                            cantidad_ia = gr.Slider(
                                minimum=5, maximum=30, value=10, step=5,
                                label="Cuántos versículos agregar",
                            )
                            btn_generar_ia = gr.Button("+ Agregar con IA", variant="secondary", size="sm")
                        info_ia = gr.Textbox(label="", interactive=False, lines=1, elem_classes=["status-box"])

                    gr.HTML("<div style='margin-top:8px'></div>")

                    # ── PASO 2: IMAGEN ──────────────────────────────
                    gr.HTML("<div class='step-header'><div class='step-num'>2</div><div class='step-title'>Fondo del Video</div></div>")
                    gr.HTML("<p class='step-hint'>Elige un fondo bonito o sube tu propia foto.</p>")

                    estilo_imagen = gr.Dropdown(
                        choices=list(PRESET_LABELS.keys()),
                        value="Amanecer dorado",
                        label="Estilo del fondo",
                    )
                    prompt_imagen = gr.Textbox(
                        label="Descripción del fondo (opcional)",
                        lines=1,
                        placeholder="Ej: montaña al amanecer, cielo estrellado...",
                    )
                    with gr.Row():
                        btn_gen_img = gr.Button("🎨  Crear imagen", variant="primary", size="sm")
                        btn_subir_img = gr.UploadButton(
                            "📁  Usar mi foto", file_types=["image"], size="sm",
                        )
                    preview_img = gr.Image(label="Vista previa del fondo", height=160)
                    info_imagen = gr.Textbox(label="", interactive=False, lines=1, elem_classes=["status-box"])

                    with gr.Accordion("📂  Usar una imagen que ya creé antes", open=True):
                        info_galeria = gr.Textbox(label="", interactive=False, lines=1, elem_classes=["status-box"])
                        galeria_imgs = gr.Gallery(
                            label="",
                            columns=3,
                            height=200,
                            object_fit="cover",
                            allow_preview=False,
                        )
                        btn_refresh_imgs = gr.Button("↻  Ver mis imágenes guardadas", variant="secondary", size="sm")

                    gr.HTML("<div style='margin-top:8px'></div>")

                    # ── PASO 3: MÚSICA ──────────────────────────────
                    gr.HTML("<div class='step-header'><div class='step-num'>3</div><div class='step-title'>Música de Fondo</div></div>")
                    gr.HTML("<p class='step-hint'>Elige el tipo de música o sube tu propia canción.</p>")

                    mood_dropdown = gr.Dropdown(
                        choices=list(MOODS.keys()),
                        value=list(MOODS.keys())[0],
                        label="Tipo de música",
                    )
                    duracion_radio = gr.Radio(
                        choices=["30", "60", "90", "120"],
                        value="60",
                        label="Duración del video (minutos)",
                        visible=False,
                    )
                    with gr.Row():
                        btn_gen_musica = gr.Button("🎵  Crear música", variant="primary", size="sm")
                        btn_gen_musica_ia = gr.Button("🤖  Música con IA", variant="secondary", size="sm")
                    btn_subir_audio = gr.UploadButton(
                        "📁  Usar mi propia música", file_types=["audio"], size="sm",
                    )
                    audio_player = gr.Audio(label="Música seleccionada", type="filepath")
                    info_musica = gr.Textbox(label="", interactive=False, lines=1, elem_classes=["status-box"])

                # ── COLUMNA DERECHA — Preview + Render ─────────────
                with gr.Column(scale=3):

                    # Preview
                    gr.HTML("<div class='step-header'><div class='step-num'>▶</div><div class='step-title'>Vista Previa del Video</div></div>")
                    gr.HTML("<p class='step-hint'>Así se verá tu video. Puedes ajustar y volver a ver cuantas veces quieras.</p>")
                    btn_preview = gr.Button("👁  Ver cómo quedará el video", variant="primary", size="lg", elem_classes=["preview-btn"])
                    preview_html = gr.HTML(
                        value="<div style='color:#555;text-align:center;padding:80px 40px;background:#111;border-radius:12px;font-size:16px;line-height:2;'>Completa los pasos 1, 2 y 3<br>y luego haz clic en el botón de arriba 👆</div>",
                    )

                    # Estilo avanzado (colapsado)
                    with gr.Accordion("⚙️  Personalizar el texto (opcional)", open=False):
                        efecto_imagen = gr.Radio(
                            choices=["Sin efecto", "Zoom lento ↗", "Zoom lento ↙", "Paneo suave →"],
                            value="Zoom lento ↗",
                            label="Movimiento del fondo (efecto Ken Burns)",
                        )
                        fade_dur = gr.Slider(
                            minimum=0.5, maximum=3.0,
                            value=config.get("default_fade_duration", 1.5),
                            step=0.1, label="Suavidad al aparecer el texto (segundos)",
                        )
                        with gr.Row():
                            posicion_texto = gr.Radio(
                                choices=["top", "center", "bottom"],
                                value=config.get("default_text_position", "bottom"),
                                label="¿Dónde aparece el texto?",
                            )
                            tamano_texto = gr.Slider(
                                minimum=32, maximum=72,
                                value=config.get("default_font_size", 52),
                                step=2, label="Tamaño de letra",
                            )
                        with gr.Row():
                            color_texto = gr.ColorPicker(value="#FFFFFF", label="Color de las letras")
                            color_referencia = gr.ColorPicker(value="#E8D5A3", label="Color del versículo")
                            mostrar_ref = gr.Checkbox(value=True, label="Mostrar referencia")

                    gr.HTML("<div style='margin-top:16px'></div>")

                    # Render
                    gr.HTML("<div style='border-top:1px solid #2a2a2a;margin:20px 0 16px'></div>")
                    gr.HTML("<div class='step-header'><div class='step-num'>4</div><div class='step-title'>Crear el Video</div></div>")
                    gr.HTML("<p class='step-hint'>Elige cuánto durará el video y dale clic al botón para crearlo.</p>")
                    with gr.Row():
                        nombre_archivo = gr.Textbox(
                            label="Nombre del video (opcional)",
                            placeholder="mi_video_paz.mp4",
                            scale=3,
                        )
                        duracion_render = gr.Radio(
                            choices=["30", "60", "90", "120"],
                            value="60",
                            label="¿Cuántos minutos durará el video?",
                            scale=2,
                        )
                    btn_render = gr.Button(
                        "🎬  Crear mi Video",
                        variant="primary",
                        size="lg",
                        elem_classes=["render-btn"],
                    )
                    info_render = gr.Textbox(label="", interactive=False, lines=1, elem_classes=["status-box"])
                    btn_abrir = gr.Button("📂  Ver mis videos guardados", variant="secondary", size="sm")

        # ═══ TAB CONFIGURACIÓN ════════════════════════════════════
        with gr.Tab("Configuración"):
            gr.Markdown("### API Keys (Opcionales)")
            gr.Markdown(
                "La app funciona sin API keys — todo se genera localmente. "
                "Las claves se guardan en `config.json` en tu máquina."
            )
            gemini_input = gr.Textbox(
                label="Gemini API Key (imágenes IA)",
                value=config.get("gemini_api_key", ""),
                type="password",
            )
            claude_input = gr.Textbox(
                label="Claude API Key (generar más versículos)",
                value=config.get("claude_api_key", ""),
                type="password",
            )
            btn_guardar_config = gr.Button("Guardar", variant="primary")
            info_config = gr.Textbox(label="Estado", interactive=False, lines=1)
            estado_apis = gr.Textbox(label="APIs", interactive=False, lines=2)

    # ─── Eventos ────────────────────────────────────────────────

    btn_cargar.click(
        fn=al_cargar_tema,
        inputs=[tema_dropdown],
        outputs=[tabla_versiculos, prompt_imagen, mood_dropdown, info_versiculos, preview_html],
    )

    btn_generar_ia.click(
        fn=generar_mas_con_ia,
        inputs=[tema_dropdown, cantidad_ia, tabla_versiculos],
        outputs=[tabla_versiculos, info_ia],
    )

    btn_gen_img.click(
        fn=al_generar_imagen,
        inputs=[prompt_imagen, estilo_imagen],
        outputs=[preview_img, info_imagen],
    )

    btn_subir_img.upload(
        fn=subir_imagen,
        inputs=[btn_subir_img],
        outputs=[preview_img, info_imagen],
    )

    btn_refresh_imgs.click(
        fn=listar_imagenes_guardadas,
        outputs=[galeria_imgs, info_galeria],
    )

    galeria_imgs.select(
        fn=al_seleccionar_imagen_guardada,
        outputs=[preview_img, info_imagen],
    )

    btn_gen_musica.click(
        fn=al_generar_musica,
        inputs=[mood_dropdown, duracion_render],
        outputs=[audio_player, info_musica],
    )

    btn_gen_musica_ia.click(
        fn=al_generar_musica_ia,
        inputs=[mood_dropdown, duracion_render],
        outputs=[audio_player, info_musica],
    )

    btn_subir_audio.upload(
        fn=al_subir_audio,
        inputs=[btn_subir_audio],
        outputs=[audio_player, info_musica],
    )

    preview_inputs = [
        tabla_versiculos, seg_por_verso, fade_dur, posicion_texto,
        tamano_texto, color_texto, color_referencia, mostrar_ref,
    ]

    btn_preview.click(
        fn=al_actualizar_preview,
        inputs=preview_inputs,
        outputs=[preview_html],
    )

    seg_por_verso.release(
        fn=al_actualizar_preview,
        inputs=preview_inputs,
        outputs=[preview_html],
    )

    btn_render.click(
        fn=al_generar_video,
        inputs=[
            tabla_versiculos, seg_por_verso, duracion_render, posicion_texto,
            tamano_texto, color_texto, color_referencia, mostrar_ref,
            fade_dur, efecto_imagen, nombre_archivo,
        ],
        outputs=[info_render],
    )

    btn_abrir.click(fn=abrir_carpeta_salida, outputs=[info_render])

    btn_guardar_config.click(
        fn=guardar_configuracion,
        inputs=[gemini_input, claude_input],
        outputs=[info_config, estado_apis],
    )


    app.load(fn=listar_imagenes_guardadas, outputs=[galeria_imgs, info_galeria])

# ─── Launch ─────────────────────────────────────────────────────

if __name__ == "__main__":
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        inbrowser=True,
        share=False,
    )
