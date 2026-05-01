# Estado de intervencion por area auditada

| Area auditada | Intervencion realizada | Estado |
|---|---|---|
| Claridad del problema clinico | Manual de usuario, ruta final, estado real del proyecto | Mejorado |
| Adecuacion epidemiologica IAAS | Registro operativo de criterios para 11 IAAS | Mejorado, pendiente revision formal |
| Arquitectura modular | Separacion en extractor, parser, analizador, criterios, privacidad, validacion, reportes | Mejorado |
| Extractor PDF | Correccion de signos vitales, PHI basico, folios y estructura | Mejorado, pendiente validacion con PDFs reales |
| Prompts clinicos | Prompts conservados e inyectados con criterio operativo versionado | Mejorado |
| Motor LLM/dictamen | Modo seguro local, modo IA externa, cliente configurable, auditoria interna | Mejorado |
| Integracion/runtime | CLI, app escritorio, lanzadores `.bat`, empaquetado `.exe` preparado | Mejorado, pendiente Python real |
| Validacion clinica | Safety gate, protocolo de validacion, pruebas planeadas | Mejorado |
| Seguridad del paciente | Bloqueo de confirmaciones sin evidencia, revision humana obligatoria | Mejorado |
| Privacidad/compliance | PrivacyGuard, politica operativa, bloqueo de reportes con PHI | Mejorado |
| UX/reportes | App de escritorio, HTML legible, CSV, boton abrir reporte | Mejorado |
| Escalabilidad/mantenibilidad | Contratos, registry de criterios, preflight, checklist tecnico | Mejorado |
| Diferenciacion de producto | Flujo IAAS auditable con evidencia y descarte, no solo chatbot | Mejorado |
| Preparacion para piloto | Checklist, matriz de riesgos, protocolo retrospectivo | Mejorado, pendiente validacion humana |

## Pendientes que no deben ocultarse

- Validacion real con Python instalado.
- Prueba con PDF real anonimizado.
- Revision formal de criterios INS/SIVIGILA/CDC.
- Medicion de sensibilidad/especificidad.
- Decision institucional sobre IA externa.
