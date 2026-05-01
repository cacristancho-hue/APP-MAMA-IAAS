# Matriz de riesgos clinicos IAAS

## Riesgos principales

| Riesgo | Ejemplo | Control implementado | Pendiente |
|---|---|---|---|
| Falso positivo IAAS | Cultivo tomado dia 2 se clasifica como hospitalario | Regla temporal en parser laboratorio | Validar contra criterios INS/SIVIGILA por tipo |
| Falso negativo IAAS | Nota clinica relevante no extraida del PDF | Reporte exige revision humana | Validar extractor contra PDFs reales |
| PHI residual | Nombre/documento llega a reporte o API externa | `PrivacyGuard` bloquea reporte | Ampliar pruebas con datos reales anonimizados |
| Uso como diagnostico definitivo | Usuario interpreta "Cumple" como diagnostico final | Reportes marcan revision humana obligatoria | Agregar firma de revisor en etapa futura |
| Criterio desactualizado | Cambia definicion INS/CDC | Registro de criterios versionado | Mantener fecha/version formal de fuentes |
| Error de fecha | Fecha inicial mayor que final | Validacion de rango | Pruebas con fechas ambiguas |
| Dependencia de IA externa | Envio accidental de datos sensibles | Modo predeterminado `Seguro local` | Boton IA externa debe seguir protegido por clave |

## Regla de oro

El sistema solo debe producir una preclasificacion auditable. La decision final debe ser humana.

## Antes de piloto

- Revisar 30 casos retrospectivos.
- Medir falsos positivos.
- Medir falsos negativos.
- Confirmar que no hay PHI en `outputs`.
- Confirmar que cada dictamen tiene motivo y evidencia.
