#!/usr/bin/env python3
import argparse
import sys
from src import simulador


# Modo CLI (sin interfaz gráfica)
def modo_cli():
    print("---BIENVENIDO AL SIMULADOR DE EFECTO FOTOELÉCTRICO---")
    porcen_inten = simulador.obtener_intensidad()
    long_onda = simulador.obtener_lon_onda()
    elemen_dic = simulador.cargar_elementos()
    material = simulador.elegir_elemento(elemen_dic)
    trabajo = material["phi_eV"]

    print(f"Ha seleccionado: {material['nombre']} ({material['simbolo']})\n")

    ef = simulador.convertir_energia(long_onda)
    print(f"Fotón: {ef:.2f} eV " + "|" + f" Umbral: {trabajo} eV")

    if ef > trabajo:
        k = ef - trabajo
        print("¡Hay emisión de electrones!")
        print(f"Energía cinética: {k:.2f} eV")
        fr = simulador.obtener_corriente(porcen_inten, k)
        if fr is not None:
            print(f"Corriente estimada: {fr:.4f}")
        else:
            print("Corriente estimada: Indeterminada (división por cero)")
    else:
        print("¡No hay emisión de electrones!")


# Modo GUI (con interfaz gráfica)
def modo_gui():
    try:
        import interfaz
    except Exception as e:
        print("No se encontró 'interfaz.py' o falló al importarlo:", e)
        sys.exit(1)
    interfaz.ejecutar()


def main():
    # Se definen los argumentos de línea de comandos
    parser = argparse.ArgumentParser()
    parser.add_argument("--modo", choices=["cli", "gui"], default="cli")
    args = parser.parse_args()

    if args.modo == "cli":
        modo_cli()
    elif args.modo == "gui":
        modo_gui()


if __name__ == "__main__":
    main()
