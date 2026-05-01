# Contrato operativo para IAs y agentes

Este repositorio es un sistema de vigilancia IAAS en fase MVP tecnico. Cualquier IA que trabaje aqui debe avanzar de forma progresiva, sin omitir informacion, sin sobreprometer madurez clinica y sin tratar el sistema como diagnostico definitivo.

## Reglas obligatorias

1. Leer primero `TRASPASO_PROGRESIVO_IAS.md`.
2. Revisar `ESTADO_INTERVENCION_AUDITORIA.md` antes de proponer cambios.
3. No borrar ni reemplazar archivos completos sin justificarlo.
4. No afirmar que algo funciona si no fue ejecutado o verificado.
5. No usar datos clinicos reales en ejemplos, logs o reportes.
6. No enviar informacion a IA externa salvo que el usuario lo pida explicitamente y exista control de privacidad.
7. Todo dictamen IAAS debe mantener `requiere_revision_humana`.
8. Todo resultado positivo debe tener evidencia trazable por folio/cita; si no, debe bloquearse o marcarse como duda tecnica.

## Orden de lectura minimo

1. `TRASPASO_PROGRESIVO_IAS.md`
2. `ESTADO_INTERVENCION_AUDITORIA.md`
3. `README_RUN.md`
4. `MANUAL_USUARIO_FINAL.md`
5. `PROTOCOLO_VALIDACION_CLINICA.md`
6. `POLITICA_PRIVACIDAD_OPERATIVA.md`
7. `VERSIONAMIENTO_CRITERIOS_IAAS.md`
8. `CHECKLIST_ENTREGA_TECNICA.md`

## Superficies canonicas

- Motor CLI: `main.py`
- Interfaz escritorio: `app_escritorio.py`
- Contratos: `src/contracts.py`
- Criterios: `src/criteria/registry.py`
- Analizador: `src/llm_analyzer/analyzer.py`
- Extractor PDF: `src/pdf_extractor/extractor.py`
- Parser laboratorio: `src/excel_parser/parser.py`
- Privacidad: `src/privacy/guard.py`
- Seguridad clinica: `src/validation/clinical_safety.py`
- Reportes: `src/reporting/reporter.py`

## Forma correcta de trabajar

Cada intervencion debe seguir este ciclo:

1. Identificar el area auditada que se esta mejorando.
2. Revisar el archivo canonico correspondiente.
3. Aplicar un cambio pequeno y trazable.
4. Actualizar documentacion si cambia flujo, riesgo o uso.
5. Actualizar pruebas o preflight si cambia comportamiento.
6. Registrar el cambio en `REGISTRO_PROGRESO_IAS.md`.

## Areas que no se deben omitir

- Seguridad del paciente.
- Privacidad y PHI.
- Evidencia trazable.
- Motivo de descarte.
- Revision humana.
- Versionamiento de criterios.
- UX para usuaria no tecnica.
- Preparacion para piloto.
- Empaquetado Windows.
- Validacion con casos sinteticos y retrospectivos.

## Prohibiciones

- No cambiar el modo predeterminado `Seguro local`.
- No llamar a IA externa por defecto.
- No ocultar limitaciones por falta de Python, PDF real o validacion clinica.
- No presentar `stub` como diagnostico.
- No agregar capas nuevas si se puede mejorar una capa existente.
