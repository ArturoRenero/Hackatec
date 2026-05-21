# server.py
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

from validador_verificamex import validar_ine, validar_curp
from ocr_curp import extraer_curps_archivo

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)


# ── Sirve el frontend ─────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory("templates", "index.html")


# ── Endpoint: Validar INE ─────────────────────────────────────────────────────

@app.route("/api/validar-ine", methods=["POST"])
def api_validar_ine():
    frente = request.files.get("frente")
    reverso = request.files.get("reverso")

    if not frente:
        return jsonify({
            "error": True,
            "mensaje": "Se requiere al menos la imagen del frente de la INE."
        }), 400

    tmp_dir = "documentos"
    os.makedirs(tmp_dir, exist_ok=True)

    ruta_frente = os.path.join(tmp_dir, "frente" + os.path.splitext(frente.filename)[1])
    ruta_reverso = os.path.join(
        tmp_dir,
        "reverso" + os.path.splitext(reverso.filename if reverso else frente.filename)[1]
    )

    frente.save(ruta_frente)

    if reverso:
        reverso.save(ruta_reverso)
    else:
        import shutil
        shutil.copy(ruta_frente, ruta_reverso)

    try:
        resultado = validar_ine(ruta_frente, ruta_reverso)

    except (FileNotFoundError, ValueError) as e:
        return jsonify({"error": True, "mensaje": str(e)}), 400

    except Exception as e:
        return jsonify({"error": True, "mensaje": f"Error inesperado: {str(e)}"}), 500

    finally:
        for p in [ruta_frente, ruta_reverso]:
            try:
                os.remove(p)
            except OSError:
                pass

    status_code = resultado.get("status_code", 200)
    return jsonify(resultado), (200 if not resultado.get("error") else status_code)


# ── Endpoint: Validar CURP escrita ────────────────────────────────────────────

@app.route("/api/validar-curp", methods=["POST"])
def api_validar_curp():
    body = request.get_json(silent=True) or {}
    curp = body.get("curp", "").strip().upper()

    if not curp:
        return jsonify({
            "error": True,
            "mensaje": "Se requiere el campo 'curp'."
        }), 400

    if len(curp) != 18:
        return jsonify({
            "error": True,
            "mensaje": f"La CURP debe tener 18 caracteres (recibidos: {len(curp)})."
        }), 400

    try:
        resultado = validar_curp(curp)

    except Exception as e:
        return jsonify({
            "error": True,
            "mensaje": f"Error inesperado: {str(e)}"
        }), 500

    status_code = resultado.get("status_code", 200)
    return jsonify(resultado), (200 if not resultado.get("error") else status_code)


# ── Endpoint: Extraer CURP desde PDF o imagen con OCR ─────────────────────────

@app.route("/api/extraer-curp", methods=["POST"])
def api_extraer_curp():
    archivo = request.files.get("archivo")

    if not archivo:
        return jsonify({
            "error": True,
            "mensaje": "No se recibió ningún archivo."
        }), 400

    tmp_dir = "documentos"
    os.makedirs(tmp_dir, exist_ok=True)

    extension = os.path.splitext(archivo.filename)[1].lower()
    ruta_archivo = os.path.join(tmp_dir, "archivo_extraer" + extension)

    archivo.save(ruta_archivo)

    try:
        resultado = extraer_curps_archivo(ruta_archivo)

        print("========== TEXTO EXTRAÍDO ==========")
        print(resultado["texto_raw"])
        print("========== CURPS ENCONTRADAS ==========")
        print(resultado["curps"])

        return jsonify({
            "error": False,
            "curps": resultado["curps"],
            "texto_raw": resultado["texto_raw"]
        })

    except Exception as e:
        return jsonify({
            "error": True,
            "mensaje": "Error al extraer la CURP del archivo.",
            "detalle": str(e)
        }), 500

    finally:
        try:
            os.remove(ruta_archivo)
        except OSError:
            pass


# ── Arranque ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("🟢 Servidor Verificamex corriendo en http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)