@echo off
echo ============================================================
echo  TGC APP LOGISTICA - Instalacion Windows
echo ============================================================

REM Crear entorno virtual
echo Creando entorno virtual...
python -m venv venv

REM Activar entorno virtual
echo Activando entorno virtual...
call venv\Scripts\activate

REM Instalar dependencias
echo Instalando dependencias...
pip install -r requirements.txt

REM Copiar .env si no existe
if not exist .env (
    echo Copiando configuracion de ejemplo...
    copy .env.example .env
)

REM Inicializar base de datos
echo Inicializando base de datos...
flask db init
flask db migrate -m "Inicio"
flask db upgrade

echo ============================================================
echo  Instalacion completa.
echo  Para iniciar el servidor ejecute:  python run.py
echo  Acceda desde:                      http://localhost:5000
echo ============================================================
pause
