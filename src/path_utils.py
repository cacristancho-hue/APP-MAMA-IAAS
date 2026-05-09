import sys
from pathlib import Path
from os import environ


def app_root():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[1]


def resource_path(relative_path):
    base = Path(getattr(sys, "_MEIPASS", app_root()))
    return base / relative_path


def user_data_dir():
    if getattr(sys, "frozen", False):
        base = environ.get("LOCALAPPDATA") or environ.get("APPDATA")
        if base:
            path = Path(base) / "SistemaIAAS"
        else:
            path = Path.home() / "SistemaIAAS"
    else:
        path = app_root()
    path.mkdir(parents=True, exist_ok=True)
    return path


def writable_path(relative_path):
    path = user_data_dir() / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    return path
