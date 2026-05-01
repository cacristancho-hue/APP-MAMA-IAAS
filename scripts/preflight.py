import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

from contracts import normalize_dictamen
from criteria.registry import CRITERIA_REGISTRY
from excel_parser.parser import MicrobiologyExcelParser
from llm_analyzer.analyzer import ClinicalAnalyzerIA
from pdf_extractor.extractor import HistoriClinicaExtractor
from privacy.guard import PrivacyGuard
from reporting.reporter import IAASReporter
from validation.clinical_safety import ClinicalSafetyValidator


def main():
    checks = []

    required = [
        ROOT / "app_escritorio.py",
        ROOT / "main.py",
        ROOT / "data" / "raw_excel" / "microbiologia_sintetica.csv",
        ROOT / "src" / "llm_analyzer" / "prompts_clinicos" / "ivu_prompt.md",
    ]
    for path in required:
        checks.append((path.exists(), f"existe {path.relative_to(ROOT)}"))

    analyzer = ClinicalAnalyzerIA(mode="stub")
    checks.append((set(CRITERIA_REGISTRY) == set(analyzer.prompts_disponibles), "criterios y prompts (11 IAAS) alineados"))

    extractor = HistoriClinicaExtractor()
    signos = extractor.extraer_signos_duros("Temp: 38.5 F.C: 120 F.R: 40 SpO2: 98")
    checks.append((signos["saturaciones"] == [98], "extraccion de saturacion (Regex robusta)"))

    sospechosos = MicrobiologyExcelParser().parse(ROOT / "data" / "raw_excel" / "microbiologia_sintetica.csv")
    checks.append((len(sospechosos) >= 2, "parser CSV laboratorio (Mapeo flexible)"))

    # V3 - Pruebas del Motor de Inteligencia Determinística
    # 1. Motor de Negación Bidireccional
    checks.append((analyzer._es_hallazgo_negado("Paciente estable, sin fiebre ni tos.", "fiebre"), "NLP: Detecta negación prefijo (Sin)"))
    checks.append((analyzer._es_hallazgo_negado("Examen físico: Fiebre: No. Dolor ausente.", "fiebre"), "NLP: Detecta negación sufijo (Lista)"))
    checks.append((not analyzer._es_hallazgo_negado("Fiebre de 39C con escalofríos.", "fiebre"), "NLP: Permite hallazgos positivos (No Falsos Negativos)"))
    
    # 2. Motor de Temporalidad y Tendencias (Día >= 3 y +0.5C)
    # Ingreso: Día 1. Evento: Día 3.
    hoy = datetime.now()
    ingreso = hoy - timedelta(days=3)
    checks.append((analyzer._es_dia_3_o_mayor(hoy.strftime("%Y-%m-%d"), ingreso), "Matemática: Confirma Día 3 (>=48h)"))
    checks.append((not analyzer._es_dia_3_o_mayor((hoy - timedelta(days=1)).strftime("%Y-%m-%d"), ingreso), "Matemática: Bloquea Día 1-2 (IPI/POA)"))
    
    checks.append((analyzer._detectar_deterioro_significativo(38.5, 37.0, "fiebre"), "Tendencia: Detecta fiebre nueva vs basal normal"))
    checks.append((not analyzer._detectar_deterioro_significativo(38.2, 38.0, "fiebre"), "Tendencia: Filtra fluctuación febril menor a +0.5C"))
    checks.append((analyzer._detectar_deterioro_significativo(50, 21, "oxigenacion"), "Tendencia: Detecta deterioro de FiO2 > 20%"))

    # V3 - Safety Gate Multidimensional
    dictamen_vacio = normalize_dictamen("IVU", {"cumple": True, "dictamen_final": "CAUTI", "evidencia": []}, mode="stub")
    dictamen_vacio = ClinicalSafetyValidator().validate(dictamen_vacio)
    checks.append((not dictamen_vacio["cumple"], "Safety Gate: bloquea confirmacion sin evidencia"))

    # Falla dimensión por no cubrir todas las matrices (Ej. IVU necesita Clínica, Lab, Dispositivo)
    dictamen_parcial = normalize_dictamen("IVU", {
        "cumple": True, 
        "dictamen_final": "CAUTI", 
        "evidencia": [{"texto": "Pico febril confirmado"}, {"texto": "Urocultivo positivo E. coli"}]
    }, mode="stub")
    dictamen_parcial = ClinicalSafetyValidator().validate(dictamen_parcial)
    # Debería revocar porque falta la dimensión de dispositivo (sonda)
    checks.append((not dictamen_parcial["cumple"] and "DISPOSITIVO" in dictamen_parcial["motivo_descarte"], "Safety Gate: audita Matriz Multidimensional y exige todas las dimensiones"))

    # V3 - Motor Zero-PHI
    try:
        # Prueba con nueva Regex Colombiana (CC con puntos y EPS)
        PrivacyGuard().assert_safe_payload({"contenido": "Paciente: JUAN PEREZ, CC: 1.018.123.456, EPS: SURA"})
        checks.append((False, "PrivacyGuard: bloquea PHI colombiano complejo"))
    except RuntimeError:
        checks.append((True, "PrivacyGuard: bloquea PHI colombiano complejo"))
        
    texto_redactado = PrivacyGuard().redact_text("Paciente: ANA GOMEZ, CC 1234567. Historia Clínica 001-A.")
    checks.append(("[PACIENTE_NOMBRE_ANONIMIZADO]" in texto_redactado and "[DOCUMENTO_ANONIMIZADO]" in texto_redactado, "PrivacyGuard: redacción proactiva Zero-PHI"))

    report = IAASReporter(output_dir=ROOT / "outputs_preflight").write_case_report(
        tipo_iaas="IVU",
        notas=[],
        resultados=[
            {
                "tipo_iaas": "IVU",
                "cumple": False,
                "clasificacion": "No cumple",
                "motivo_descarte": "Preflight",
                "justificacion": "",
                "nivel_confianza": "bajo",
                "requiere_revision_humana": True,
                "evidencia": [],
                "mode": "stub",
            }
        ],
        sospechosos=sospechosos,
        source_pdf="preflight.pdf",
        mode="stub",
    )
    checks.append((report.exists() and report.with_suffix(".html").exists(), "Reportes: generación de Dashboard V3 JSON/HTML"))

    failed = [message for ok, message in checks if not ok]
    print(json.dumps({"checks": checks, "failed": failed}, ensure_ascii=False, indent=2))
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
