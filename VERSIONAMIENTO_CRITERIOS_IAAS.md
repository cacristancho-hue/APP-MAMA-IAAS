# Versionamiento de Criterios IAAS

## Regla de Rigor
Cada criterio IAAS en este sistema se evalúa bajo una **Matriz de Validación Multidimensional** (V3) que exige evidencia en dimensiones independientes antes de la confirmación.

## Estado del Registro
**Versión:** `operativo_intermedio_sivigila_v1` (Mayo 2026)
**Cobertura:** 11 categorías de IAAS estandarizadas.
**Fuente Primaria:** Protocolos de Vigilancia Salud Pública - INS / SIVIGILA Colombia (Actualización 2024).

## Criterios Estandarizados (11)
| IAAS | Estado V3 | Matriz Implementada | Lexical Map |
|---|---|---|---|
| IVU / CAUTI | Listo | Clínica + Lab + Dispositivo | Sí |
| NAV / VAP | Listo | Clínica + Lab + Rx + Oxig + Disp | Sí |
| ITS-CVC / CLABSI | Listo | Clínica + Lab + Disp + Foco | Sí |
| ISQ | Listo | Clínica + Quirúrgico + Lab | Sí |
| Sepsis Tardía | Listo | Clínica + Lab + Cronología | Sí |
| ECN | Listo | Clínica + Radiología + Bell | Sí |
| Endometritis | Listo | Clínica + Antecedente + Tiempo | Sí |
| Clostridioides | Listo | Clínica + Lab + Antibiótico | Sí |
| Meningitis | Listo | Clínica + LCR + Dispositivo | Sí |
| Piel / Blandos | Listo | Clínica + Lab + Contexto | Sí |
| Neonatal Local | Listo | Clínica + Localización + Tiempo | Sí |

## Registro de Cambios Arquitectónicos
- **2026-05-01:** Upgrade masivo de V2 (narrativo) a V3 (matriz). Se añadieron umbrales de co-ocurrencia y sensibilidad léxica para todas las categorías.
- **2026-05-01:** Implementación de motor de negaciones clínicas para mejorar la especificidad del registro.
