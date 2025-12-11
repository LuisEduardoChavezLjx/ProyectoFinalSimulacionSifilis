import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import os
import sys
import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import estilos
import utilidades

try:
    from tkcalendar import DateEntry
except ImportError:
    messagebox.showerror("Error", "Falta tkcalendar. Instala: pip install tkcalendar")
    sys.exit()

# ===================== CONFIGURACIÓN =====================
RUTA_EXCEL = sys.argv[1] if len(sys.argv) > 1 else None

df_datos = None
modelo_alpha = 0.0
modelo_beta = 0.0
modelo_listo = False

# ===================== UTILIDADES =====================
def seleccionar_excel():
    ruta = filedialog.askopenfilename(
        title="Selecciona el Excel de datos",
        filetypes=[("Excel", "*.xlsx *.xls")]
    )
    return ruta or None

def leer_excel():
    global RUTA_EXCEL
    if not RUTA_EXCEL or not os.path.exists(RUTA_EXCEL):
        RUTA_EXCEL = seleccionar_excel()
    if not RUTA_EXCEL or not os.path.exists(RUTA_EXCEL):
        messagebox.showerror("Error", "No se seleccionó un Excel válido.")
        return None
    try:
        df = pd.read_excel(RUTA_EXCEL, sheet_name=0)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo leer el Excel:\n{e}")
        return None

    df = df.rename(columns={
        "Numero de Semana Epidemiologica": utilidades.COL_SEMANA,
        "No. Semana": utilidades.COL_SEMANA,
        "Indice": utilidades.COL_INDICE,
        "Indice t-1": utilidades.COL_INDICE_PREV,
        "Casos Reportados": utilidades.COL_CASOS,
        "Casos": utilidades.COL_CASOS
    })

    cols_necesarias = [utilidades.COL_SEMANA, utilidades.COL_PERIODO, utilidades.COL_INDICE, utilidades.COL_INDICE_PREV, utilidades.COL_CASOS]
    for col in cols_necesarias:
        if col not in df.columns:
            df[col] = np.nan

    if utilidades.COL_PERIODO in df.columns:
        df[utilidades.COL_PERIODO] = pd.to_datetime(df[utilidades.COL_PERIODO], errors="coerce")

    faltantes = [utilidades.COL_SEMANA, utilidades.COL_INDICE, utilidades.COL_CASOS]
    if any(c not in df.columns for c in faltantes):
        messagebox.showerror("Error", f"Faltan columnas requeridas: {', '.join(faltantes)}")
        return None

    return df[cols_necesarias].copy()

def guardar_excel(df):
    global RUTA_EXCEL
    if not RUTA_EXCEL:
        RUTA_EXCEL = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx *.xls"), ("Todos los archivos", "*.*")]
        )
    if not RUTA_EXCEL:
        messagebox.showwarning("Aviso", "No se guardó el archivo.")
        return
    try:
        df_export = df.copy()
        for col in [utilidades.COL_EST_SIN, utilidades.COL_EST_CON]:
            if col in df_export.columns:
                df_export = df_export.drop(columns=[col])
        df_export = df_export.rename(columns={
            utilidades.COL_SEMANA: "Numero de Semana Epidemiologica",
            utilidades.COL_INDICE: "Indice",
            utilidades.COL_INDICE_PREV: "Indice t-1",
            utilidades.COL_CASOS: "Casos Reportados"
        })
        df_export.to_excel(RUTA_EXCEL, index=False)
        messagebox.showinfo("Guardado", f"Datos guardados en:\n{RUTA_EXCEL}")
    except PermissionError:
        messagebox.showerror("Error de Permiso", f"No se pudo guardar el archivo.\n\nPARECE QUE TIENES EL EXCEL ABIERTO.\nCierra el archivo '{os.path.basename(RUTA_EXCEL)}' y vuelve a intentarlo.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar:\n{e}")

# ===================== LÓGICA MODELO B =====================
def calcular_modelo_b_completo(df):
    global modelo_alpha, modelo_beta, modelo_listo
    modelo_listo = False
    df[utilidades.COL_EST_SIN] = 0.0
    df[utilidades.COL_EST_CON] = 0.0

    if df is None or len(df) < 3:
        return df

    df_calc = df.copy()
    df_calc[utilidades.COL_INDICE_PREV] = df_calc[utilidades.COL_INDICE].shift(1)
    df_calc["Delta_Casos"] = df_calc[utilidades.COL_CASOS].diff()
    df_calc["Delta_Indice"] = df_calc[utilidades.COL_INDICE_PREV].diff()

    df_train = df_calc.dropna(subset=["Delta_Casos", "Delta_Indice"])
    if df_train.empty:
        return df

    X = df_train[["Delta_Indice"]].values
    y = df_train["Delta_Casos"].values
    try:
        modelo = LinearRegression(fit_intercept=True)
        modelo.fit(X, y)
        modelo_alpha = modelo.intercept_
        modelo_beta = modelo.coef_[0]
        modelo_listo = True
    except Exception:
        return df

    lista_sin = [0.0] * len(df)
    lista_con = [0.0] * len(df)
    for i in range(1, len(df)):
        casos_prev = df_calc.iloc[i - 1][utilidades.COL_CASOS]
        ind_t1_actual = df_calc.iloc[i][utilidades.COL_INDICE_PREV]
        ind_t1_prev = df_calc.iloc[i - 1][utilidades.COL_INDICE_PREV]
        delta_ind = 0 if (pd.isna(ind_t1_actual) or pd.isna(ind_t1_prev)) else ind_t1_actual - ind_t1_prev
        est_sin = casos_prev + modelo_beta * delta_ind
        est_con = casos_prev + modelo_alpha + modelo_beta * delta_ind
        lista_sin[i] = est_sin
        lista_con[i] = est_con

    df[utilidades.COL_EST_SIN] = lista_sin
    df[utilidades.COL_EST_CON] = lista_con
    return df

# ===================== GESTIÓN DE DATOS =====================
def cargar_datos():
    global df_datos
    df = leer_excel()
    if df is None:
        return
    df_datos = df.sort_values(by=utilidades.COL_PERIODO).reset_index(drop=True)
    df_datos[utilidades.COL_INDICE_PREV] = df_datos[utilidades.COL_INDICE].shift(1)
    df_datos[utilidades.COL_INDICE_PREV] = df_datos[utilidades.COL_INDICE].shift(1)
    actualizar_tabla_ui()
    sugerir_siguientes_datos()

def guardar_cambios():
    global df_datos
    if df_datos is None:
        return
    df_datos = df_datos.sort_values(by=utilidades.COL_PERIODO).reset_index(drop=True)
    df_datos[utilidades.COL_INDICE_PREV] = df_datos[utilidades.COL_INDICE].shift(1)
    guardar_excel(df_datos)
    actualizar_tabla_ui()

# ===================== PREDICCIÓN FUTURA =====================
def predecir_siguiente():
    global df_datos, modelo_alpha, modelo_beta, modelo_listo
    if df_datos is None or df_datos.empty:
        messagebox.showwarning("Aviso", "No hay datos suficientes.")
        return
    if not modelo_listo:
        messagebox.showwarning("Aviso", "Se necesitan al menos 3 semanas para el modelo.")
        return

    last_row = df_datos.iloc[-1]
    try:
        casos_actuales = last_row[utilidades.COL_CASOS]
        semana_actual = last_row[utilidades.COL_SEMANA]
        delta_ind_next = last_row[utilidades.COL_INDICE] - last_row[utilidades.COL_INDICE_PREV]
        pred_sin = casos_actuales + modelo_beta * delta_ind_next
        pred_con = casos_actuales + modelo_alpha + modelo_beta * delta_ind_next
        mensaje = (
            f"📊 PREDICCIÓN PARA LA SIGUIENTE SEMANA (aprox. {int(semana_actual)+1})\n"
            f"----------------------------------------------------\n"
            f"Basado en los últimos datos:\n"
            f"• Casos última semana: {casos_actuales}\n"
            f"• Tendencia del Índice Google: {delta_ind_next:+.2f}\n\n"
            f"RESULTADOS DEL MODELO B:\n"
            f"🟢 Estimado SIN intercepto:  {pred_sin:.2f} casos\n"
            f"🔵 Estimado CON intercepto:  {pred_con:.2f} casos\n"
        )
        messagebox.showinfo("Predicción Futura", mensaje)
    except Exception as e:
        messagebox.showerror("Error de Cálculo", f"No se pudo predecir: {e}")

# ===================== GRÁFICA DE SERIE =====================
def mostrar_grafica_serie():
    if df_datos is None or df_datos.empty:
        messagebox.showwarning("Aviso", "No hay datos cargados.")
        return

    top = tk.Toplevel(root)
    top.title("Serie Temporal: Reales vs Estimados")
    estilos.aplicar_tema(top)
    
    # Crear figura y ejes
    fig = Figure(figsize=(9, 5), dpi=100)
    ax = fig.add_subplot(111)

    # Convertir fechas para matplotlib si es necesario
    fechas = df_datos[utilidades.COL_PERIODO]
    
    # Graficar líneas
    line_real, = ax.plot(fechas, df_datos[utilidades.COL_CASOS], marker="o", label="Reales", color="blue", markersize=4)
    line_sin, = ax.plot(fechas, df_datos[utilidades.COL_EST_SIN], linestyle="--", label="Est. sin intercepto", color="green")
    line_con, = ax.plot(fechas, df_datos[utilidades.COL_EST_CON], linestyle=":", label="Est. con intercepto", color="purple")

    ax.set_title("Reales vs Estimados (Modelo B)")
    ax.set_xlabel("Fecha")
    ax.set_ylabel("Casos")
    ax.legend()
    ax.grid(True, linestyle=":", alpha=0.6)
    
    # Formato de fecha en eje X
    fig.autofmt_xdate()

    # --- ELEMENTOS INTERACTIVOS (Cursor y Tooltip) ---
    # Línea vertical que sigue al mouse
    cursor_line = ax.axvline(x=fechas.iloc[0], color='gray', linestyle='--', alpha=0.5)
    cursor_line.set_visible(False)

    # Texto flotante (Tooltip)
    annot = ax.annotate("", xy=(0,0), xytext=(10,10), textcoords="offset points",
                        bbox=dict(boxstyle="round", fc="w", alpha=0.9),
                        arrowprops=dict(arrowstyle="->"))
    annot.set_visible(False)

    def update_annot(ind):
        # Obtener la fecha (x) y casos (y) del punto más cercano
        x = fechas.iloc[ind]
        y = df_datos[utilidades.COL_CASOS].iloc[ind]
        
        # Mover la anotación
        annot.xy = (x, y)
        
        # Texto del tooltip
        semana = df_datos[utilidades.COL_SEMANA].iloc[ind]
        est_sin = df_datos[utilidades.COL_EST_SIN].iloc[ind]
        est_con = df_datos[utilidades.COL_EST_CON].iloc[ind]
        
        text = (f"Semana: {semana}\n"
                f"Fecha: {x.strftime('%d/%m/%Y')}\n"
                f"Reales: {y}\n"
                f"Sin Int: {est_sin:.2f}\n"
                f"Con Int: {est_con:.2f}")
        
        annot.set_text(text)
        annot.get_bbox_patch().set_alpha(0.9)

    def hover(event):
        vis = annot.get_visible()
        if event.inaxes == ax:
            # Encontrar el índice de la fecha más cercana
            # Convertimos las fechas a números de matplotlib para comparar
            import matplotlib.dates as mdates
            x_mouse = event.xdata
            if x_mouse is None: return
            
            # Buscar el índice más cercano en el dataframe
            # (Asumiendo que las fechas están ordenadas)
            try:
                # Convertir la columna de fechas a números float de matplotlib
                x_dates = mdates.date2num(fechas)
                # Encontrar el índice del valor más cercano
                ind = (np.abs(x_dates - x_mouse)).argmin()
                
                # Actualizar línea vertical
                cursor_line.set_xdata([fechas.iloc[ind]])
                cursor_line.set_visible(True)
                
                # Actualizar tooltip
                update_annot(ind)
                annot.set_visible(True)
                fig.canvas.draw_idle()
            except Exception:
                pass
        else:
            if vis:
                annot.set_visible(False)
                cursor_line.set_visible(False)
                fig.canvas.draw_idle()

    # Conectar evento
    fig.canvas.mpl_connect("motion_notify_event", hover)

    # --- CANVAS Y TOOLBAR ---
    canvas = FigureCanvasTkAgg(fig, master=top)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)
    
    # Barra de herramientas (Zoom, Pan, Save)
    toolbar = NavigationToolbar2Tk(canvas, top)
    toolbar.update()
    canvas.get_tk_widget().pack(fill="both", expand=True)

# ===================== CRUD =====================
def agregar_registro():
    global df_datos
    try:
        sem = ent_semana.get().strip()
        fecha = pd.Timestamp(ent_fecha.get_date())
        ind = float(ent_indice.get().strip())
        casos = float(ent_casos.get().strip())
        if sem == "":
            return
        nueva = {utilidades.COL_SEMANA: sem, utilidades.COL_PERIODO: fecha, utilidades.COL_INDICE: ind, utilidades.COL_INDICE_PREV: 0, utilidades.COL_CASOS: casos}
        if df_datos is None:
            df_datos = pd.DataFrame([nueva])
        else:
            df_datos = pd.concat([df_datos, pd.DataFrame([nueva])], ignore_index=True)
        guardar_cambios()
        limpiar_formulario()
    except ValueError:
        messagebox.showerror("Error", "Números inválidos.")

def actualizar_registro():
    global df_datos
    sel = tabla.selection()
    if not sel:
        return
    try:
        idx = int(sel[0])
        df_datos.at[idx, utilidades.COL_SEMANA] = ent_semana.get().strip()
        df_datos.at[idx, utilidades.COL_PERIODO] = pd.Timestamp(ent_fecha.get_date())
        df_datos.at[idx, utilidades.COL_INDICE] = float(ent_indice.get().strip())
        df_datos.at[idx, utilidades.COL_CASOS] = float(ent_casos.get().strip())
        guardar_cambios()
        limpiar_formulario()
    except ValueError:
        messagebox.showerror("Error", "Datos inválidos.")

def eliminar_registro():
    global df_datos
    sel = tabla.selection()
    if not sel:
        return
    if messagebox.askyesno("Confirmar", "¿Eliminar?"):
        idx = int(sel[0])
        df_datos = df_datos.drop(df_datos.index[idx]).reset_index(drop=True)
        guardar_cambios()
        limpiar_formulario()

def sugerir_siguientes_datos():
    """Rellena los campos con la siguiente semana y fecha probable (7 días después)."""
    if df_datos is None or df_datos.empty:
        return

    try:
        last_row = df_datos.iloc[-1]
        # Semana
        last_sem = str(last_row[utilidades.COL_SEMANA])
        if last_sem.isdigit():
            next_sem = int(last_sem) + 1
            ent_semana.delete(0, tk.END)
            ent_semana.insert(0, str(next_sem))
        
        # Fecha
        last_date = last_row[utilidades.COL_PERIODO]
        if isinstance(last_date, pd.Timestamp):
            next_date = last_date + pd.Timedelta(days=7)
            ent_fecha.set_date(next_date)
    except Exception as e:
        print(f"No se pudo sugerir datos: {e}")

def limpiar_formulario():
    ent_semana.delete(0, tk.END)
    ent_fecha.set_date(datetime.date.today())
    ent_indice.delete(0, tk.END)
    ent_casos.delete(0, tk.END)
    # Intentar sugerir después de limpiar
    sugerir_siguientes_datos()

# ===================== UI =====================
def actualizar_tabla_ui():
    global df_datos
    for row in tabla.get_children():
        tabla.delete(row)
    if df_datos is None or df_datos.empty:
        return

    df_datos[utilidades.COL_INDICE_PREV] = df_datos[utilidades.COL_INDICE].shift(1)
    df_datos = calcular_modelo_b_completo(df_datos)

    for i, row in df_datos.iterrows():
        fecha_str = row[utilidades.COL_PERIODO].strftime('%d/%m/%Y') if isinstance(row[utilidades.COL_PERIODO], pd.Timestamp) else str(row[utilidades.COL_PERIODO])
        ind_t1 = row.get(utilidades.COL_INDICE_PREV, 0)
        ind_t1_str = f"{ind_t1:.1f}" if pd.notna(ind_t1) else "0.0"
        est_sin = row.get(utilidades.COL_EST_SIN, 0)
        est_con = row.get(utilidades.COL_EST_CON, 0)
        str_sin = f"{est_sin:.2f}" if est_sin != 0 else "-"
        str_con = f"{est_con:.2f}" if est_con != 0 else "-"
        tabla.insert("", tk.END, iid=str(i), values=[
            row[utilidades.COL_SEMANA], fecha_str, row[utilidades.COL_INDICE], ind_t1_str, row[utilidades.COL_CASOS], str_sin, str_con
        ])

def on_select(event):
    sel = tabla.selection()
    if not sel:
        return
    idx = int(sel[0])
    if df_datos is None or idx >= len(df_datos):
        return
    row = df_datos.iloc[idx]
    ent_semana.delete(0, tk.END); ent_semana.insert(0, str(row[utilidades.COL_SEMANA]))
    try:
        ent_fecha.set_date(row[utilidades.COL_PERIODO])
    except Exception:
        ent_fecha.set_date(datetime.date.today())
    ent_indice.delete(0, tk.END); ent_indice.insert(0, str(row[utilidades.COL_INDICE]))
    ent_casos.delete(0, tk.END); ent_casos.insert(0, str(row[utilidades.COL_CASOS]))

# ===================== GUI SETUP =====================
root = tk.Tk()
root.title("Gestor de Datos + Modelo B (Completo)")
root.state('zoomed')
estilos.aplicar_tema(root)

# Header
frame_header = tk.Frame(root, bg=estilos.COLOR_FONDO)
frame_header.pack(fill="x", pady=20)
tk.Label(frame_header, text="ADMINISTRACIÓN DE DATOS Y PROYECCIONES", font=estilos.FONT_H1, bg=estilos.COLOR_FONDO, fg=estilos.COLOR_TEXTO).pack()

estilos.crear_boton(frame_header, "⬅ Volver al Menú", root.destroy, tipo="secondary", width=20).pack(anchor="nw", padx=20)

# Input Card
card_input = estilos.crear_card(root)
card_input.pack(fill="x", padx=20, pady=10)
estilos.crear_label_subtitulo(card_input, "Datos Semanales", bg=estilos.COLOR_PANEL).pack(anchor="w", pady=(0, 10))

frame_form = tk.Frame(card_input, bg=estilos.COLOR_PANEL)
frame_form.pack(fill="x")

tk.Label(frame_form, text="Semana:", bg=estilos.COLOR_PANEL, fg="white", font=estilos.FONT_BODY).grid(row=0, column=0, padx=5)
ent_semana = tk.Entry(frame_form, width=10, font=estilos.FONT_BODY); ent_semana.grid(row=0, column=1, padx=5)

tk.Label(frame_form, text="Fecha:", bg=estilos.COLOR_PANEL, fg="white", font=estilos.FONT_BODY).grid(row=0, column=2, padx=5)
ent_fecha = DateEntry(frame_form, width=12, date_pattern='dd/mm/y', background=estilos.COLOR_ACCENT, foreground='white')
ent_fecha.grid(row=0, column=3, padx=5)

tk.Label(frame_form, text="Índice (t):", bg=estilos.COLOR_PANEL, fg="white", font=estilos.FONT_BODY).grid(row=0, column=4, padx=5)
ent_indice = tk.Entry(frame_form, width=10, font=estilos.FONT_BODY); ent_indice.grid(row=0, column=5, padx=5)

tk.Label(frame_form, text="Casos Reales:", bg=estilos.COLOR_PANEL, fg="white", font=estilos.FONT_BODY).grid(row=0, column=6, padx=5)
ent_casos = tk.Entry(frame_form, width=10, font=estilos.FONT_BODY); ent_casos.grid(row=0, column=7, padx=5)

# Actions
frame_actions = tk.Frame(card_input, bg=estilos.COLOR_PANEL)
frame_actions.pack(pady=15)
estilos.crear_boton(frame_actions, "💾 AGREGAR", agregar_registro, tipo="success", width=15).pack(side="left", padx=5)
estilos.crear_boton(frame_actions, "✏ EDITAR", actualizar_registro, tipo="warning", width=15).pack(side="left", padx=5)
estilos.crear_boton(frame_actions, "🗑 BORRAR", eliminar_registro, tipo="danger", width=15).pack(side="left", padx=5)
estilos.crear_boton(frame_actions, "LIMPIAR", limpiar_formulario, tipo="secondary", width=15).pack(side="left", padx=5)

# Prediction Card
card_pred = estilos.crear_card(root)
card_pred.pack(fill="x", padx=20, pady=5)
estilos.crear_label_subtitulo(card_pred, "Predicciones", bg=estilos.COLOR_PANEL).pack(anchor="w", pady=(0, 10))

frame_pred_actions = tk.Frame(card_pred, bg=estilos.COLOR_PANEL)
frame_pred_actions.pack(pady=5)

estilos.crear_boton(frame_pred_actions, "🔮 PREDECIR SIGUIENTE SEMANA", predecir_siguiente, tipo="info", width=30).pack(side="left", padx=10)
estilos.crear_boton(frame_pred_actions, "📈 Gráfica Reales vs Estimados", mostrar_grafica_serie, tipo="primary", width=30).pack(side="left", padx=10)

# Table
frame_table = tk.Frame(root, bg=estilos.COLOR_FONDO)
frame_table.pack(fill="both", expand=True, padx=20, pady=10)

cols = [utilidades.COL_SEMANA, utilidades.COL_PERIODO, utilidades.COL_INDICE, utilidades.COL_INDICE_PREV, utilidades.COL_CASOS, utilidades.COL_EST_SIN, utilidades.COL_EST_CON]
scroll = ttk.Scrollbar(frame_table, orient="vertical")
tabla = ttk.Treeview(frame_table, columns=cols, show="headings", yscrollcommand=scroll.set)
scroll.config(command=tabla.yview); scroll.pack(side="right", fill="y")
tabla.pack(side="left", fill="both", expand=True)

tabla.heading(utilidades.COL_SEMANA, text="Semana")
tabla.heading(utilidades.COL_PERIODO, text="Fecha")
tabla.heading(utilidades.COL_INDICE, text="Índice (t)")
tabla.heading(utilidades.COL_INDICE_PREV, text="Índice (t-1)")
tabla.heading(utilidades.COL_CASOS, text="Casos")
tabla.heading(utilidades.COL_EST_SIN, text="Est. SIN Intercepto")
tabla.heading(utilidades.COL_EST_CON, text="Est. CON Intercepto")
for c in cols:
    tabla.column(c, width=100, anchor="center")
tabla.bind("<<TreeviewSelect>>", on_select)

cargar_datos()
root.mainloop()
