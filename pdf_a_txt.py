import os
from PyPDF2 import PdfReader

def extraer_texto_pdf(ruta_pdf, ruta_txt):
    if not os.path.exists(ruta_pdf):
        print(f"El archivo {ruta_pdf} no existe.")
        return

    try:
        lector = PdfReader(ruta_pdf)
        texto_completo = ""

        for num_pagina, pagina in enumerate(lector.pages):
            texto = pagina.extract_text()
            if texto:
                texto_completo += f"\n\n--- Página {num_pagina + 1} ---\n\n"
                texto_completo += texto
            else:
                print(f"[Advertencia] No se pudo extraer texto de la página {num_pagina + 1}.")

        with open(ruta_txt, "w", encoding="utf-8") as archivo_txt:
            archivo_txt.write(texto_completo)

        print(f"Texto extraído correctamente en: {ruta_txt}")

    except Exception as e:
        print(f"Error al procesar el PDF: {e}")

# Ejemplo de uso
pdf_path = "rusicrucian.pdf"
txt_path = "salida-rusicrucian.txt"
extraer_texto_pdf(pdf_path, txt_path)
