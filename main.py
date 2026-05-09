import argparse
import json
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent / "src"))

from excel_parser.parser import MicrobiologyExcelParser
from llm_analyzer.analyzer import ClinicalAnalyzerIA
from pdf_extractor.extractor import HistoriClinicaExtractor
from reporting.persistence import IAASPersistenceManager
from reporting.reporter import IAASReporter
from contracts import parse_fecha
from path_utils import writable_path


DEFAULT_PDF = "HISTORIA CLINICA TIPO HOSPITAL REGIONAL DE LA ORINOQUIA EJEMPLO.pdf"


def ejecutar_vigilancia_iaas(
    ruta_pdf,
    tipo_iaas="IVU",
    mode="stub",
    excel_path=None,
    output_dir=None,
    persistence_db_path=None,
    persist=True,
    fecha_inicio=None,
    fecha_fin=None,
):
    validar_rango_fechas(fecha_inicio, fecha_fin)
    output_dir = output_dir or str(writable_path("outputs"))
    persistence_db_path = persistence_db_path or str(writable_path("data/iaas_vigilancia.db"))

    print(f"\n{'=' * 72}")
    print(f" SISTEMA DE VIGILANCIA IAAS - TIPO: {tipo_iaas} - MODO: {mode}")
    print(f"{'=' * 72}\n")

    sospechosos = []
    if excel_path:
        print("[PASO 1] Procesando microbiologia en Excel...")
        sospechosos = MicrobiologyExcelParser().parse(excel_path)
        sospechosos = filtrar_sospechosos_por_fecha(sospechosos, fecha_inicio, fecha_fin)
        print(f"  -> {len(sospechosos)} pacientes sospechosos identificados.")
    else:
        print("[PASO 1] Sin Excel: se analizara el PDF indicado como caso individual.")

    print("[PASO 2] Extrayendo y deidentificando historia clinica PDF...")
    extractor = HistoriClinicaExtractor()
    notas_estructuradas = extractor.extraer_texto_real(ruta_pdf)
    if isinstance(notas_estructuradas, str):
        raise RuntimeError(notas_estructuradas)
    if not notas_estructuradas:
        raise RuntimeError("No se encontraron folios clinicos procesables en el PDF.")
    notas_estructuradas = filtrar_notas_por_fecha(notas_estructuradas, fecha_inicio, fecha_fin)
    if not notas_estructuradas:
        raise RuntimeError("No quedaron folios clinicos dentro del rango de fechas seleccionado.")
    print(f"  -> {len(notas_estructuradas)} folios identificados.")

    print("[PASO 3] Analizando criterios IAAS...")
    analizador = ClinicalAnalyzerIA(mode=mode)
    tipos = sorted(analizador.prompts_disponibles) if tipo_iaas.upper() == "TODAS" else [tipo_iaas]
    resultados = []
    for tipo in tipos:
        resultados.extend(analizador.analizar_historia_completa(notas_estructuradas, tipo, sospechosos=sospechosos))
    print(f"  -> {len(resultados)} dictamen(es) generados.")

    print("[PASO 4] Generando reporte auditable...")
    output_path = IAASReporter(
        output_dir=output_dir,
        persistence_db_path=persistence_db_path,
        persist=persist,
    ).write_case_report(
        tipo_iaas=tipo_iaas,
        notas=notas_estructuradas,
        resultados=resultados,
        sospechosos=sospechosos,
        source_pdf=ruta_pdf,
        mode=mode,
    )
    print(f"  -> Reporte: {output_path}")
    historial_db = str(IAASPersistenceManager(persistence_db_path).db_path) if persist else None
    if historial_db:
        print(f"  -> Historial local: {historial_db}")

    return {
        "tipo_iaas": tipo_iaas,
        "mode": mode,
        "folios": len(notas_estructuradas),
        "sospechosos": len(sospechosos),
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "resultados": resultados,
        "reporte": str(output_path),
        "historial_db": historial_db,
    }


def filtrar_notas_por_fecha(notas, fecha_inicio=None, fecha_fin=None):
    inicio = parse_fecha(fecha_inicio)
    fin = parse_fecha(fecha_fin)
    if not inicio and not fin:
        return notas

    filtradas = []
    for nota in notas:
        fecha = parse_fecha(nota.get("fecha"))
        if not fecha:
            continue
        if inicio and fecha < inicio:
            continue
        if fin and fecha.date() > fin.date():
            continue
        filtradas.append(nota)
    return filtradas


def filtrar_sospechosos_por_fecha(sospechosos, fecha_inicio=None, fecha_fin=None):
    inicio = parse_fecha(fecha_inicio)
    fin = parse_fecha(fecha_fin)
    if not inicio and not fin:
        return sospechosos

    filtrados = []
    for item in sospechosos:
        fecha = parse_fecha(item.get("fecha_muestra"))
        if not fecha:
            continue
        if inicio and fecha < inicio:
            continue
        if fin and fecha.date() > fin.date():
            continue
        filtrados.append(item)
    return filtrados


def validar_rango_fechas(fecha_inicio=None, fecha_fin=None):
    inicio = parse_fecha(fecha_inicio)
    fin = parse_fecha(fecha_fin)
    if fecha_inicio and not inicio:
        raise ValueError("La fecha inicial no es valida. Use DD/MM/AAAA o AAAA-MM-DD.")
    if fecha_fin and not fin:
        raise ValueError("La fecha final no es valida. Use DD/MM/AAAA o AAAA-MM-DD.")
    if inicio and fin and inicio.date() > fin.date():
        raise ValueError("La fecha inicial no puede ser posterior a la fecha final.")


def build_parser():
    parser = argparse.ArgumentParser(description="Sistema de Vigilancia IAAS - Auditoría Forense 11 Categorías")
    parser.add_argument("--pdf", default=DEFAULT_PDF, help="Ruta del PDF de historia clinica.")
    parser.add_argument("--excel", default=None, help="Ruta opcional del Excel de microbiologia.")
    parser.add_argument("--tipo-iaas", default="IVU", help="Tipo IAAS (IVU, NAV, ITS-CVC, ISQ, etc. o 'TODAS')")
    parser.add_argument("--fecha-inicio", default=None, help="Fecha inicial del analisis: DD/MM/AAAA o AAAA-MM-DD.")
    parser.add_argument("--fecha-fin", default=None, help="Fecha final del analisis: DD/MM/AAAA o AAAA-MM-DD.")
    parser.add_argument(
        "--mode",
        default=os.environ.get("IAAS_LLM_MODE", "stub"),
        choices=["stub", "llm"],
        help="stub genera salida deterministica; llm usa proveedor configurado por entorno.",
    )
    parser.add_argument("--output-dir", default=None, help="Directorio de reportes.")
    parser.add_argument("--db-path", default=None, help="Base local SQLite anonima.")
    parser.add_argument("--no-persist", action="store_true", help="No guardar historial local SQLite.")
    return parser


if __name__ == "__main__":
    args = build_parser().parse_args()
    result = ejecutar_vigilancia_iaas(
        ruta_pdf=args.pdf,
        tipo_iaas=args.tipo_iaas,
        mode=args.mode,
        excel_path=args.excel,
        output_dir=args.output_dir,
        persistence_db_path=args.db_path,
        persist=not args.no_persist,
        fecha_inicio=args.fecha_inicio,
        fecha_fin=args.fecha_fin,
    )
    
    print("\n" + "="*72)
    print(" ANALISIS FINALIZADO CON EXITO")
    print(f" Reporte JSON: {result['reporte']}")
    print(f" DASHBOARD HTML: {Path(result['reporte']).with_suffix('.html')}")
    print("="*72)
