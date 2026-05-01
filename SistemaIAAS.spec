# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

ROOT = Path.cwd()

datas = [
    (str(ROOT / "src" / "llm_analyzer" / "prompts_clinicos"), "src/llm_analyzer/prompts_clinicos"),
    (str(ROOT / "data" / "raw_excel" / "PLANTILLA_LABORATORIO.csv"), "data/raw_excel"),
    (str(ROOT / "data" / "raw_excel" / "microbiologia_sintetica.csv"), "data/raw_excel"),
    (str(ROOT / "MANUAL_USUARIO_FINAL.md"), "."),
    (str(ROOT / "README_RUN.md"), "."),
    (str(ROOT / "DISEÑO_SISTEMA_IAAS.md"), "."),
    (str(ROOT / "DICCIONARIO_LABORATORIO.md"), "."),
    (str(ROOT / "HISTORIA CLINICA TIPO HOSPITAL REGIONAL DE LA ORINOQUIA EJEMPLO.pdf"), "."),
]

a = Analysis(
    ["app_escritorio.py"],
    pathex=[str(ROOT), str(ROOT / "src")],
    binaries=[],
    datas=datas,
    hiddenimports=[
        "fitz",
        "pandas",
        "openpyxl",
        "tkinter",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="SistemaIAAS",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
