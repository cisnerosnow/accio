#!/usr/bin/env python3
"""
merge_textual_pdfs.py
---------------------

• Revisa todos los .pdf de una carpeta dada.
• Comprueba si cada PDF contiene al menos `min_chars` caracteres de texto
  seleccionable (por defecto: 100).
• Los que superan el umbral se añaden, página por página, a un PDF combinado.
• Al final guarda el resultado en `salida.pdf`.

USO BÁSICO
    python merge_textual_pdfs.py /ruta/a/carpeta  salida.pdf
OPCIONES
    -t / --threshold  <nº>   caracteres mínimos para considerar legible (100)
    -r / --recursive        busca PDFs también en subcarpetas
DEPENDENCIAS
    pip install pdfminer.six pypdf tqdm
"""

import argparse
from pathlib import Path

from pdfminer.high_level import extract_text
from pypdf import PdfReader, PdfWriter
from tqdm import tqdm


def has_selectable_text(pdf_path: Path, min_chars: int = 100) -> bool:
    """
    Devuelve True si el PDF contiene texto extraíble.  Usa solo las primeras
    5 páginas para acelerar el chequeo (casi siempre basta).
    """
    try:
        text = extract_text(str(pdf_path), maxpages=5)
    except Exception:
        # PDF corrupto o protegido → tratar como no legible
        return False
    return len(text.strip()) >= min_chars


def collect_candidates(folder: Path, recursive: bool, threshold: int):
    pattern = "**/*.pdf" if recursive else "*.pdf"
    pdfs = sorted(folder.glob(pattern))
    legibles = []
    for pdf in tqdm(pdfs, desc="Escaneando PDFs", ascii=True):
        if has_selectable_text(pdf, threshold):
            legibles.append(pdf)
    return legibles


def merge_pdfs(pdfs: list[Path], output_file: Path):
    writer = PdfWriter()
    for pdf in tqdm(pdfs, desc="Fusionando", ascii=True):
        reader = PdfReader(str(pdf))
        for page in reader.pages:
            writer.add_page(page)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("wb") as fh:
        writer.write(fh)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("carpeta", type=Path, help="carpeta con PDFs")
    ap.add_argument("salida", type=Path, help="nombre de PDF combinado")
    ap.add_argument("-t", "--threshold", type=int, default=100,
                    help="caracteres mínimos para marcar un PDF como legible")
    ap.add_argument("-r", "--recursive", action="store_true",
                    help="buscar también en subcarpetas")
    args = ap.parse_args()

    if not args.carpeta.exists():
        ap.error(f"La carpeta {args.carpeta} no existe")

    candidatos = collect_candidates(args.carpeta, args.recursive, args.threshold)

    if not candidatos:
        print("⚠️  No se encontró ningún PDF con texto seleccionable.")
        return

    merge_pdfs(candidatos, args.salida)
    print(f"\n✅ PDF combinado guardado en {args.salida} ({len(candidatos)} archivos incluidos).")


if __name__ == "__main__":
    main()
