#!/usr/bin/env python
import os
import json
import sys


def obtener_intensidad():
    while True:
        try:
            val = float(input("Ingrese la intensidad porcentual de la luz (0-100): "))
            if 0 <= val <= 100:
                return val / 100.0
            print("Por favor ingrese un valor entre 0 y 100.")
        except ValueError:
            print("Entrada inválida. Ingrese un número.")


def obtener_lon_onda():
    while True:
        try:
            long_onda = int(input("Ingrese la longitud de onda (en nm): "))
            if long_onda > 0:
                return long_onda
            print("Por favor ingrese un número entero positivo mayor a 0.")
        except ValueError:
            print("Entrada inválida. Ingrese un número entero positivo.")


def cargar_elementos():
    path = os.path.join(os.path.dirname(__file__), "elementos.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: El archivo '{path}' no se encuentra. Verifique su existencia.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(
            f"Error: El archivo '{path}' está mal formado. Verifique el formato JSON."
        )
        sys.exit(1)


def elegir_elemento(elemen_dic):
    elemen = []
    for simbolo, datos in elemen_dic.items():
        entrada = dict(datos)
        entrada["simbolo"] = simbolo
        elemen.append(entrada)

    print("Seleccione el material del que desea obtener el trabajo de salida: ")
    for i, elemento in enumerate(elemen):
        print(f"{i + 1}. {elemento['nombre']} ({elemento['simbolo']})")

    while True:
        try:
            opcion = int(input("Ingrese el número correspondiente al material: "))
            if 1 <= opcion <= len(elemen):
                return elemen[opcion - 1]
            print(f"Por favor ingrese un número entre 1 y {len(elemen)}.")
        except ValueError:
            print(f"Por favor ingrese un número entre 1 y {len(elemen)}.")


def convertir_energia(long_onda_nm):
    """Convierte longitud de onda (nm) a eV"""
    return 1240.0 / long_onda_nm


def obtener_corriente(porcen_inten, k):
    divisor = k + 0.5
    if divisor == 0:
        return None
    return porcen_inten * k / divisor


# Ejecuta el modo CLI por defecto
def main():
    print("---BIENVENIDO AL SIMULADOR DE EFECTO FOTOELÉCTRICO---")
    porcen_inten = obtener_intensidad()
    long_onda = obtener_lon_onda()
    elemen_dic = cargar_elementos()
    material = elegir_elemento(elemen_dic)
    trabajo = material["phi_eV"]

    print(f"Ha seleccionado: {material['nombre']} ({material['simbolo']})\n")

    ef = convertir_energia(long_onda)
    print(f"Fotón: {ef:.2f} eV " + "|" + f" Umbral: {trabajo} eV")

    if ef > trabajo:
        k = ef - trabajo
        print("¡Hay emisión de electrones!")
        print(f"Energía cinética: {k:.2f} eV")
        corriente = obtener_corriente(porcen_inten, k)
        if corriente is not None:
            print(f"Corriente estimada: {corriente:.4f}")
        else:
            print("Corriente estimada: Indeterminada (división por cero)")
    else:
        print("¡No hay emisión de electrones!")


if __name__ == "__main__":
    main()
