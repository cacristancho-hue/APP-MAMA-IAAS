# Checklist de Preparacion para Piloto IAAS

## Puertas tecnicas

- Python real instalado, no alias de Microsoft Store.
- `python -m unittest discover -s tests` pasa completo.
- `python main.py --excel data\raw_excel\microbiologia_sintetica.csv --pdf "<PDF>" --tipo-iaas IVU --mode stub` genera JSON/CSV.
- Modo `llm` solo se usa con `IAAS_LLM_API_KEY` y despues de pasar privacy gate.
- Todo reporte tiene `revision_humana_obligatoria: true`.

## Puertas de privacidad

- Ningun nombre, documento, telefono, direccion o email en `outputs/`.
- El nombre del PDF se guarda como basename, no como ruta local completa.
- Casos reales deben pasar por deidentificacion antes de salir del equipo.
- No enviar texto clinico a API externa si `PrivacyGuard` detecta PHI residual.

## Puertas clinicas

- Validar primero IVU, NAV e ITS-CVC antes de activar las 11 IAAS.
- Cada dictamen debe tener: fecha ancla, criterio temporal, evidencia por folio y motivo de descarte si es negativo.
- Ningun caso se considera confirmado sin revision de epidemiólogo/infectólogo.
- Registrar falsos positivos y falsos negativos por tipo IAAS.

## Paquete minimo de validacion

- 5 casos positivos sinteticos por IAAS prioritaria.
- 5 casos negativos sinteticos por IAAS prioritaria.
- 5 casos IPI/POA por fecha de toma dia 1-2.
- 5 casos con PHI residual para verificar bloqueo.
- 5 casos con evidencia incompleta para verificar `motivo_descarte`.
