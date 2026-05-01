# Estado del Proyecto: Sistema Automatizado de Vigilancia IAAS

## Estado operativo real

El proyecto esta en fase MVP tecnico. Ya tiene prompts clinicos modulares para 11 tipos de IAAS, extractor PDF, parser Excel inicial, analizador con modo `stub`/`llm` y reporter JSON/CSV. No debe considerarse producto clinico ni sistema diagnostico.

## Modulos implementados

### Módulo PDF

- Archivo: `src/pdf_extractor/extractor.py`
- Extrae texto con PyMuPDF.
- Segmenta por folios.
- Deidentifica PHI basico.
- Extrae signos vitales determinísticos.

### Módulo Excel

- Archivo: `src/excel_parser/parser.py`
- Lee microbiologia desde `.xlsx`.
- Identifica cultivos positivos por columnas flexibles.
- Calcula dia de estancia y clasifica `SOSPECHA_IAAS` vs `IPI_POA`.

### Módulo IAAS

- Archivo: `src/llm_analyzer/analyzer.py`
- Mantiene prompts clinicos en `src/llm_analyzer/prompts_clinicos/`.
- Modo `stub`: salida deterministica, baja confianza, para pruebas de pipeline.
- Modo `llm`: usa proveedor compatible con OpenAI mediante variables de entorno.
- Todo dictamen requiere revision humana.

### Módulo Reporte

- Archivo: `src/reporting/reporter.py`
- Genera reporte JSON completo y CSV resumido en `outputs/`.

## Pendientes antes de piloto

1. Instalar Python real y dependencias.
2. Ejecutar pruebas: `python -m unittest discover -s tests`.
3. Validar con casos sinteticos positivos/negativos por IAAS.
4. Reemplazar criterios narrativos por matriz versionada INS/SIVIGILA/CDC.
5. Validar privacidad con PHI realista antes de usar una API externa.
6. Medir falsos positivos y falsos negativos con revision de especialista.
