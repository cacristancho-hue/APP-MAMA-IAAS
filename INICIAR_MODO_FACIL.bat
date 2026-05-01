@echo off
title Sistema IAAS - Modo Facil
cd /d "%~dp0"

echo ================================================
echo  SISTEMA IAAS - MODO FACIL
echo ================================================
echo.
echo Este modo NO envia datos a internet.
echo Genera un reporte local en la carpeta outputs.
echo.

set "PYTHON_EXE="
for /f "delims=" %%P in ('where python 2^>nul') do if not defined PYTHON_EXE set "PYTHON_EXE=%%P"
if not defined PYTHON_EXE (
  echo No se encontro Python instalado.
  echo Cuando pueda instalarlo, vuelva a abrir este archivo.
  echo.
  pause
  exit /b 1
)

echo %PYTHON_EXE% | find /I "WindowsApps" >nul
if not errorlevel 1 (
  echo Windows solo encontro el acceso directo de Microsoft Store, no Python real.
  echo Cuando pueda instalar Python real, vuelva a abrir este archivo.
  echo.
  pause
  exit /b 1
)

"%PYTHON_EXE%" main.py --excel "data\raw_excel\microbiologia_sintetica.csv" --pdf "HISTORIA CLINICA TIPO HOSPITAL REGIONAL DE LA ORINOQUIA EJEMPLO.pdf" --tipo-iaas IVU --mode stub

echo.
echo Si no hubo errores, revise la carpeta outputs.
echo.
pause
