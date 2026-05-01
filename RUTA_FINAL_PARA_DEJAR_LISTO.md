# Ruta final para dejar el sistema listo

## Antes de que trabaje otra IA

Debe leer:

```text
AGENTS.md
TRASPASO_PROGRESIVO_IAS.md
REGISTRO_PROGRESO_IAS.md
```

## Ahora, sin Python

Puede ejecutar:

```text
VERIFICAR_SIN_PYTHON.bat
```

Esto revisa que los archivos principales existan y que no hayan quedado referencias obsoletas.

## Cuando Python este instalado

Ejecute en este orden:

1. `ABRIR_PROGRAMA.bat`
2. `python -m unittest discover -s tests`
3. `python main.py --excel data\raw_excel\microbiologia_sintetica.csv --pdf "HISTORIA CLINICA TIPO HOSPITAL REGIONAL DE LA ORINOQUIA EJEMPLO.pdf" --tipo-iaas IVU --mode stub`
4. Revisar la carpeta `outputs`

## Para crear el ejecutable

Cuando todo lo anterior funcione:

```text
CREAR_EXE.bat
```

El programa quedara en:

```text
dist\SistemaIAAS.exe
```

## Para uso diario

La usuaria final debe abrir:

```text
SistemaIAAS.exe
```

Luego:

1. Cargar PDF.
2. Cargar laboratorio.
3. Colocar fechas.
4. Elegir tipo IAAS.
5. Usar `Seguro local`.
6. Presionar `ANALIZAR`.
7. Abrir reporte HTML.
