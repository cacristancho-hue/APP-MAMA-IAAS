# Auditoria externa internacional - trabajo del 2026-05-09

## Alcance y metodo

Evaluacion externa simulada por panel multidisciplinario internacional sobre el trabajo ejecutado el 2026-05-09 en el MVP tecnico de vigilancia IAAS. Esta auditoria se basa en evidencia del repositorio, commits, validaciones ejecutadas y documentos operativos. No certifica validez clinica ni aptitud para piloto.

Evidencia revisada:

- Commits del dia:
  - `e38f9b6 Estabilizar runtime Python y GitHub`
  - `40f3d41 Agregar historial SQLite local anonimo`
  - `8545848 Preparar rutas portables para exe`
- Validaciones frescas:
  - `python scripts\preflight.py`: pasa.
  - `python -m unittest discover -s tests`: 15/15 OK.
- Runtime validado previamente hoy:
  - PDF sintetico formato HORO + CSV sintetico.
  - 252 folios extraidos.
  - Reporte JSON/HTML generado.
  - SQLite local generado con historial.
- Documentos revisados:
  - `TRASPASO_PROGRESIVO_IAS.md`
  - `ESTADO_INTERVENCION_AUDITORIA.md`
  - `ESTADO_HERRAMIENTAS_2026-05-09.md`
  - `REGISTRO_PROGRESO_IAS.md`
  - `PROMPT_AUDITORIA_HERRAMIENTAS_2026-05-09.md`

## Veredicto ejecutivo

El trabajo del dia transformo el repositorio de un MVP con dependencias y configuracion parcialmente bloqueadas a una base local ejecutable, versionada en GitHub, con persistencia SQLite anonima, pruebas activas y preparacion razonable para empaquetado Windows.

El avance mas importante no fue agregar mas IA, sino cerrar brechas operativas: Python real, `pdftotext`, GitHub, pruebas, runtime PDF, reporte, historial local y rutas escribibles para `.exe`.

No debe declararse listo para piloto. Las puertas pendientes son: build real con PyInstaller, prueba manual del `.exe`, revision visual de reportes/historial, validacion con casos sinteticos ampliados por IAAS, revision formal por especialista y politica institucional antes de cualquier nube/Supabase.

## Panel de expertos

### 1. Arquitectura clinica IAAS

Evaluador: experto en vigilancia epidemiologica hospitalaria, IAAS, SIVIGILA/CDC/NHSN.

Hallazgos:

- Se preservo correctamente la postura de apoyo a vigilancia, no diagnostico definitivo.
- `ClinicalSafetyValidator` mantiene bloqueo de confirmaciones sin evidencia y `requiere_revision_humana`.
- La prueba IVU fue ajustada para exigir temporalidad dia 3, evitando una confirmacion artificial con una sola nota sin ancla basal.
- El modo `stub` sigue siendo el modo local seguro, lo cual es correcto para evitar dependencia prematura de IA externa.

Riesgos:

- La matriz de criterios puede parecer mas madura de lo que esta clinicamente validada.
- Falta bateria sintetica amplia por cada IAAS, especialmente NAV, ITS-CVC, ECN, ISQ y neonatal.
- Aun no hay sensibilidad/especificidad ni revision formal por comite.

Puntuacion: 7/10.

Criterio de no avance:

- No avanzar a piloto si aparece un `cumple=True` sin evidencia trazable por folio/cita o si un negativo carece de motivo de descarte.

### 2. Privacidad y seguridad de datos

Evaluador: experto en privacidad sanitaria, minimizacion de datos, Ley 1581/HIPAA-style controls.

Hallazgos:

- `PrivacyGuard` se mantiene como puerta antes de reportes y antes de SQLite.
- Se ignoran `data/*.db`, outputs, wheels e indices temporales para evitar subir historiales locales o artefactos.
- La persistencia SQLite guarda resumen operativo, no PDF completo ni notas clinicas completas.
- Supabase se mantuvo fuera del flujo por defecto, decision correcta.

Riesgos:

- `source_pdf` conserva el nombre del archivo. Si un usuario usa nombres con PHI, el sistema debe bloquearlo o sugerir renombrado seguro.
- El historial HTML incluye rutas de reporte. Si esas rutas contienen nombres sensibles, podrian filtrar datos indirectos.
- Falta un test especifico para rutas/nombres de archivo con cedula o nombre propio mas realista.

Puntuacion: 7.5/10.

Criterio de no avance:

- No activar Supabase ni IA externa con datos reales hasta tener politica institucional, desidentificacion revisada y pruebas de PHI residual en outputs/DB.

### 3. Extraccion PDF y ETL hospitalario

Evaluador: experto en procesamiento de documentos clinicos, PDF nativo, Poppler, OCR y ETL.

Hallazgos:

- El fallback `pdftotext` es pragmatico y estable dada la instalacion local.
- PyMuPDF quedo parcialmente instalado/no funcional; se removio como dependencia dura del `.spec`, lo cual evita romper el build.
- El runtime con PDF sintetico tipo HORO proceso 252 folios, evidencia relevante para viabilidad.

Riesgos:

- `pdftotext` no queda empaquetado por PyInstaller automaticamente.
- En equipos sin Poppler, el `.exe` podria fallar al extraer PDF.
- Si llegan PDFs escaneados sin texto, se necesitara OCR/Tesseract o flujo alterno.

Puntuacion: 7/10.

Criterio de no avance:

- No distribuir `.exe` a otra maquina sin confirmar que `pdftotext` esta disponible o empaquetado junto con sus DLLs.

### 4. Persistencia local y trazabilidad

Evaluador: experto en bases locales, auditoria de eventos y software clinico offline.

Hallazgos:

- `src/reporting/persistence.py` ahora es capa SQLite formal y anonima.
- Se guardan: analisis, dictamenes, safety gate, evidencia, conteos y revision humana.
- El historial local HTML mejora la auditabilidad para usuaria no tecnica.
- `--no-persist` y `--db-path` permiten control operativo.

Riesgos:

- Aun no hay migraciones versionadas de esquema.
- No hay UI para filtrar historial por fecha/tipo.
- No hay export controlado del historial para comite.

Puntuacion: 8/10.

Criterio de no avance:

- No sincronizar SQLite con nube hasta definir esquema anonimo, versionamiento y politica de retencion.

### 5. UX escritorio

Evaluador: experto en aplicaciones desktop para usuarias clinicas no tecnicas.

Hallazgos:

- La interfaz conserva flujo simple: cargar PDF, cargar laboratorio, elegir IAAS, analizar, abrir reporte, ver historial.
- El boton `Ver historial local` aporta valor practico sin exponer SQL ni CLI.
- Se mantiene `Seguro local` como opcion predeterminada visible.

Riesgos:

- El texto visible aun contiene terminos tecnicos y mojibake en algunos documentos/reportes (`AnÃ¡lisis`, `CategorÃ­a`, etc.).
- Falta prueba manual real de la ventana empaquetada.
- Falta manejar mejor mensajes si `pdftotext` no existe en la maquina destino.

Puntuacion: 6.5/10.

Criterio de no avance:

- No entregar a usuarias finales si el `.exe` no abre reporte e historial con mensajes claros sin terminal.

### 6. Empaquetado Windows

Evaluador: experto en PyInstaller, distribucion Windows y rutas escribibles.

Hallazgos:

- Se corrigio el problema mas frecuente de PyInstaller: escritura junto al ejecutable.
- En modo `.exe`, `outputs` y SQLite van a `%LOCALAPPDATA%\SistemaIAAS`.
- El `.spec` incluye prompts, CSVs, manuales y PDF sintetico.
- `CREAR_EXE.bat` fija `PIP_NO_INDEX=0`, relevante por el entorno local detectado.

Riesgos:

- El build PyInstaller aun no fue ejecutado tras estos ajustes.
- `pdftotext.exe` no esta empaquetado.
- PyMuPDF no debe entrar al build si sigue roto.

Puntuacion: 6.5/10.

Criterio de no avance:

- No declarar paquete entregable hasta ejecutar `python -m PyInstaller SistemaIAAS.spec --clean --noconfirm` y probar el `.exe`.

### 7. DevOps, GitHub y reproducibilidad

Evaluador: experto en GitHub, CI/CD, supply chain y repositorios clinicos.

Hallazgos:

- GitHub CLI quedo autenticado.
- Se corrigio proxy local roto `127.0.0.1:9`.
- Git remoto publico tiene rama `master`.
- Commits del dia estan subidos y trazables.

Riesgos:

- El repo publico contiene PDF sintetico formato HORO. El usuario confirmo que es inventado; aun asi debe marcarse explicitamente como sintetico.
- No hay GitHub Actions para `preflight` y tests.
- No hay proteccion contra subida accidental de datos clinicos reales mas alla de `.gitignore`.

Puntuacion: 7/10.

Criterio de no avance:

- No usar GitHub para datos reales. Agregar CI y escaneo basico antes de trabajo colaborativo amplio.

### 8. Preparacion Supabase/Postgres

Evaluador: experto en Supabase, Postgres, RLS y arquitectura offline-first.

Hallazgos:

- Decision correcta: no instalar ni conectar Supabase todavia.
- SQLite local define una base conceptual para futura sincronizacion.
- La app ya separa datos operativos resumidos de reportes completos.

Riesgos:

- No hay modelo RLS ni esquema Supabase.
- No hay politica de sincronizacion manual vs automatica.
- No hay clasificacion formal de campos permitidos/prohibidos.

Puntuacion: 4/10.

Criterio de no avance:

- Supabase debe permanecer desactivado por defecto y solo aceptar datos sinteticos/anonimizados hasta aprobacion institucional.

## Score global por area

| Area | Score |
|---|---:|
| Runtime local | 8 |
| Privacidad / PHI | 7.5 |
| Seguridad del paciente | 7 |
| Evidencia trazable | 7.5 |
| UX escritorio | 6.5 |
| Validacion automatizada | 7 |
| Empaquetado Windows | 6.5 |
| DevOps / GitHub | 7 |
| Supabase readiness | 4 |
| Preparacion para piloto clinico | 4.5 |

Score global ponderado: 6.5/10.

Interpretacion: base tecnica local razonable para seguir endureciendo; no lista para piloto clinico ni despliegue institucional.

## Hallazgos criticos priorizados

1. El build `.exe` aun no esta probado.
2. `pdftotext` no se empaqueta automaticamente; dependencia externa critica.
3. Supabase no debe activarse aun.
4. Falta bateria sintetica por IAAS y revision clinica formal.
5. Hay riesgo de PHI indirecta en nombres de archivo/rutas si la usuaria usa nombres reales.
6. Falta CI GitHub.
7. Falta prueba visual/manual del historial local en el `.exe`.

## Plan 72 horas

1. Ejecutar build:
   `python -m PyInstaller SistemaIAAS.spec --clean --noconfirm`
2. Probar `dist\SistemaIAAS.exe`:
   - abrir app
   - cargar PDF sintetico
   - cargar CSV sintetico
   - analizar IVU en Seguro local
   - abrir ultimo reporte
   - abrir historial local
3. Confirmar donde quedan archivos:
   - `%LOCALAPPDATA%\SistemaIAAS\outputs`
   - `%LOCALAPPDATA%\SistemaIAAS\data\iaas_vigilancia.db`
4. Agregar prueba de nombres de archivo con PHI y bloqueo/advertencia.
5. Agregar nota visible "PDF sintetico" en docs y repo.

## Plan 2 semanas

1. Crear suite sintetica minima:
   - IVU, NAV, ITS-CVC: positivos, negativos, IPI/POA, incompletos, PHI residual.
2. Agregar GitHub Actions:
   - `python scripts/preflight.py`
   - `python -m unittest discover -s tests`
3. Definir esquema de migracion SQLite -> Supabase sin PHI.
4. Mejorar historial local:
   - filtros por fecha/tipo IAAS
   - export anonimo CSV para comite
5. Empaquetar `pdftotext.exe` o documentar instalacion Poppler para equipos destino.

## Plan 6 semanas

1. Validacion retrospectiva anonima con minimo 30 casos y dictamen humano.
2. Revision formal de criterios por infectologia/epidemiologia.
3. Medir sensibilidad/especificidad sin prometer resultados.
4. Preparar politica institucional para IA externa y Supabase.
5. Crear instalador Windows con ruta de datos de usuario y versionamiento.
6. Definir mecanismo de firma/revision humana final.

## Decision del panel

Recomendacion: avanzar al build `.exe` y prueba manual controlada. No avanzar a Supabase ni piloto clinico todavia.

Condicion para siguiente hito: `.exe` debe ejecutar el flujo completo con PDF/CSV sinteticos, generar reporte, guardar SQLite en ruta de usuario y abrir historial local sin terminal.
