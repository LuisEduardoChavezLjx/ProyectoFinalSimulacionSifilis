import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import sys
import os
import estilos
import utilidades
import webbrowser

ARCHIVO_MODELO_A = "modelo_a.py"
ARCHIVO_MODELO_B = "modelo_b.py"
ARCHIVO_GESTOR = "gestor_datos.py"

# Ruta seleccionada para modelos A/B
RUTA_EXCEL = None

# ===================== EJECUCIÓN DE SCRIPTS =====================
def ejecutar_script(nombre_script, pasar_excel=True):
    if not os.path.exists(nombre_script):
        messagebox.showerror("Error", f"Falta el archivo: {nombre_script}\nAsegúrate de que esté en la misma carpeta.")
        return
    args = [sys.executable, nombre_script]
    if pasar_excel and RUTA_EXCEL:
        args.append(RUTA_EXCEL)
    try:
        subprocess.Popen(args)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def elegir_excel():
    global RUTA_EXCEL
    ruta = filedialog.askopenfilename(
        title="Selecciona el Excel de datos (Modelos A/B)",
        filetypes=[("Archivos de Excel", "*.xlsx *.xls")]
    )
    if ruta:
        RUTA_EXCEL = ruta
        lbl_estado_excel.config(text=f"Archivo cargado: {os.path.basename(ruta)}", fg=estilos.COLOR_SUCCESS)
        messagebox.showinfo("Excel seleccionado", f"Usando:\n{RUTA_EXCEL}")
    else:
        lbl_estado_excel.config(text="No se ha seleccionado archivo", fg=estilos.COLOR_WARNING)

# ===================== VENTANA DE PRESENTACIÓN =====================
def abrir_presentacion():
    ventana_pres = tk.Toplevel(root)
    ventana_pres.title("Presentación y Marco Teórico")
    ventana_pres.geometry("1000x700")
    estilos.aplicar_tema(ventana_pres)

    tk.Label(ventana_pres, text="Análisis de Epidemiología Digital: Sífilis en México",
             font=estilos.FONT_H2, bg=estilos.COLOR_FONDO, fg=estilos.COLOR_TEXTO).pack(pady=20)

    notebook = ttk.Notebook(ventana_pres)
    notebook.pack(fill="both", expand=True, padx=20, pady=10)

    # Estilo para el texto
    def crear_pagina(titulo, contenido):
        frame = tk.Frame(notebook, bg="white")
        notebook.add(frame, text=f"  {titulo}  ")
        txt = tk.Text(frame, wrap="word", font=estilos.FONT_BODY, padx=30, pady=30, bd=0)
        txt.insert("1.0", contenido)
        txt.config(state="disabled")
        txt.pack(fill="both", expand=True)

    txt_intro = """
    La simulación es una herramienta clave en ingeniería porque permite analizar y anticipar 
    el comportamiento de sistemas reales sin detenerlos. En salud pública esto es crítico, 
    ya que enfermedades como la sífilis presentan cambios rápidos mientras que los reportes 
    oficiales suelen publicarse con una o dos semanas de retraso, generando periodos de 
    incertidumbre.

    Este proyecto explora si las búsquedas en Google Trends relacionadas con “sífilis” pueden 
    funcionar como una señal temprana que complemente la vigilancia epidemiológica. Para ello 
    se evaluaron dos enfoques: un modelo estático basado en correlación, que mostró una 
    relación muy baja, y un modelo dinámico incremental que trabaja con variaciones 
    semanales. Este último logró reconstruir la tendencia real con un error medio aceptable, 
    demostrando su utilidad para estimar cambios próximos en los casos.

    La plataforma desarrollada en Python integra ambos modelos y permite cargar datos, 
    visualizar tendencias y obtener una proyección operativa de la semana siguiente. Con ello, 
    el sistema ofrece una herramienta accesible para apoyar la toma de decisiones en 
    vigilancia digital de la sífilis.
    """
    crear_pagina("📖 Introducción", txt_intro)

    txt_a = """
    El Modelo A es el primer enfoque del sistema y analiza la relación entre el nivel absoluto 
    de búsquedas en Google Trends y los casos reales de sífilis reportados en la misma semana. 
    Su objetivo no es predecir, sino evaluar si existe una correlación directa entre el interés 
    digital y la incidencia real.

    Para ello se aplica una regresión lineal simple entre el índice de Google Trends y los casos 
    confirmados por semana. Los resultados muestran que la relación es muy baja, lo cual indica 
    que los valores absolutos del índice no reflejan adecuadamente el comportamiento real de la 
    enfermedad.

    Aunque el Modelo A no es útil como predictor, sí funciona como referencia descriptiva y 
    permite visualizar que las búsquedas no se mueven en sincronía con los casos. Esta conclusión 
    motiva el uso de un enfoque más dinámico, que se implementa posteriormente en el Modelo B.
    """

    crear_pagina("� Modelo A", txt_a)

    txt_b = """
    El Modelo B es el enfoque predictivo del sistema y se basa en analizar los cambios 
    semanales tanto en los casos reales como en el índice de Google Trends. A diferencia del 
    Modelo A, este modelo no trabaja con valores absolutos, sino con variaciones (deltas) y con 
    el índice de la semana previa, lo que permite capturar la dinámica real del comportamiento 
    epidemiológico.

    Mediante una regresión lineal entre el cambio en búsquedas y el cambio en casos, el modelo 
    estima cuánto debería aumentar o disminuir la incidencia la semana siguiente. Posteriormente, 
    esta variación se suma al valor real de la semana anterior, lo que convierte al modelo en un 
    método incremental.

    Aunque la correlación entre deltas es baja, el Modelo B logra reconstruir la tendencia real 
    con un error medio aceptable (≈13.79%), lo que lo hace útil como herramienta de alerta 
    temprana. En la plataforma, el usuario puede visualizar estos cálculos, comparar valores 
    reales vs. estimados y obtener una proyección operativa para la siguiente semana.
    """

    crear_pagina("📈 Modelo B", txt_b)

    estilos.crear_boton(ventana_pres, "Cerrar Presentación", ventana_pres.destroy, tipo="danger").pack(pady=10)

# ===================== INTERFAZ GRÁFICA PRINCIPAL =====================
root = tk.Tk()
root.title("Sistema Integral de Epidemiología - México")
root.state('zoomed')
estilos.aplicar_tema(root)

# --- HEADER ---
frame_header = tk.Frame(root, bg=estilos.COLOR_FONDO)
frame_header.pack(fill="x", pady=(30, 20))

tk.Label(frame_header, text="SISTEMA DE ANÁLISIS EPIDEMIOLÓGICO",
         font=estilos.FONT_H1, fg=estilos.COLOR_TEXTO, bg=estilos.COLOR_FONDO).pack()
tk.Label(frame_header, text="Modelo Matemático: Google Trends vs Casos Reales",
         font=("Segoe UI", 12, "italic"), fg=estilos.COLOR_ACCENT, bg=estilos.COLOR_FONDO).pack()

# --- CONTENEDOR PRINCIPAL (GRID) ---
main_container = tk.Frame(root, bg=estilos.COLOR_FONDO)
main_container.pack(fill="both", expand=True, padx=50)

# COLUMNA IZQUIERDA: CONFIGURACIÓN Y AYUDA
col_izq = tk.Frame(main_container, bg=estilos.COLOR_FONDO)
col_izq.pack(side="left", fill="y", padx=20, anchor="n")

card_config = estilos.crear_card(col_izq)
card_config.pack(fill="x", pady=10)
estilos.crear_label_subtitulo(card_config, "📂 Configuración de Datos", bg=estilos.COLOR_PANEL).pack(pady=(0, 10))

lbl_estado_excel = tk.Label(card_config, text="No se ha seleccionado archivo", 
                            font=estilos.FONT_SMALL, fg=estilos.COLOR_WARNING, bg=estilos.COLOR_PANEL)
lbl_estado_excel.pack(pady=5)

estilos.crear_boton(card_config, "Seleccionar Excel (Modelos A/B)", elegir_excel, tipo="secondary", width=25).pack(pady=5)
estilos.crear_boton(card_config, "Descargar Plantilla", utilidades.generar_plantilla, tipo="success", width=25).pack(pady=5)

card_help = estilos.crear_card(col_izq)
card_help.pack(fill="x", pady=20)
estilos.crear_label_subtitulo(card_help, "📘 Ayuda y Documentación", bg=estilos.COLOR_PANEL).pack(pady=(0, 10))
estilos.crear_boton(card_help, "Ver Marco Teórico", abrir_presentacion, tipo="info", width=25).pack(pady=5)

card_fuentes = estilos.crear_card(col_izq)
card_fuentes.pack(fill="x", pady=10)
estilos.crear_label_subtitulo(card_fuentes, "🌐 Consultar Datos", bg=estilos.COLOR_PANEL).pack(pady=(0, 10))

import datetime

def abrir_selector_fechas_trends():
    ventana_fechas = tk.Toplevel(root)
    ventana_fechas.title("Seleccionar Rango de Fechas")
    ventana_fechas.geometry("400x350")
    estilos.aplicar_tema(ventana_fechas)

    tk.Label(ventana_fechas, text="Configurar Búsqueda en Google Trends", 
             font=estilos.FONT_H3, bg=estilos.COLOR_FONDO, fg=estilos.COLOR_TEXTO).pack(pady=15)

    frame_form = tk.Frame(ventana_fechas, bg=estilos.COLOR_FONDO)
    frame_form.pack(pady=10)

    from tkcalendar import DateEntry

    # --- Helpers para fechas ---
    hoy = datetime.date.today()
    
    def crear_selector_fecha(parent, label_text, fecha_default):
        frame = tk.Frame(parent, bg=estilos.COLOR_FONDO)
        frame.pack(pady=5)
        tk.Label(frame, text=label_text, width=15, anchor="e", bg=estilos.COLOR_FONDO, fg=estilos.COLOR_TEXTO).pack(side="left")
        
        cal = DateEntry(frame, width=12, background='darkblue',
                        foreground='white', borderwidth=2, year=fecha_default.year, month=fecha_default.month, day=fecha_default.day,
                        maxdate=hoy, date_pattern='y-mm-dd')
        cal.pack(side="left", padx=10)
        return cal

    # Fecha inicio default: 1 año antes
    fecha_inicio_default = hoy - datetime.timedelta(days=365)
    
    cal_ini = crear_selector_fecha(frame_form, "Fecha Inicio:", fecha_inicio_default)
    cal_fin = crear_selector_fecha(frame_form, "Fecha Fin:", hoy)

    def abrir_url():
        try:
            fecha_ini = cal_ini.get_date()
            fecha_fin = cal_fin.get_date()
            
            if fecha_fin > hoy:
                messagebox.showwarning("Fecha Inválida", "La fecha final no puede ser mayor al día de hoy.")
                return

            if fecha_ini > fecha_fin:
                messagebox.showwarning("Fecha Inválida", "La fecha de inicio no puede ser mayor a la fecha final.")
                return

            # Formato URL: YYYY-MM-DD%20YYYY-MM-DD
            str_ini = fecha_ini.strftime("%Y-%m-%d")
            str_fin = fecha_fin.strftime("%Y-%m-%d")
            
            url_dinamica = f"https://trends.google.com/trends/explore?date={str_ini}%20{str_fin}&geo=MX&q=%2Fm%2F074m2&hl=es-419"
            webbrowser.open(url_dinamica)
            ventana_fechas.destroy()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    estilos.crear_boton(ventana_fechas, "Abrir en Google Trends", abrir_url, tipo="primary").pack(pady=20)


url_trends = "https://trends.google.com/trends/explore?date=2024-12-29%202025-12-04&geo=MX&q=%2Fm%2F074m2&hl=es-419"
url_boletin = "https://www.gob.mx/salud/documentos/boletinepidemiologico-sistema-nacional-de-vigilancia-epidemiologica-sistema-unico-de-informacion-387843"

estilos.crear_boton(card_fuentes, "Google Trends", abrir_selector_fechas_trends, tipo="info", width=25).pack(pady=5)
estilos.crear_boton(card_fuentes, "Boletín Epidemiológico", lambda: webbrowser.open(url_boletin), tipo="info", width=25).pack(pady=5)


# COLUMNA DERECHA: MÓDULOS OPERATIVOS
col_der = tk.Frame(main_container, bg=estilos.COLOR_FONDO)
col_der.pack(side="left", fill="both", expand=True, padx=20)

tk.Label(col_der, text="MÓDULOS OPERATIVOS", font=estilos.FONT_H3, fg=estilos.COLOR_TEXTO_SEC, bg=estilos.COLOR_FONDO).pack(anchor="w", pady=(10, 10))

# Módulo 1: Gestor
card_gestor = estilos.crear_card(col_der)
card_gestor.pack(fill="x", pady=10)
estilos.crear_label_subtitulo(card_gestor, "1. Gestión de Datos en Vivo", bg=estilos.COLOR_PANEL).pack(anchor="w")
tk.Label(card_gestor, text="Registro semanal, edición y pronóstico inmediato.", font=estilos.FONT_BODY, fg="#bdc3c7", bg=estilos.COLOR_PANEL).pack(anchor="w", pady=2)
estilos.crear_boton(card_gestor, "Abrir Gestor de Datos", lambda: ejecutar_script(ARCHIVO_GESTOR, pasar_excel=False), tipo="primary", width=30).pack(pady=10)

# Módulo 2: Modelo A
card_mod_a = estilos.crear_card(col_der)
card_mod_a.pack(fill="x", pady=10)
estilos.crear_label_subtitulo(card_mod_a, "2. Modelo A (Correlacional)", bg=estilos.COLOR_PANEL).pack(anchor="w")
tk.Label(card_mod_a, text="Análisis estadístico estático (Regresión Lineal Simple).", font=estilos.FONT_BODY, fg="#bdc3c7", bg=estilos.COLOR_PANEL).pack(anchor="w", pady=2)
estilos.crear_boton(card_mod_a, "Ejecutar Modelo A", lambda: ejecutar_script(ARCHIVO_MODELO_A, pasar_excel=True), tipo="warning", width=30).pack(pady=10)

# Módulo 3: Modelo B
card_mod_b = estilos.crear_card(col_der)
card_mod_b.pack(fill="x", pady=10)
estilos.crear_label_subtitulo(card_mod_b, "3. Modelo B (Predictivo)", bg=estilos.COLOR_PANEL).pack(anchor="w")
tk.Label(card_mod_b, text="Análisis dinámico de tendencias y predicción basada en cambios (Deltas).", font=estilos.FONT_BODY, fg="#bdc3c7", bg=estilos.COLOR_PANEL).pack(anchor="w", pady=2)
estilos.crear_boton(card_mod_b, "Ejecutar Modelo B", lambda: ejecutar_script(ARCHIVO_MODELO_B, pasar_excel=True), tipo="success", width=30).pack(pady=10)

# Footer
tk.Label(root, text="© 2025 Sistema de Vigilancia Epidemiológica", font=estilos.FONT_SMALL, fg="#7f8c8d", bg=estilos.COLOR_FONDO).pack(side="bottom", pady=10)

root.mainloop()
