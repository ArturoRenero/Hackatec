# ocr_curp.py
import os
import re
import fitz  # PyMuPDF
import pytesseract
from PIL import Image

# Ruta de Tesseract en Windows
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

CURP_RE = re.compile(
    r"[A-Z]{4}\d{6}[HM][A-Z]{2}[A-Z]{3}[A-Z0-9]\d",
    re.IGNORECASE
)


def extraer_curps_de_texto(texto):
    if not texto:
        return []

    texto = texto.upper()

    # Limpieza básica
    texto_limpio = texto.replace("\n", " ")
    texto_limpio = re.sub(r"\s+", " ", texto_limpio)

    curps = []

    # Caso normal: CONJ060921HJCNVSA9
    encontrados = CURP_RE.findall(texto_limpio)
    curps.extend(encontrados)

    # Caso del PDF oficial: Clave: CONJ060921HJCNVSA9
    claves = re.findall(
        r"CLAVE[:\s]*([A-Z0-9\s]{18,45})",
        texto_limpio,
        re.IGNORECASE
    )

    for bloque in claves:
        candidato = re.sub(r"[^A-Z0-9]", "", bloque.upper())
        match = CURP_RE.search(candidato)
        if match:
            curps.append(match.group())

    # Caso donde OCR separa letras: C O N J 0 6 0 9...
    texto_sin_espacios = re.sub(r"[^A-Z0-9]", "", texto.upper())
    encontrados_sin_espacios = CURP_RE.findall(texto_sin_espacios)
    curps.extend(encontrados_sin_espacios)

    # Quitar duplicados
    curps_unicas = list(set([c.upper() for c in curps]))

    return curps_unicas


def extraer_texto_pdf(ruta_pdf):
    texto_total = ""

    documento = fitz.open(ruta_pdf)

    for num_pagina in range(len(documento)):
        pagina = documento[num_pagina]

        # Primero intenta extraer texto normal del PDF
        texto = pagina.get_text()
        texto_total += "\n" + texto

        # Luego aplica OCR por si el PDF es imagen escaneada
        pix = pagina.get_pixmap(matrix=fitz.Matrix(3, 3))
        imagen_path = f"temp_pagina_{num_pagina}.png"
        pix.save(imagen_path)

        imagen = Image.open(imagen_path)
        texto_ocr = pytesseract.image_to_string(imagen, lang="spa")
        texto_total += "\n" + texto_ocr

        try:
            os.remove(imagen_path)
        except OSError:
            pass

    documento.close()

    return texto_total


def extraer_texto_imagen(ruta_imagen):
    imagen = Image.open(ruta_imagen)
    texto = pytesseract.image_to_string(imagen, lang="spa")
    return texto


def extraer_curps_archivo(ruta_archivo):
    extension = os.path.splitext(ruta_archivo)[1].lower()

    if extension == ".pdf":
        texto = extraer_texto_pdf(ruta_archivo)

    elif extension in [".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"]:
        texto = extraer_texto_imagen(ruta_archivo)

    else:
        raise ValueError("Formato no soportado. Usa PDF, JPG, JPEG, PNG, WEBP, BMP o TIFF.")

    curps = extraer_curps_de_texto(texto)

    return {
        "curps": curps,
        "texto_raw": texto
    }