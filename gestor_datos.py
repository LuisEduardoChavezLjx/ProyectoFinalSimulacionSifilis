import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import datetime
import os
try:
    from tkcalendar import DateEntry
except ImportError:
    messagebox.showerror("Error", "Falta tkcalendar. Instala: pip install tkcalendar")
import utilidades
import estilos

# ===================== VARIABLES GLOBALES =====================
df_datos = None
ruta_actual = None  # Ruta del archivo de trabajo actual
modelo_alpha = 0.0
modelo_beta = 0.0
modelo_listo = False

# Variables para el modelo de referencia (Cold Start)
ref_alpha = None
ref_beta = None
ref_nombre = None

# ===================== LÓGICA =====================
def inicializar_nuevo():
    """Inicializa el gestor con una tabla vacía."""
    global df_datos, ruta_actual
    df_datos = pd.DataFrame(columns=[utilidades.COL_SEMANA, utilidades.COL_PERIODO, utilidades.COL_INDICE, utilidades.COL_INDICE_PREV, utilidades.COL_CASOS])
    ruta_actual = None
    actualizar_tabla_ui()
    sugerir_siguientes_datos()

def cargar_modelo_referencia():
    """Carga un Excel antiguo para usar su fórmula."""
    global ref_alpha, ref_beta, ref_nombre
    ruta = filedialog.askopenfilename(
        title="Selecciona un Excel ANTERIOR (Modelo de Referencia)",
        filetypes=[("Excel", "*.xlsx *.xls")]
    )
    if not ruta:
        return

    try:
        df_ref = pd.read_excel(ruta)
        # Normalizar columnas (intento básico)
        df_ref = df_ref.rename(columns={
            "Numero de Semana Epidemiologica": utilidades.COL_SEMANA,
            "Indice": utilidades.COL_INDICE,
            "Indice t-1": utilidades.COL_INDICE_PREV,
            "Casos Reportados": utilidades.COL_CASOS
        })
        
        alpha, beta = utilidades.calcular_coeficientes(df_ref)
        
        if alpha is not None:
            ref_alpha = alpha
            ref_beta = beta
            ref_nombre = os.path.basename(ruta)
            lbl_ref_status.config(text=f"Referencia: {ref_nombre}", fg=estilos.COLOR_SUCCESS)
            messagebox.showinfo("Referencia Cargada", f"Se usará la fórmula de:\n{ref_nombre}\n\nCuando no haya suficientes datos nuevos.")
        else:
            messagebox.showwarning("Error", "El archivo seleccionado no tiene suficientes datos para crear un modelo.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo cargar la referencia:\n{e}")

def accion_abrir():
    """Abre un archivo Excel existente."""
    global df_datos, ruta_actual
    df, ruta = utilidades.leer_excel()
    if df is None:
        return
    
    df_datos = df.sort_values(by=utilidades.COL_PERIODO).reset_index(drop=True)
    ruta_actual = ruta
    actualizar_tabla_ui()
    sugerir_siguientes_datos()

def accion_guardar():
    """Guarda los datos actuales en un archivo Excel."""
    global df_datos, ruta_actual
    if df_datos is None or df_datos.empty:
        messagebox.showwarning("Aviso", "No hay datos para guardar.")
        return
    
    # Guardar usando utilidades
    nueva_ruta = utilidades.guardar_excel(df_datos, ruta_actual)
    
    if nueva_ruta:
        ruta_actual = nueva_ruta

def actualizar_memoria():
    """Ordena los datos y actualiza la tabla sin guardar en disco."""
    global df_datos
    if df_datos is None:
        return
    df_datos = df_datos.sort_values(by=utilidades.COL_PERIODO).reset_index(drop=True)
    actualizar_tabla_ui()

def predecir_siguiente():
    global df_datos, modelo_alpha, modelo_beta, modelo_listo
    global ref_alpha, ref_beta, ref_nombre

    if df_datos is None or df_datos.empty:
        messagebox.showwarning("Aviso", "No hay datos suficientes.")
        return
    
    # Determinar qué modelo usar
    usando_referencia = False
    alpha_uso = modelo_alpha
    beta_uso = modelo_beta
    
    if not modelo_listo:
        if ref_alpha is not None:
            alpha_uso = ref_alpha
            beta_uso = ref_beta
            usando_referencia = True
        else:
            messagebox.showwarning("Aviso", "Se necesitan al menos 3 semanas para el modelo propio.\n\n💡 TIP: Carga un 'Modelo de Referencia' para predecir desde la semana 1.")
            return

    last_row = df_datos.iloc[-1]
    try:
        casos_actuales = last_row[utilidades.COL_CASOS]
        semana_actual = last_row[utilidades.COL_SEMANA]
        delta_ind_next = last_row[utilidades.COL_INDICE] - last_row[utilidades.COL_INDICE_PREV]
        
        pred_sin = casos_actuales + beta_uso * delta_ind_next
        pred_con = casos_actuales + alpha_uso + beta_uso * delta_ind_next
        
        titulo_msg = "Predicción Futura"
        if usando_referencia:
            titulo_msg += " (USANDO REFERENCIA)"
            subtitulo = f"⚠️ USANDO FÓRMULA DE: {ref_nombre}"
        else:
            subtitulo = "✅ Usando modelo propio (Datos actuales)"

        mensaje = (
            f"{subtitulo}\n"
            f"----------------------------------------------------\n"
            f"📊 PREDICCIÓN PARA LA SIGUIENTE SEMANA (aprox. {int(semana_actual)+1})\n"
            f"• Casos última semana: {casos_actuales}\n"
            f"• Tendencia del Índice Google: {delta_ind_next:+.2f}\n\n"
            f"RESULTADOS:\n"
            f"🟢 Estimado SIN intercepto:  {pred_sin:.2f} casos\n"
            f"🔵 Estimado CON intercepto:  {pred_con:.2f} casos\n"
        )
        messagebox.showinfo(titulo_msg, mensaje)
    except Exception as e:
        messagebox.showerror("Error de Cálculo", f"No se pudo predecir: {e}")

# ===================== CRUD =====================
def agregar_registro():
    global df_datos
    try:
        sem = ent_semana.get().strip()
        fecha = pd.Timestamp(ent_fecha.get_date())
        ind = float(ent_indice.get().strip())
        casos = float(ent_casos.get().strip())
        if sem == "": return
        nueva = {utilidades.COL_SEMANA: sem, utilidades.COL_PERIODO: fecha, utilidades.COL_INDICE: ind, utilidades.COL_INDICE_PREV: 0, utilidades.COL_CASOS: casos}
        if df_datos is None:
            df_datos = pd.DataFrame([nueva])
        else:
            df_datos = pd.concat([df_datos, pd.DataFrame([nueva])], ignore_index=True)
        actualizar_memoria()
        limpiar_formulario()
    except ValueError:
        messagebox.showerror("Error", "Números inválidos.")

def actualizar_registro():
    global df_datos
    sel = tabla.selection()
    if not sel: return
    try:
        idx = int(sel[0])
        df_datos.at[idx, utilidades.COL_SEMANA] = ent_semana.get().strip()
        df_datos.at[idx, utilidades.COL_PERIODO] = pd.Timestamp(ent_fecha.get_date())
        df_datos.at[idx, utilidades.COL_INDICE] = float(ent_indice.get().strip())
        df_datos.at[idx, utilidades.COL_CASOS] = float(ent_casos.get().strip())
        actualizar_memoria()
        limpiar_formulario()
    except ValueError:
        messagebox.showerror("Error", "Datos inválidos.")

def eliminar_registro():
    global df_datos
    sel = tabla.selection()
    if not sel: return
    if messagebox.askyesno("Confirmar", "¿Eliminar?"):
        idx = int(sel[0])
        df_datos = df_datos.drop(df_datos.index[idx]).reset_index(drop=True)
        actualizar_memoria()
        limpiar_formulario()

def sugerir_siguientes_datos():
    if df_datos is None or df_datos.empty: return
    try:
        last_row = df_datos.iloc[-1]
        last_sem = str(last_row[utilidades.COL_SEMANA])
        if last_sem.isdigit():
            next_sem = int(last_sem) + 1
            ent_semana.delete(0, tk.END); ent_semana.insert(0, str(next_sem))
        last_date = last_row[utilidades.COL_PERIODO]
        if isinstance(last_date, pd.Timestamp):
            next_date = last_date + pd.Timedelta(days=7)
            ent_fecha.set_date(next_date)
    except Exception as e: print(f"No se pudo sugerir datos: {e}")

def limpiar_formulario():
    ent_semana.delete(0, tk.END)
    ent_fecha.set_date(datetime.date.today())
    ent_indice.delete(0, tk.END)
    ent_casos.delete(0, tk.END)
    sugerir_siguientes_datos()

# ===================== UI =====================
def actualizar_tabla_ui():
    global df_datos, modelo_alpha, modelo_beta, modelo_listo
    for row in tabla.get_children(): tabla.delete(row)
    if df_datos is None or df_datos.empty: return
    
    df_datos = utilidades.calcular_modelo_b_completo(df_datos)
    
    # Recalcular modelo local
    alpha, beta = utilidades.calcular_coeficientes(df_datos)
    if alpha is not None:
        modelo_alpha = alpha
        modelo_beta = beta
        modelo_listo = True
    else:
        modelo_listo = False

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
    if not sel: return
    idx = int(sel[0])
    if df_datos is None or idx >= len(df_datos): return
    row = df_datos.iloc[idx]
    ent_semana.delete(0, tk.END); ent_semana.insert(0, str(row[utilidades.COL_SEMANA]))
    try: ent_fecha.set_date(row[utilidades.COL_PERIODO])
    except: ent_fecha.set_date(datetime.date.today())
    ent_indice.delete(0, tk.END); ent_indice.insert(0, str(row[utilidades.COL_INDICE]))
    ent_casos.delete(0, tk.END); ent_casos.insert(0, str(row[utilidades.COL_CASOS]))

# ===================== GUI SETUP =====================
root = tk.Tk()
root.title("Gestor de Datos en Vivo")
root.state('zoomed')
estilos.aplicar_tema(root)

# HEADER
frame_header = tk.Frame(root, bg=estilos.COLOR_FONDO)
frame_header.pack(fill="x", pady=20)
tk.Label(frame_header, text="GESTIÓN DE DATOS Y PROYECCIONES", font=estilos.FONT_H1, bg=estilos.COLOR_FONDO, fg=estilos.COLOR_TEXTO).pack()
estilos.crear_boton(frame_header, "⬅ Volver al Menú", root.destroy, tipo="secondary", width=20).pack(anchor="nw", padx=20)

# INPUT CARD
card_input = estilos.crear_card(root)
card_input.pack(fill="x", padx=20, pady=10)
estilos.crear_label_subtitulo(card_input, "📝 Registro Semanal", bg=estilos.COLOR_PANEL).pack(anchor="w", pady=(0, 10))

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

# ACTIONS
frame_actions = tk.Frame(card_input, bg=estilos.COLOR_PANEL)
frame_actions.pack(pady=15)
estilos.crear_boton(frame_actions, "➕ AGREGAR", agregar_registro, tipo="success", width=15).pack(side="left", padx=5)
estilos.crear_boton(frame_actions, "✏ EDITAR", actualizar_registro, tipo="warning", width=15).pack(side="left", padx=5)
estilos.crear_boton(frame_actions, "🗑 BORRAR", eliminar_registro, tipo="danger", width=15).pack(side="left", padx=5)
estilos.crear_boton(frame_actions, "🧹 LIMPIAR", limpiar_formulario, tipo="secondary", width=15).pack(side="left", padx=5)
estilos.crear_boton(frame_actions, "📂 ABRIR ARCHIVO", accion_abrir, tipo="info", width=20).pack(side="left", padx=20)
estilos.crear_boton(frame_actions, "💾 GUARDAR ARCHIVO", accion_guardar, tipo="success", width=20).pack(side="left", padx=5)

# PREDICTION CARD
card_pred = estilos.crear_card(root)
card_pred.pack(fill="x", padx=20, pady=5)
estilos.crear_label_subtitulo(card_pred, "🔮 Predicción y Modelos", bg=estilos.COLOR_PANEL).pack(anchor="w", pady=(0, 10))

# Status label for reference model
lbl_ref_status = tk.Label(card_pred, text="Referencia: Ninguna (Usando modelo local)", font=estilos.FONT_SMALL, bg=estilos.COLOR_PANEL, fg=estilos.COLOR_TEXTO_SEC)
lbl_ref_status.pack(pady=2)

frame_pred_actions = tk.Frame(card_pred, bg=estilos.COLOR_PANEL)
frame_pred_actions.pack(pady=5)

estilos.crear_boton(frame_pred_actions, "📂 Cargar Modelo de Referencia", cargar_modelo_referencia, tipo="secondary", width=30).pack(side="left", padx=10)
estilos.crear_boton(frame_pred_actions, "✨ PREDECIR SIGUIENTE SEMANA", predecir_siguiente, tipo="info", width=30).pack(side="left", padx=10)


# TABLE
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
tabla.heading(utilidades.COL_EST_SIN, text="Est. SIN Int")
tabla.heading(utilidades.COL_EST_CON, text="Est. CON Int")
for c in cols: tabla.column(c, width=100, anchor="center")
tabla.bind("<<TreeviewSelect>>", on_select)

inicializar_nuevo()
root.mainloop()
