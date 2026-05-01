# Protocolo de validacion clinica IAAS

## Objetivo

Validar que el sistema ayuda a priorizar sospechas IAAS sin reemplazar la decision humana.

## Fase 1: Casos sinteticos

Crear por cada IAAS prioritaria:

- 5 casos positivos claros.
- 5 casos negativos claros.
- 5 casos IPI/POA por fecha de toma dia 1 o 2.
- 5 casos con datos incompletos.
- 5 casos con PHI residual.

IAAS prioritarias iniciales:

1. IVU
2. NAV
3. ITS-CVC

## Fase 2: Retrospectiva local

Usar minimo 30 casos historicos anonimizados:

- 10 IVU
- 10 NAV
- 10 ITS-CVC

Cada caso debe tener dictamen humano de referencia.

## Metricas minimas

| Metrica | Meta inicial |
|---|---|
| Reportes generados sin error | 100% |
| PHI residual en outputs | 0 |
| Dictamen con evidencia trazable | 100% |
| Dictamen negativo con motivo de descarte | 100% |
| Sensibilidad | medir, no prometer |
| Especificidad | medir, no prometer |

## Criterio de no avance

No avanzar a piloto si:

- Hay PHI en `outputs`.
- Hay dictamen "Cumple" sin evidencia por folio.
- Hay errores con fechas.
- El especialista no puede entender el motivo de descarte.

## Firma de revision humana

En version futura, cada caso debe registrar:

- Revisor.
- Fecha de revision.
- Decision final.
- Comentario.
