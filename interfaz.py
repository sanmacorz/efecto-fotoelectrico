#!/usr/bin/env python
import customtkinter as ctk
from tkinter import ttk
from src import simulador
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import ctypes

# Constantes físicas
CARGA_E = 1.602176634e-19  # C
EV_A_J = 1.602176634e-19  # J / eV


def _corriente_a_amperios_local(fraccion, e_foton_ev, p_max_w=1e-3, qe=1.0):
    if fraccion <= 0:
        return 0.0
    e_photon_j = e_foton_ev * EV_A_J
    P = float(fraccion) * float(p_max_w)
    n_fot_s = P / e_photon_j
    I = n_fot_s * CARGA_E * float(qe)
    return I


def _convertir_energia_safe(lambda_nm):
    try:
        return simulador.convertir_energia(lambda_nm)
    except Exception:
        return 1240.0 / float(lambda_nm)


def _obtener_fraccion_safe(intensidad_frac, intensidad_pct, k):
    try:
        return simulador.obtener_corriente(intensidad_frac, k)
    except Exception:
        try:
            return simulador.obtener_corriente(intensidad_pct, k) / 100.0
        except Exception:
            return 0.0 if k <= 0 else intensidad_frac * (k / (k + 0.5))


def _obtener_corriente_amp(fr, e_foton):
    if hasattr(simulador, "corriente_a_amperios"):
        try:
            return simulador.corriente_a_amperios(fr, e_foton)
        except Exception:
            return _corriente_a_amperios_local(fr, e_foton)
    return _corriente_a_amperios_local(fr, e_foton)


def _actualizar_graficos(ax1, ax2, canvas, e_foton, phi, k, fr, i_amp):
    ax1.clear()
    labels = ["E_fotón", "Φ", "k"]
    values = [e_foton, phi, max(0.0, k)]
    bars = ax1.bar(labels, values)
    ax1.set_ylabel("Energía (eV)")
    ax1.set_title("Energías: fotón vs trabajo vs cinética")

    for rect, val in zip(bars, values):
        ax1.annotate(
            f"{val:.2f}",
            xy=(rect.get_x() + rect.get_width() / 2, val),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9,
        )
    ax2.clear()
    ax2.set_title("Corriente fotoeléctrica")
    ax2.bar(["Fracción (0.1)"], [fr])
    ax2.set_ylim(0, 1.0)
    ax2.set_ylabel("Fracción de corriente")
    ax2.annotate(
        f"{fr:.4f}",
        xy=(0, fr),
        xytext=(0, 6),
        textcoords="offset points",
        ha="center",
    )
    ax2.text(
        0.5,
        0.5,
        f"I ≈ {i_amp:.3e} A",
        transform=ax2.transAxes,
        ha="center",
        va="center",
        bbox={"boxstyle": "round", "alpha": 0.2},
    )
    canvas.draw_idle()


def _calcular_ui(
    lambda_slider, inten_slider, combo, elementos, info_text, ax1, ax2, canvas
):
    try:
        lambda_nm = int(lambda_slider.get())
    except Exception:
        info_text.configure(text="Longitud de onda inválida")
        return

    intensidad_pct = float(inten_slider.get())
    intensidad_frac = intensidad_pct / 100.0

    sel = combo.get()
    simbolo = sel.split(" - ")[0].strip()

    if simbolo not in elementos:
        info_text.configure(text="Elemento no válido")
        return

    elem = elementos[simbolo]
    phi = float(elem["phi_eV"])

    e_foton = _convertir_energia_safe(lambda_nm)
    k = e_foton - phi

    fr = _obtener_fraccion_safe(intensidad_frac, intensidad_pct, k)
    i_amp = _obtener_corriente_amp(fr, e_foton)

    # Actualizar texto de resultados
    txt = []
    txt.append(f"Material: {elem['nombre']} ({simbolo})")
    txt.append(f"λ = {lambda_nm} nm → E_fotón = {e_foton:.3f} eV")
    txt.append(f"Φ = {phi:.3f} eV")
    if k > 0:
        txt.append(f"Energía cinética k = {k:.3f} eV  → Emisión: SÍ")
    else:
        txt.append(f"Energía cinética k = {k:.3f} eV  → Emisión: NO")
    txt.append(f"Corriente (fracción 0.1) = {fr:.4f}")
    txt.append(f"Corriente (aprox.) = {i_amp:.3e} A (asumiendo P_max=1 mW, QE=1)")
    info_text.configure(text="\n".join(txt))
    _actualizar_graficos(ax1, ax2, canvas, e_foton, phi, k, fr, i_amp)


def ejecutar():
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    root.title("Simulador de efecto fotoeléctrico")
    root.resizable(False, False)

    left_frame = ctk.CTkFrame(root, width=320, corner_radius=8)
    left_frame.pack(side="left", fill="y", padx=16, pady=16)

    right_frame = ctk.CTkFrame(root, corner_radius=8)
    right_frame.pack(side="right", fill="both", expand=True, padx=16, pady=16)

    ctk_label_title = ctk.CTkLabel(
        left_frame, text="Controles", font=ctk.CTkFont(size=18, weight="bold")
    )
    ctk_label_title.pack(pady=(6, 12))

    lambda_label = ctk.CTkLabel(left_frame, text="Longitud de onda: 400 nm")
    lambda_label.pack(pady=(6, 2))
    lambda_slider = ctk.CTkSlider(
        left_frame,
        from_=200,
        to=800,
        number_of_steps=600,
        command=lambda v: lambda_label.configure(text=f"Longitud de onda: {int(v)} nm"),
    )
    lambda_slider.set(400)
    lambda_slider.pack(fill="x", padx=12, pady=(0, 8))

    inten_label = ctk.CTkLabel(left_frame, text="Intensidad: 100 %")
    inten_label.pack(pady=(6, 2))
    inten_slider = ctk.CTkSlider(
        left_frame,
        from_=0,
        to=100,
        command=lambda v: inten_label.configure(text=f"Intensidad: {int(v)} %"),
    )
    inten_slider.set(100)
    inten_slider.pack(fill="x", padx=12, pady=(0, 8))

    # Dropdown de elementos
    elementos = simulador.cargar_elementos()
    claves = sorted(elementos.keys())
    valores_menu = [f"{s} - {elementos[s]['nombre']}" for s in claves]
    combo = ctk.CTkOptionMenu(left_frame, values=valores_menu)
    combo.set(valores_menu[0])
    ctk.CTkLabel(left_frame, text="Elemento:").pack(pady=(10, 2))
    combo.pack(fill="x", padx=12, pady=(0, 8))

    resultado_label = ctk.CTkLabel(left_frame, text="", justify="left")
    resultado_label.pack(pady=(8, 6), padx=6)
    btn_calcular = ctk.CTkButton(
        left_frame,
        text="Calcular",
        command=lambda: _calcular_ui(
            lambda_slider, inten_slider, combo, elementos, info_text, ax1, ax2, canvas
        ),
    )
    btn_calcular.pack(padx=12, pady=(6, 12), fill="x")

    # Frame de resultados
    res_frame = ctk.CTkFrame(right_frame)
    res_frame.pack(side="top", fill="x", padx=6, pady=6)

    res_title = ctk.CTkLabel(
        res_frame, text="Resultados", font=ctk.CTkFont(size=16, weight="bold")
    )
    res_title.pack(anchor="w", padx=8, pady=(6, 4))

    info_text = ctk.CTkLabel(
        res_frame, text="Aquí aparecerán los resultados", justify="left"
    )
    info_text.pack(anchor="w", padx=8, pady=(2, 8))

    # Graficas con matplotlib
    matplotlib.rcParams["figure.autolayout"] = True
    fig = Figure(figsize=(6.5, 4.0))
    ax1 = fig.add_subplot(211)  # para energía
    ax2 = fig.add_subplot(212)  # para corriente

    canvas = FigureCanvasTkAgg(fig, master=right_frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(fill="both", expand=True, padx=6, pady=6)

    # Ejecuta el loop
    root.mainloop()


if __name__ == "__main__":
    ejecutar()
