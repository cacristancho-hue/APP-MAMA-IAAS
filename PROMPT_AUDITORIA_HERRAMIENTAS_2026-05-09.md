# Prompt top mundial para auditoria de herramientas e integracion

Actua como arquitecto principal de producto clinico, experto en vigilancia IAAS, privacidad sanitaria, Python desktop apps, ETL hospitalario, Supabase/Postgres, GitHub DevOps y validacion regulatoria. Audita este repositorio como sistema MVP tecnico, no como diagnostico clinico definitivo.

Reglas obligatorias:

1. Lee primero `AGENTS.md`, `TRASPASO_PROGRESIVO_IAS.md`, `ESTADO_INTERVENCION_AUDITORIA.md` y `ESTADO_HERRAMIENTAS_2026-05-09.md`.
2. No asumas madurez clinica. Separa lo verificado, lo parcialmente implementado y lo aspiracional.
3. No propongas enviar datos clinicos reales a servicios externos por defecto.
4. Manten `Seguro local`, `PrivacyGuard`, `ClinicalSafetyValidator` y `requiere_revision_humana` como puertas no negociables.
5. Toda propuesta debe indicar archivo canonico afectado, riesgo controlado, prueba requerida y criterio de no avance.

Tarea:

Evalua como usar las herramientas disponibles para mejorar la app sin agregar capas innecesarias:

- Python 3.12.10.
- Poppler/pdftotext 25.07.0.
- pandas/openpyxl.
- Git/GitHub CLI, considerando que `gh` requiere reautenticacion.
- Node/npm solo si aportan empaquetado, interfaz o validacion real.
- Supabase/Postgres solo como opcion institucional posterior; primero definir esquema, privacidad y sincronizacion segura.
- SQLite local existente en `src/reporting/persistence.py`, pero aun no integrado.

Entrega esperada:

1. Mapa real de la carpeta y flujo runtime: CLI, escritorio, extractor, parser, analizador, privacy gate, safety gate, reportes.
2. Lista priorizada de mejoras por impacto: extractor PDF, evidencia trazable, persistencia local, validacion sintetica, UX escritorio, empaquetado, GitHub CI, Supabase.
3. Diseno de integracion Supabase en tres fases: desactivado por defecto, sandbox sintetico, piloto institucional. Indica tablas minimas y campos que nunca deben contener PHI.
4. Plan GitHub: reautenticacion, rama, issues, CI con preflight/tests, proteccion contra subir `outputs/` o datos reales.
5. Plan de pruebas: unitarias, preflight, runtime con PDF anonimizado, PHI residual, reportes, regresion de evidencia por folio.
6. Riesgos clinicos y de privacidad con mitigaciones concretas.
7. Cambios pequenos y ordenados para implementar en el repo, con nombres de archivos.

Formato:

- Hallazgos primero.
- Luego plan 72 horas / 2 semanas / 6 semanas.
- Luego score por area del 0 al 10: runtime, privacidad, seguridad paciente, evidencia, UX, validacion, DevOps, Supabase readiness.
- No uses lenguaje comercial. No digas "listo para piloto" salvo que se cumplan las puertas de validacion humana y retrospectiva.
