# server.py
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

from validador_verificamex import validar_ine, validar_curp

app = Flask(__name__, static_folder=".")
CORS(app)

# ── Sirve el frontend ─────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(".", "index.html")


# ── Endpoint: Validar INE ─────────────────────────────────────────────────────

@app.route("/api/validar-ine", methods=["POST"])
def api_validar_ine():
    frente  = request.files.get("frente")
    reverso = request.files.get("reverso")

    if not frente:
        return jsonify({"error": True, "mensaje": "Se requiere al menos la imagen del frente de la INE."}), 400

    # Guardar temporalmente los archivos recibidos
    tmp_dir = "/tmp/verificamex"
    os.makedirs(tmp_dir, exist_ok=True)

    ruta_frente  = os.path.join(tmp_dir, "frente"  + os.path.splitext(frente.filename)[1])
    ruta_reverso = os.path.join(tmp_dir, "reverso" + os.path.splitext(reverso.filename if reverso else frente.filename)[1])

    frente.save(ruta_frente)
    if reverso:
        reverso.save(ruta_reverso)
    else:
        # Si no hay reverso, duplica el frente (la función lo requiere)
        import shutil
        shutil.copy(ruta_frente, ruta_reverso)

    try:
        resultado = validar_ine(ruta_frente, ruta_reverso)
    except (FileNotFoundError, ValueError) as e:
        return jsonify({"error": True, "mensaje": str(e)}), 400
    except Exception as e:
        return jsonify({"error": True, "mensaje": f"Error inesperado: {str(e)}"}), 500
    finally:
        # Limpia archivos temporales
        for p in [ruta_frente, ruta_reverso]:
            try:
                os.remove(p)
            except OSError:
                pass

    status_code = resultado.get("status_code", 200)
    return jsonify(resultado), (200 if not resultado.get("error") else status_code)


# ── Endpoint: Validar CURP ────────────────────────────────────────────────────

@app.route("/api/validar-curp", methods=["POST"])
def api_validar_curp():
    body = request.get_json(silent=True) or {}
    curp = body.get("curp", "").strip().upper()

    if not curp:
        return jsonify({"error": True, "mensaje": "Se requiere el campo 'curp'."}), 400

    if len(curp) != 18:
        return jsonify({"error": True, "mensaje": f"La CURP debe tener 18 caracteres (recibidos: {len(curp)})."}), 400

    try:
        resultado = validar_curp(curp)
    except Exception as e:
        return jsonify({"error": True, "mensaje": f"Error inesperado: {str(e)}"}), 500

    status_code = resultado.get("status_code", 200)
    return jsonify(resultado), (200 if not resultado.get("error") else status_code)


# ── Arranque ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("🟢  Servidor Verificamex corriendo en http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
