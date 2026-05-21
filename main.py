# main.py
from validador_verificamex import validar_ine, validar_curp, imprimir_json  # ← corregido


def main():
    print("====================================")
    print("  VALIDADOR DE INE + CURP")
    print("  Usando API de Verificamex")
    print("====================================")

    modo = input("\n¿Qué deseas validar? [1] INE  [2] CURP  [3] Ambos: ").strip()

    if modo in ("1", "3"):
        print("\n--- Validación de INE ---")
        ruta_frente  = input("Ruta de la imagen frontal de la INE: ").strip()
        ruta_reverso = input("Ruta de la imagen trasera de la INE: ").strip()

        try:
            resultado = validar_ine(ruta_frente, ruta_reverso)
            if resultado.get("error"):
                print("\n❌ Error al validar INE.")
                print("Código:", resultado["status_code"])
                print("Detalle:", resultado["detalle"])
            else:
                interp = resultado["interpretacion"]
                print("\n✅ INE procesada.")
                print("Válida en lista nominal:", interp["lista_nominal"])
                print("Mensaje:", interp["mensaje"])
                print("\n--- Datos extraídos ---")
                imprimir_json(interp["datos_extraidos"])
        except (FileNotFoundError, ValueError) as e:
            print("Error:", e)
        except requests.exceptions.ReadTimeout:
            print("\n⏱ Timeout: el servidor tardó demasiado. Intenta de nuevo en unos segundos.")

    if modo in ("2", "3"):
        print("\n--- Validación de CURP ---")
        curp = input("Ingresa la CURP a validar: ").strip().upper()

        try:
            resultado = validar_curp(curp)
            if resultado.get("error"):
                print("\n❌ Error al validar CURP.")
                print("Código:", resultado["status_code"])
                print("Detalle:", resultado["detalle"])
            else:
                interp = resultado["interpretacion"]
                print("\n✅ CURP consultada ante RENAPO.")
                print("Válida:", interp["valida"])
                print("Nombre:", interp["nombre"])
                print("Sexo:", interp["sexo"])
                print("Fecha de nacimiento:", interp["fecha_nacimiento"])
                print("Entidad:", interp["entidad"])
                print("Status CURP:", interp["status_curp"])
        except Exception as e:
            print("Error inesperado:", e)


if __name__ == "__main__":
    import requests  # para capturar ReadTimeout arriba
    main()