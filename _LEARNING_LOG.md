# _LEARNING_LOG — loop-video-maker

> Auto-reflexión por sesión (convención CLAUDE.md global Fernando).
> Bugs técnicos detallados van en `logs/LEARNINGS.md`.
> Esto captura: ¿cómo le diríamos a Claude la próxima vez para llegar al mismo resultado en menos turnos?

---

### 2026-06-01 · venom monetización VD + Sistema de Operaciones

**Pros (qué salió bien):**
- `venom_truth.json` como SSOT vivo mató el "27%" stale (era Shorts mezclados; real 3.8% long-form).
- Verify-before-build (regla #17): disk-check corrigió 2 errores — el Explore que dijo "no hay long-form" y el propio venom_truth que double-conteaba "30h parado".
- 2 research en background (ads + biz models) mientras se escribía el doc = paralelización real, data citada.
- Reflejé el modelo de Operaciones antes de construir (regla #13) — confirmación A/B/C antes de 5 archivos.

**Cons (qué se atoró):**
- El SSOT se auto-contradijo (`anomalia` double-conteaba). "venom manda" se leyó como "venom correcto" — no lo era. Solo el disk-check manual lo cachó.
- Explore agent concluyó "no existe long-form" alrededor de un gap que él mismo declaró ("no examiné sleep/"). Casi propaga premisa falsa.
- 1 Explore murió "Prompt is too long" (repo cero-agent grande, prompt sin acotar lectura).

**Consejo Claude Code (cómo prompteamos mejor):**
- Antes de construir sobre un número de un SSOT → spot-check los de alto impacto contra ground-truth (`find`/`ls`/DB). La fuente de verdad puede estar stale o auto-contradictoria.
- Explore de inventario: dar dirs exactos + "si no pudiste revisar algo, repórtalo como gap, NO concluyas alrededor".

**Patrón nuevo capturado:**
- **"venom manda" = controla + delega + SUPERVISA, no "venom infalible".** venom tiene el control y delega ejecución (sensores/API/agentes), pero la supervisión incluye validar lo delegado contra ground-truth. El fallo fue delegar sin supervisar: venom_truth tomó un dato sin validarlo con `find`/`ls`. La regla #17 corre DENTRO del flujo de venom. Retro: `angels/focus/_RETRO-2026-06-01-venom-monetizacion.md`.

---

### 2026-05-31 · Upload + análisis estratégico (retro: `_RETRO-2026-05-31.md`)

**Pros:**
- Discovery-first en thumbnails (copy ANTES de generar) = cero loops, 1-2 intentos por pieza
- QA honesto post-gen detectó mismatch imagen-copy (José/Pentecostés aurora≠fuego) ANTES de subir
- Agentes en paralelo (background) mientras avanzaba upload — hilo principal productivo
- Acepté data sobre corazonada: pedí re-test Resurrección/Jonás, data dijo Pródigo/Daniel, cambié

**Cons:**
- Asumí "27% YPP" del _NEXT viejo sin validar — real 3.6% (contaba Shorts que NO cuentan al gate). Toda la estrategia inicial midió contra baseline incorrecto
- Upload falló silencioso 2x: prompt `input() (y/N)` muere en background con EOFError. Tardé en ver que era stdin, no auth
- Glitches de display dieron estado fantasma (PLACEHOLDER/MOCK/logs viejos) — casi actúo sobre estado falso. Mitigué verificando vía API read-only antes de cada irreversible
- Traté "venom" como skill (es agente). Fernando lo señaló

**Consejo Claude Code:**
- Validar TODA métrica de objetivo (YPP%, watch hrs) contra API en vivo al inicio — NO heredar del _NEXT. Skill `vd-youtube` ahora lo fuerza
- Scripts batch con `input()` → flag `--yes`/no-TTY detect. Arreglar `upload_to_youtube.py` (no depender de `echo "y" |`)
- APRUEBO para writes externos con verbo EXACTO del write ("sube los thumbnails"), no "sí" genérico — el classifier frena el "sí" ambiguo
- venom = agente, no skill. Anclar vía skill que lo invoca con contexto

**Patrón nuevo capturado:**
- Número heredado de docs/_NEXT = sospechoso hasta validar contra la fuente (mismo error raíz que regla global #1: consultar fuentes antes de asumir). Aplica a métricas, no solo a teléfonos/montos.
- **Agentes background para código aislado (cero writes externos) = paralelo sin fricción.** Fix upload --yes + hex CC + accent clean corrieron simultáneos, cada uno verificado, sin commit. Patrón a repetir para deuda técnica.
- **Verificar entry point REAL del tooling antes de escribirlo en un skill.** Inventé `scripts/focus_add.py` (no existe; era `f.py add`) y lo metí al skill supernova. Igual: `for $FILES` sin comillas rompió un sed (usar `while IFS= read -r`).

---

### 2026-05-27 · Análisis sistema + FDA daemons + dry-run bug

**Pros:**
- Diagnóstico exhaustivo del sistema en 1 sesión: daemons, upload state, errores silenciosos
- FDA root cause resuelto definitivamente: bash wrapper en plists = launchd hereda FDA de /bin/bash
- Bug dry-run→save_state encontrado y corregido antes de que dañara producción masiva
- 4/4 daemons exit 0 al cerrar sesión

**Cons:**
- yt-fb-uploader llevaba con exit 1 desde días anteriores sin detectarse — monitoring reactivo, no proactivo
- No hay health-check automático que alerte cuando daemon falla (solo se ve al abrir Claude)

**Consejo Claude Code:**
- Prompt óptimo: "revisa todos los daemons con `launchctl list | grep versiculodedios` Y sus stderr logs antes de reportar estado" — exit code + log juntos
- Para FDA en macOS Sequoia: plist siempre con `/bin/bash -c "cd WORKDIR && .venv/bin/python3 script.py"` — nunca python directo en ProgramArguments
- Dry-run en cualquier daemon: verificar que NO guarda state antes de correr — patrón `if not dry_run: save_state()`

**Patrón nuevo capturado:**
- macOS Sequoia launchd FDA: bash (si está en FDA) puede lanzar python sin que python tenga FDA propio. Bash abre el .py via fork/exec, python hereda el file descriptor ya abierto.

---

### 2026-05-27 · Debug IG upload 400 + bulk FB fix

**Pros:**
- Bug root cause encontrado en <10 pasos: single-request vs chunked LSVP — test empírico directo
- venom_001 publicado en IG en misma sesión que se encontró el bug
- Identificamos 3 sistemas independientes publicando en FB (schedule_vd, venom batch, batch anterior)

**Cons:**
- Se iteró 5+ variantes (Content-Type, bytes vs fileobj, versión API, token type) antes de probar chunked — la doc de Meta no dice claramente que LSVP requiere chunks
- El daemon `yt-fb-uploader` lleva roto sin detectarse (PermissionError silencioso)
- No hay monitoring centralizado — cada daemon loguea a `/tmp` o a `logs/` separados sin vista unificada

**Consejo Claude Code:**
- Para errores `rupload.facebook.com 400`: PRIMERO probar chunked 4MB antes de cualquier otra variante — es el protocolo LSVP de Meta, no soporta single-request >4MB
- Al diagnosticar bulk uploads en FB: siempre `GET /{page}/posts?limit=50` en lugar del JSON cacheado — el cache solo trae 10
- Antes de reportar "el daemon está corriendo", verificar exit code en `launchctl list` Y revisar stderr log — `-1` o `-9` = fallando silencioso

**Patrón nuevo capturado:**
- Meta LSVP (rupload.facebook.com): chunks de 4MB con headers `offset` + `file_size` + `Content-Type: application/octet-stream`. Respuestas 206 × N chunks + 200 en último.

---

### 2026-05-26 · Sesión gym + FDA + cleanup PR

**Pros (qué salió bien):**
- Spec persistido (`docs/SESSION_SPEC_2026-05-25.md`) salvó contexto cross-session
- `_NEXT.md` apuntando al spec → próxima sesión leyó todo en 1 turn
- Auto-mode bloqueó correctamente acciones destructivas (PR merge sin autorización explícita)
- Daemons funcionaron en cuanto Fernando dio FDA grant — diagnóstico previo correcto

**Cons (qué se atoró):**
- `gh pr merge` bloqueado por auto-mode aunque Fernando dijo "mergea" — necesitó "correlo tu" explícito
- `git pull` post-merge dejó local main diverged (5 commits unique local + 2 unique remote) — confundió
- Bug bash multi-line `grep -c | echo 0` → necesitó `head -1` + `${VAR:-0}` fallback
- FDA grant requirió 2 intentos para Fernando entender qué binarios agregar

**Consejo Claude Code (cómo prompteamos mejor):**
- Cuando el usuario dice "mergea", explicitar "Auto-mode requiere `correlo tu` literal antes de gh pr merge a main"
- Si hay `git pull` post-merge → SIEMPRE `git fetch && git reset --hard origin/main` con backup branch primero
- Bash multi-line outputs (`grep -c`, `wc -l` pipeline) → SIEMPRE `head -1` + default fallback
- FDA grant: dar OBVIA path completa `/bin/bash` + `/usr/bin/python3` con Cmd+Shift+G en file picker

**Patrón nuevo capturado:**
- Session Spec pattern (`docs/SESSION_SPEC_YYYY-MM-DD.md`) = entry point reliable para próxima sesión
- Living spec (`_SCHEDULE_VENOM.md`) = trackeable por video × plataforma con status emojis
- FDA grant solo aplica a binary que escribiste en TCC db — daemon context puede ser distinto que terminal

---

### 2026-05-25 · Batch venom + Sleep pipeline + monitoring

**Pros:**
- 1-antes-del-batch salvó 19 renders rotos cuando descubrimos bug EQ silence
- QA score automático bloqueó upload de mala calidad
- Spec-driven content tracking (`spec_venom.replica_de`) → permite analizar fórmula 30 días después
- Agent shorts-qa auto-actualizado con bugs nuevos = no repite errores
- FFmpeg ya tiene su engine de Pillow (no drawtext) — replicable en pipelines nuevos
- Persistir TODO en files = chat history descartable

**Cons:**
- Drawtext bug recurrente en pipelines nuevos (render_sleep cayó en mismo issue)
- Sub-agente background terminó dejando 8 renders corruptos (kill abrupto) — perdió consistency
- YT quota daily 6 uploads pegó después del 7° — script abortaba en 429 sin retry siguientes
- LUFS global pasó QA score 9/10 con voz SILENCIADA total (música rellenaba)
- Dry-run sobrescribió `shorts_schedule.json` real → perdimos yt_id/fb_id

**Consejo Claude Code:**
- Pipelines ffmpeg nuevos: ASUMIR `DRAWTEXT_OK=False` desde día 1, usar Pillow PNG overlay
- Background sub-agentes: NUNCA para batch renders pesados (kill abrupto = corrupted files). Bash loop sequential mejor
- Upload scripts batch: SIEMPRE try/except + skip-error + persistir IDs reales pre-error
- Dry-run: NUNCA sobrescribir state files de producción (separate dry_run.json)
- QA: voice-band check 300-3kHz mean OBLIGATORIO — LUFS global miente con música
- Cuando Fernando dice "calidad 2/10" → isolar bugs uno por uno con tests aislados ffmpeg, NO defender

**Patrón nuevo capturado:**
- FFmpeg 8.1+ strict mode: `equalizer:t=o:w=>5` (octavas) = silence. Auditar EQ chains heredados al upgrade
- `zoompan` no acepta `t` → usar `on/d` para progresión 0-1
- `overlay` no acepta `alpha` option → fade alpha en PNG stream ANTES de overlay
- `amix` default `normalize=1` divide entre N → loudnorm SIEMPRE post-mix
- macOS Sequoia: launchd no puede leer `~/Documents/` por default → FDA grant a binaries
