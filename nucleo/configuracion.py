"""Capa 1 — Configuración: lo único que llega de afuera del código."""
import os
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

RAIZ = Path(__file__).resolve().parent.parent


def leer_database_url() -> str:
    url = os.environ.get("DATABASE_URL")

    if not url and (RAIZ / ".env").exists():
        for linea in (RAIZ / ".env").read_text(encoding="utf-8-sig").splitlines():
            if linea.strip().startswith("DATABASE_URL="):
                url = linea.split("=", 1)[1].strip().strip('"').strip("'")

    for nombre in ("cadena", "cadena.txt", "Docs/cadena"):
        archivo = RAIZ / nombre
        if not url and archivo.exists():
            url = archivo.read_text(encoding="utf-8-sig").strip()

    if not url:
        raise RuntimeError(f"No se encontró la URL de la base de datos. Busqué en: {RAIZ}")

    # asyncpg no entiende channel_binding: se quita de la URL
    partes = urlsplit(url)
    query = [(k, v) for k, v in parse_qsl(partes.query) if k != "channel_binding"]
    return urlunsplit(partes._replace(query=urlencode(query)))


class Configuracion:
    """Se lee una sola vez, al arrancar."""

    def __init__(self) -> None:
        self.base_datos: str = leer_database_url()
        self.nombre_app: str = "Productos"


CONFIGURACION = Configuracion()