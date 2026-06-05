#!/usr/bin/env python3
"""
WF#4 — Generador de email devocional semanal (Versiculos de Dios / beehiiv).

Por que existe: beehiiv plan Launch (free) NO incluye Send API, asi que el envio
automatico via n8n no es viable. Este script genera el email LISTO PARA PEGAR en
beehiiv (HTML + texto), 2 min de trabajo manual. Cierra el retorno del flywheel:
el email recircula al VIDEO LARGO (sube watch hours = gate YPP) + empuja Ko-fi.

Uso:
  python3 scripts/weekly_devotional_email.py            # semana ISO actual
  python3 scripts/weekly_devotional_email.py --week 24  # semana especifica
  python3 scripts/weekly_devotional_email.py --list     # ver rotacion

Output: output/email/week_YYYY-WW.html  +  .txt  (subject en la 1ra linea del .txt)
"""
import argparse, json, os, datetime, html

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KOFI = "https://ko-fi.com/versiculosdedios"

# Largos del canal con tema + devocional corto (versiculo + reflexion 3-4 lineas).
# Rotan 1 por semana. El email SIEMPRE manda al video largo (watch hours = gate).
WEEKLY = [
    {
        "video_id": "6eHgRtGjaYA", "theme": "Ansiedad",
        "title": "Salmos para dormir y soltar la ansiedad",
        "verse": "\"Echa sobre Jehova tu carga, y el te sustentara.\" — Salmo 55:22",
        "devotional": "Esta noche no tienes que cargar todo tu solo. La ansiedad pesa porque "
                      "intentas controlar lo que solo Dios sostiene. Suelta. Cierra los ojos, "
                      "respira, y deja que Su paz te cubra mientras duermes.",
    },
    {
        "video_id": "N7YzBNgd3l4", "theme": "Esperanza",
        "title": "Salmos para dormir con esperanza en Dios",
        "verse": "\"Porque yo se los pensamientos que tengo acerca de vosotros... pensamientos de paz.\" — Jeremias 29:11",
        "devotional": "Aunque hoy no veas la salida, Dios ya ve el final del camino. Tu esperanza "
                      "no depende de tus circunstancias, sino de Quien las sostiene. Descansa: "
                      "manana es otra oportunidad para ver Su fidelidad.",
    },
    {
        "video_id": "9ydXq8BlvWY", "theme": "Sanacion",
        "title": "Salmos de sanacion para dormir",
        "verse": "\"El sana a los quebrantados de corazon, y venda sus heridas.\" — Salmo 147:3",
        "devotional": "Hay heridas que nadie ve pero El conoce. Esta noche, en vez de revivir el "
                      "dolor, entregalo. Dios no solo consuela: sana de raiz. Permitele entrar "
                      "donde mas te duele.",
    },
    {
        "video_id": "wF356NTu_I0", "theme": "Fe",
        "title": "Versiculos para dormir que fortalecen tu fe",
        "verse": "\"Es, pues, la fe la certeza de lo que se espera.\" — Hebreos 11:1",
        "devotional": "La fe no es ausencia de miedo, es confiar a pesar de el. No necesitas verlo "
                      "todo claro para dar el siguiente paso. Hoy alimenta tu fe con Su Palabra y "
                      "duerme sabiendo que El va delante de ti.",
    },
    {
        "video_id": "zSxs3wnTq9U", "theme": "Provision",
        "title": "Versiculos para dormir sobre provision y bendicion",
        "verse": "\"Mi Dios, pues, suplira todo lo que os falta.\" — Filipenses 4:19",
        "devotional": "Lo que te falta hoy no toma a Dios por sorpresa. El que viste los campos y "
                      "alimenta las aves conoce tu necesidad. Deja de calcular con miedo y empieza "
                      "a confiar con fe: Su provision llega a tiempo.",
    },
    {
        "video_id": "7cOYmo27qS4", "theme": "Oracion",
        "title": "Lo-Fi cristiano para orar",
        "verse": "\"Orad sin cesar.\" — 1 Tesalonicenses 5:17",
        "devotional": "Orar no es decir palabras bonitas: es abrir tu corazon tal como esta. Hoy no "
                      "tienes que tener las frases perfectas. Solo ven. Dios prefiere tu honestidad "
                      "antes que tu elocuencia.",
    },
    {
        "video_id": "l5LFYLVZOd4", "theme": "Paz",
        "title": "Versiculos contra la ansiedad",
        "verse": "\"La paz os dejo, mi paz os doy.\" — Juan 14:27",
        "devotional": "El mundo te da motivos para preocuparte; Dios te da Su paz. No es una paz que "
                      "depende de que todo este bien, sino de que El esta contigo aunque nada lo este. "
                      "Recibela esta noche.",
    },
]


def featured(week_idx: int) -> dict:
    return WEEKLY[week_idx % len(WEEKLY)]


def build_email(item: dict) -> tuple:
    vid = item["video_id"]
    url = "https://youtube.com/watch?v=" + vid
    subject = f"\U0001F54A️ {item['theme']}: un momento con Dios antes de dormir"
    # Texto plano
    txt = (
        f"{subject}\n\n"
        f"{item['verse']}\n\n"
        f"{item['devotional']}\n\n"
        f"\U0001F3A7 Esta semana te acompano con: {item['title']} (2 horas, sin anuncios)\n"
        f"Ponlo esta noche -> {url}\n\n"
        f"☕ Si este ministerio te bendice, puedes apoyarlo (y recibir gratis el PDF "
        f"\"7 Dias de Paz\"): {KOFI}\n\n"
        f"Que Dios te bendiga esta semana.\n— Versiculos de Dios\n\n"
        f"Contenido creado con asistencia de IA \U0001F64F"
    )
    # HTML (beehiiv acepta pegar bloque)
    h = html.escape
    html_body = f"""<div style="font-family:Georgia,serif;max-width:560px;margin:0 auto;color:#1a1a2e;line-height:1.6">
  <p style="font-size:18px;font-style:italic;color:#444">{h(item['verse'])}</p>
  <p style="font-size:17px">{h(item['devotional'])}</p>
  <div style="background:#0d1220;border-radius:12px;padding:20px;text-align:center;margin:24px 0">
    <p style="color:#ffd700;font-size:15px;margin:0 0 12px">\U0001F3A7 Esta semana: {h(item['title'])}</p>
    <a href="{url}" style="display:inline-block;background:#ffd700;color:#0d1220;text-decoration:none;
       padding:12px 28px;border-radius:8px;font-weight:bold;font-size:16px">Ponlo esta noche →</a>
    <p style="color:#888;font-size:12px;margin:12px 0 0">2 horas · sin anuncios</p>
  </div>
  <p style="font-size:15px;text-align:center">
    ☕ <a href="{KOFI}" style="color:#c0392b">Apoya el ministerio</a> y recibe gratis el PDF "7 Días de Paz"
  </p>
  <p style="font-size:14px;color:#666;text-align:center;margin-top:24px">
    Que Dios te bendiga esta semana.<br>— Versículos de Dios
  </p>
  <p style="font-size:11px;color:#aaa;text-align:center">Contenido creado con asistencia de IA \U0001F64F</p>
</div>"""
    return subject, txt, html_body


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--week", type=int, help="numero de semana ISO (default: actual)")
    ap.add_argument("--list", action="store_true", help="ver rotacion completa")
    a = ap.parse_args()

    if a.list:
        for i, it in enumerate(WEEKLY):
            print(f"semana%{len(WEEKLY)}=={i}: {it['theme']:10} -> {it['video_id']} | {it['title']}")
        return

    now = datetime.date.today()
    iso_year, iso_week, _ = now.isocalendar()
    week = a.week if a.week is not None else iso_week
    item = featured(week - 1)
    subject, txt, html_body = build_email(item)

    outdir = os.path.join(BASE, "output", "email")
    os.makedirs(outdir, exist_ok=True)
    stamp = f"{iso_year}-W{week:02d}"
    txt_path = os.path.join(outdir, f"week_{stamp}.txt")
    html_path = os.path.join(outdir, f"week_{stamp}.html")
    with open(txt_path, "w") as f:
        f.write(txt)
    with open(html_path, "w") as f:
        f.write(html_body)

    print(f"=== Email semana {stamp} — tema: {item['theme']} ===")
    print(f"SUBJECT: {subject}\n")
    print(txt)
    print(f"\n--- Archivos ---\nTexto: {txt_path}\nHTML:  {html_path}")
    print("\nPegar el HTML en beehiiv -> New Post -> bloque HTML. Subject arriba.")


if __name__ == "__main__":
    main()
