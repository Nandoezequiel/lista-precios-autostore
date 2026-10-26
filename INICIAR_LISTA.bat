@echo off
title Lista de Precios AutoStore
cd /d "%~dp0"
echo Iniciando la Lista de Precios AutoStore (cerrar esta ventana para apagarla)...
python server.py
pause
