import json
from criteria.registry import get_criteria_summary


class ClinicalSafetyValidator:
    def validate(self, dictamen):
        warnings = []
        criteria = get_criteria_summary(dictamen.get("tipo_iaas"))
        evidencia = dictamen.get("evidencia") or []
        texto_evidencia = json.dumps(evidencia, ensure_ascii=False).lower()
        matrix = criteria.get("validation_matrix", {})

        # 1. Bloqueo total si no hay ninguna evidencia
        if dictamen.get("cumple") and not evidencia:
            dictamen["cumple"] = False
            dictamen["clasificacion"] = "Duda técnica - evidencia insuficiente"
            dictamen["motivo_descarte"] = "Se bloqueó confirmación porque no hay evidencia trazable por folio/cita."
            warnings.append("confirmacion_bloqueada_sin_evidencia")

        # 2. Validación granular por DIMENSIONES de la matriz (Nivel Auditoría Superior)
        faltantes_dimensiones = []
        if dictamen.get("cumple") and matrix:
            for dimension, items in matrix.items():
                # Verificamos si al menos un keyword de la dimensión aparece en la evidencia
                hallado_dimension = False
                for req in items:
                    keyword = req.split()[0].lower()
                    if keyword in texto_evidencia:
                        hallado_dimension = True
                        break
                
                if not hallado_dimension:
                    faltantes_dimensiones.append(dimension.upper())
            
            if faltantes_dimensiones:
                dictamen["cumple"] = False
                dictamen["clasificacion"] = "Duda técnica - falta dimensión clínica"
                dictamen["motivo_descarte"] = f"Faltan evidencias para las dimensiones obligatorias: {', '.join(faltantes_dimensiones)}."
                warnings.append("dimensiones_matriz_faltantes")

        # 3. Asegurar motivo de descarte en negativos
        if not dictamen.get("cumple") and not dictamen.get("motivo_descarte"):
            dictamen["motivo_descarte"] = "No hay evidencia suficiente para clasificar como IAAS según criterios operativos multidimensionales."
            warnings.append("motivo_descarte_agregado")

        if dictamen.get("nivel_confianza") not in {"alto", "medio", "bajo"}:
            dictamen["nivel_confianza"] = "bajo"
            warnings.append("confianza_normalizada")

        if dictamen.get("mode") == "stub":
            warnings.append("modo_seguro_local_no_confirma_diagnostico")

        dictamen["safety_gate"] = {
            "status": "REQUIERE_REVISION_HUMANA",
            "warnings": warnings,
            "criterio_base": criteria.get("name"),
            "matriz_validada": list(matrix.keys()),
            "dimensiones_faltantes": faltantes_dimensiones,
            "fecha_ancla_requerida": criteria.get("anchor_date"),
            "exclusiones_a_revisar": criteria.get("exclusions", []),
        }
        dictamen["requiere_revision_humana"] = True
        return dictamen
