import sys
from pathlib import Path


def app_root():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[1]


def resource_path(relative_path):
    base = Path(getattr(sys, "_MEIPASS", app_root()))
    return base / relative_path
