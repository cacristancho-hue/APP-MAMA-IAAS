import json
import re


class PrivacyGuard:
    SAFE_PLACEHOLDERS = {"[ANONIMIZADO]", "[PROTEGIDO]", "[OCULTO]", "[EMAIL_OCULTO]"}

    PATTERNS = {
        "email": re.compile(r"\b[\w\.-]+@[\w\.-]+\.\w+\b", re.I),
        "telefono": re.compile(r"\b(?:(?:\+?57)?\s*3\d{2}[\s\-]?\d{3}[\s\-]?\d{4}|60\d[\s\-]?\d{3}[\s\-]?\d{4}|\d{7,10})\b"),
        "documento": re.compile(r"\b(?:CC|C\.?C\.?|TI|RC|CE|PEP|PPT|NIT|Pasaporte|No\.?\s*Documento|Identificacion|ID|DNI)\s*:?\s*(\d{1,3}(\.?\d{3}){1,3}|[A-Z0-9]{5,15})\b", re.I),
        "direccion": re.compile(r"\b(?:Direccion|Dirección|Calle|Carrera|Cra\.|Cl\.|Transversal|Diag|Avenida|Av\.|Barrio|Vereda)\b[^\n,;]{3,80}", re.I),
        "paciente_nombre": re.compile(r"\b(?:Paciente|Nombre|Afiliado|Usuario|Paciente\s*Nombre|Titular|Responsable)\s*:\s*(?!\[ANONIMIZADO\])([A-ZÁÉÍÓÚÑa-záéíóúñ]{2,}(?:\s+[A-ZÁÉÍÓÚÑa-záéíóúñ]{2,})+)", re.I),
        "historia_clinica": re.compile(r"\b(?:No\.?\s*Historia|Historia\s*Clínica|HC|Nro\s*HC|Folio\s*Adm|Cama|Ubicacion|Municipio)\b\s*:?\s*[^\n,;]{3,40}\b", re.I),
        "seguridad_social": re.compile(r"\b(?:EPS|Aseguradora|Regimen|Contributivo|Subsidiado|Convenio|Entidad)\b\s*:?\s*[^\n,;]{3,50}", re.I),
    }

    # Términos médicos que NUNCA deben ser anonimizados (Evita sobre-redacción)
    WHITE_LIST = {
        "KLEBSIELLA", "PSEUDOMONAS", "ESCHERICHIA", "STAPHYLOCOCCUS", "ENTEROCOCCUS",
        "SINDROME", "INSUFICIENCIA", "DIFICULTAD", "RESPIRATORIA", "PRESENTA", "SINTOMAS",
        "INGRESO", "EVOLUCION", "MEDICA", "ENFERMERIA", "VALORACION", "CONDUCTA",
        "PACIENTE", "USUARIO", "AFILIADO", "TITULAR"
    }

    def redact_text(self, text):
        """
        Limpia proactivamente el texto de cualquier rastro de PHI.
        Incluye filtro de falsos positivos para evitar sobre-redacción clínica.
        """
        redacted = text

        # 1. Aplicamos redacción determinística de patrones no nominales (IDs, Tel, Email)
        for kind in ["email", "documento", "telefono", "direccion", "historia_clinica", "seguridad_social"]:
            redacted = self.PATTERNS[kind].sub(f" [{kind.upper()}_ANONIMIZADO] ", redacted)

        # 2. Redacción de Nombres con Filtro de Vocabulario Clínico (Anti Over-redaction)
        def _name_scrubber(match):
            name_candidate = match.group(1).upper()
            label = match.group(0).split(":")[0].strip()

            # Si alguna palabra del nombre está en la lista blanca, NO redactamos
            palabras = name_candidate.split()
            if any(p in self.WHITE_LIST for p in palabras):
                return match.group(0) # Mantenemos el original

            return f"{label}: [PACIENTE_NOMBRE_ANONIMIZADO]"

        redacted = self.PATTERNS["paciente_nombre"].sub(_name_scrubber, redacted)

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
