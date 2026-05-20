import os
import json
import requests
from config import ACCESS_TOKEN, API_URL, TIMEOUT


def validar_archivo_existe(ruta):
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"No se encontró el archivo: {ruta}")

    extensiones_validas = [".jpg", ".jpeg", ".png", ".pdf"]
    extension = os.path.splitext(ruta)[1].lower()

    if extension not in extensiones_validas:
        raise ValueError(
            f"Formato no permitido: {extension}. Usa JPG, JPEG, PNG o PDF."
        )


def imprimir_json(data):
    print(json.dumps(data, indent=4, ensure_ascii=False))


def validar_ine_curp(ruta_frente, ruta_reverso):
    validar_archivo_existe(ruta_frente)
    validar_archivo_existe(ruta_reverso)

    if ACCESS_TOKEN == "PEGA_AQUI_TU_ACCESS_TOKEN_NUEVO":
        raise ValueError("Falta configurar tu ACCESS_TOKEN en config.py")

    if API_URL == "PEGA_AQUI_LA_URL_DEL_ENDPOINT":
        raise ValueError("Falta configurar tu API_URL en config.py")

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Accept": "application/json"
    }

    payload = {
        "model": "ine"
    }

    with open(ruta_frente, "rb") as frente, open(ruta_reverso, "rb") as reverso:
        files = {
            "ine_front": ("ine_frente.jpg", frente, "image/jpeg"),
            "ine_back": ("ine_reverso.jpg", reverso, "image/jpeg")
        }

        response = requests.post(
            API_URL,
            headers=headers,
            data=payload,
            files=files,
            timeout=TIMEOUT
        )

        response = requests.post(
            API_URL,
            headers=headers,
            data=payload,
            files=files,
            timeout=TIMEOUT
        )

    if response.status_code not in [200, 201]:
        return {
            "error": True,
            "status_code": response.status_code,
            "mensaje": "La API respondió con error.",
            "detalle": response.text
        }

    try:
        data = response.json()
    except ValueError:
        return {
            "error": True,
            "status_code": response.status_code,
            "mensaje": "La API no devolvió un JSON válido.",
            "detalle": response.text
        }

    return {
        "error": False,
        "status_code": response.status_code,
        "respuesta_original": data
    }