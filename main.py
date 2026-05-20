# main.py

from validador_verificamex import validar_ine_curp, imprimir_json


def main():
    print("====================================")
    print("VALIDADOR DE INE + CURP")
    print("Usando API de Verificamex")
    print("====================================")

    ruta_frente = input("Ruta de la imagen frontal de la INE: ")
    ruta_reverso = input("Ruta de la imagen trasera de la INE: ")

    try:
        resultado = validar_ine_curp(ruta_frente, ruta_reverso)

        print("\n========== RESULTADO RESUMIDO ==========")

        if resultado.get("error"):
            print("Error al validar.")
            print("Código:", resultado.get("status_code"))
            print("Mensaje:", resultado.get("mensaje"))
            print("Detalle:", resultado.get("detalle"))
            return

        interpretacion = resultado["interpretacion"]

        print("Validación general:", interpretacion["valida_general"])
        print("INE válida:", interpretacion["ine_valida"])
        print("CURP válida:", interpretacion["curp_valida"])
        print("OCR correcto:", interpretacion["ocr_correcto"])
        print("Mensaje:", interpretacion["mensaje"])

        print("\n========== DATOS EXTRAÍDOS ==========")
        imprimir_json(interpretacion["datos_extraidos"])

        print("\n========== RESPUESTA ORIGINAL DE LA API ==========")
        imprimir_json(resultado["respuesta_original"])

    except FileNotFoundError as e:
        print("Error de archivo:", e)

    except ValueError as e:
        print("Error de configuración:", e)

    except Exception as e:
        print("Error inesperado:", e)


if __name__ == "__main__":
    main()