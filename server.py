# server.py
import os
import tempfile
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from validador_verificamex import validar_ine, validar_curp

app = Flask(__name__, static_folder=".")
CORS(app)  # permite peticiones desde el mismo origen o distinto puerto


# ── Sirve el index.html ──────────────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory(".", "index.html")


# ── Endpoint INE ─────────────────────────────────────────────────────────────
@app.route("/api/validar-ine", methods=["POST"])
def api_validar_ine():
    frente  = request.files.get("frente")
    reverso = request.files.get("reverso")

    if not frente or not reverso:
        return jsonify({"error": True, "mensaje": "Se requieren ambas imágenes (frente y reverso)."}), 400

    ext_f = os.path.splitext(frente.filename)[1] or ".jpg"
    ext_r = os.path.splitext(reverso.filename)[1] or ".jpg"

    tf = tempfile.NamedTemporaryFile(delete=False, suffix=ext_f)
    tb = tempfile.NamedTemporaryFile(delete=False, suffix=ext_r)
    try:
        frente.save(tf.name);  tf.close()
        reverso.save(tb.name); tb.close()
        resultado = validar_ine(tf.name, tb.name)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"error": True, "mensaje": str(e)}), 500
    finally:
        os.unlink(tf.name)
        os.unlink(tb.name)


# ── Endpoint CURP ────────────────────────────────────────────────────────────
@app.route("/api/validar-curp", methods=["POST"])
def api_validar_curp():
    data = request.get_json(silent=True) or {}
    curp = data.get("curp", "").strip().upper()

    if not curp:
        return jsonify({"error": True, "mensaje": "El campo 'curp' es requerido."}), 400

    try:
        resultado = validar_curp(curp)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"error": True, "mensaje": str(e)}), 500


# ── Arranque ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Servidor Verificamex corriendo en http://127.0.0.1:5500")
    app.run(debug=True, port=5500)