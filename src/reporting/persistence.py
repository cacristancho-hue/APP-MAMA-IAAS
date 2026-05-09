import json
import sqlite3
from datetime import datetime
from pathlib import Path

from privacy.guard import PrivacyGuard


class IAASPersistenceManager:
    def __init__(self, db_path="data/iaas_vigilancia.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.privacy_guard = PrivacyGuard()
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS analisis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha_proceso TEXT NOT NULL,
                    tipo_iaas TEXT NOT NULL,
                    mode TEXT NOT NULL,
                    source_pdf TEXT,
                    privacy_status TEXT NOT NULL,
                    folios_procesados INTEGER NOT NULL,
                    sospechosos_count INTEGER NOT NULL,
                    resultados_count INTEGER NOT NULL,
                    revision_humana_obligatoria INTEGER NOT NULL,
                    report_json_path TEXT,
                    report_html_path TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS dictamenes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analisis_id INTEGER NOT NULL,
                    fecha_proceso TEXT NOT NULL,
                    tipo_iaas TEXT NOT NULL,
                    cumple INTEGER NOT NULL,
                    clasificacion TEXT,
                    nivel_confianza TEXT,
                    motivo_descarte TEXT,
                    justificacion TEXT,
                    requiere_revision_humana INTEGER NOT NULL,
                    safety_gate_json TEXT,
                    evidencia_json TEXT,
                    raw_json TEXT,
                    FOREIGN KEY (analisis_id) REFERENCES analisis(id)
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_analisis_fecha ON analisis(fecha_proceso)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_dictamenes_tipo ON dictamenes(tipo_iaas)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_dictamenes_analisis ON dictamenes(analisis_id)")

    def save_analysis(self, payload, report_json_path=None, report_html_path=None):
        """Persiste solo datos anonimizados y trazabilidad operativa local."""
        safe_payload = self._build_safe_payload(payload, report_json_path, report_html_path)
        self.privacy_guard.assert_safe_payload(safe_payload)
        fecha_proceso = datetime.now().isoformat()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                INSERT INTO analisis (
                    fecha_proceso, tipo_iaas, mode, source_pdf, privacy_status,
                    folios_procesados, sospechosos_count, resultados_count,
                    revision_humana_obligatoria, report_json_path, report_html_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    fecha_proceso,
                    safe_payload["tipo_iaas"],
                    safe_payload["mode"],
                    safe_payload["source_pdf"],
                    safe_payload["privacy_status"],
                    safe_payload["folios_procesados"],
                    safe_payload["sospechosos_count"],
                    safe_payload["resultados_count"],
                    1 if safe_payload["revision_humana_obligatoria"] else 0,
                    safe_payload["report_json_path"],
                    safe_payload["report_html_path"],
                ),
            )
            analisis_id = cursor.lastrowid
            for item in safe_payload["resultados"]:
                conn.execute(
                    """
                    INSERT INTO dictamenes (
                        analisis_id, fecha_proceso, tipo_iaas, cumple,
                        clasificacion, nivel_confianza, motivo_descarte, justificacion,
                        requiere_revision_humana, safety_gate_json, evidencia_json, raw_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        analisis_id,
                        fecha_proceso,
                        item.get("tipo_iaas"),
                        1 if item.get("cumple") else 0,
                        item.get("clasificacion"),
                        item.get("nivel_confianza"),
                        item.get("motivo_descarte"),
                        item.get("justificacion"),
                        1 if item.get("requiere_revision_humana") else 0,
                        json.dumps(item.get("safety_gate"), ensure_ascii=False),
                        json.dumps(item.get("evidencia"), ensure_ascii=False),
                        json.dumps(item, ensure_ascii=False),
                    ),
                )
            conn.commit()
        return analisis_id

    def get_recent_analyses(self, limit=50):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT
                    a.*,
                    SUM(CASE WHEN d.cumple = 1 THEN 1 ELSE 0 END) AS positivos
                FROM analisis a
                LEFT JOIN dictamenes d ON d.analisis_id = a.id
                GROUP BY a.id
                ORDER BY a.fecha_proceso DESC
                LIMIT ?
                """,
                (int(limit),),
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_dictamenes_for_analysis(self, analisis_id):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM dictamenes WHERE analisis_id = ? ORDER BY id ASC",
                (int(analisis_id),),
            )
            return [dict(row) for row in cursor.fetchall()]

    def write_history_html(self, output_path=None, limit=100):
        output_path = Path(output_path or self.db_path.with_suffix(".historial.html"))
        rows = []
        for item in self.get_recent_analyses(limit=limit):
            rows.append(
                "<tr>"
                f"<td>{self._esc(item.get('fecha_proceso'))}</td>"
                f"<td>{self._esc(item.get('tipo_iaas'))}</td>"
                f"<td>{self._esc(item.get('mode'))}</td>"
                f"<td>{self._esc(item.get('folios_procesados'))}</td>"
                f"<td>{self._esc(item.get('resultados_count'))}</td>"
                f"<td>{self._esc(item.get('positivos') or 0)}</td>"
                f"<td>{self._esc(item.get('privacy_status'))}</td>"
                f"<td>{self._esc(item.get('report_html_path'))}</td>"
                "</tr>"
            )

        html = f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>Historial local IAAS</title>
  <style>
    body {{ font-family: Segoe UI, Arial, sans-serif; margin: 32px; color: #1f2933; }}
    h1 {{ font-size: 24px; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #d9e2ec; padding: 9px; text-align: left; font-size: 13px; }}
    th {{ background: #334e68; color: white; }}
    tr:nth-child(even) {{ background: #f7f9fb; }}
    .notice {{ background: #fffbea; border: 1px solid #f0d46b; padding: 12px; margin: 16px 0; }}
  </style>
</head>
<body>
  <h1>Historial local IAAS</h1>
  <div class="notice">Base local anonima. No contiene PDF completo, nombres, documentos ni rutas clinicas completas. Todo resultado requiere revision humana.</div>
  <table>
    <thead>
      <tr>
        <th>Fecha</th><th>Tipo</th><th>Modo</th><th>Folios</th><th>Dictamenes</th><th>Posibles</th><th>Privacidad</th><th>Reporte HTML</th>
      </tr>
    </thead>
    <tbody>{''.join(rows) if rows else '<tr><td colspan="8">Sin analisis guardados.</td></tr>'}</tbody>
  </table>
</body>
</html>
"""
        output_path.write_text(html, encoding="utf-8")
        return output_path

    def _build_safe_payload(self, payload, report_json_path, report_html_path):
        resultados = []
        for item in payload.get("resultados", []):
            resultados.append({
                "tipo_iaas": item.get("tipo_iaas"),
                "cumple": bool(item.get("cumple")),
                "clasificacion": item.get("clasificacion"),
                "nivel_confianza": item.get("nivel_confianza"),
                "motivo_descarte": item.get("motivo_descarte"),
                "justificacion": item.get("justificacion") or item.get("justificacion_forense"),
                "requiere_revision_humana": bool(item.get("requiere_revision_humana", True)),
                "safety_gate": item.get("safety_gate") or {},
                "evidencia": item.get("evidencia") or [],
            })

        return {
            "tipo_iaas": payload.get("tipo_iaas"),
            "mode": payload.get("mode"),
            "source_pdf": Path(payload.get("source_pdf")).name if payload.get("source_pdf") else None,
            "privacy_status": payload.get("privacy_status"),
            "folios_procesados": int(payload.get("folios_procesados") or 0),
            "sospechosos_count": len(payload.get("sospechosos") or []),
            "resultados_count": len(resultados),
            "revision_humana_obligatoria": bool(payload.get("revision_humana_obligatoria", True)),
            "report_json_path": str(report_json_path) if report_json_path else None,
            "report_html_path": str(report_html_path) if report_html_path else None,
            "resultados": resultados,
        }

    def _esc(self, value):
        text = "" if value is None else str(value)
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )
