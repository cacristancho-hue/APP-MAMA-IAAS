import json
from criteria.registry import get_criteria_summary


class ClinicalSafetyValidator:
    def validate(self, dictamen):
        import re
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

        # 2. Validación granular por DIMENSIONES con SEMÁNTICA (Lookarounds)
        faltantes_dimensiones = []
        lexical_map = criteria.get("lexical_map", {})
        # Patrón de negación universal para evitar bypass
        patron_negacion = r"\b(?:sin|no|niega|ausencia|descarta|negativo|libre de|no se evidencia)\b"

        if dictamen.get("cumple") and matrix:
            for dimension, config in matrix.items():
                items_dimension = config.get("items", [])
                hallado_dimension = False
                for req in items_dimension:
                    base_kw = req.split()[0].lower()
                    # Buscamos no solo la palabra base, sino todos sus sinónimos del mapa léxico
                    keywords_a_validar = lexical_map.get(base_kw, [base_kw])

                    for kw in keywords_a_validar:
                        # Regex que busca el keyword pero ASEGURA que no esté precedido por una negación en los últimos 40 caracteres
                        for match in re.finditer(rf"\b{re.escape(kw[:6])}\w*\b", texto_evidencia):
                            contexto_previo = texto_evidencia[max(0, match.start()-40):match.start()]
                            if not re.search(patron_negacion, contexto_previo):
                                hallado_dimension = True
                                break
                        if hallado_dimension: break
                    if hallado_dimension: break
                
                if not hallado_dimension:
                    faltantes_dimensiones.append(dimension.upper())
            
            if faltantes_dimensiones:
                dictamen["cumple"] = False
                dictamen["clasificacion"] = "Duda técnica - falla validación semántica"
                dictamen["motivo_descarte"] = f"Faltan evidencias AFIRMATIVAS para las dimensiones obligatorias: {', '.join(faltantes_dimensiones)}. Se detectaron menciones pero posiblemente en contextos negativos o insuficientes."
                warnings.append("dimensiones_matriz_faltantes_semantica")

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
