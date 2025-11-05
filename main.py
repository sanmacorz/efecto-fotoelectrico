#!/usr/bin/env python3
import argparse
import sys
import ctypes
from src import simulador


# Abrir consola antes de cualquier input() si se solicitó modo CLI
def asegurar_consola(modo):
    if modo != "cli":
        return

    if sys.platform != "win32" or not getattr(sys, "frozen", False):
        return

    kernel32 = ctypes.windll.kernel32
    ATTACH_PARENT_PROCESS = -1
    attached = False
    try:
        attached = bool(kernel32.AttachConsole(ATTACH_PARENT_PROCESS))
    except Exception:
        attached = False

    if not attached and not bool(kernel32.AllocConsole()):
        return

    # Ahora reabrimos los streams en modo texto (NO 'wb'/'rb')
    try:
        sys.stdin = open("CONIN$", "r", encoding="utf-8", buffering=1)
    except Exception:
        pass
    try:
        sys.stdout = open("CONOUT$", "w", encoding="utf-8", buffering=1)
    except Exception:
        pass
    try:
        sys.stderr = open("CONOUT$", "w", encoding="utf-8", buffering=1)
    except Exception:
        pass

    try:
        kernel32.SetConsoleTitleW("SimuladorFotoelectrico - CLI")
    except Exception:
        pass


# Modo CLI (sin interfaz gráfica)
def modo_cli(parsed_args):
    try:
        if sys.stdin is None or sys.stdin.closed:
            print(
                "No hay consola disponible; para usar la interfaz gráfica ejecute sin --modo o con --modo gui."
            )
            return
    except Exception:
        print("No hay consola disponible; abortando modo CLI.")
        return

    print("---BIENVENIDO AL SIMULADOR DE EFECTO FOTOELÉCTRICO---")

    # Intentar usar argumentos pasados, si no pedirlos otra vez
    if parsed_args.longitud_onda_nm is not None:
        long_onda = parsed_args.longitud_onda_nm
    else:
        long_onda = simulador.obtener_lon_onda()

    if parsed_args.intensidad is not None:
        porcen_inten = parsed_args.intensidad / 100.0
    else:
        porcen_inten = simulador.obtener_intensidad()  # ya devuelve fracción

    elemen_dic = simulador.cargar_elementos()
    material = simulador.elegir_elemento(elemen_dic)
    trabajo = material["phi_eV"]

    print(f"Ha seleccionado: {material['nombre']} ({material['simbolo']})\n")

    ef = simulador.convertir_energia(long_onda)
    print(f"Fotón: {ef:.2f} eV | Umbral: {trabajo} eV")

    if ef > trabajo:
        k = ef - trabajo
        print("¡Hay emisión de electrones!")
        print(f"Energía cinética: {k:.2f} eV")
        fr = simulador.obtener_corriente(porcen_inten, k)
        if fr is not None:
            print(f"Corriente estimada (fracción 0..1): {fr:.4f}")
        else:
            print("Corriente estimada: Indeterminada (división por cero)")
    else:
        print("¡No hay emisión de electrones!")

    # Esperar a que el usuario confirme antes de cerrar la consola
    try:
        input("\nPresione Enter para salir...")
    except Exception:
        pass


# Modo GUI (con interfaz gráfica)
def modo_gui():
    # Importar la interfaz aquí (lazy import) para no crear ventana al importar main
    try:
        import interfaz
    except Exception as e:
        print("No se encontró 'interfaz.py' o falló al importarlo:", e)
        sys.exit(1)

    # Ejecutar la GUI. tu interfaz debe exponer run() o ejecutar()
    if hasattr(interfaz, "run"):
        interfaz.run()
    elif hasattr(interfaz, "ejecutar"):
        interfaz.ejecutar()
    else:
        raise RuntimeError(
            "El módulo 'interfaz' no define run() ni ejecutar().\n"
            "Por favor, agregue una función 'run()' o 'ejecutar()' en 'interfaz.py' que inicie la interfaz gráfica.\n"
            "Ejemplo:\n"
            "def run():\n"
            "    # Código para iniciar la GUI\n"
            "    pass\n"
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--modo", choices=["cli", "gui"], default="gui")
    parser.add_argument(
        "--longitud-onda",
        "--longitud-onda-nm",
        dest="longitud_onda_nm",
        type=float,
        help="Longitud de onda (nm)",
    )
    parser.add_argument("--intensidad", type=float, help="Intensidad en % (0-100)")

    args = parser.parse_args()

    # Abrir consola antes de cualquier input() si se solicitó modo CLI
    asegurar_consola(args.modo)

    if args.modo == "cli":
        modo_cli(args)
    else:
        modo_gui()


if __name__ == "__main__":
    main()
