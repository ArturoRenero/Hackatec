# mock_server.py  — corre esto con: python mock_server.py
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

RESPONSES = {
    "/identity/v1/validations/basic": {
        "data": {
            "object": "ine_validations",
            "status": True,
            "message": "Documento válido [MOCK]",
            "documentInformation": {
                "documentData": [
                    {"type": "FullName",       "name": "Nombre Completo",    "value": "RENERO LOPEZ ARTURO",     "source": "OCR"},
                    {"type": "FatherSurname",  "name": "Apellido Paterno",   "value": "RENERO",                  "source": "OCR"},
                    {"type": "MotherSurname",  "name": "Apellido Materno",   "value": "LOPEZ",                   "source": "OCR"},
                    {"type": "Name",           "name": "Nombre",             "value": "ARTURO",                  "source": "OCR"},
                    {"type": "DateOfBirth",    "name": "Fecha de Nacimiento","value": "21/05/2004",              "source": "OCR"},
                    {"type": "DateOfExpiry",   "name": "Fecha de Expiración","value": "31/12/2032",              "source": "OCR"},
                    {"type": "Sex",            "name": "Sexo",               "value": "M",                       "source": "OCR"},
                    {"type": "PersonalNumber", "name": "CURP",               "value": "RELA040521HMNNPRA5",      "source": "OCR"},
                    {"type": "Voter_Key",      "name": "Clave de Elector",   "value": "RNLPAR04052116H000",      "source": "OCR"},
                    {"type": "PermanentAddress","name": "Dirección",         "value": "C ISLA COZUMEL 9 FRACC ARVENTO 45670 TLAJOMULCO DE ZUNIGA JAL", "source": "OCR"},
                ]
            },
            "ineNominalList": {
                "status": True,
                "message": "Credencial vigente [MOCK]"
            }
        },
        "meta": {"include": [], "custom": []}
    },
    "/identity/v1/scraping/renapo": {
        "data": {
            "object": "citizeninformations",
            "citizen": {
                "mensaje": "Búsqueda exitosa por curp [MOCK]",
                "codigo": 0,
                "status": True,
                "registros": [{
                    "curp":            "RELA040521HMNNPRA5",
                    "nombres":         "ARTURO",
                    "primerApellido":  "RENERO",
                    "segundoApellido": "LOPEZ",
                    "sexo":            "Hombre",
                    "fechaNacimiento": "2004-05-21",
                    "nacionalidad":    "MEX",
                    "entidad":         "Jalisco",
                    "claveEntidad":    "JAL",
                    "statusCurp":      "RCN"
                }]
            }
        },
        "meta": {"include": [], "custom": []}
    }
}

class MockHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        path = self.path.split("?")[0]
        body = RESPONSES.get(path, {"error": "endpoint no encontrado en mock"})
        response = json.dumps(body).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def log_message(self, format, *args):
        print(f"[MOCK] {self.path} → {args[1]}")

if __name__ == "__main__":
    server = HTTPServer(("localhost", 8080), MockHandler)
    print("Mock server corriendo en http://localhost:8080")
    print("Presiona Ctrl+C para detener\n")
    server.serve_forever()