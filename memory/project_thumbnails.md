---
name: Thumbnail generation pipeline
description: YouTube thumbnail system — Impact bold title, oil painting bg, glow effect, auto-generated after each video render
type: project
---

Thumbnails are auto-generated as part of the video render pipeline.

**Why:** YouTube CTR depends heavily on thumbnail. Oil painting backgrounds are unique and differentiate the channel. Impact font at 130px with glow halo matches high-performing devotional channels.

**How to apply:** After any video render, thumbnail is auto-created in the same output folder via `generate_thumbnail_for_theme(theme, output_dir)`. To batch-regenerate: `.venv/bin/python3 generate_thumbnails.py`.

## Key files
- `core/thumbnail_gen.py` — core module, importable
- `generate_thumbnails.py` — batch CLI
- Both `generate_video.py` and `render_60min.py` call `generate_thumbnail_for_theme` after render

## Design system
- Size: 1280×720 JPEG
- Font title: Impact.ttf 130px (`/System/Library/Fonts/Supplemental/Impact.ttf`)
- Font subtitle: Arial Bold.ttf 42px
- Overlay: quadratic ease-out gradient (left dark zone), stays dark past 70% width
- Glow: title drawn on separate RGBA layer → GaussianBlur(r=22) → composite before final text
- Left accent bar: 6px vertical strip (matches lateral_izq video template)
- Arrow: diagonal ↘ shaft + filled triangle head

## Accent colors per theme
fe/fuerza/salmos/victoria → #FFD700 (gold)
amor → #FF9F6B (warm orange)
esperanza/paz → #A8D8FF (soft blue)
gratitud → #B8F5A0 (soft green)

## Best backgrounds
fuerza_mountains > salmos_celestial > paz_cielo > fe_light
