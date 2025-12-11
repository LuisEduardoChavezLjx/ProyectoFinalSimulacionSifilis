import tkinter as tk
from tkinter import ttk

# ===================== PALETA DE COLORES =====================
COLOR_FONDO = "#1e272e"       # Dark Blue/Grey (Background)
COLOR_PANEL = "#2f3640"       # Lighter Grey (Panels)
COLOR_TEXTO = "#f5f6fa"       # White/Off-white (Text)
COLOR_TEXTO_SEC = "#dcdde1"   # Light Grey (Secondary Text)

COLOR_ACCENT = "#00a8ff"      # Bright Blue (Primary Actions)
COLOR_SUCCESS = "#4cd137"     # Green (Success/Go)
COLOR_WARNING = "#fbc531"     # Yellow (Warning)
COLOR_DANGER = "#e84118"      # Red (Danger/Stop)
COLOR_INFO = "#9c88ff"        # Purple (Info)

# ===================== FUENTES =====================
FONT_H1 = ("Segoe UI", 24, "bold")
FONT_H2 = ("Segoe UI", 18, "bold")
FONT_H3 = ("Segoe UI", 14, "bold")
FONT_BODY = ("Segoe UI", 11)
FONT_BODY_BOLD = ("Segoe UI", 11, "bold")
FONT_SMALL = ("Segoe UI", 9)

# ===================== CONFIGURACIÓN GLOBAL =====================
def aplicar_tema(root):
    """Aplica configuración básica a la ventana raíz."""
    root.configure(bg=COLOR_FONDO)
    
    # Configurar estilos de ttk
    style = ttk.Style()
    style.theme_use('clam')  # 'clam' suele ser más flexible para colores
    
    # Treeview
    style.configure("Treeview", 
                    background="white",
                    foreground="black",
                    rowheight=25,
                    fieldbackground="white",
                    font=FONT_BODY)
    style.configure("Treeview.Heading", 
                    font=FONT_BODY_BOLD,
                    background=COLOR_PANEL,
                    foreground="white")
    style.map("Treeview", background=[('selected', COLOR_ACCENT)])

# ===================== WIDGETS PERSONALIZADOS =====================
def crear_boton(parent, text, command, tipo="primary", width=30):
    """Crea un botón estilizado."""
    bg_color = COLOR_ACCENT
    fg_color = "white"
    
    if tipo == "success": bg_color = COLOR_SUCCESS
    elif tipo == "warning": bg_color = COLOR_WARNING; fg_color = "#2f3640"
    elif tipo == "danger": bg_color = COLOR_DANGER
    elif tipo == "info": bg_color = COLOR_INFO
    elif tipo == "secondary": bg_color = "#7f8c8d"
    
    btn = tk.Button(parent, text=text, command=command,
                    font=FONT_BODY_BOLD,
                    bg=bg_color, fg=fg_color,
                    activebackground=fg_color, activeforeground=bg_color,
                    bd=0, cursor="hand2",
                    width=width, pady=10)
    
    # Efecto Hover simple
    def on_enter(e): btn['bg'] = _ajustar_brillo(bg_color, 1.1)
    def on_leave(e): btn['bg'] = bg_color
    
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    
    return btn

def crear_card(parent):
    """Crea un frame con estilo de tarjeta."""
    frame = tk.Frame(parent, bg=COLOR_PANEL, padx=20, pady=20)
    return frame

def crear_label_titulo(parent, text):
    return tk.Label(parent, text=text, font=FONT_H1, bg=COLOR_FONDO, fg=COLOR_TEXTO)

def crear_label_subtitulo(parent, text, bg=COLOR_FONDO):
    return tk.Label(parent, text=text, font=FONT_H3, bg=bg, fg=COLOR_TEXTO_SEC)

def _ajustar_brillo(color_hex, factor):
    """Ajusta el brillo de un color hex."""
    # (Implementación simple para hover)
    return color_hex 
