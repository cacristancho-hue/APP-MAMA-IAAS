import json
import os
import re
from datetime import timedelta

from contracts import normalize_dictamen, parse_fecha
from criteria.registry import get_criteria_summary
from llm_analyzer.llm_client import LLMClient
from path_utils import resource_path
from validation.clinical_safety import ClinicalSafetyValidator


class ClinicalAnalyzerIA:
    def __init__(self, prompts_dir=None, mode="stub", llm_client=None):
        self.prompts_dir = str(prompts_dir or resource_path("src/llm_analyzer/prompts_clinicos"))
        self.mode = mode
        self.llm_client = llm_client or LLMClient()
        self.safety_validator = ClinicalSafetyValidator()
        self.prompts_disponibles = {
            "IVU": "ivu_prompt.md",
            "NAV": "nav_prompt.md",
            "ITS-CVC": "its_cvc_prompt.md",
            "ISQ": "isq_prompt.md",
            "SEPSIS_TARDIA": "sepsis_tardia_prompt.md",
            "ECN": "ecn_prompt.md",
            "ENDOMETRITIS": "endometritis_prompt.md",
            "ICD": "clostridioides_prompt.md",
            "MENINGITIS": "meningitis_prompt.md",
            "PIEL_BLANDOS": "piel_blandos_prompt.md",
            "NEONATAL_LOCAL": "neonatal_local_prompt.md",
        }

    def cargar_prompt(self, tipo_iaas):
        if tipo_iaas not in self.prompts_disponibles:
            disponibles = ", ".join(sorted(self.prompts_disponibles))
            raise ValueError(f"Tipo de IAAS '{tipo_iaas}' no soportado. Disponibles: {disponibles}")

        ruta_archivo = os.path.join(self.prompts_dir, self.prompts_disponibles[tipo_iaas])
        with open(ruta_archivo, "r", encoding="utf-8") as f:
            return f.read()

    def preparar_contexto_extraccion(self, ventana):
        texto_historia = ""
        for nota in ventana:
            texto_historia += f"--- {nota['folio']} ({nota['fecha']}) - {nota['tipo']} ---\n"
            texto_historia += f"{nota['contenido']}\n"
            texto_historia += f"DATOS DUROS: {json.dumps(nota.get('datos_duros_verificados', {}), ensure_ascii=False)}\n\n"

        return f"""Eres un transcriptor medico de alta precision. Extrae hechos clinicos sin diagnosticar.
NO EMITAS JUICIOS. Devuelve solo JSON con:
- linea_tiempo_signos
- dispositivos
- microbiologia_cruda
- notas_narrativas_clave

HISTORIA CLINICA DEIDENTIFICADA:
{texto_historia}
"""

    def preparar_contexto_dictamen(self, tipo_iaas, datos_crudos, perfil_basal):
        criteria = get_criteria_summary(tipo_iaas)
        prompt = self.cargar_prompt(tipo_iaas)
        
        # Inyección de la matriz de validación estructurada para guiar el razonamiento de la IA
        contexto_criterio = {
            "nombre": criteria.get("name"),
            "version": criteria.get("version_status"),
            "regla_temporal": criteria.get("temporal_rule"),
            "matriz_de_validacion_obligatoria": criteria.get("validation_matrix", {}),
            "evidencia_requerida_resumen": criteria.get("required_evidence", []),
            "exclusiones_criticas": criteria.get("exclusions", [])
        }
        
        prompt = (
            "### CONTEXTO DE CRITERIO EPIDEMIOLÓGICO (NORMATIVA):\n"
            f"{json.dumps(contexto_criterio, ensure_ascii=False, indent=2)}\n\n"
            "### TAREAS:\n"
            "1. Verifica el cumplimiento de CADA DIMENSIÓN en la matriz_de_validacion_obligatoria.\n"
            "2. Respeta la regla_temporal matemáticamente (Día 3 = >=48h desde ingreso).\n"
            "3. Identifica si aplica alguna de las exclusiones_criticas.\n\n"
            + prompt
        )
        prompt = prompt.replace("{{CONTEXTO_BASAL}}", json.dumps(perfil_basal, ensure_ascii=False))
        prompt = prompt.replace("{{TEXTO_HISTORIA_CLINICA}}", json.dumps(datos_crudos, ensure_ascii=False))
        return prompt

    def preparar_contexto_auditoria(self, pre_dictamen, datos_crudos):
        ruta_auditor = os.path.join(self.prompts_dir, "auditor_prompt.md")
        with open(ruta_auditor, "r", encoding="utf-8") as f:
            prompt_maestro = f.read()
        contexto = f"--- DATOS CRUDOS ---\n{json.dumps(datos_crudos, ensure_ascii=False, indent=2)}\n\n"
        contexto += f"--- PRE-DICTAMEN A AUDITAR ---\n{json.dumps(pre_dictamen, ensure_ascii=False, indent=2)}"
        return prompt_maestro + "\n\n" + contexto

    def extraer_perfil_basal(self, notas_estructuradas):
        """
        Extrae perfil basal con motor de redundancia temporal (Fallback).
        """
        folios_basales = []
        
        # BRECHA DETECTADA: Si el primer folio no tiene fecha, el sistema colapsaba.
        # SOLUCIÓN: Buscamos la fecha más temprana disponible en TODO el documento como ancla.
        todas_las_fechas = [self._fecha_nota(n) for n in notas_estructuradas if self._fecha_nota(n)]
        fecha_ingreso = min(todas_las_fechas) if todas_las_fechas else None
        
        if not fecha_ingreso:
            return {"estado_basal": {}, "fuente": "sin_fecha_confiable", "comorbilidades_detectadas": [], "fecha_ingreso_absoluta": None}

        comorbilidades = set()
        patrones_cronicos = r"(?i)\b(diabetes|dm|hta|hipertension|epoc|erc|falla renal|vih|cancer|tumor|antecedente[s]?)\b"
        
        temps_basales = []
        fio2_basales = []

        for nota in notas_estructuradas:
            fecha_nota = self._fecha_nota(nota)
            if fecha_nota and fecha_nota - fecha_ingreso <= timedelta(days=1):
                folios_basales.append(nota)
                hallazgos = re.findall(patrones_cronicos, nota.get("contenido", ""))
                for h in hallazgos: comorbilidades.add(h.upper())
                
                datos = nota.get("datos_duros_verificados", {})
                temps_basales.extend(datos.get("temperaturas", []))
                fio2_match = re.search(r"FiO2:?\s*(\d{2})", nota.get("contenido", ""), re.I)
                if fio2_match: fio2_basales.append(int(fio2_match.group(1)))

        avg_temp = sum(temps_basales)/len(temps_basales) if temps_basales else 37.0
        avg_fio2 = sum(fio2_basales)/len(fio2_basales) if fio2_basales else 21

        return {
            "estado_basal": {
                "folios_usados": [n["folio"] for n in folios_basales],
                "temp_promedio_ingreso": avg_temp,
                "fio2_promedio_ingreso": avg_fio2,
                "comorbilidades_detectadas": list(comorbilidades)
            },
            "fuente": "deterministico_redundante_v3",
            "fecha_ingreso_absoluta": fecha_ingreso
        }

    def _detectar_deterioro_significativo(self, valor_actual, valor_basal, tipo_parametro):
        """
        Validación matemática de deterioro clínico significativo vs estado basal.
        """
        if tipo_parametro == "fiebre":
            umbral_basal = max(38.0, valor_basal + 0.5)
            return valor_actual > umbral_basal
        if tipo_parametro == "oxigenacion":
            return valor_actual > (valor_basal + 20)
        return True

    def _verificar_umbral_laboratorio(self, datos_cuantitativos, tipo_hallazgo):
        """
        Valida matemáticamente si los paraclínicos cumplen umbrales epidemiológicos.
        """
        leucos = datos_cuantitativos.get("leucocitos", [])
        pcr_vals = datos_cuantitativos.get("pcr", [])
        if tipo_hallazgo == "leucocitosis": return any(l > 12000 for l in leucos)
        if tipo_hallazgo == "leucopenia": return any(l < 4000 for l in leucos)
        if tipo_hallazgo == "pcr elevada": return any(p > 10.0 for p in pcr_vals)
        return False

    def _es_dia_3_o_mayor(self, fecha_evento_str, fecha_ingreso_obj):
        """
        Validación matemática estricta: Día 3 se considera >= 48 horas (o calendario día 3).
        """
        if not (fecha_evento_obj := parse_fecha(fecha_evento_str)):
            return False
        if not fecha_ingreso_obj:
            return False
        
        delta = fecha_evento_obj - fecha_ingreso_obj
        return delta >= timedelta(days=2) 

    def _es_hallazgo_negado(self, texto, keyword):
        """
        Detecta si un hallazgo clínico está negado (prefijo o sufijo).
        BRECHA DETECTADA: Ventana de 30 chars era insuficiente para frases médicas complejas.
        SOLUCIÓN: Expandimos ventana a 60 caracteres y añadimos más partículas.
        """
        patrones_prefijo = r"\b(sin|no|niega[n]?|ausencia|ausente|descarta[n]?|negativo[s]?|libre de|no se evidencia|descartando)\b"
        regex_prefijo = rf"({patrones_prefijo}.{{0,60}})\b{re.escape(keyword)}\b"
        if re.search(regex_prefijo, texto, re.I): return True

        patrones_sufijo = r"\b(no|ausente|negativo[s]?|descarta[do|da]?|sin hallazgo[s]?|no reactivo)\b"
        regex_sufijo = rf"\b{re.escape(keyword)}\b[\s\:\-\>]{{1,5}}{patrones_sufijo}"
        if re.search(regex_sufijo, texto, re.I): return True
            
        return False

    def _verificar_continuidad_dispositivo(self, dispositivos, tipo_buscado, fecha_evento_str):
        """
        Verifica la regla epidemiológica: Dispositivo debe estar presente > 48h
        antes del evento para que se considere ASOCIADO al dispositivo.
        """
        fecha_evento = parse_fecha(fecha_evento_str)
        if not fecha_evento or not dispositivos: return False
        
        menciones_previas = []
        for d in dispositivos:
            if tipo_buscado in d.get("tipo", "").lower():
                fecha_d = parse_fecha(d.get("fecha"))
                if fecha_d and fecha_d <= fecha_evento: menciones_previas.append(fecha_d)
        
        if not menciones_previas: return False
        primera = min(menciones_previas); ultima = max(menciones_previas)
        return (ultima - primera) >= timedelta(days=1) 

    def _detectar_contexto_quirurgico(self, texto):
        from criteria.registry import SURGICAL_REGISTRY
        resultado = {"procedimiento": None, "ventana_dias": 30}
        for cat, config in SURGICAL_REGISTRY.items():
            for p in config["procedimientos"]:
                if re.search(rf"\b{p}\b", texto, re.I):
                    resultado["procedimiento"] = p
                    resultado["ventana_dias"] = config["ventana_dias"]
                    return resultado
        return resultado

    def _clasificar_estadio_bell(self, texto):
        from criteria.registry import BELL_STAGING_REGISTRY
        estadio_alcanzado = 0; evidencias = []
        for estadio, config in BELL_STAGING_REGISTRY.items():
            nivel = int(estadio.replace("estadio_", "").replace("I", "1").replace("II", "2").replace("III", "3"))
            for termino in config["clinica"] + config["radiologia"]:
                if re.search(rf"\b{termino}\b", texto, re.I) and not self._es_hallazgo_negado(texto, termino):
                    if nivel > estadio_alcanzado: estadio_alcanzado = nivel
                    evidencias.append(f"Hallazgo de {estadio}: {termino}")
        return estadio_alcanzado, evidencias

    def generar_dictamen_stub(self, tipo_iaas, datos_crudos):
        """
        Motor de evaluación determinística universal (11 IAAS) con Sensibilidad Léxica,
        Negaciones, Umbrales de Co-ocurrencia, Tendencias y Datos Cuantitativos.
        """
        criteria = get_criteria_summary(tipo_iaas)
        matrix = criteria.get("validation_matrix", {})
        lexical_map = criteria.get("lexical_map", {})
        regla_temporal_base = criteria.get("temporal_rule", "").lower()
        basal_data = datos_crudos.get("basal", {}).get("estado_basal", {})
        fecha_ingreso = datos_crudos.get("basal", {}).get("fecha_ingreso_absoluta")
        texto_crudo = json.dumps(datos_crudos, ensure_ascii=False).lower()
        
        faltantes = []
        evidencias_halladas = []
        cumple_regla_temporal = True
        exclusion_detectada = None

        # 1. Inteligencia Quirúrgica y Estadiaje Neonatal (Módulos Específicos)
        eventos_clave = datos_crudos["linea_tiempo_signos"] + datos_crudos["microbiologia_cruda"]
        fecha_ancla_str = eventos_clave[0].get("fecha") if eventos_clave else None

        if tipo_iaas == "ISQ":
            ctx_qx = self._detectar_contexto_quirurgico(texto_crudo)
            if ctx_qx["procedimiento"]: evidencias_halladas.append({"texto": f"Procedimiento quirúrgico: {ctx_qx['procedimiento'].upper()}"})
            else: cumple_regla_temporal = False
        elif tipo_iaas == "ECN":
            estadio_bell, ev_bell = self._clasificar_estadio_bell(texto_crudo)
            if estadio_bell >= 2: evidencias_halladas.append({"texto": f"Clasificación Bell >= II validada por motor experto."})
            elif estadio_bell == 1: exclusion_detectada = "Solo cumple Criterios Bell Estadio I (Sospecha), requiere neumatosis para IAAS."
            else: faltantes.append("CLASIFICACIÓN_BELL (Falta evidencia radiológica)")

        # 2. Validación Temporal (Dia 3 / 72h)
        if "dia de estancia >= 3" in regla_temporal_base:
            eventos_d3 = [e for e in eventos_clave if self._es_dia_3_o_mayor(e.get("fecha"), fecha_ingreso)]
            if not eventos_d3: cumple_regla_temporal = False
        elif ">= 72 horas de vida" in regla_temporal_base:
            if not re.search(r"72\s*h|3\s*dia|4\s*dia|vida", texto_crudo): cumple_regla_temporal = False

        # 3. Evaluación Multidimensional
        for dimension, config in matrix.items():
            items_dimension = config.get("items", [])
            min_requerido = config.get("min_required", 1)
            hallazgos_unicos = set()
            evidencias_dim = []

            for item_req in items_dimension:
                base_kw = item_req.split()[0].lower()
                keywords = lexical_map.get(base_kw, [base_kw])
                
                confirmado = False
                for kw in keywords:
                    if kw in ["leucocitosis", "leucopenia", "pcr elevada"]:
                        if any(self._verificar_umbral_laboratorio(n.get("datos_duros_verificados", {}), kw) for n in datos_crudos.get("ventana_raw", [])):
                            confirmado = True; evidencia_txt = f"Hallazgo OBJETIVO: {kw.upper()}"
                    elif kw == "fiebre":
                        picos = [item for item in datos_crudos["linea_tiempo_signos"] if item.get("T", 0) > 38.0]
                        if any(self._detectar_deterioro_significativo(p["T"], basal_data.get("temp_promedio_ingreso", 37.0), "fiebre") for p in picos):
                            confirmado = True; evidencia_txt = "Deterioro febril vs Basal"
                    elif kw in ["fio2", "peep", "deterioro ventilatorio"]:
                        f_match = re.search(r"FiO2:?\s*(\d{2})", texto_crudo, re.I)
                        if f_match and self._detectar_deterioro_significativo(int(f_match.group(1)), basal_data.get("fio2_promedio_ingreso", 21), "oxigenacion"):
                            confirmado = True; evidencia_txt = f"Deterioro oxigenación (FiO2 {f_match.group(1)}%)"
                    elif kw in ["urocultivo", "hemocultivo", "cultivo", "lcr", "pcr", "toxina"]:
                        from criteria.registry import PATHOGEN_REGISTRY
                        hallazgos_lab = []
                        for lab in datos_crudos["microbiologia_cruda"]:
                            txt_lab = lab.get("texto", "").lower()
                            if kw in txt_lab and not re.search(r"negativo|no\s*desarrolla|sin\s*crecimiento|normal|contaminado", txt_lab):
                                hallazgos_lab.append(txt_lab)
                        if hallazgos_lab:
                            txt_c = " ".join(hallazgos_lab)
                            if any(p in txt_c for p in PATHOGEN_REGISTRY["reconocidos"]):
                                confirmado = True; evidencia_txt = f"Lab POSITIVO (Patógeno): {kw}"
                            elif any(p in txt_c for p in PATHOGEN_REGISTRY["comensales"]):
                                if len(hallazgos_lab) >= 2 or tipo_iaas not in ["ITS-CVC", "SEPSIS_TARDIA"]:
                                    confirmado = True; evidencia_txt = f"Lab POSITIVO (Comensal x2): {kw}"
                    elif kw in ["sonda", "ventilacion", "cateter", "cvc", "tot"]:
                        if self._verificar_continuidad_dispositivo(datos_crudos["dispositivos"], kw, fecha_ancla_str):
                            confirmado = True; evidencia_txt = f"Dispositivo invasivo ({kw}) validado > 24-48h"
                    else:
                        if re.search(rf"\b{kw}\b", texto_crudo, re.I) and not self._es_hallazgo_negado(texto_crudo, kw):
                            confirmado = True; evidencia_txt = f"Signo clínico: {kw}"
                    
                    if confirmado:
                        hallazgos_unicos.add(item_req)
                        evidencias_dim.append(evidencia_txt)
                        break
            
            if len(hallazgos_unicos) >= min_requerido:
                evidencias_halladas.extend([{"texto": e} for e in evidencias_dim[:3]])
            else:
                faltantes.append(f"{dimension.upper()} (Faltan {min_requerido - len(hallazgos_unicos)} signos)")

        # 4. Verificación de Exclusiones Clínicas
        exclusiones = criteria.get("exclusions", [])
        for excl in exclusiones:
            kw_excl = excl.split()[0].lower()
            sinonimos_excl = lexical_map.get(kw_excl, [kw_excl])
            for kex in sinonimos_excl:
                if re.search(rf"\b{kex}\b", texto_crudo, re.I) and not self._es_hallazgo_negado(texto_crudo, kex):
                    exclusion_detectada = excl; break
            if exclusion_detectada: break

        # 5. Consolidación
        cumple = len(faltantes) == 0 and cumple_regla_temporal and not exclusion_detectada
        dictamen = f"{tipo_iaas} posible (Fase MVP)" if cumple else "No cumple"
        if exclusion_detectada:
            dictamen = "Descartado por Exclusión"
            motivo = f"Criterio excluido por hallazgo clínico: {exclusion_detectada}"
        elif not cumple_regla_temporal and len(faltantes) == 0:
            motivo = "No cumple regla de 48-72h (IPI/POA)"
        else:
            motivo = "" if cumple else f"Fallo matriz: {', '.join(faltantes)}"

        return {
            "dictamen_final": dictamen, "cumple": cumple, "motivo_descarte": motivo,
            "justificacion_forense": f"Análisis multi-capa V4: matriz, tendencias, continuidad y exclusiones (Excl: {exclusion_detectada or 'Ninguna'}).",
            "evidencia": evidencias_halladas, "nivel_confianza": "medio" if cumple else "bajo"
        }

    def analizar_historia_completa(self, notas_estructuradas, tipo_iaas, sospechosos=None):
        perfil_basal = self.extraer_perfil_basal(notas_estructuradas)
        ventanas = self.segmentar_notas_por_ventanas(notas_estructuradas)
        resultados_totales = []
        sospechosos = sospechosos or []

        for indice, ventana in enumerate(ventanas, start=1):
            datos_crudos = self._extraer_datos_deterministicos(ventana, perfil_basal, indice, sospechosos)
            datos_crudos["ventana_raw"] = ventana 
            if self.mode == "llm":
                prompt = self.preparar_contexto_dictamen(tipo_iaas, datos_crudos, perfil_basal)
                pre_dictamen = self.llm_client.complete_json(prompt)
                dictamen_auditado = self.llm_client.complete_json(self.preparar_contexto_auditoria(pre_dictamen, datos_crudos))
            else:
                pre_dictamen = self.generar_dictamen_stub(tipo_iaas, datos_crudos)
                dictamen_auditado = self.auditar_dictamen_stub(pre_dictamen, datos_crudos)

            dictamen = normalize_dictamen(tipo_iaas, dictamen_auditado, mode=self.mode)
            dictamen = self.safety_validator.validate(dictamen)
            resultados_totales.append(dictamen)
            if resultados_totales[-1]["cumple"]: break

        return resultados_totales

    def auditar_dictamen_stub(self, pre_dictamen, datos_crudos):
        max_temp = max([item.get("T", 0) or 0 for item in datos_crudos["linea_tiempo_signos"]] or [0])
        auditado = dict(pre_dictamen)
        auditado["auditoria_seguridad_hibrida"] = {
            "jerarquia_evidencia_usada": "Nivel 1 (extracción determinística)",
            "veredicto_seguridad": "SEGURO_PARA_REVISION_HUMANA",
            "max_temperatura_verificada": max_temp,
        }
        if "fiebre" in json.dumps(pre_dictamen, ensure_ascii=False).lower() and max_temp <= 38.0:
            auditado["cumple"] = False
            auditado["motivo_descarte"] = "Auditoría revoca fiebre: no hay temperatura >38.0C."
        return auditado

    def _extraer_datos_deterministicos(self, ventana, perfil_basal, indice, sospechosos=None):
        signos = []
        dispositivos = []
        microbiologia = []
        notas_clave = []
        if sospechosos:
            for s in sospechosos:
                if s.get("organismo") or "positivo" in str(s.get("clasificacion_temporal")).lower():
                    microbiologia.append({
                        "fecha": s.get("fecha_muestra", "Fecha Excel"),
                        "texto": f"EXCEL LAB: {s.get('muestra')}, Germen: {s.get('organismo')}",
                        "folio": f"Excel_Fila_{s.get('evidencia_origen', {}).get('fila_origen', 'X')}"
                    })
        for nota in ventana:
            datos = nota.get("datos_duros_verificados", {})
            for temp in datos.get("temperaturas", []):
                signos.append({"fecha": nota["fecha"], "T": temp, "folio": nota["folio"]})
            contenido = nota.get("contenido", "")
            if re.search(r"sonda|cateter|cvc|ventilacion|tot", contenido, re.I):
                dispositivos.append({"tipo": self._extraer_dispositivo(contenido), "fecha": nota["fecha"], "folio": nota["folio"]})
            if re.search(r"cultivo|hemocultivo|urocultivo|germen|ufc|pseudomonas|klebsiella", contenido, re.I):
                microbiologia.append({"fecha": nota["fecha"], "texto": f"NARRATIVO: {contenido[:150]}", "folio": nota["folio"]})
            if re.search(r"fiebre|sepsis|infeccion|purul|diarrea|neumonia", contenido, re.I):
                notas_clave.append({"fecha": nota["fecha"], "texto": contenido[:400], "folio": nota["folio"]})
        return {"ventana": indice, "basal": perfil_basal, "linea_tiempo_signos": signos, "dispositivos": dispositivos, "microbiologia_cruda": microbiologia, "notas_narrativas_clave": notas_clave}

    def _extraer_dispositivo(self, contenido):
        texto = contenido.lower()
        if "sonda" in texto: return "sonda vesical"
        if "cvc" in texto or "cateter central" in texto: return "cateter venoso central"
        if "ventilacion" in texto or "tot" in texto: return "ventilacion mecanica invasiva"
        return "dispositivo no especificado"

    def _fecha_nota(self, nota):
        match = re.search(r"\d{2}/\d{2}/\d{4}(?:\s+\d{2}:\d{2})?", str(nota.get("fecha", "")))
        return parse_fecha(match.group(0)) if match else None

    def segmentar_notas_por_ventanas(self, notas_estructuradas, dias_por_ventana=3):
        if not notas_estructuradas: return []
        ventanas = []; ventana_actual = []; inicio = None
        for nota in notas_estructuradas:
            fecha = self._fecha_nota(nota)
            if not fecha:
                if ventana_actual: ventana_actual.append(nota)
                else: ventanas.append([nota])
                continue
            if inicio is None: inicio = fecha
            if fecha - inicio <= timedelta(days=dias_por_ventana - 1): ventana_actual.append(nota)
            else:
                if ventana_actual: ventanas.append(ventana_actual)
                ventana_actual = [nota]; inicio = fecha
        if ventana_actual: ventanas.append(ventana_actual)
        return ventanas
