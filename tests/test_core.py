import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

from llm_analyzer.analyzer import ClinicalAnalyzerIA
from contracts import normalize_dictamen
from excel_parser.parser import MicrobiologyExcelParser
from pdf_extractor.extractor import HistoriClinicaExtractor
from privacy.guard import PrivacyGuard
from reporting.persistence import IAASPersistenceManager
from reporting.reporter import IAASReporter
from validation.clinical_safety import ClinicalSafetyValidator


class ExtractorTests(unittest.TestCase):
    def test_extrae_signos_duros_incluida_saturacion(self):
        extractor = HistoriClinicaExtractor()
        signos = extractor.extraer_signos_duros("Temp: 38.5 F.C: 120 F.R: 40 SpO2: 98")
        self.assertEqual(signos["temperaturas"], [38.5])
        self.assertEqual(signos["frecuencias_cardiacas"], [120])
        self.assertEqual(signos["frecuencias_respiratorias"], [40])
        self.assertEqual(signos["saturaciones"], [98])

    def test_deidentifica_phi_basico(self):
        extractor = HistoriClinicaExtractor()
        texto = "Paciente: JUAN PEREZ\nNo Documento: 123456\nTelefono: 3001234567\nDireccion: Calle 1"
        seguro = extractor.deidentificar_texto(texto)
        self.assertNotIn("JUAN PEREZ", seguro)
        self.assertNotIn("123456", seguro)
        self.assertNotIn("3001234567", seguro)
        self.assertNotIn("Calle 1", seguro)

    def test_procesar_historia_formatos_flexibles(self):
        extractor = HistoriClinicaExtractor()
        texto_crudo = (
            "FOLIO: 1\nFecha: 2026-04-11 16:11\nNOTAS DE ENFERMERIA\nPaciente estable.\n"
            "Folio No. 2\nFecha: 12/04/2026\nRESULTADO DE LABORATORIO\nUrocultivo positivo."
        )
        notas = extractor.procesar_historia(texto_crudo)
        self.assertEqual(len(notas), 2)
        
        self.assertEqual(notas[0]["folio"], "FOLIO: 1")
        self.assertEqual(notas[0]["fecha"], "2026-04-11 16:11")
        self.assertEqual(notas[0]["tipo"], "NOTA DE ENFERMERIA")
        
        self.assertEqual(notas[1]["folio"], "Folio No. 2")
        self.assertEqual(notas[1]["fecha"], "12/04/2026 00:00")
        self.assertEqual(notas[1]["tipo"], "RESULTADO LABORATORIO")


class AnalyzerTests(unittest.TestCase):
    def test_stub_ivu_confirma_solo_con_fiebre_y_sonda(self):
        analyzer = ClinicalAnalyzerIA(mode="stub")
        notas = [
            {
                "folio": "FOLIO N 0",
                "fecha": "09/04/2026 16:11",
                "tipo": "EVOLUCION MEDICA",
                "contenido": "Paciente con sonda vesical. T: 37.0C.",
                "datos_duros_verificados": {
                    "temperaturas": [37.0],
                    "frecuencias_cardiacas": [],
                    "frecuencias_respiratorias": [],
                    "saturaciones": [],
                },
            },
            {
                "folio": "FOLIO N 1",
                "fecha": "11/04/2026 16:11",
                "tipo": "EVOLUCION MEDICA",
                "contenido": "Paciente con sonda vesical. T: 38.2C. Resultado de urocultivo positivo para E. coli.",
                "datos_duros_verificados": {
                    "temperaturas": [38.2],
                    "frecuencias_cardiacas": [],
                    "frecuencias_respiratorias": [],
                    "saturaciones": [],
                },
            }
        ]
        resultado = analyzer.analizar_historia_completa(notas, "IVU")[0]
        self.assertTrue(resultado["cumple"])
        self.assertTrue(resultado["requiere_revision_humana"])

    def test_normaliza_evidencia_directa(self):
        dictamen = normalize_dictamen(
            "IVU",
            {
                "dictamen_final": "CAUTI posible",
                "cumple": True,
                "evidencia": [{"folio": "FOLIO N 1", "texto": "T: 38.2"}],
            },
        )
        self.assertEqual(len(dictamen["evidencia"]), 1)


class ExcelParserTests(unittest.TestCase):
    def test_csv_sintetico_no_requiere_pandas(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "micro.csv"
            path.write_text(
                "paciente,fecha_ingreso,fecha_toma,muestra,organismo,resultado,servicio\n"
                "123456,2026-04-01,2026-04-04,Urocultivo,E coli,positivo,UCI\n"
                "789000,2026-04-01,2026-04-02,Hemocultivo,S epidermidis,positivo,UCI\n"
                "555555,2026-04-01,2026-04-05,Urocultivo,,negativo,UCI\n",
                encoding="utf-8",
            )
            sospechosos = MicrobiologyExcelParser().parse(path)
        self.assertEqual(len(sospechosos), 2)
        self.assertEqual(sospechosos[0]["clasificacion_temporal"], "SOSPECHA_IAAS")
        self.assertEqual(sospechosos[1]["clasificacion_temporal"], "IPI_POA")

    def test_csv_nuevos_alias_columnas(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "micro2.csv"
            path.write_text(
                "nro_doc,fecha_admision,recepcion,material,bacteria,interpretacion,pabellon\n"
                "88888,2026-04-01,2026-04-05,Sangre,Aureus,crecimiento,Piso 3\n",
                encoding="utf-8",
            )
            sospechosos = MicrobiologyExcelParser().parse(path)
        self.assertEqual(len(sospechosos), 1)
        self.assertEqual(sospechosos[0]["organismo"], "Aureus")
        self.assertEqual(sospechosos[0]["servicio"], "Piso 3")


class PrivacyTests(unittest.TestCase):
    def test_privacy_guard_bloquea_phi_residual(self):
        payload = {"contenido": "Paciente: JUAN PEREZ No Documento: 123456"}
        with self.assertRaises(RuntimeError):
            PrivacyGuard().assert_safe_payload(payload)

    def test_privacy_guard_bloquea_nuevos_patrones(self):
        # Prueba con PEP y telefono con formato
        payload1 = {"contenido": "PEP: 1234567890"}
        with self.assertRaises(RuntimeError):
            PrivacyGuard().assert_safe_payload(payload1)
        
        payload2 = {"contenido": "Contacto: 300-123-4567"}
        with self.assertRaises(RuntimeError):
            PrivacyGuard().assert_safe_payload(payload2)
        
        payload3 = {"contenido": "Nombre: MARIA GOMEZ"}
        with self.assertRaises(RuntimeError):
            PrivacyGuard().assert_safe_payload(payload3)


class ClinicalSafetyTests(unittest.TestCase):
    def test_bloquea_cumple_sin_evidencia(self):
        dictamen = {
            "tipo_iaas": "IVU",
            "cumple": True,
            "clasificacion": "CAUTI",
            "motivo_descarte": "",
            "justificacion": "Sin evidencia",
            "evidencia": [],
            "nivel_confianza": "alto",
            "mode": "stub",
        }
        validado = ClinicalSafetyValidator().validate(dictamen)
        self.assertFalse(validado["cumple"])
        self.assertIn("safety_gate", validado)
        self.assertIn("confirmacion_bloqueada_sin_evidencia", validado["safety_gate"]["warnings"])

    def test_bloquea_cumple_si_falta_evidencia_especifica(self):
        # IVU requiere: "clinica" (fiebre), "laboratorio" (urocultivo), "dispositivo" (sonda)
        dictamen = {
            "tipo_iaas": "IVU",
            "cumple": True,
            "clasificacion": "CAUTI",
            "motivo_descarte": "",
            "justificacion": "Tiene fiebre y urocultivo, pero no menciona sonda",
            "evidencia": [
                {"folio": "F1", "texto": "Fiebre 39C"},
                {"folio": "F2", "texto": "Urocultivo positivo E. coli"}
            ],
            "nivel_confianza": "alto",
            "mode": "stub",
        }
        validado = ClinicalSafetyValidator().validate(dictamen)
        self.assertFalse(validado["cumple"])
        self.assertEqual(validado["clasificacion"], "Duda técnica - falla validación semántica")
        self.assertIn("DISPOSITIVO", validado["motivo_descarte"])
        self.assertIn("dimensiones_matriz_faltantes_semantica", validado["safety_gate"]["warnings"])


class ReporterTests(unittest.TestCase):
    def test_reporte_json_y_csv(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
            path = IAASReporter(output_dir=tmp).write_case_report(
                tipo_iaas="IVU",
                notas=[],
                resultados=[
                    {
                        "tipo_iaas": "IVU",
                        "cumple": False,
                        "clasificacion": "No cumple",
                        "nivel_confianza": "bajo",
                        "requiere_revision_humana": True,
                        "motivo_descarte": "Sin evidencia",
                        "justificacion": "",
                    }
                ],
            )
            self.assertTrue(path.exists())
            self.assertTrue(path.with_suffix(".csv").exists())
            self.assertTrue(path.with_suffix(".html").exists())
            db_path = Path(tmp) / "data" / "iaas_vigilancia.db"
            self.assertTrue(db_path.exists())
            historial = IAASPersistenceManager(db_path).get_recent_analyses()
            self.assertEqual(len(historial), 1)
            self.assertTrue(historial[0]["revision_humana_obligatoria"])

    def test_reporte_bloquea_phi_residual(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(RuntimeError):
                IAASReporter(output_dir=tmp).write_case_report(
                    tipo_iaas="IVU",
                    notas=[],
                    resultados=[{"tipo_iaas": "IVU", "cumple": False, "justificacion": "Paciente: JUAN PEREZ"}],
                )

    def test_persistencia_local_bloquea_phi(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
            manager = IAASPersistenceManager(Path(tmp) / "iaas.db")
            with self.assertRaises(RuntimeError):
                manager.save_analysis(
                    {
                        "tipo_iaas": "IVU",
                        "mode": "stub",
                        "source_pdf": "Paciente JUAN PEREZ.pdf",
                        "privacy_status": "SIN_PHI_DETECTABLE_EN_REPORTE",
                        "folios_procesados": 1,
                        "sospechosos": [],
                        "resultados": [{"tipo_iaas": "IVU", "cumple": False, "justificacion": "Paciente: JUAN PEREZ"}],
                        "revision_humana_obligatoria": True,
                    }
                )

    def test_historial_local_html(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
            db_path = Path(tmp) / "iaas.db"
            manager = IAASPersistenceManager(db_path)
            manager.save_analysis(
                {
                    "tipo_iaas": "IVU",
                    "mode": "stub",
                    "source_pdf": "caso_sintetico.pdf",
                    "privacy_status": "SIN_PHI_DETECTABLE_EN_REPORTE",
                    "folios_procesados": 2,
                    "sospechosos": [],
                    "resultados": [
                        {
                            "tipo_iaas": "IVU",
                            "cumple": False,
                            "clasificacion": "No cumple",
                            "motivo_descarte": "Sin evidencia",
                            "requiere_revision_humana": True,
                        }
                    ],
                    "revision_humana_obligatoria": True,
                }
            )
            html = manager.write_history_html()
            self.assertTrue(html.exists())
            self.assertIn("Historial local IAAS", html.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
