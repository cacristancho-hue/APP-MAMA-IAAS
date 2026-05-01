# Empaquetar como programa instalable

Esta etapa se hace despues de instalar Python y verificar que el sistema funciona.

## Objetivo final

Crear un archivo `.exe` para que la usuaria abra el sistema sin ver codigo ni terminal.

## Opcion recomendada

Use el archivo:

```text
CREAR_EXE.bat
```

Este archivo instala dependencias, ejecuta pruebas y crea el ejecutable usando `SistemaIAAS.spec`.

El ejecutable quedara en:

```text
dist\SistemaIAAS.exe
```

## Importante

- Primero debe pasar `python -m unittest discover -s tests`.
- Primero debe abrir correctamente `ABRIR_PROGRAMA.bat`.
- El archivo `SistemaIAAS.spec` incluye prompts clinicos y plantillas necesarias.
- No empaquetar datos reales de pacientes dentro del `.exe`.
- Los reportes deben seguir saliendo a `outputs`.

## Instalador completo

Cuando el `.exe` funcione, se puede crear un instalador con Inno Setup o similar. Esa etapa es posterior.
