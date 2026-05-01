# REGISTRO DE PATÓGENOS PARA DIFERENCIACIÓN EPIDEMIOLÓGICA (SIVIGILA/CDC)
# REGISTRO DE PROCEDIMIENTOS QUIRÚRGICOS Y VENTANAS DE VIGILANCIA (SIVIGILA/CDC)
SURGICAL_REGISTRY = {
    "con_implante": {
        "procedimientos": [
            "artroplastia", "reemplazo articular", "protesis", "valvula cardiaca", "bypass",
            "material de osteosintesis", "fijacion interna", "marcapasos", "derivacion ventriculoperitoneal"
        ],
        "ventana_dias": 90
    },
    "general": {
        "procedimientos": [
            "apendicectomia", "colecistectomia", "laparotomia", "cesarea", "herniorrafia",
            "tiroidectomia", "mastectomia", "nefrectomia", "toracotomia", "amputacion"
        ],
        "ventana_dias": 30
    }
}

# REGISTRO DE ESTADIAJE NEONATAL PARA ENTEROCOLITIS (CRITERIOS DE BELL)
BELL_STAGING_REGISTRY = {
    "estadio_I": {
        "descripcion": "Sospecha de ECN",
        "clinica": ["distension abdominal", "residuo gastrico", "sangre oculta en heces", "sangre macroscopica leve", "bradicardia", "apnea"],
        "radiologia": ["ileo leve", "dilatacion de asas", "normal"]
    },
    "estadio_II": {
        "descripcion": "ECN Confirmada",
        "clinica": ["sangre macroscopica franca", "ausencia de ruidos intestinales", "masa abdominal", "celulitis abdominal"],
        "radiologia": ["neumatosis intestinal", "gas en vena porta"]
    },
    "estadio_III": {
        "descripcion": "ECN Avanzada / Perforada",
        "clinica": ["deterioro respiratorio", "shock", "acidosis", "cid", "signos de peritonitis"],
        "radiologia": ["neumoperitoneo", "aire libre subdiafragmatico"]
    }
}

PATHOGEN_REGISTRY = {
    "reconocidos": [
        "escherichia coli", "e. coli", "klebsiella", "pseudomonas", "staphylococcus aureus", "s. aureus",
        "enterococcus", "enterobacter", "candida", "acinetobacter", "serratia", "proteus",
        "clostridioides difficile", "c. diff", "streptococcus pneumoniae", "neisseria"
    ],
    "comensales": [
        "staphylococcus epidermidis", "s. epidermidis", "estafilococo coagulasa negativo", 
        "coagulasa negativo", "difteroides", "corynebacterium", "bacillus", "propionibacterium",
        "micrococcus"
    ]
}

CRITERIA_REGISTRY = {
    "IVU": {
        "name": "IVU asociada a cateter / CAUTI",
        "version_status": "operativo_intermedio_sivigila_v1",
        "source_basis": ["INS/SIVIGILA Colombia 2024", "CDC/NHSN 2024"],
        "anchor_date": "fecha de toma de urocultivo",
        "temporal_rule": "dia de estancia >= 3 y sonda vesical presente en las 48h previas",
        "validation_matrix": {
            "clinica": {"items": ["fiebre > 38.0C", "dolor suprapubico", "urgencia", "disuria"], "min_required": 1},
            "laboratorio": {"items": ["urocultivo >= 10^5 ufc/ml", "maximo 2 especies", "leucocituria > 10/campo"], "min_required": 1},
            "dispositivo": {"items": ["sonda vesical (Foley)"], "min_required": 1}
        },
        "lexical_map": {
            "fiebre": ["fiebre", "pico febril", "hipertermia", "febril", "T > 38", "temperatura > 38"],
            "dolor suprapubico": ["dolor suprapubico", "dolor hipogastrio", "dolor en vejiga", "sensibilidad suprapubica"],
            "disuria": ["disuria", "ardor al orinar", "molestia miccional", "dificultad miccional"],
            "sonda": ["sonda vesical", "foley", "sv", "cateter urinario", "sondaje"],
            "urocultivo": ["urocultivo", "cultivo de orina", "parcial de orina", "sedimento urinario"]
        },
        "required_evidence": ["fiebre o sintoma local", "urocultivo positivo", "sonda vesical"],
        "exclusions": ["evento dia 1-2", "cultivo contaminado", "foco abdominal alterno"],
    },
    "NAV": {
        "name": "Neumonia asociada a ventilador / VAP",
        "version_status": "operativo_intermedio_sivigila_v1",
        "source_basis": ["INS/SIVIGILA Colombia 2024", "CDC/NHSN 2024"],
        "anchor_date": "deterioro respiratorio o toma de muestra",
        "temporal_rule": "ventilacion mecanica > 48h y estabilidad previa de FiO2/PEEP",
        "validation_matrix": {
            "clinica": {"items": ["fiebre > 38.0C", "secrecion purulenta", "estertores/roncus", "leucocitosis/leucopenia"], "min_required": 2},
            "radiologia": {"items": ["infiltrado nuevo", "consolidacion", "cavitacion"], "min_required": 1},
            "oxigenacion": {"items": ["aumento FiO2 > 0.20", "aumento PEEP > 3cmH2O"], "min_required": 1},
            "dispositivo": {"items": ["ventilacion mecanica invasiva"], "min_required": 1}
        },
        "lexical_map": {
            "secrecion purulenta": ["secrecion purulenta", "pus", "esputo purulento", "secreciones amarillentas", "secreciones verdosas", "aspirado purulento"],
            "estertores/roncus": ["estertores", "roncus", "crepitos", "sibilancias", "ruidos agregados", "hipoventilacion"],
            "infiltrado": ["infiltrado", "opacidad", "vidrio esmerilado", "mancha", "consolidacion", "atelectasia"],
            "ventilacion": ["ventilacion mecanica", "tot", "tubo orotraqueal", "vm", "ventilado", "intubado"],
            "oxigenacion": ["fio2", "peep", "deterioro ventilatorio", "requerimientos de o2"]
        },
        "required_evidence": ["ventilacion invasiva", "empeoramiento respiratorio", "radiologia/microbiologia"],
        "exclusions": ["SDR basal sin cambio", "edema pulmonar agudo", "tromboembolismo"],
    },
    "ITS-CVC": {
        "name": "Infeccion del torrente sanguineo asociada a CVC / CLABSI",
        "version_status": "operativo_intermedio_sivigila_v1",
        "source_basis": ["INS/SIVIGILA Colombia 2024", "CDC/NHSN 2024"],
        "anchor_date": "fecha de toma del hemocultivo",
        "temporal_rule": "dia de estancia >= 3 y CVC presente el dia del evento o el anterior",
        "validation_matrix": {
            "clinica": {"items": ["fiebre > 38.0C", "escalofrios", "hipotension"], "min_required": 1},
            "laboratorio": {"items": ["hemocultivo positivo (patogeno reconocido)", "sin foco primario en otro sitio"], "min_required": 1},
            "dispositivo": {"items": ["cateter venoso central"], "min_required": 1}
        },
        "lexical_map": {
            "escalofrios": ["escalofrios", "tiritona", "estremecimiento", "frio"],
            "hipotension": ["hipotension", "toma de tension baja", "choque", "shock", "soporte vasopresor"],
            "cateter": ["cvc", "cateter venoso central", "picc", "cateter central", "acceso central"],
            "hemocultivo": ["hemocultivo", "cultivo de sangre", "botellas de cultivo", "hemoc", "sangre"]
        },
        "required_evidence": ["hemocultivo positivo", "CVC", "ausencia de foco alterno"],
        "exclusions": ["ITS secundaria", "contaminante de piel unico", "hemocultivo dia 1-2"],
    },
    "ISQ": {
        "name": "Infeccion de sitio quirurgico",
        "version_status": "operativo_intermedio_sivigila_v1",
        "source_basis": ["SIVIGILA 2024"],
        "anchor_date": "hallazgo operatorio o drenaje",
        "temporal_rule": "ventana posquirurgica 30-90 dias",
        "validation_matrix": {
            "clinica": {"items": ["purulencia", "dolor localizado", "eritema", "calor"], "min_required": 1},
            "quirurgico": {"items": ["nota operatoria", "procedimiento invasivo", "descripcion de herida"], "min_required": 1},
            "laboratorio": {"items": ["cultivo de herida", "cultivo de tejido", "aspirado purulento"], "min_required": 1}
        },
        "lexical_map": {
            "purulencia": ["purulento", "pus", "secrecion purulenta", "material purulento", "drenaje purulento"],
            "eritema": ["eritema", "enrojecimiento", "rubor", "coloracion roja"],
            "quirurgico": ["quirofano", "cirugia", "acto operatorio", "incisión", "sutura", "dehiscencia"],
            "calor": ["calor", "caliente", "hipertermia local", "temperatura local aumentada"]
        },
        "required_evidence": ["procedimiento", "sitio anatomico", "purulencia/cultivo"],
        "exclusions": ["herida limpia", "secrecion no purulenta", "foco no relacionado"],
    },
    "SEPSIS_TARDIA": {
        "name": "Sepsis neonatal tardia",
        "version_status": "operativo_intermedio_sivigila_v1",
        "source_basis": ["SIVIGILA 2024"],
        "anchor_date": "toma de hemocultivo",
        "temporal_rule": ">= 72 horas de vida",
        "validation_matrix": {
            "clinica": {"items": ["apnea", "bradicardia", "inestabilidad termica", "rechazo a la via oral", "letargia"], "min_required": 2},
            "laboratorio": {"items": ["hemocultivo positivo", "PCR elevada", "leucocitosis/leucopenia neonatal"], "min_required": 1},
            "cronologia": {"items": ["horas de vida >= 72h"], "min_required": 1}
        },
        "lexical_map": {
            "apnea": ["apnea", "pausa respiratoria", "olvido respiratorio", "episodio de cianosis"],
            "letargia": ["letargia", "hipotonia", "pobre succion", "rechazo a la via oral", "hipoactividad"],
            "inestabilidad termica": ["hipotermia", "fiebre", "distermia", "frialdad"],
            "bradicardia": ["bradicardia", "caida de fc", "fc < 100"]
        },
        "required_evidence": ["signos clinicos", "cultivo", "cronologia neonatal"],
        "exclusions": ["sepsis temprana (0-71h)", "infeccion congenita"],
    },
    "ECN": {
        "name": "Enterocolitis necrotizante",
        "version_status": "operativo_intermedio_sivigila_v1",
        "source_basis": ["SIVIGILA 2024", "Criterios de Bell"],
        "anchor_date": "radiografia abdominal",
        "temporal_rule": "evento nuevo hospitalario",
        "validation_matrix": {
            "clinica": {"items": ["distension abdominal", "sangre en heces", "residuo gastrico porraceo"], "min_required": 1},
            "radiologia": {"items": ["neumatosis intestinal", "gas en vena porta", "neumoperitoneo"], "min_required": 1},
            "clasificacion": {"items": ["Estadio Bell II o III"], "min_required": 1}
        },
        "lexical_map": {
            "distension abdominal": ["distension", "abdomen globoso", "peristaltismo ausente", "pared abdominal tensa"],
            "sangre en heces": ["sangre en heces", "melenas", "heces con sangre", "sangre rutilante"],
            "residuo gastrico": ["residuo", "porraceo", "bilioso", "gastroparesia"],
            "neumatosis": ["neumatosis", "gas intramural", "aire en pared", "burbujas en pared intestinal"]
        },
        "required_evidence": ["clinica abdominal", "radiologia compatible", "estadio Bell"],
        "exclusions": ["Estadio Bell I (sospecha)", "distension funcional"],
    },
    "ENDOMETRITIS": {
        "name": "Endometritis puerperal",
        "version_status": "operativo_intermedio_sivigila_v1",
        "source_basis": ["SIVIGILA 2024"],
        "anchor_date": "inicio de sintomas posparto",
        "temporal_rule": "posterior al parto/cesarea y no presente al ingreso",
        "validation_matrix": {
            "clinica": {"items": ["fiebre > 38.0C", "dolor uterino a la palpacion", "loquios fétidos"], "min_required": 1},
            "antecedente": {"items": ["parto", "cesarea", "legrado"], "min_required": 1},
            "laboratorio": {"items": ["cultivo endometrial (opcional)", "leucocitosis"], "min_required": 1}
        },
        "lexical_map": {
            "dolor uterino": ["dolor uterino", "dolor a la palpacion de utero", "utero doloroso", "sensibilidad uterina"],
            "loquios fétidos": ["loquios", "secrecion vaginal fetida", "loquios malolientes", "fetidez"],
            "antecedente": ["parto", "cesarea", "legrado", "puerperio", "posparto"]
        },
        "required_evidence": ["evento obstetrico", "fiebre", "dolor uterino"],
        "exclusions": ["foco alterno (ej. IVU posparto)", "corioamnionitis previa"],
    },
    "ICD": {
        "name": "Clostridioides difficile",
        "version_status": "operativo_intermedio_sivigila_v1",
        "source_basis": ["SIVIGILA 2024"],
        "anchor_date": "toma de heces",
        "temporal_rule": "dia de estancia >= 3 o contacto previo hospitalario",
        "validation_matrix": {
            "clinica": {"items": ["diarrea (3 o mas deposiciones liquidas en 24h)", "dolor abdominal"], "min_required": 1},
            "laboratorio": {"items": ["toxina A/B positiva", "PCR para C. difficile", "GDH positivo"], "min_required": 1},
            "contexto": {"items": ["uso previo de antibioticos"], "min_required": 1}
        },
        "lexical_map": {
            "diarrea": ["diarrea", "deposiciones liquidas", "deposiciones blandas", "aumento de frecuencia evacuatoria"],
            "antibioticos": ["clindamicina", "cefalosporinas", "fluoroquinolonas", "antibioticoterapia prolongada"],
            "toxina": ["toxina a", "toxina b", "c. diff", "clostridium", "pcr heces"]
        },
        "required_evidence": ["diarrea", "toxina/PCR"],
        "exclusions": ["toxina negativa", "uso de laxantes", "diarrea funcional"],
    },
    "MENINGITIS": {
        "name": "Meningitis/ventriculitis asociada a atencion",
        "version_status": "operativo_intermedio_sivigila_v1",
        "source_basis": ["SIVIGILA 2024"],
        "anchor_date": "puncion lumbar o toma de LCR",
        "temporal_rule": "dia de estancia >= 3 o posprocedimiento neuroquirurgico",
        "validation_matrix": {
            "clinica": {"items": ["fiebre", "rigidez de nuca", "alteracion del sensorio", "cefalea"], "min_required": 1},
            "laboratorio": {"items": ["LCR: pleocitosis", "LCR: hipoglucorraquia", "LCR: cultivo positivo"], "min_required": 1},
            "dispositivo": {"items": ["derivacion ventricular externa (opcional)", "cateter de PIC"], "min_required": 1}
        },
        "lexical_map": {
            "rigidez de nuca": ["rigidez de nuca", "signos meningeos", "kerning", "brudzinski", "nuca rigida"],
            "sensorio": ["obnubilacion", "letargia", "coma", "estupor", "confusion", "alteracion del sensorio"],
            "pleocitosis": ["pleocitosis", "celulas aumentadas en lcr", "leucocitos en lcr", "lcr turbio"],
            "dispositivo": ["dve", "derivacion ventricular", "cateter pic", "valvula", "neurocirugia"]
        },
        "required_evidence": ["LCR alterado", "perfil infeccioso", "clinica"],
        "exclusions": ["meningitis quimica posquirurgica", "hemorragia subaracnoidea"],
    },
    "PIEL_BLANDOS": {
        "name": "Infeccion de piel y tejidos blandos",
        "version_status": "operativo_intermedio_sivigila_v1",
        "source_basis": ["SIVIGILA 2024"],
        "anchor_date": "primera nota de lesion",
        "temporal_rule": "dia de estancia >= 3",
        "validation_matrix": {
            "clinica": {"items": ["eritema", "calor local", "edema", "purulencia", "dolor"], "min_required": 1},
            "laboratorio": {"items": ["cultivo de secrecion", "gram de lesion"], "min_required": 1},
            "contexto": {"items": ["lesion no presente al ingreso", "sitio de insercion (opcional)"], "min_required": 1}
        },
        "lexical_map": {
            "eritema": ["eritema", "rojo", "enrojecimiento", "celulitis", "flogosis"],
            "edema": ["edema", "hinchazon", "inflamacion", "tumefaccion"],
            "purulencia": ["pus", "purulento", "secrecion purulenta", "material purulento"],
            "lesion": ["ulcera", "herida", "sitio de puncion", "insercion", "lesion cutanea"]
        },
        "required_evidence": ["eritema/calor/purulencia", "sitio anatomico"],
        "exclusions": ["lesion presente al ingreso", "ulcera por presion no infectada"],
    },
    "NEONATAL_LOCAL": {
        "name": "Onfalitis/conjuntivitis neonatal",
        "version_status": "operativo_intermedio_sivigila_v1",
        "source_basis": ["SIVIGILA 2024"],
        "anchor_date": "inicio de secrecion purulenta",
        "temporal_rule": ">= 72 horas de vida",
        "validation_matrix": {
            "clinica": {"items": ["purulencia umbilical", "eritema periumbilical", "secrecion ocular purulenta"], "min_required": 1},
            "localizacion": {"items": ["ombligo", "conjuntiva"], "min_required": 1},
            "cronologia": {"items": ["horas de vida >= 72h"], "min_required": 1}
        },
        "lexical_map": {
            "purulencia umbilical": ["onfalitis", "pus en ombligo", "secrecion umbilical purulenta", "mal olor umbilical"],
            "eritema periumbilical": ["rojo alrededor del ombligo", "halo eritematoso", "piel roja umbilical"],
            "secrecion ocular": ["legaña purulenta", "pus en ojos", "conjuntivitis purulenta"]
        },
        "required_evidence": ["purulencia", "sitio local", "horas de vida"],
        "exclusions": ["secrecion clara fisiologica", "conjuntivitis quimica"],
    },
}


def get_criteria_summary(tipo_iaas):
    return CRITERIA_REGISTRY.get(tipo_iaas, {"name": tipo_iaas, "required_evidence": [], "exclusions": []})
