import json
import re


class PrivacyGuard:
    SAFE_PLACEHOLDERS = {"[ANONIMIZADO]", "[PROTEGIDO]", "[OCULTO]", "[EMAIL_OCULTO]"}

    PATTERNS = {
        "email": re.compile(r"[\w\.-]+@[\w\.-]+\.\w+", re.I),
        "telefono": re.compile(r"\b(?:(?:\+?57)?\s*3\d{2}[\s\-]?\d{3}[\s\-]?\d{4}|60\d[\s\-]?\d{3}[\s\-]?\d{4}|\d{7,10})\b"),
        # Soporte para Cédula con puntos: 1.234.567.890
        "documento": re.compile(r"\b(?:CC|C\.?C\.?|TI|RC|CE|PEP|PPT|NIT|Pasaporte|No\.?\s*Documento|Identificacion|ID|DNI)\s*:?\s*(\d{1,3}(\.?\d{3}){1,3}|[A-Z0-9]{5,15})\b", re.I),
        "direccion": re.compile(r"\b(?:Direccion|Dirección|Calle|Carrera|Cra\.|Cl\.|Transversal|Diag|Avenida|Av\.|Barrio|Vereda)\b[^\n,;]{3,80}", re.I),
        "paciente_nombre": re.compile(r"(?:Paciente|Nombre|Afiliado|Usuario|Paciente\s*Nombre|Titular|Responsable)\s*:\s*(?!\[ANONIMIZADO\])([A-ZÁÉÍÓÚÑa-záéíóúñ]{2,}(?:\s+[A-ZÁÉÍÓÚÑa-záéíóúñ]{2,})+)", re.I),
        "historia_clinica": re.compile(r"\b(?:No\.?\s*Historia|Historia\s*Clínica|HC|Nro\s*HC|Folio\s*Adm|Cama|Ubicacion|Municipio)\s*:?\s*[^\n,;]{3,40}\b", re.I),
        "seguridad_social": re.compile(r"\b(?:EPS|Aseguradora|Regimen|Contributivo|Subsidiado|Convenio|Entidad)\s*:?\s*[^\n,;]{3,50}", re.I),
    }

    # Términos médicos que NO deben ser anonimizados (Lista Blanca)
    WHITE_LIST = {"KLEBSIELLA", "PSEUDOMONAS", "ESCHERICHIA", "STAPHYLOCOCCUS", "ENTEROCOCCUS"}

    def redact_text(self, text):
        """
        Limpia proactivamente el texto de cualquier rastro de PHI.
        Se usa en la etapa de ingesta antes de que el motor de IA vea los datos.
        """
        redacted = text
        # Iteramos en reversa o por longitud para no romper offsets si aplicara, 
        # pero con sub es directo.
        for kind, pattern in self.PATTERNS.items():
            redacted = pattern.sub(f" [{kind.upper()}_ANONIMIZADO] ", redacted)
        return redacted

    def scan_payload(self, payload):
        text = json.dumps(payload, ensure_ascii=False)
        return self.scan_text(text)

    def scan_text(self, text):
        findings = []
        safe_text = text
        for placeholder in self.SAFE_PLACEHOLDERS:
            safe_text = safe_text.replace(placeholder, "")

        for kind, pattern in self.PATTERNS.items():
            for match in pattern.finditer(safe_text):
                snippet = match.group(0)
                findings.append(
                    {
                        "type": kind,
                        "snippet": self._mask(snippet),
                        "start": match.start(),
                    }
                )
        return findings

    def assert_safe_payload(self, payload):
        findings = self.scan_payload(payload)
        if findings:
            raise RuntimeError(f"PHI residual detectado; reporte bloqueado: {findings[:5]}")
        return True

    def _mask(self, value):
        value = str(value)
        if len(value) <= 4:
            return "***"
        return value[:2] + "***" + value[-2:]
