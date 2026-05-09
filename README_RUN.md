# Guía de Ejecución Técnica - Sistema IAAS V3

## Arquitectura de Rigor Clínico
Este MVP ha sido robustecido para operar como un motor de auditoría epidemiológica de alto nivel, incorporando:
1. **Motor NLP Determinístico:** Detección de sinónimos clínicos y negaciones bidireccionales.
2. **Matriz de Validación:** 11 categorías de IAAS con umbrales de co-ocurrencia por dimensión.
3. **Análisis de Tendencias:** Comparación matemática contra el perfil basal de ingreso (Día 3).

## Instalación Profesional
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Nota operativa 2026-05-09:
- El entorno local ya tiene Python 3.12.10 y Poppler/pdftotext 25.07.0.
- Si `pymupdf` no esta instalado, el extractor PDF usa `pdftotext` como fallback local.
- Mantener `--mode stub` como modo seguro por defecto.

## Flujo de Ejecución (CLI)
Para un análisis forense completo desde consola:

### Análisis Universal (Todas las IAAS)
```powershell
python main.py --pdf "historia.pdf" --excel "lab.xlsx" --tipo-iaas TODAS --mode stub
```

### Análisis Específico con Rango de Fechas
```powershell
python main.py --pdf "historia.pdf" --tipo-iaas NAV --fecha-inicio 01/05/2026 --fecha-fin 15/05/2026 --mode stub
```

## Capas de Validación Interna
- **Día de Estancia >= 3:** Calculado por delta `timedelta(days=2)` entre ingreso y evento.
- **Deterioro Significativo:** +0.5°C en fiebre basal o +20 pts en FiO2 respiratorio.
- **Negaciones:** Filtra términos como "sin hallazgos", "niega", "negativo" antes y después del síntoma.

## Pruebas de Sistema
Antes de entregar al piloto, ejecute la batería de pruebas completa:
```powershell
# Verificación de integridad de archivos y contratos
python scripts\preflight.py

# Pruebas unitarias de motor léxico, negaciones y matrices
python -m unittest discover -s tests
```

Si la suite se ejecuta dentro de un sandbox que bloquee `tempfile`, repetirla fuera del sandbox o fijar `TMP/TEMP` a una carpeta local con permisos de escritura.

## Reportes Auditables
Ubicación: `outputs/iaas_[TIPO]_[FECHA].html`
- El archivo `.json` contiene la traza técnica completa para integración con otros sistemas.
- El archivo `.html` es el Dashboard de Auditoría para el médico especialista.
- La base local SQLite anonima queda por defecto en `data/iaas_vigilancia.db`.
- Para desactivar el historial local use `--no-persist`.
- Para cambiar la base local use `--db-path "ruta\iaas_vigilancia.db"`.
- En el `.exe`, reportes e historial se escriben en `%LOCALAPPDATA%\SistemaIAAS` para evitar errores de permisos.
