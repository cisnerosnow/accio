#!/usr/bin/env python3
"""
Descarga todos los documentos de https://cdn.preterhuman.net/texts/religion.occult.new_age/
y extrae automáticamente los ZIP encontrados.

▶ Cómo usar
    1. Crea un entorno:  python -m venv venv && source venv/bin/activate
    2. Instala dependencias:  pip install requests tqdm beautifulsoup4
    3. Ejecuta:  python fetch_preterhuman.py
"""

import os
import re
import sys
import zipfile
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

BASE_URL   = "https://cdn.preterhuman.net/texts/religion.occult.new_age/Rosicrucian/"
DEST_DIR   = Path("rosicrucian").resolve()
# extensiones que consideraremos “texto” (añade o quita a tu gusto)
TEXT_LIKE  = {".pdf"}#, ".txt", ".rtf", ".doc", ".docx", ".html", ".htm", ".odt",".epub", ".mobi", ".djvu", ".zip"}                  

session = requests.Session()           # re-usa conexión TCP


def is_directory(href: str) -> bool:
    """Detecta si el enlace del listing es una sub-carpeta."""
    return href.endswith("/")


def list_links(url: str) -> list[str]:
    """Devuelve todos los href visibles en un listing tipo Apache/NGINX."""
    resp = session.get(url, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    return [a.get("href") for a in soup.find_all("a", href=True) if a.get("href") not in ("../", "./")]


def download_file(file_url: str, dest_folder: Path) -> Path:
    """Descarga el archivo remoto con barra de progreso adaptativa."""
    local_name = dest_folder / Path(urlparse(file_url).path).name
    if local_name.exists():                                                # evita duplicados
        return local_name

    with session.get(file_url, stream=True, timeout=60) as r:
        r.raise_for_status()
        total = int(r.headers.get("Content-Length", 0))
        with tqdm(total=total, unit="B", unit_scale=True,
                  desc=local_name.name, ascii=True) as bar, \
             open(local_name, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
                bar.update(len(chunk))
    return local_name


def unzip(path: Path):
    """Extrae un .zip junto a su fuente y borra el comprimido (opcional)."""
    try:
        with zipfile.ZipFile(path) as zf:
            zf.extractall(path.parent)
        # path.unlink()   #  ← descomenta para borrar el .zip tras extraer
    except zipfile.BadZipFile:
        print(f"⚠️  Archivo ZIP corrupto: {path.name}")


def crawl_and_fetch(url: str, dest: Path):
    """Recorre recursivamente el árbol de carpetas y descarga lo que coincida."""
    for href in list_links(url):
        full_url = urljoin(url, href)
        if is_directory(href):
            crawl_and_fetch(full_url, dest)                # recursion
        else:
            ext = Path(href).suffix.lower()
            if not ext or ext not in TEXT_LIKE:
                continue                                   # ignora binarios raros
            dest.mkdir(parents=True, exist_ok=True)
            local_path = download_file(full_url, dest)
            if local_path.suffix.lower() == ".zip":
                unzip(local_path)


if __name__ == "__main__":
    try:
        crawl_and_fetch(BASE_URL, DEST_DIR)
        print("\n✅ Descarga completa. Archivos guardados en:", DEST_DIR)
    except KeyboardInterrupt:
        sys.exit("\n⏹️  Interrumpido por el usuario.")
