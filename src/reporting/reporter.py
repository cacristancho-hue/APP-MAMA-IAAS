import csv
import json
from datetime import datetime
from pathlib import Path

from privacy.guard import PrivacyGuard


class IAASReporter:
    def __init__(self, output_dir="outputs"):
        self.output_dir = Path(output_dir)
        self.privacy_guard = PrivacyGuard()

    def write_case_report(self, tipo_iaas, notas, resultados, sospechosos=None, source_pdf=None, mode="stub"):
        self.output_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base = self.output_dir / f"iaas_{tipo_iaas.lower()}_{stamp}"

        payload = {
            "tipo_iaas": tipo_iaas,
            "mode": mode,
            "source_pdf": Path(source_pdf).name if source_pdf else None,
            "privacy_status": "PENDIENTE_VALIDACION",
            "folios_procesados": len(notas),
            "sospechosos": sospechosos or [],
            "resultados": resultados,
            "revision_humana_obligatoria": True,
        }
        self.privacy_guard.assert_safe_payload(payload)
        payload["privacy_status"] = "SIN_PHI_DETECTABLE_EN_REPORTE"

        json_path = base.with_suffix(".json")
        json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

        csv_path = base.with_suffix(".csv")
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "tipo_iaas",
                    "cumple",
                    "clasificacion",
                    "nivel_confianza",
                    "requiere_revision_humana",
                    "motivo_descarte",
                    "justificacion",
                ],
            )
            writer.writeheader()
            for item in resultados:
                writer.writerow({key: item.get(key) for key in writer.fieldnames})

        html_path = base.with_suffix(".html")
        html_path.write_text(self._render_html(payload), encoding="utf-8")

        return json_path

    def _render_html(self, payload):
        rows = []
        total_cumplen = sum(1 for item in payload["resultados"] if item.get("cumple"))
        total_no_cumplen = len(payload["resultados"]) - total_cumplen
        
        for item in payload["resultados"]:
            estado = "CONFIRMADA" if item.get("cumple") else "NO CUMPLE"
            css_class = "ok" if item.get("cumple") else "no"
            gate = item.get("safety_gate") or {}
            
            # Visualización de la Matriz de Validación
            matrix_html = ""
            if "matriz_validada" in gate:
                for dim in gate["matriz_validada"]:
                    status = "✔️" if dim.upper() not in gate.get("dimensiones_faltantes", []) else "❌"
                    status_class = "m-ok" if "✔️" in status else "m-err"
                    matrix_html += f"<span class='badge {status_class}'>{status} {dim}</span> "
            
            rows.append(
                "<tr>"
                f"<td><strong>{self._esc(item.get('tipo_iaas'))}</strong></td>"
                f"<td><span class='{css_class}'>{estado}</span></td>"
                f"<td>{matrix_html or 'N/A'}</td>"
                f"<td>{self._esc(item.get('nivel_confianza'))}</td>"
                f"<td>{self._esc(item.get('motivo_descarte'))}</td>"
                f"<td>{self._esc(item.get('justificacion_forense') or item.get('justificacion'))}</td>"
                "</tr>"
            )

        sospechosos = payload.get("sospechosos") or []
        sospechosos_rows = []
        for item in sospechosos:
            sospechosos_rows.append(
                "<tr>"
                f"<td>{self._esc(item.get('paciente_id'))}</td>"
                f"<td>{self._esc(item.get('fecha_muestra'))}</td>"
                f"<td>{self._esc(item.get('dia_estancia_muestra'))}</td>"
                f"<td>{self._esc(item.get('muestra'))}</td>"
                f"<td>{self._esc(item.get('organismo'))}</td>"
                f"<td>{self._esc(item.get('clasificacion_temporal'))}</td>"
                "</tr>"
            )
        
        evidence_sections = []
        for idx, item in enumerate(payload.get("resultados", []), start=1):
            evidence_rows = []
            for evidence in item.get("evidencia") or []:
                evidence_rows.append(
                    "<tr>"
                    f"<td>{self._esc(evidence.get('folio'))}</td>"
                    f"<td>{self._esc(evidence.get('fecha'))}</td>"
                    f"<td>{self._esc(evidence.get('texto'))}</td>"
                    "</tr>"
                )
            if evidence_rows:
                evidence_sections.append(
                    f"<h3>Detalle de Evidencia: {self._esc(item.get('tipo_iaas'))}</h3>"
                    "<table><thead><tr><th>Folio</th><th>Fecha</th><th>Hallazgo / Cita Textual</th></tr></thead>"
                    f"<tbody>{''.join(evidence_rows)}</tbody></table>"
                )

        stub_warning = ""
        if payload.get("mode") == "stub":
            stub_warning = "<div class='notice warning'><strong>MODO SEGURO LOCAL (STUB):</strong> Análisis basado en motor determinístico de reglas. <strong>No utiliza IA externa.</strong> Los resultados exigen cumplimiento estricto de la matriz de validación.</div>"

        return f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>Reporte Avanzado de Vigilancia IAAS</title>
  <style>
    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; color: #102a43; line-height: 1.5; background-color: #f0f4f8; }}
    .container {{ background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
    h1 {{ color: #243b53; border-bottom: 3px solid #334e68; padding-bottom: 10px; }}
    h2 {{ color: #334e68; margin-top: 30px; border-left: 5px solid #627d98; padding-left: 10px; }}
    .meta {{ color: #627d98; font-size: 0.9em; margin-bottom: 20px; }}
    .summary {{ display: flex; gap: 15px; margin-bottom: 30px; flex-wrap: wrap; }}
    .box {{ background: #f0f4f8; border: 1px solid #d9e2ec; border-radius: 6px; padding: 15px; min-width: 160px; text-align: center; }}
    .box strong {{ display: block; font-size: 24px; color: #102a43; }}
    .box span {{ font-size: 0.8em; color: #627d98; text-transform: uppercase; }}
    table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; background: white; }}
    th, td {{ border: 1px solid #d9e2ec; padding: 12px; text-align: left; }}
    th {{ background: #334e68; color: white; }}
    tr:nth-child(even) {{ background: #f9fafb; }}
    .ok {{ color: #147d64; font-weight: bold; background: #e3f8ec; padding: 4px 8px; border-radius: 4px; }}
    .no {{ color: #a61b1b; font-weight: bold; background: #ffe3e3; padding: 4px 8px; border-radius: 4px; }}
    .badge {{ padding: 3px 8px; border-radius: 12px; font-size: 0.75em; font-weight: bold; margin-right: 4px; display: inline-block; }}
    .m-ok {{ background: #e3f8ec; color: #147d64; border: 1px solid #147d64; }}
    .m-err {{ background: #ffe3e3; color: #a61b1b; border: 1px solid #a61b1b; }}
    .notice {{ background: #fff3c4; border: 1px solid #fce588; padding: 15px; border-radius: 6px; margin: 20px 0; }}
    .warning {{ background: #ffe3e3; border-color: #f7a8a8; color: #610404; }}
    .footer {{ font-size: 0.8em; color: #829ab1; text-align: center; margin-top: 40px; border-top: 1px solid #d9e2ec; padding-top: 20px; }}
  </style>
</head>
<body>
  <div class="container">
    <h1>Reporte Avanzado de Vigilancia IAAS</h1>
    <div class="meta">
        <strong>PDF Origen:</strong> {self._esc(payload.get("source_pdf"))} | 
        <strong>Modo:</strong> {self._esc(payload.get("mode").upper())} | 
        <strong>Fecha Proceso:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M")}
    </div>
    
    {stub_warning}

    <div class="summary">
      <div class="box"><span>Folios</span><strong>{payload.get("folios_procesados", 0)}</strong></div>
      <div class="box"><span>Alertas Lab</span><strong>{len(sospechosos)}</strong></div>
      <div class="box"><span>Análisis</span><strong>{len(payload.get("resultados", []))}</strong></div>
      <div class="box"><span>IAAS Confirmadas</span><strong>{total_cumplen}</strong></div>
      <div class="box"><span>Privacidad</span><strong>VÁLIDA</strong></div>
    </div>

    <h2>Resultados de Auditoría (11 IAAS)</h2>
    <table>
      <thead>
        <tr>
          <th>Categoría IAAS</th>
          <th>Estado Final</th>
          <th>Cumplimiento de Matriz</th>
          <th>Confianza</th>
          <th>Motivo Descarte / IPI</th>
          <th>Razonamiento Técnico</th>
        </tr>
      </thead>
      <tbody>
        {''.join(rows)}
      </tbody>
    </table>

    <h2>Cruces de Laboratorio / Microbiología</h2>
    {'<p>No se detectaron hallazgos positivos en los archivos de laboratorio cargados.</p>' if not sospechosos_rows else f"""
    <table>
      <thead>
        <tr>
          <th>Paciente</th>
          <th>Fecha Toma</th>
          <th>Día Estancia</th>
          <th>Muestra</th>
          <th>Germen / Aislamiento</th>
          <th>Clasificación Temporal</th>
        </tr>
      </thead>
      <tbody>{''.join(sospechosos_rows)}</tbody>
    </table>
    """}

    <h2>Evidencia Trazable por Folios</h2>
    {evidence_html}

    <div class="notice">
      <strong>NORMATIVA:</strong> Este reporte aplica los criterios de vigilancia activa **SIVIGILA 2024 / CDC NHSN**. 
      La clasificación "IAAS Posible" indica cumplimiento de la matriz de validación obligatoria (Clínica + Lab + Dispositivo + Tiempo). 
      <strong>Todo resultado requiere validación final por el comité de infecciones.</strong>
    </div>

    <div class="footer">
        Generado automáticamente por el Sistema de Vigilancia IAAS - Fase MVP Robustecida
    </div>
  </div>
</body>
</html>
"""

    def _esc(self, value):
        text = "" if value is None else str(value)
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )
