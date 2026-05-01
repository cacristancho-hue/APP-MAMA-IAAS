# Uso facil del sistema IAAS

Este sistema debe usarse como una ayuda para organizar casos sospechosos de IAAS. No reemplaza el criterio medico ni la revision de epidemiologia/infectologia.

## La mejor forma de usarlo

Use siempre este orden:

1. Ponga los archivos en la carpeta correcta.
2. Ejecute el modo facil.
3. Revise el reporte generado.

## 1. Donde poner los archivos

### Historia clinica PDF

Ponga el PDF en:

```text
data\raw_pdf
```

Si todavia no tiene otro PDF, puede usar el PDF de ejemplo que ya esta en la carpeta principal.

### Microbiologia

Si tiene archivo de laboratorio en CSV, pongalo en:

```text
data\raw_excel
```

El archivo de ejemplo ya existe:

```text
data\raw_excel\microbiologia_sintetica.csv
```

## 2. Como ejecutarlo sin confundirse

Antes de instalar Python, puede hacer una revision basica con:

```text
VERIFICAR_SIN_PYTHON.bat
```

La forma mas sencilla sera abrir el programa con doble clic:

```text
ABRIR_PROGRAMA.bat
```

Ese archivo abre una pantalla con botones para cargar PDF, cargar laboratorio, escoger fechas y analizar.

Mientras se completa la instalacion final, tambien existe un modo de prueba:

Cuando Python este instalado, haga doble clic en:

```text
INICIAR_MODO_FACIL.bat
```

Ese archivo ejecuta el analisis de ejemplo en modo seguro, sin enviar datos a internet.

## 3. Que revisar al final

El sistema creara una carpeta:

```text
outputs
```

Dentro encontrara:

- Un archivo `.json` con el detalle completo.
- Un archivo `.csv` para revisar en Excel.

Lo importante para usted es revisar estas columnas:

- `cumple`
- `clasificacion`
- `motivo_descarte`
- `requiere_revision_humana`

## Reglas simples

- Si dice `requiere_revision_humana: true`, eso es normal.
- Si dice `No cumple`, mire `motivo_descarte`.
- Si el sistema bloquea el reporte por PHI, no es un error: esta protegiendo datos sensibles.
- No use `IA externa` con datos reales hasta confirmar que la privacidad esta limpia.

## Recomendacion practica

Para usted, la mejor version futura no debe ser por comandos. Debe ser una pantalla con:

1. Boton para cargar PDF.
2. Boton para cargar laboratorio.
3. Fecha inicial y fecha final.
4. Boton "Analizar".
5. Resultado en colores: Confirmado, No cumple, Duda tecnica.
6. Boton para exportar Excel.

Ese debe ser el objetivo de interfaz.
