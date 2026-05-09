import os
import queue
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from main import DEFAULT_PDF, ejecutar_vigilancia_iaas
from reporting.persistence import IAASPersistenceManager


ROOT = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
MODO_SEGURO = "Seguro local"
MODO_IA_EXTERNA = "IA externa"
TIPOS_IAAS = [
    "IVU",
    "NAV",
    "ITS-CVC",
    "ISQ",
    "SEPSIS_TARDIA",
    "ECN",
    "ENDOMETRITIS",
    "ICD",
    "MENINGITIS",
    "PIEL_BLANDOS",
    "NEONATAL_LOCAL",
    "TODAS",
]


class IAASDesktopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema IAAS")
        self.root.geometry("880x620")
        self.root.minsize(760, 560)
        self.queue = queue.Queue()

        self.pdf_path = tk.StringVar(value=str(ROOT / DEFAULT_PDF))
        self.lab_path = tk.StringVar(value=str(ROOT / "data" / "raw_excel" / "microbiologia_sintetica.csv"))
        self.fecha_inicio = tk.StringVar()
        self.fecha_fin = tk.StringVar()
        self.tipo_iaas = tk.StringVar(value="IVU")
        self.mode = tk.StringVar(value=MODO_SEGURO)
        self.last_report = None
        self.db_path = ROOT / "data" / "iaas_vigilancia.db"

        self._build_ui()
        self.root.after(200, self._drain_queue)

    def _build_ui(self):
        pad = {"padx": 14, "pady": 8}

        header = ttk.Frame(self.root)
        header.pack(fill="x", padx=18, pady=(18, 8))
        ttk.Label(header, text="Sistema de Vigilancia IAAS - SIVIGILA 2024", font=("Segoe UI", 18, "bold")).pack(anchor="w")
        ttk.Label(
            header,
            text="Análisis Multidimensional de 11 categorías de IAAS con rigor epidemiológico forense.",
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(4, 0))

        form = ttk.LabelFrame(self.root, text="Archivos y rango de revision")
        form.pack(fill="x", padx=18, pady=8)
        form.columnconfigure(1, weight=1)

        ttk.Label(form, text="Historia clinica PDF").grid(row=0, column=0, sticky="w", **pad)
        ttk.Entry(form, textvariable=self.pdf_path).grid(row=0, column=1, sticky="ew", **pad)
        ttk.Button(form, text="Cargar PDF", command=self._choose_pdf).grid(row=0, column=2, sticky="ew", **pad)

        ttk.Label(form, text="Microbiologia Excel/CSV").grid(row=1, column=0, sticky="w", **pad)
        ttk.Entry(form, textvariable=self.lab_path).grid(row=1, column=1, sticky="ew", **pad)
        ttk.Button(form, text="Cargar laboratorio", command=self._choose_lab).grid(row=1, column=2, sticky="ew", **pad)

        ttk.Label(form, text="Fecha inicial").grid(row=2, column=0, sticky="w", **pad)
        ttk.Entry(form, textvariable=self.fecha_inicio, width=18).grid(row=2, column=1, sticky="w", **pad)
        ttk.Label(form, text="Use DD/MM/AAAA o AAAA-MM-DD").grid(row=2, column=1, sticky="e", **pad)

        ttk.Label(form, text="Fecha final").grid(row=3, column=0, sticky="w", **pad)
        ttk.Entry(form, textvariable=self.fecha_fin, width=18).grid(row=3, column=1, sticky="w", **pad)

        options = ttk.Frame(self.root)
        options.pack(fill="x", padx=18, pady=8)
        ttk.Label(options, text="Tipo IAAS").pack(side="left", padx=(0, 8))
        ttk.Combobox(options, values=TIPOS_IAAS, textvariable=self.tipo_iaas, state="readonly", width=22).pack(side="left")
        ttk.Label(options, text="Modo").pack(side="left", padx=(24, 8))
        ttk.Combobox(
            options,
            values=[MODO_SEGURO, MODO_IA_EXTERNA],
            textvariable=self.mode,
            state="readonly",
            width=16,
        ).pack(side="left")

        actions = ttk.Frame(self.root)
        actions.pack(fill="x", padx=18, pady=8)
        self.run_button = ttk.Button(actions, text="ANALIZAR", command=self._run_analysis)
        self.run_button.pack(side="left", ipadx=20, ipady=6)
        ttk.Button(actions, text="Abrir carpeta de reportes", command=self._open_outputs).pack(side="left", padx=12)
        ttk.Button(actions, text="Abrir ultimo reporte", command=self._open_last_report).pack(side="left")
        ttk.Button(actions, text="Ver historial local", command=self._open_local_history).pack(side="left", padx=12)
        ttk.Button(actions, text="Limpiar mensajes", command=self._clear_log).pack(side="left")

        help_box = ttk.LabelFrame(self.root, text="Resultado")
        help_box.pack(fill="both", expand=True, padx=18, pady=(8, 18))
        self.log = tk.Text(help_box, height=14, wrap="word", font=("Consolas", 10))
        self.log.pack(fill="both", expand=True, padx=10, pady=10)
        self._write(
            "Listo. El modo 'Seguro local' no envia datos a internet.\n"
            "Seleccione archivos, fechas opcionales y presione ANALIZAR.\n"
        )

    def _choose_pdf(self):
        path = filedialog.askopenfilename(
            title="Seleccione historia clinica PDF",
            filetypes=[("PDF", "*.pdf"), ("Todos los archivos", "*.*")],
            initialdir=str(ROOT),
        )
        if path:
            self.pdf_path.set(path)

    def _choose_lab(self):
        path = filedialog.askopenfilename(
            title="Seleccione laboratorio",
            filetypes=[("Excel o CSV", "*.xlsx *.xls *.csv"), ("Todos los archivos", "*.*")],
            initialdir=str(ROOT / "data" / "raw_excel"),
        )
        if path:
            self.lab_path.set(path)

    def _run_analysis(self):
        pdf = self.pdf_path.get().strip()
        lab = self.lab_path.get().strip()
        if not pdf or not Path(pdf).exists():
            messagebox.showerror("Falta PDF", "Seleccione un PDF valido de historia clinica.")
            return
        if lab and not Path(lab).exists():
            messagebox.showerror("Laboratorio no encontrado", "Seleccione un Excel/CSV valido o deje el campo vacio.")
            return
        if self._selected_mode() == "llm" and not os.environ.get("IAAS_LLM_API_KEY"):
            messagebox.showwarning(
                "IA externa no configurada",
                "No hay clave configurada para IA externa. Use 'Seguro local'.",
            )
            return

        self.run_button.config(state="disabled")
        self._write("\nIniciando analisis...\n")
        thread = threading.Thread(target=self._worker, args=(pdf, lab), daemon=True)
        thread.start()

    def _worker(self, pdf, lab):
        try:
            result = ejecutar_vigilancia_iaas(
                ruta_pdf=pdf,
                tipo_iaas=self.tipo_iaas.get(),
                mode=self._selected_mode(),
                excel_path=lab or None,
                output_dir=str(ROOT / "outputs"),
                persistence_db_path=str(self.db_path),
                persist=True,
                fecha_inicio=self.fecha_inicio.get().strip() or None,
                fecha_fin=self.fecha_fin.get().strip() or None,
            )
            self.queue.put(("ok", result))
        except Exception as exc:
            self.queue.put(("error", str(exc)))

    def _drain_queue(self):
        try:
            while True:
                kind, payload = self.queue.get_nowait()
                self.run_button.config(state="normal")
                if kind == "ok":
                    self.last_report = payload["reporte"]
                    self._write("Analisis terminado.\n")
                    self._write(f"Folios procesados: {payload['folios']}\n")
                    self._write(f"Sospechosos: {payload['sospechosos']}\n")
                    self._write(f"Reporte: {payload['reporte']}\n")
                    html_report = str(Path(payload["reporte"]).with_suffix(".html"))
                    self._write(f"Reporte facil: {html_report}\n")
                else:
                    self._write("No se pudo completar el analisis.\n")
                    self._write(f"Detalle: {payload}\n")
        except queue.Empty:
            pass
        self.root.after(200, self._drain_queue)

    def _open_outputs(self):
        path = ROOT / "outputs"
        path.mkdir(exist_ok=True)
        os.startfile(path)

    def _open_last_report(self):
        if not self.last_report:
            messagebox.showinfo("Sin reporte", "Todavia no se ha generado un reporte.")
            return
        html_path = Path(self.last_report).with_suffix(".html")
        os.startfile(html_path if html_path.exists() else self.last_report)

    def _open_local_history(self):
        try:
            html_path = IAASPersistenceManager(self.db_path).write_history_html()
            os.startfile(html_path)
        except Exception as exc:
            messagebox.showerror("Historial no disponible", f"No se pudo abrir el historial local.\n{exc}")

    def _clear_log(self):
        self.log.delete("1.0", "end")

    def _write(self, text):
        self.log.insert("end", text)
        self.log.see("end")

    def _selected_mode(self):
        return "llm" if self.mode.get() == MODO_IA_EXTERNA else "stub"


def main():
    root = tk.Tk()
    style = ttk.Style()
    if "vista" in style.theme_names():
        style.theme_use("vista")
    IAASDesktopApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
