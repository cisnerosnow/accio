# accio

Pipeline para armar un corpus de textos esotéricos: descarga libros del archivo
público de [preterhuman.net](https://cdn.preterhuman.net/texts/religion.occult.new_age/),
descarta los escaneos sin texto y los vuelca a `.txt`.

## Flujo

```
accio.py  →  merge_textual_pdfs.py  →  pdf_a_txt.py
descargar    filtrar + fusionar        extraer texto
```

## Uso

```bash
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install requests tqdm beautifulsoup4 pdfminer.six pypdf PyPDF2

# 1. Descargar una colección (editar BASE_URL y DEST_DIR en el script)
python accio.py

# 2. Filtrar los PDFs con texto seleccionable y fusionarlos en uno
python merge_textual_pdfs.py alchemy fusionado-alchemy.pdf -r

# 3. Volcar a texto plano (editar pdf_path y txt_path al final del script)
python pdf_a_txt.py
```

## Scripts

- **`accio.py`** — recorre recursivamente el listing de directorios remoto y
  baja todo lo que coincida con `TEXT_LIKE` (por defecto solo `.pdf`),
  descomprimiendo los ZIP. `BASE_URL` y `DEST_DIR` se cambian a mano por colección.
- **`merge_textual_pdfs.py`** — comprueba con pdfminer que las primeras 5 páginas
  de cada PDF tengan al menos N caracteres extraíbles (`-t`, default 100) y
  concatena los que pasan. `-r` para buscar en subcarpetas.
- **`pdf_a_txt.py`** — extrae el texto del PDF fusionado con marcadores
  `--- Página N ---`. Rutas hardcodeadas al final del archivo.

Las colecciones descargadas y las salidas quedan fuera de git (ver `.gitignore`):
son cientos de MB y se regeneran ejecutando el pipeline.
