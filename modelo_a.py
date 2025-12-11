import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import os
import sys
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import estilos
import utilidades

# ===================== RUTA DEL EXCEL (DINÁMICA) =====================
RUTA_EXCEL = sys.argv[1] if len(sys.argv) > 1 else None

df_modelo = None
pendiente_g = None
intercepto_g = None
r2_g = None
corr_g = None

def seleccionar_excel():
    ruta = filedialog.askopenfilename(
        title="Selecciona el Excel de datos",
        filetypes=[("Excel", "*.xlsx *.xls")]
    )
    return ruta if ruta else None

def obtener_df():
    global RUTA_EXCEL
    if not RUTA_EXCEL or not os.path.exists(RUTA_EXCEL):
        RUTA_EXCEL = seleccionar_excel()
    if not RUTA_EXCEL or not os.path.exists(RUTA_EXCEL):
        messagebox.showerror("Error", "No se seleccionó un archivo Excel válido.")
        return None

    try:
        df = pd.read_excel(RUTA_EXCEL, sheet_name=0)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo leer el Excel:\n{e}")
        return None

    df = df.rename(columns={
        "Numero de Semana Epidemiologica": utilidades.COL_SEMANA,
        "Indice": utilidades.COL_INDICE,
        "Indice t-1": utilidades.COL_INDICE_PREV,
        "Casos Reportados": utilidades.COL_CASOS
    })

    # Validación mínima
    if utilidades.COL_SEMANA not in df.columns or utilidades.COL_CASOS not in df.columns:
        messagebox.showerror("Error", "Faltan columnas requeridas: Semana y/o Casos Reportados.")
        return None
    if utilidades.COL_INDICE_PREV not in df.columns and utilidades.COL_INDICE not in df.columns:
        messagebox.showerror("Error", "Falta la columna Indice (o Indice t-1) en el Excel.")
        return None

    # Si falta Indice_t_1 pero existe Indice_t, lo calculamos con shift
    if utilidades.COL_INDICE_PREV not in df.columns and utilidades.COL_INDICE in df.columns:
        df[utilidades.COL_INDICE_PREV] = df[utilidades.COL_INDICE].shift(1)

    return df

def procesar_modelo_a():
    global df_modelo, pendiente_g, intercepto_g, r2_g, corr_g
    try:
        df = obtener_df()
        if df is None:
            return

        df[utilidades.COL_SEMANA] = pd.to_numeric(df[utilidades.COL_SEMANA], errors='coerce')
        df_a = df[df[utilidades.COL_SEMANA] >= 2].copy()
        df_a = df_a.dropna(subset=[utilidades.COL_INDICE_PREV, utilidades.COL_CASOS]).reset_index(drop=True)

        if df_a.empty:
            messagebox.showwarning("Aviso", "No hay datos en el rango.")
            return

        X = df_a[[utilidades.COL_INDICE_PREV]].values
        y = df_a[utilidades.COL_CASOS].values

        modelo = LinearRegression(fit_intercept=True)
        modelo.fit(X, y)

        pendiente = modelo.coef_[0]
        intercepto = modelo.intercept_
        corr = np.corrcoef(df_a[utilidades.COL_INDICE_PREV], df_a[utilidades.COL_CASOS])[0, 1]
        r2 = corr ** 2

        pendiente_g = pendiente
        intercepto_g = intercepto
        r2_g = r2
        corr_g = corr
        df_modelo = df_a

        lbl_pendiente.config(text=f"Pendiente (b): {pendiente:.4f}")
        lbl_intercepto.config(text=f"Intercepto (a): {intercepto:.4f}")
        color_r2 = estilos.COLOR_DANGER if r2 < 0.1 else estilos.COLOR_TEXTO
        lbl_r2.config(text=f"R² (Varianza explicada): {r2:.5f} ({r2*100:.2f}%)", fg=color_r2)
        lbl_corr.config(text=f"Correlación (r): {corr:.5f}")

        actualizar_tabla()
        btn_grafica.config(state="normal")
        btn_exportar.config(state="normal")
        btn_conclusion.config(state="normal")
        messagebox.showinfo("Éxito", "Análisis Correlacional (Modelo A) completado.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def actualizar_tabla():
    for row in tabla.get_children():
        tabla.delete(row)
    if df_modelo is None:
        return
    for _, row in df_modelo.iterrows():
        periodo = row.get(utilidades.COL_PERIODO, "-")
        if isinstance(periodo, pd.Timestamp):
            periodo = periodo.strftime('%d/%m/%Y')
        tabla.insert("", tk.END, values=[
            row.get(utilidades.COL_SEMANA),
            periodo,
            row.get(utilidades.COL_INDICE_PREV),
            row.get(utilidades.COL_CASOS)
        ])

def exportar_excel():
    if df_modelo is None:
        return
    ruta = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel", "*.xlsx")],
        title="Guardar Datos Modelo A"
    )
    if ruta:
        try:
            cols_export = [utilidades.COL_SEMANA, utilidades.COL_PERIODO, utilidades.COL_INDICE_PREV, utilidades.COL_CASOS]
            final_cols = [c for c in cols_export if c in df_modelo.columns]
            df_modelo[final_cols].to_excel(ruta, index=False)
            messagebox.showinfo("Exportado", f"Datos guardados en:\n{ruta}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

def mostrar_grafica():
    if df_modelo is None:
        return
    top = tk.Toplevel(root)
    top.title("Dispersión: ¿Existe relación?")
    top.geometry("700x500")
    estilos.aplicar_tema(top)
    
    fig = Figure(figsize=(6, 4), dpi=100)
    ax = fig.add_subplot(111)
    x = df_modelo[utilidades.COL_INDICE_PREV]
    y = df_modelo[utilidades.COL_CASOS]
    ax.scatter(x, y, label="Observaciones Reales", color='blue', alpha=0.6)
    x_line = np.linspace(x.min(), x.max(), 50)
    y_line = intercepto_g + pendiente_g * x_line
    ax.plot(x_line, y_line, label=f"Tendencia (R²={r2_g:.4f})", color='red', linestyle='--')
    ax.set_title("Correlación: Búsquedas (t-1) vs Casos")
    ax.set_xlabel("Índice Google (t-1)")
    ax.set_ylabel("Casos Reportados")
    ax.legend()
    ax.grid(True, linestyle=':', alpha=0.6)
    canvas = FigureCanvasTkAgg(fig, master=top)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

    # Barra de herramientas (Zoom, Pan, Save)
    toolbar = NavigationToolbar2Tk(canvas, top)
    toolbar.update()
    canvas.get_tk_widget().pack(fill="both", expand=True)

def mostrar_conclusion():
    if r2_g is None:
        return
    msg = (
        f"CONCLUSIÓN DEL MODELO A:\n\n"
        f"El coeficiente R² es de {r2_g:.5f} (aprox {r2_g*100:.2f}%).\n\n"
        f"Interpretación:\n"
        f"Como el valor es extremadamente bajo (cercano a 0%), concluimos que "
        f"NO existe una relación lineal explicativa entre el índice de Google "
        f"y los casos de sífilis en este conjunto de datos.\n\n"
        f"Este modelo sirve para DESCARTAR Google Trends como predictor directo."
    )
    messagebox.showinfo("Interpretación Estadística", msg)

# ===================== GUI =====================
root = tk.Tk()
root.title("Modelo A: Análisis Correlacional (Sin Predicción)")
root.state('zoomed')
estilos.aplicar_tema(root)

# Header
frame_header = tk.Frame(root, bg=estilos.COLOR_FONDO)
frame_header.pack(fill="x", pady=20)
tk.Label(frame_header, text="Modelo A: Análisis de Correlación", font=estilos.FONT_H1, bg=estilos.COLOR_FONDO, fg=estilos.COLOR_TEXTO).pack()

estilos.crear_boton(frame_header, "⬅ Volver al Menú", root.destroy, tipo="secondary", width=20).pack(anchor="nw", padx=20)
tk.Label(frame_header, text="(Este modelo solo mide la relación entre variables, no predice)", font=estilos.FONT_SMALL, bg=estilos.COLOR_FONDO, fg=estilos.COLOR_TEXTO_SEC).pack()

# Auto-cargar al iniciar
root.after(100, procesar_modelo_a)

# Stats Card
card_stats = estilos.crear_card(root)
card_stats.pack(fill="x", padx=20, pady=10)
estilos.crear_label_subtitulo(card_stats, "Resultados Estadísticos", bg=estilos.COLOR_PANEL).pack(anchor="w", pady=(0, 10))

frame_stats_grid = tk.Frame(card_stats, bg=estilos.COLOR_PANEL)
frame_stats_grid.pack(fill="x")

lbl_pendiente = tk.Label(frame_stats_grid, text="Pendiente: --", font=estilos.FONT_BODY, bg=estilos.COLOR_PANEL, fg=estilos.COLOR_TEXTO)
lbl_pendiente.grid(row=0, column=0, padx=20, pady=5)
lbl_intercepto = tk.Label(frame_stats_grid, text="Intercepto: --", font=estilos.FONT_BODY, bg=estilos.COLOR_PANEL, fg=estilos.COLOR_TEXTO)
lbl_intercepto.grid(row=0, column=1, padx=20, pady=5)
lbl_corr = tk.Label(frame_stats_grid, text="Correlación (r): --", font=estilos.FONT_BODY_BOLD, bg=estilos.COLOR_PANEL, fg=estilos.COLOR_ACCENT)
lbl_corr.grid(row=1, column=0, padx=20, pady=5)
lbl_r2 = tk.Label(frame_stats_grid, text="R²: --", font=estilos.FONT_BODY_BOLD, bg=estilos.COLOR_PANEL, fg=estilos.COLOR_TEXTO)
lbl_r2.grid(row=1, column=1, padx=20, pady=5)

# Actions
frame_btn = tk.Frame(root, bg=estilos.COLOR_FONDO)
frame_btn.pack(pady=10)
btn_grafica = estilos.crear_boton(frame_btn, "Ver Dispersión", mostrar_grafica, tipo="info", width=20)
btn_grafica.pack(side="left", padx=5)

btn_conclusion = estilos.crear_boton(frame_btn, "Leer Conclusión", mostrar_conclusion, tipo="primary", width=20)
btn_conclusion.pack(side="left", padx=5)

btn_exportar = estilos.crear_boton(frame_btn, "Exportar Datos a Excel", exportar_excel, tipo="success", width=25)
btn_exportar.pack(side="left", padx=5)

# Table
frame_tab = tk.Frame(root, bg=estilos.COLOR_FONDO)
frame_tab.pack(fill="both", expand=True, padx=20, pady=10)

cols = [utilidades.COL_SEMANA, utilidades.COL_PERIODO, utilidades.COL_INDICE_PREV, utilidades.COL_CASOS]
scroll = ttk.Scrollbar(frame_tab, orient="vertical")
tabla = ttk.Treeview(frame_tab, columns=cols, show="headings", yscrollcommand=scroll.set)
scroll.config(command=tabla.yview)
scroll.pack(side="right", fill="y")
tabla.pack(side="left", fill="both", expand=True)

tabla.heading(utilidades.COL_SEMANA, text="Semana")
tabla.heading(utilidades.COL_PERIODO, text="Periodo")
tabla.heading(utilidades.COL_INDICE_PREV, text="Índice (t-1)")
tabla.heading(utilidades.COL_CASOS, text="Casos")
for col in cols:
    tabla.column(col, anchor="center")

root.mainloop()
