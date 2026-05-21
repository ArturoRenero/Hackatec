# validador_verificamex.py
import os
import json
import base64
import requests
from config import ACCESS_TOKEN, API_URL_INE, API_URL_CURP, TIMEOUT


def validar_archivo_existe(ruta):
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"No se encontró el archivo: {ruta}")
    extensiones_validas = [".jpg", ".jpeg", ".png", ".pdf"]
    extension = os.path.splitext(ruta)[1].lower()
    if extension not in extensiones_validas:
        raise ValueError(f"Formato no permitido: {extension}. Usa JPG, JPEG, PNG o PDF.")


def imagen_a_base64(ruta):
    extension = os.path.splitext(ruta)[1].lower().replace(".", "")
    mime = "jpeg" if extension in ("jpg", "jpeg") else extension  # png, pdf, etc.
    with open(ruta, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:image/{mime};base64,{b64}"


def imprimir_json(data):
    print(json.dumps(data, indent=4, ensure_ascii=False))


def headers():
    return {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }


def validar_ine(ruta_frente, ruta_reverso):
    """Validación completa de INE con OCR + Lista Nominal + RENAPO."""
    validar_archivo_existe(ruta_frente)
    validar_archivo_existe(ruta_reverso)

    payload = {
        "ine_front": imagen_a_base64(ruta_frente),
        "ine_back":  imagen_a_base64(ruta_reverso),
        "model":     "D"   # "D" = detección automática del modelo de INE
    }

    response = requests.post(API_URL_INE, headers=headers(), json=payload, timeout=TIMEOUT)

    if response.status_code not in [200, 201]:
        return {
            "error": True,
            "status_code": response.status_code,
            "mensaje": "La API de INE respondió con error.",
            "detalle": response.text
        }

    data = response.json().get("data", {})

    # Extraer campos legibles del documentInformation
    datos_extraidos = {}
    for campo in data.get("documentInformation", {}).get("documentData", []):
        tipo = campo.get("type")
        valor = campo.get("value")
        fuente = campo.get("source")
        # Preferir fuente OCR sobre MRZ si hay duplicados
        if tipo not in datos_extraidos or fuente == "OCR":
            datos_extraidos[tipo] = valor

    return {
        "error": False,
        "status_code": response.status_code,
        "interpretacion": {
            "valida_general": data.get("status", False),
            "mensaje":        data.get("message", "Sin mensaje"),
            "lista_nominal":  data.get("ineNominalList", {}).get("status", False),
            "datos_extraidos": datos_extraidos
        },
        "respuesta_original": response.json()
    }


def validar_curp(curp):
    """Valida una CURP directamente ante RENAPO."""
    payload = {"curp": curp}

    response = requests.post(API_URL_CURP, headers=headers(), json=payload, timeout=TIMEOUT)

    if response.status_code not in [200, 201]:
        return {
            "error": True,
            "status_code": response.status_code,
            "mensaje": "La API de CURP respondió con error.",
            "detalle": response.text
        }

    data = response.json()
    citizen = data.get("data", {}).get("citizen", {})
    registros = citizen.get("registros", [])
    registro = registros[0] if registros else {}

    return {
        "error": False,
        "status_code": response.status_code,
        "interpretacion": {
            "valida": citizen.get("status", False),
            "mensaje": citizen.get("mensaje", "Sin mensaje"),
            "nombre":  f"{registro.get('nombres','')} {registro.get('primerApellido','')} {registro.get('segundoApellido','')}".strip(),
            "sexo":    registro.get("sexo", ""),
            "fecha_nacimiento": registro.get("fechaNacimiento", ""),
            "entidad": registro.get("entidad", ""),
            "status_curp": registro.get("statusCurp", "")
        },
        "respuesta_original": data
    }