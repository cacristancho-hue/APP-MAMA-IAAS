# Estado de herramientas y carpeta - 2026-05-09

## Verificacion local ejecutada

- Python real disponible: `Python 3.12.10`.
- `pdftotext` disponible: Poppler `25.07.0`.
- `pandas` disponible: `3.0.2`.
- `openpyxl` disponible: `3.1.5`.
- `pymupdf` no esta instalado; el extractor ahora usa `pdftotext` como fallback local si falta PyMuPDF.
- Node disponible: `v20.20.2`.
- npm disponible: `10.8.2`.
- Git disponible: `2.53.0.windows.3`.
- GitHub CLI disponible: `2.92.0`, pero el token local esta invalido.

## Estado del repo y runtime

- Carpeta: MVP tecnico de vigilancia IAAS con CLI, escritorio, criterios, extractor PDF, parser laboratorio, privacidad, safety gate y reportes.
- Pruebas: `python scripts\preflight.py` pasa.
- Pruebas unitarias: `python -m unittest discover -s tests` pasa fuera del sandbox local de Codex; dentro del sandbox falla `tempfile` por permisos de subdirectorios temporales.
- Runtime validado: `python main.py --pdf "HISTORIA CLINICA TIPO HOSPITAL REGIONAL DE LA ORINOQUIA EJEMPLO.pdf" --excel "data\raw_excel\microbiologia_sintetica.csv" --tipo-iaas IVU --mode stub` genero reporte con 252 folios procesados.

## Supabase

- No hay carpeta `supabase/`.
- No hay variables de entorno `SUPABASE_*`, `DATABASE_URL`, `POSTGRES_*` visibles.
- No se encontro configuracion local de Supabase en el codigo.
- `supabase`, `docker`, `psql` y `sqlite3` no estan disponibles como comandos en PATH.
- Existe `src/reporting/persistence.py` sin versionar que apunta a SQLite local (`data/iaas_vigilancia.db`), pero no esta integrado al flujo canonico.

## GitHub

- Remoto configurado: `https://github.com/cacristancho-hue/APP-MAMA-IAAS.git`.
- Rama local: `master`, commit base `720b0a0`.
- `gh auth status` reporta token invalido en keyring para `cacristancho-hue`.
- `git remote show origin` responde, pero `HEAD branch` aparece como `(unknown)`.
- `git ls-remote origin` no devolvio referencias visibles en esta verificacion.

## Lectura tecnica

La carpeta ya no esta bloqueada por falta de Python. La prioridad no es conectar Supabase de inmediato: primero conviene estabilizar persistencia local auditable, esquema de eventos, migracion opcional a Supabase y reautenticacion GitHub. Supabase debe entrar solo como backend institucional controlado, nunca como envio automatico de PHI.
