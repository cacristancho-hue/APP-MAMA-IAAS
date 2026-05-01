import re

class HistoriClinicaExtractor:
    def __init__(self):
        # Patrones para limpiar encabezados y pies de página
        self.patrones_limpieza = [
            r"HOSPITAL REGIONAL DE LA ORINOQUÍA E\.S\.E",
            r"NIT 8918550295",
            r"Calle 15 N° 07-95 Manzana L - Vía Marginal de la Selva",
            r"Yopal - Casanare",
            r"Teléfono: \(8\) 634 4650 - Contact Center \(57\) 300-9132663",
            r"LICENCIADO A: \[HOSPITAL REGIONAL DE LA ORINOQUIA E\.S\.E\.\] NIT \[891855029-5\]",
            r"“La historia clínica no lleva la firma y sello teniendo en cuenta el artículo 18 de la resolución 1995, Julio 08 de 1999”",
            r"Usuario: .*?Fecha Impresión: .*?\d{2}:\d{2}",
            r"Nombre reporte : HCRPHistoBase",
            r"ESCANEE\s*CODIGO QR\s*INDICACIONES DEL\s*PACIENTE",
            r"Página \d+/\d+",
            r"N° Ingreso:.*?No Documento.*?\n\d+.*?\d{2}/\d{2}/\d{4}.*?\d+",
            r"Paciente:.*?\n",
            r"Entidad Ingreso:.*?Contrato Ingreso:.*?\n",
            r"Entidad Paciente:.*?Contrato Paciente:.*?\n",
            r"Regimen\s+Subsidiado",
            r"Fecha Nacimiento:.*?Sexo:.*?Estado Civil:.*?\n",
            r"Municipio:.*?Direccion:.*?Telefono:.*?\n",
            r"Edad en el folio:.*?\n"
        ]

    def deidentificar_texto(self, texto):
        """
        Ofusca datos sensibles para cumplir con Ley 1581 (Habeas Data).
        Utiliza el motor avanzado de PrivacyGuard para una redacción proactiva.
        """
        from privacy.guard import PrivacyGuard
        guard = PrivacyGuard()
        return guard.redact_text(texto)

    def extraer_texto_real(self, ruta_pdf):
        """
        Extrae el texto del PDF usando PyMuPDF (fitz) con preservación de bloques.
        """
        try:
            import fitz # PyMuPDF
        except ImportError:
            return "Error: La librería 'pymupdf' no está instalada. Ejecute 'pip install pymupdf'."

        doc = fitz.open(ruta_pdf)
        texto_completo = ""
        
        for pagina in doc:
            bloques = pagina.get_text("blocks")
            bloques.sort(key=lambda b: (b[1], b[0]))
            for b in bloques:
                contenido_bloque = b[4].strip()
                if re.search(r"SIGNOS VITALES|PARACLINICOS|ANALISIS|ORDENES", contenido_bloque, re.I):
                    texto_completo += f"\n\n[SECCION: {contenido_bloque.upper()}]\n"
                else:
                    texto_completo += contenido_bloque + " "
            texto_completo += "\n--- FIN DE PAGINA ---\n"
        
        return self.procesar_historia(texto_completo)

    def extraer_datos_cuantitativos(self, texto):
        """
        Extrae signos vitales y paraclínicos numéricos usando RegEx (Sin IA).
        Incluye Leucocitos y PCR para validación objetiva de IAAS.
        """
        datos = {
            "temperaturas": [],
            "frecuencias_cardiacas": [],
            "frecuencias_respiratorias": [],
            "saturaciones": [],
            "leucocitos": [],
            "pcr": []
        }
        
        # Patrones específicos robustos
        patron_temp = r"\b(?:T|Temp(?:eratura)?)\s*:?\s*(\d{2}(?:\.\d)?)"
        patron_fc = r"(?:FC|F\.C\.?|Frecuencia Cardiaca)\s*:?\s*(\d{2,3})"
        patron_fr = r"(?:FR|F\.R\.?|Frecuencia Respiratoria)\s*:?\s*(\d{2,3})"
        patron_sat = r"(?:Sat(?:uracion)?(?:O2)?|SpO2)\s*:?\s*(\d{2,3})"
        
        # Leucocitos: maneja 12000, 12.000, 12,000
        patron_leuco = r"(?i)(?:Leucocito[s]?|WBC|Blancos)\s*:?\s*(\d{1,2}(?:[\.,]\d{3})?|\d{4,5})"
        # PCR: maneja 12.5, 120
        patron_pcr = r"(?i)\bPCR\b\s*:?\s*(\d{1,3}(?:\.\d)?)"

        datos["temperaturas"] = [float(t) for t in re.findall(patron_temp, texto, re.I)]
        datos["frecuencias_cardiacas"] = [int(f) for f in re.findall(patron_fc, texto, re.I)]
        datos["frecuencias_respiratorias"] = [int(f) for f in re.findall(patron_fr, texto, re.I)]
        datos["saturaciones"] = [int(s) for s in re.findall(patron_sat, texto, re.I)]
        
        # Normalización de Leucocitos (Eliminar puntos de miles)
        leucos_raw = re.findall(patron_leuco, texto, re.I)
        for l in leucos_raw:
            l_clean = l.replace(".", "").replace(",", "")
            try:
                val = int(l_clean)
                if 100 < val < 100000: datos["leucocitos"].append(val)
            except ValueError: pass

        datos["pcr"] = [float(p) for p in re.findall(patron_pcr, texto, re.I)]
        
        return datos

    def procesar_historia(self, texto_crudo):
        """
        Divide la historia en Folios, limpia, deidentifica y extrae datos cuantitativos.
        """
        from datetime import datetime
        
        texto_seguro = self.deidentificar_texto(texto_crudo)
        
        # Soporte para múltiples formas de decir "Folio"
        folios_raw = re.split(r"(?i)(FOLIO N[°o]?\s*\d+|FOLIO:\s*\d+)", texto_seguro)
        notas_estructuradas = []
        
        for i in range(1, len(folios_raw), 2):
            titulo_folio = folios_raw[i].strip()
            contenido = folios_raw[i+1]
            
            match_fecha = re.search(r"(?i)Fecha\s*:?\s*(\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2})(?:\s*(\d{2}:\d{2}))?", contenido)
            timestamp_obj = None
            fecha_display = "Fecha no encontrada"
            
            if match_fecha:
                try:
                    fecha_val = match_fecha.group(1)
                    hora_val = match_fecha.group(2) or "00:00"
                    fmt = "%Y-%m-%d %H:%M" if "-" in fecha_val else "%d/%m/%Y %H:%M"
                    timestamp_obj = datetime.strptime(f"{fecha_val} {hora_val}", fmt)
                    fecha_display = f"{fecha_val} {hora_val}"
                except ValueError: pass

            if not timestamp_obj: timestamp_obj = datetime.max 

            contenido_limpio = self.limpiar_texto(contenido)
            datos_cuantitativos = self.extraer_datos_cuantitativos(contenido)
            
            tipo_nota = "OTRA NOTA"
            contenido_upper = contenido.upper()
            if "EVOLUCION MEDICA" in contenido_upper: tipo_nota = "EVOLUCION MEDICA"
            elif "TERAPIA RESPIRATORIA" in contenido_upper: tipo_nota = "TERAPIA RESPIRATORIA"
            elif "ENFERMERIA" in contenido_upper: tipo_nota = "NOTA DE ENFERMERIA"
            elif "PROCEDIMIENTO" in contenido_upper: tipo_nota = "PROCEDIMIENTO"
            elif "LABORATORIO" in contenido_upper: tipo_nota = "RESULTADO LABORATORIO"

            notas_estructuradas.append({
                "timestamp": timestamp_obj,
                "folio": titulo_folio,
                "fecha": fecha_display,
                "tipo": tipo_nota,
                "contenido": contenido_limpio,
                "datos_duros_verificados": datos_cuantitativos
            })
            
        notas_estructuradas.sort(key=lambda x: x["timestamp"])
        for n in notas_estructuradas: del n["timestamp"]
            
        return notas_estructuradas

    def limpiar_texto(self, texto):
        """
        Remueve el ruido administrativo y formatea secciones clave.
        """
        texto_limpio = texto
        for patron in self.patrones_limpieza:
            texto_limpio = re.sub(patron, "", texto_limpio, flags=re.IGNORECASE | re.MULTILINE)
        texto_limpio = re.sub(r'\n\s*\n', '\n', texto_limpio)
        texto_limpio = re.sub(r'[ \t]+', ' ', texto_limpio)
        return texto_limpio.strip()
