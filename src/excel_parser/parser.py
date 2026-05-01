import csv
from pathlib import Path

from contracts import PacienteSospechoso, fecha_iso, parse_fecha


class MicrobiologyExcelParser:
    COLUMN_ALIASES = {
        "paciente_id": ["paciente", "id", "documento", "identificacion", "historia", "cc", "cedula", "nro_doc", "nro_historia"],
        "fecha_ingreso": ["fecha_ingreso", "ingreso", "fecha ingreso", "admision", "fecha_admision", "fecha hosp", "fecha_hosp"],
        "fecha_muestra": ["fecha_muestra", "fecha toma", "toma", "cultivo fecha", "fecha cultivo", "fecha recepcion", "recepcion", "fecha_orden"],
        "muestra": ["muestra", "tipo muestra", "origen", "sitio", "tipo de muestra", "descripcion_muestra", "material"],
        "organismo": ["organismo", "germen", "microorganismo", "aislamiento", "bacteria", "resultado_micro", "identificacion micro", "micro"],
        "resultado": ["resultado", "estado", "positivo", "crecimiento", "interpretacion", "valor", "hallazgo"],
        "servicio": ["servicio", "unidad", "ubicacion", "cama", "pabellon", "sala", "centro_costo", "area"],
    }

    def parse(self, excel_path):
        if Path(excel_path).suffix.lower() == ".csv":
            return self.parse_csv(excel_path)

        try:
            import pandas as pd
        except ImportError as exc:
            raise RuntimeError(
                "pandas/openpyxl no estan instalados para leer .xlsx. "
                "Puede usar un .csv sin dependencias externas o ejecutar: pip install -r requirements.txt"
            ) from exc

        df = pd.read_excel(excel_path)
        if df.empty:
            return []

        return self._parse_records(df.iterrows(), df.columns, first_data_row=2)

    def parse_csv(self, csv_path):
        with open(csv_path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        if not rows:
            return []
        return self._parse_records(enumerate(rows), rows[0].keys(), first_data_row=2)

    def _parse_records(self, records, raw_columns, first_data_row):
        columns = self._map_columns(raw_columns)
        sospechosos = []
        for idx, row in records:
            resultado = str(self._get(row, columns, "resultado") or "").lower()
            organismo = self._get(row, columns, "organismo")
            if not organismo and not any(token in resultado for token in ["positivo", "crecimiento", "aislado"]):
                continue
            if any(token in resultado for token in ["negativo", "sin crecimiento", "contaminado"]):
                continue

            fecha_ingreso = parse_fecha(self._get(row, columns, "fecha_ingreso"))
            fecha_muestra = parse_fecha(self._get(row, columns, "fecha_muestra"))
            dia = None
            clasificacion = "SIN_FECHA_SUFICIENTE"
            if fecha_ingreso and fecha_muestra:
                dia = (fecha_muestra.date() - fecha_ingreso.date()).days + 1
                clasificacion = "SOSPECHA_IAAS" if dia >= 3 else "IPI_POA"

            excel_row = int(idx) + first_data_row
            paciente_id = str(self._get(row, columns, "paciente_id") or f"fila_{excel_row}")
            sospechosos.append(
                PacienteSospechoso(
                    paciente_id=self._anon_id(paciente_id),
                    fecha_ingreso=fecha_iso(fecha_ingreso),
                    fecha_muestra=fecha_iso(fecha_muestra),
                    dia_estancia_muestra=dia,
                    muestra=self._clean(self._get(row, columns, "muestra")),
                    organismo=self._clean(organismo),
                    servicio=self._clean(self._get(row, columns, "servicio")),
                    clasificacion_temporal=clasificacion,
                    evidencia_origen={"fila_origen": excel_row},
                ).to_dict()
            )

        return sospechosos

    def _map_columns(self, columns):
        normalized = {self._norm(col): col for col in columns}
        mapping = {}
        for target, aliases in self.COLUMN_ALIASES.items():
            for alias in aliases:
                alias_norm = self._norm(alias)
                exact = normalized.get(alias_norm)
                if exact is not None:
                    mapping[target] = exact
                    break
                partial = next((original for norm, original in normalized.items() if alias_norm in norm), None)
                if partial is not None:
                    mapping[target] = partial
                    break
        return mapping

    def _get(self, row, columns, key):
        col = columns.get(key)
        if not col:
            return None
        value = row.get(col)
        if value != value:
            return None
        return value

    def _norm(self, value):
        return str(value).strip().lower().replace("_", " ").replace("-", " ")

    def _clean(self, value):
        return None if value is None else str(value).strip()

    def _anon_id(self, value):
        value = str(value).strip()
        if len(value) <= 4:
            return f"PAC_{value}"
        return f"PAC_{value[-4:]}"
