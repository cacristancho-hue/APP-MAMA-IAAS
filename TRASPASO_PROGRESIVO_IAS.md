# Traspaso progresivo para IAs

## Proposito

Este documento permite que una IA continue el trabajo sin empezar de cero, sin omitir informacion y sin repetir errores ya detectados.

## Resumen del proyecto

Sistema de vigilancia IAAS para Colombia. El objetivo es cargar historia clinica PDF y laboratorio Excel/CSV, seleccionar fechas y tipo de IAAS, ejecutar analisis local o con IA externa controlada, y generar reportes auditables para revision humana.

El sistema no debe emitir diagnostico definitivo. Produce preclasificacion y evidencia para apoyar revision de epidemiologia/infectologia.

## Estado actual

Implementado:

- Interfaz de escritorio en `app_escritorio.py`.
- Orquestador CLI en `main.py`.
- Extractor PDF con deidentificacion basica.
- Parser de laboratorio CSV sin dependencias externas y Excel con pandas/openpyxl.
- Registro operativo de criterios para 11 IAAS.
- Analizador con modo `stub` y modo `llm`.
- Cliente LLM compatible con API tipo OpenAI.
- Safety gate clinico que bloquea positivos sin evidencia.
- Privacy gate que bloquea reportes con PHI residual.
- Reportes JSON, CSV y HTML.
- Plantilla de laboratorio.
- Manual de usuario final.
- Preparacion de empaquetado `.exe`.
- Verificador estatico sin Python.

No validado aun:

- Ejecucion real por falta de Python real en el equipo.
- Extraccion sobre PDF real en runtime.
- Build `.exe`.
- Sensibilidad/especificidad.
- Revision formal de criterios INS/SIVIGILA/CDC por especialista.

## Auditoria inicial y respuesta

La auditoria identifico debilidades en:

- Runtime/integracion.
- Validacion clinica.
- Seguridad del paciente.
- Privacidad/compliance.
- UX/reportes.
- Parser Excel/laboratorio.
- Trazabilidad de evidencia.
- Preparacion para piloto.

Las intervenciones realizadas estan resumidas en:

```text
ESTADO_INTERVENCION_AUDITORIA.md
```

## Como continuar sin omitir informacion

Antes de modificar codigo, revisar:

1. Que area auditada se esta tocando.
2. Que archivo canonico corresponde.
3. Que documento debe actualizarse.
4. Que prueba o preflight debe cubrir el cambio.
5. Que riesgo clinico o de privacidad puede aparecer.

Despues de modificar, actualizar:

```text
REGISTRO_PROGRESO_IAS.md
```

## Pendientes prioritarios

### Prioridad 1: Seguridad clinica

- Ampliar casos sinteticos por IAAS.
- Exigir evidencia trazable en todos los tipos.
- Mejorar motivos de descarte por tipo IAAS.
- Mantener revision humana obligatoria.

### Prioridad 2: Privacidad

- Ampliar patrones PHI.
- Crear pruebas con PHI sintetico.
- Documentar decision institucional para IA externa.

### Prioridad 3: UX

- Simplificar textos de la interfaz.
- Evitar terminos tecnicos visibles.
- Asegurar que el reporte HTML sea entendible para usuario no tecnico.

### Prioridad 4: Validacion

- Completar `scripts/preflight.py`.
- Alinear tests con criterios.
- Preparar paquete de casos sinteticos.

### Prioridad 5: Empaquetado

- Mantener `SistemaIAAS.spec`.
- No incluir datos reales en el ejecutable.
- Probar `CREAR_EXE.bat` cuando exista Python real.

## No repetir estos errores

- No decir que el sistema esta listo para piloto sin validacion.
- No decir que los criterios estan certificados.
- No esconder que `stub` es modo seguro local, no diagnostico.
- No tratar ausencia de Python como unico pendiente.
- No cambiar foco a instalacion si el usuario pidio mejorar producto.

## Definicion de listo antes de piloto

- Python real instalado y pruebas pasando.
- Reporte generado con PDF y laboratorio anonimizados.
- Cero PHI en outputs.
- Cada dictamen con evidencia trazable.
- Cada negativo con motivo de descarte.
- Revision humana de especialista.
- Metricas iniciales de falsos positivos y falsos negativos.
