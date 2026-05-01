# Politica operativa de privacidad

## Principio

El sistema debe minimizar datos personales. El objetivo es vigilancia IAAS, no conservar identificacion del paciente.

## Datos que deben evitarse

- Nombre completo.
- Documento.
- Telefono.
- Direccion.
- Email.
- Rutas locales con nombres sensibles.

## Controles implementados

- Deidentificacion basica en extractor PDF.
- `PrivacyGuard` antes de escribir reportes.
- Reporte guarda solo el nombre del PDF, no la ruta completa.
- Modo predeterminado `Seguro local`.
- Bloqueo si se intenta usar IA externa sin clave configurada.

## Controles pendientes antes de datos reales

- Pruebas con ejemplos anonimizados realistas.
- Revision manual de `outputs`.
- Politica institucional sobre uso de IA externa.
- Consentimiento o autorizacion institucional si aplica.

## Regla de uso

No usar `IA externa` con datos reales hasta que un responsable institucional confirme que la deidentificacion es suficiente.
