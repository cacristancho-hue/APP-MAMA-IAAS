# Diseño de Arquitectura Forense - Sistema IAAS

## Visión General
El sistema opera como una canalización (pipeline) de datos clínicos diseñada para transformar texto libre y tablas de laboratorio en dictámenes epidemiológicos estructurados, bajo los estándares de **SIVIGILA 2024**.

## Capas del Motor de Inteligencia (11 IAAS)

### 1. Ingesta y Estructuración (`pdf_extractor`)
- **Segmentación Temporal:** Divide el PDF en folios cronológicos.
- **Extracción de Signos Duros:** Motor Regex para capturar temperaturas, FiO2 y dispositivos de forma determinística.
- **Deidentificación PHI:** Capa de privacidad que anonimiza nombres y documentos antes del análisis.

### 2. Análisis Basal y de Tendencias (`llm_analyzer`)
- **Perfil de Ingreso:** Analiza las primeras 24h para establecer el estado de comorbilidad y los promedios vitales del paciente.
- **Detección de Cambio:** Los eventos posteriores se comparan contra el basal para confirmar que son hallazgos "nuevos" o "agravados".

### 3. Motor de Procesamiento Lingüístico (NLP Local)
- **Mapa Léxico:** Diccionario de sinónimos para 11 categorías de IAAS que traduce jeringa médica (ej. "tiritona" -> "escalofríos").
- **Filtro de Negaciones:** Algoritmo bidireccional que ignora síntomas descartados por el médico (ej. "Sin distensión").
- **Umbrales de Co-ocurrencia:** Verifica que se cumplan múltiples signos simultáneos para alcanzar el umbral de diagnóstico epidemiológico.

### 4. Safety Gate y Validación de Matriz
- **Auditoría de Dimensiones:** Cada IAAS exige una matriz (Clínica + Lab + Dispositivo + Tiempo). Si una dimensión falta en la evidencia, el caso se bloquea.
- **Validación de 48 Horas:** Regla matemática estricta para separar infecciones comunitarias de las asociadas a la atención.

## Flujo de Datos
`UI/CLI` -> `Excel Parser (Sospechosos)` -> `PDF Extractor (Folios)` -> `Basal Profile` -> `Evaluation Engine (11 IAAS)` -> `Safety Gate` -> `Dashboard HTML`.
