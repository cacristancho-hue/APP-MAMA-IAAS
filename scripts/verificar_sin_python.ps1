$ErrorActionPreference = "Stop"

Write-Host "Verificacion estatica del proyecto IAAS" -ForegroundColor Cyan
Write-Host ""

$required = @(
  "app_escritorio.py",
  "main.py",
  "src\llm_analyzer\analyzer.py",
  "src\pdf_extractor\extractor.py",
  "src\excel_parser\parser.py",
  "src\reporting\reporter.py",
  "src\privacy\guard.py",
  "src\criteria\registry.py",
  "data\raw_excel\PLANTILLA_LABORATORIO.csv",
  "data\raw_excel\microbiologia_sintetica.csv",
  "MANUAL_USUARIO_FINAL.md",
  "DICCIONARIO_LABORATORIO.md",
  "SistemaIAAS.spec",
  "requirements.txt",
  "AGENTS.md",
  "TRASPASO_PROGRESIVO_IAS.md",
  "REGISTRO_PROGRESO_IAS.md",
  "PROMPT_CONTINUACION_IAS.md"
)

$missing = @()
foreach ($path in $required) {
  if (-not (Test-Path $path)) {
    $missing += $path
  }
}

if ($missing.Count -gt 0) {
  Write-Host "Faltan archivos requeridos:" -ForegroundColor Red
  $missing | ForEach-Object { Write-Host " - $_" -ForegroundColor Red }
  exit 1
}

Write-Host "Archivos requeridos: OK" -ForegroundColor Green

$patterns = @(
  "preparar_contexto_llm",
  "simular_respuesta_ia",
  "datos_crudos_simulados",
  "Usando datos de simulación",
  "nivel Especialidad Médica",
  "Completado - Nivel Experto"
)

$foundBad = $false
foreach ($pattern in $patterns) {
  $hits = Select-String -Path ".\*.py",".\src\**\*.py",".\*.md" -Pattern $pattern -ErrorAction SilentlyContinue
  if ($hits) {
    $foundBad = $true
    Write-Host "Patron no deseado encontrado: $pattern" -ForegroundColor Yellow
    $hits | ForEach-Object { Write-Host " - $($_.Path):$($_.LineNumber)" -ForegroundColor Yellow }
  }
}

if ($foundBad) {
  exit 1
}

Write-Host "Patrones obsoletos: OK" -ForegroundColor Green

$python = Get-Command python -ErrorAction SilentlyContinue
if ($python -and $python.Source -notlike "*WindowsApps*") {
  Write-Host "Python real detectado: $($python.Source)" -ForegroundColor Green
} else {
  Write-Host "Python real aun no detectado. Esto es esperado si todavia no se ha instalado." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Verificacion estatica completada." -ForegroundColor Cyan
