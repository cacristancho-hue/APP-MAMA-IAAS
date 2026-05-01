# Checklist de Entrega Técnica V3 (Fase Piloto)

## Infraestructura y Código
- [ ] `main.py` y `app_escritorio.py` actualizados a soporte universal 11 IAAS.
- [ ] Motor determinístico `stub` implementa matrices multidimensionales.
- [ ] `CRITERIA_REGISTRY` contiene mapas léxicos y umbrales `min_required` para las 11 categorías.
- [ ] El sistema detecta negaciones bidireccionales (prefijo y sufijo).

## Validación Clínica y Datos
- [ ] El cálculo de "Día de Estancia >= 3" ha sido validado matemáticamente.
- [ ] El motor de tendencias basales (+0.5°C, +20 FiO2) está operativo.
- [ ] Las 11 IAAS tienen prompts V3 Forenses unificados en `prompts_clinicos/`.
- [ ] Se han inyectado las alertas de Excel en el flujo de análisis de la historia clínica.

## Reportabilidad y UX
- [ ] El Dashboard HTML visualiza la matriz de cumplimiento (badges ✔️/❌).
- [ ] El Dashboard muestra el motivo de descarte detallado por dimensión fallida.
- [ ] Los reportes JSON/CSV son coherentes con el nuevo contrato de datos.

## Pruebas de Seguridad
- [ ] `scripts/preflight.py` incluye pruebas para el Safety Gate multidimensional.
- [ ] `tests/test_core.py` cubre los nuevos casos de sinónimos y negaciones.
- [ ] El Privacy Guard ha sido validado con los nuevos patrones de documentos (PEP, CE, NIT).

## Documentación
- [ ] Manual de Usuario Final refleja el Dashboard V3.
- [ ] README técnico incluye los nuevos comandos y capas de análisis.
- [ ] Registro de Progreso tiene documentadas las 16 intervenciones.
