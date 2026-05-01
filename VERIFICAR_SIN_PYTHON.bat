@echo off
title Verificar proyecto IAAS sin Python
cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -File ".\scripts\verificar_sin_python.ps1"
pause
