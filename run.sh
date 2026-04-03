#!/bin/bash
echo ""
echo " ╔══════════════════════════════════════╗"
echo " ║      LOOP VIDEO MAKER                ║"
echo " ║      Generador de Videos Bíblicos    ║"
echo " ╚══════════════════════════════════════╝"
echo ""

if ! command -v python3 &> /dev/null; then
    echo " ERROR: Python3 no encontrado."
    echo " Instálalo con: brew install python3"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Crear virtualenv si no existe
if [ ! -d ".venv" ]; then
    echo " Creando entorno virtual..."
    python3 -m venv .venv
fi

# Activar virtualenv
source .venv/bin/activate

# Instalar dependencias
echo " Verificando dependencias..."
pip install -r requirements.txt --quiet

# Patch de compatibilidad: gradio_client 1.0.1 tiene un bug con Python 3.9
# que hace fallar el endpoint /info. Este patch lo corrige sin cambiar versión.
python3 - << 'PYEOF'
import os
path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
    ".venv/lib/python3.9/site-packages/gradio_client/utils.py")
if not os.path.exists(path):
    # buscar en cualquier version de python
    import glob
    matches = glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        ".venv/lib/python*/site-packages/gradio_client/utils.py"))
    if matches:
        path = matches[0]
    else:
        exit(0)

with open(path) as f:
    content = f.read()

old = 'def get_type(schema: dict):\n    if "const" in schema:'
new = 'def get_type(schema: dict):\n    if not isinstance(schema, dict):\n        return "unknown"\n    if "const" in schema:'

if old in content:
    content = content.replace(old, new)
    with open(path, "w") as f:
        f.write(content)
    print(" Patch gradio_client aplicado.")
PYEOF

echo " Iniciando la aplicación..."
echo " Se abrirá en: http://localhost:7860"
echo ""
python app.py
