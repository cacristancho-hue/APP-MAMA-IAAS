# Diccionario del archivo de microbiologia

Use estas columnas para que el sistema pueda leer el laboratorio sin confundirse.

## Columnas recomendadas

| Columna | Que significa | Ejemplo |
|---|---|---|
| `paciente` | Identificador del paciente, idealmente anonimizado | `PACIENTE_001` |
| `fecha_ingreso` | Fecha de ingreso hospitalario | `2026-04-01` |
| `fecha_toma` | Fecha de toma de muestra | `2026-04-04` |
| `muestra` | Tipo de muestra | `Urocultivo` |
| `organismo` | Germen aislado | `Escherichia coli` |
| `resultado` | Resultado del cultivo | `positivo` |
| `servicio` | Servicio o unidad | `UCI` |

## Reglas simples

- Use una fila por cultivo.
- Evite nombres completos de pacientes.
- Si puede, use codigos como `PACIENTE_001`.
- Use fechas en formato `AAAA-MM-DD` o `DD/MM/AAAA`.
- Para cultivos negativos, escriba `negativo` en `resultado`.

## Archivo de ejemplo

Puede copiar esta estructura desde:

```text
data\raw_excel\PLANTILLA_LABORATORIO.csv
```
