from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any


def parse_fecha(valor):
    if not valor:
        return None
    if isinstance(valor, datetime):
        return valor
    texto = str(valor).strip()
    for fmt in ("%d/%m/%Y %H:%M", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(texto, fmt)
        except ValueError:
            continue
    return None


def fecha_iso(valor):
    fecha = parse_fecha(valor)
    return fecha.isoformat() if fecha else None


@dataclass
class NotaClinica:
    folio: str
    fecha: str
    tipo: str
    contenido: str
    datos_duros_verificados: dict[str, list[Any]] = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)


@dataclass
class PacienteSospechoso:
    paciente_id: str
    fecha_ingreso: str | None
    fecha_muestra: str | None
    dia_estancia_muestra: int | None
    muestra: str | None
    organismo: str | None
    servicio: str | None
    clasificacion_temporal: str
    evidencia_origen: dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)


@dataclass
class DictamenIAAS:
    tipo_iaas: str
    cumple: bool
    clasificacion: str
    motivo_descarte: str
    justificacion: str
    evidencia: list[dict[str, Any]] = field(default_factory=list)
    nivel_confianza: str = "bajo"
    requiere_revision_humana: bool = True
    mode: str = "stub"
    raw: dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)


def normalize_dictamen(tipo_iaas, raw, mode="stub"):
    raw = raw or {}
    dictamen_final = str(raw.get("dictamen_final") or raw.get("clasificacion") or "")
    
    # Soporte para cumplimiento definido dentro de la matriz de dimensiones (Prompts V3/V4)
    cumple_matriz = False
    if dims := raw.get("evaluacion_dimensiones"):
        # Si todas las dimensiones requeridas en el JSON de la IA son True
        cumple_matriz = all(d.get("cumple", False) for d in dims.values())

    cumple = bool(
        raw.get("cumple")
        or cumple_matriz
        or raw.get("es_iaas_confirmada")
        or "confirmada" in dictamen_final.lower()
        or "posible" in dictamen_final.lower()
    )
    
    motivo_descarte = raw.get("motivo_descarte") or ""
    if not cumple and not motivo_descarte:
        motivo_descarte = "No hay evidencia suficiente trazable para confirmar IAAS según matriz multidimensional."

    return DictamenIAAS(
        tipo_iaas=tipo_iaas,
        cumple=cumple,
        clasificacion=dictamen_final or ("IAAS posible" if cumple else "No cumple"),
        motivo_descarte=motivo_descarte,
        justificacion=raw.get("justificacion_forense") or raw.get("justificacion") or "",
        evidencia=_extract_evidence(raw),
        nivel_confianza=raw.get("nivel_confianza") or ("medio" if cumple else "bajo"),
        requiere_revision_humana=True,
        mode=mode,
        raw=raw,
    ).to_dict()


def _extract_evidence(raw):
    if isinstance(raw, dict) and ("folio" in raw or "texto" in raw or "evidencia" in raw):
        return [raw]

    evidence = []
    if not isinstance(raw, dict):
        return evidence

    for value in raw.values():
        if isinstance(value, dict):
            if "folio" in value or "texto" in value or "evidencia" in value:
                evidence.append(value)
            else:
                evidence.extend(_extract_evidence(value))
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    evidence.extend(_extract_evidence(item))
    return evidence
