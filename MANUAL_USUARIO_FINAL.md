# Manual de Usuario - Sistema de Vigilancia IAAS (SIVIGILA 2024)

## Propósito del Sistema
Esta herramienta automatiza la revisión de posibles Infecciones Asociadas a la Atención en Salud (IAAS) aplicando criterios epidemiológicos de **SIVIGILA (Colombia)** y **CDC/NHSN**. El sistema permite una vigilancia activa sobre 11 categorías de infección, reduciendo el tiempo de auditoría manual.

**ADVERTENCIA:** El sistema es una herramienta de apoyo. **Todo resultado debe ser validado por el Comité de Infecciones o el especialista responsable.**

---

## 1. Inicio del Programa
Asegúrese de tener instaladas las dependencias. Para iniciar la aplicación de escritorio, haga doble clic en:
`ABRIR_PROGRAMA.bat`

---

## 2. Configuración del Análisis

### A. Carga de Archivos
- **Historia Clínica PDF:** Cargue el archivo extraído del sistema hospitalario. El sistema procesará folios, fechas y notas de evolución.
- **Microbiología Excel/CSV:** Cargue el reporte de laboratorio. El sistema buscará automáticamente cultivos positivos y los cruzará con la historia clínica.

### B. Rango de Fechas
Defina la ventana de tiempo que desea auditar. El sistema filtrará automáticamente los folios y laboratorios dentro de este rango.

### C. Categorías de IAAS (11 Disponibles)
Puede analizar una categoría específica o seleccionar **"TODAS"** para un barrido completo:
- `IVU` (Urinaria), `NAV` (Pulmonar), `ITS-CVC` (Torrente Sanguíneo).
- `ISQ` (Quirúrgica), `Endometritis`, `ECN` (Neonatal Abdominal).
- `Sepsis Tardía`, `Meningitis`, `Clostridioides`, `Piel/Blandos`, `Neonatal Local`.

### D. Modo de Análisis
- **Seguro Local (Recomendado):** Utiliza un motor de reglas determinístico avanzado. No envía datos a la nube. Es el modo de mayor privacidad.
- **IA Externa:** Utiliza modelos de lenguaje para un análisis narrativo más profundo (Requiere configuración de API).

---

## 3. Interpretación del Reporte (Dashboard HTML)
Al finalizar, presione **"Abrir último reporte"**. Se abrirá un Dashboard en su navegador con los siguientes paneles:

### Matriz de Cumplimiento Multidimensional
Verá iconos de estado (✔️/❌) por cada dimensión obligatoria del criterio:
- **Clínica:** ¿Hay signos como fiebre o purulencia?
- **Laboratorio:** ¿El cultivo es compatible?
- **Dispositivo:** ¿Tenía sonda, catéter o ventilador?
- **Tiempo:** ¿El evento ocurrió después del Día 3 (>48h)?

### Análisis de Tendencias Basales
El sistema compara matemáticamente el estado de ingreso con los síntomas actuales. Si el paciente ya era febril al ingreso, el sistema solo marcará IAAS si hay un **deterioro significativo** (ej. aumento de +0.5°C sobre el basal).

### Evidencia Trazable
Al final del reporte, encontrará las citas textuales y los números de folio donde el sistema detectó la evidencia. Use esto para la auditoría rápida.

---

## 4. Clasificación de Resultados
- **IAAS Posible:** Cumple con todas las dimensiones de la matriz y las reglas temporales.
- **IPI / POA:** Infección presente al ingreso. El síntoma ocurrió en las primeras 48 horas.
- **No cumple:** Falta evidencia en una o más dimensiones obligatorias.
