@echo off
title Sistema IAAS
cd /d "%~dp0"

set "PYTHON_EXE="
for /f "delims=" %%P in ('where python 2^>nul') do if not defined PYTHON_EXE set "PYTHON_EXE=%%P"
if not defined PYTHON_EXE (
  echo No se encontro Python instalado.
  echo.
  echo El programa ya esta construido, pero Windows necesita Python para abrirlo.
  echo Cuando Python este instalado, vuelva a hacer doble clic en este archivo.
  echo.
  pause
  exit /b 1
)

echo %PYTHON_EXE% | find /I "WindowsApps" >nul
if not errorlevel 1 (
  echo Windows solo encontro el acceso directo de Microsoft Store, no Python real.
  echo.
  echo Instale Python real y vuelva a abrir este archivo.
  echo.
  pause
  exit /b 1
)

"%PYTHON_EXE%" app_escritorio.py

if errorlevel 1 (
  echo.
  echo No se pudo abrir el programa. Revise el mensaje anterior.
  echo.
  pause
)
