@echo off
chcp 65001 >nul
echo.
echo  ╔══════════════════════════════════════╗
echo  ║      LOOP VIDEO MAKER                ║
echo  ║      Generador de Videos Bíblicos    ║
echo  ╚══════════════════════════════════════╝
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo  ERROR: Python no está instalado.
    echo  Descárgalo en: https://www.python.org/downloads/
    echo  Asegúrate de marcar "Add Python to PATH" al instalar.
    pause
    exit /b 1
)

cd /d "%~dp0"

if not exist ".venv" (
    echo  Creando entorno virtual...
    python -m venv .venv
)

call .venv\Scripts\activate.bat

echo  Verificando dependencias...
pip install -r requirements.txt --quiet

echo  Iniciando la aplicación...
echo  Abre tu navegador en: http://localhost:7860
echo.
python app.py
pause
