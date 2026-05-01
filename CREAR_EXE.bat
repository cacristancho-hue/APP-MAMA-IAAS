@echo off
title Crear SistemaIAAS.exe
cd /d "%~dp0"

set "PYTHON_EXE="
for /f "delims=" %%P in ('where python 2^>nul') do if not defined PYTHON_EXE set "PYTHON_EXE=%%P"
if not defined PYTHON_EXE (
  echo No se encontro Python.
  echo Instale Python antes de crear el ejecutable.
  pause
  exit /b 1
)

echo %PYTHON_EXE% | find /I "WindowsApps" >nul
if not errorlevel 1 (
  echo Windows solo encontro el acceso directo de Microsoft Store, no Python real.
  echo Instale Python real antes de crear el ejecutable.
  pause
  exit /b 1
)

echo Instalando dependencias necesarias para construir el ejecutable...
"%PYTHON_EXE%" -m pip install -r requirements.txt pyinstaller
if errorlevel 1 (
  echo No se pudieron instalar dependencias.
  pause
  exit /b 1
)

echo Ejecutando pruebas...
"%PYTHON_EXE%" -m unittest discover -s tests
if errorlevel 1 (
  echo Las pruebas fallaron. No se creara el .exe.
  pause
  exit /b 1
)

echo Creando SistemaIAAS.exe...
"%PYTHON_EXE%" -m PyInstaller SistemaIAAS.spec --clean --noconfirm
if errorlevel 1 (
  echo Fallo la creacion del ejecutable.
  pause
  exit /b 1
)

echo.
echo Ejecutable creado en:
echo dist\SistemaIAAS.exe
echo.
pause
