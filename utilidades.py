import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import os
from tkinter import filedialog, messagebox

# ===================== CONSTANTES =====================
COL_SEMANA = "Semana"
COL_PERIODO = "Periodo"
COL_INDICE = "Indice_t"
COL_INDICE_PREV = "Indice_t_1"
COL_CASOS = "Casos_t"
COL_EST_SIN = "Est_Sin_Int"
COL_EST_CON = "Est_Con_Int"

# ===================== UTILIDADES =====================
def leer_excel(ruta_excel=None):
    if not ruta_excel:
        ruta_excel = filedialog.askopenfilename(
            title="Selecciona el Excel de datos",
            filetypes=[("Excel", "*.xlsx *.xls")]
        )
    if not ruta_excel or not os.path.exists(ruta_excel):
        return None

    try:
        df = pd.read_excel(ruta_excel, sheet_name=0)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo leer el Excel:\n{e}")
        return None

    # Normalización de nombres
    df = df.rename(columns={
        "Numero de Semana Epidemiologica": COL_SEMANA,
        "No. Semana": COL_SEMANA,
        "Indice": COL_INDICE,
        "Indice t-1": COL_INDICE_PREV,
        "Casos Reportados": COL_CASOS,
        "Casos": COL_CASOS
    })

    cols_necesarias = [COL_SEMANA, COL_PERIODO, COL_INDICE, COL_INDICE_PREV, COL_CASOS]
    for col in cols_necesarias:
        if col not in df.columns:
            df[col] = np.nan

    if COL_PERIODO in df.columns:
        df[COL_PERIODO] = pd.to_datetime(df[COL_PERIODO], errors="coerce")

    return df[cols_necesarias].copy(), ruta_excel

def guardar_excel(df, ruta_excel=None):
    if not ruta_excel:
        ruta_excel = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx *.xls")]
        )
    if not ruta_excel:
        return

    try:
        df_export = df.copy()
        # Limpiar columnas calculadas antes de guardar
        for col in [COL_EST_SIN, COL_EST_CON]:
            if col in df_export.columns:
                df_export = df_export.drop(columns=[col])
        
        df_export = df_export.rename(columns={
            COL_SEMANA: "Numero de Semana Epidemiologica",
            COL_INDICE: "Indice",
            COL_INDICE_PREV: "Indice t-1",
            COL_CASOS: "Casos Reportados"
        })
        df_export.to_excel(ruta_excel, index=False)
        messagebox.showinfo("Guardado", f"Datos guardados en:\n{ruta_excel}")
        return ruta_excel
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar:\n{e}")
        return None

def calcular_coeficientes(df):
    """Calcula alpha y beta para un dataframe dado."""
    if df is None or len(df) < 3:
        return None, None
    
    df_calc = df.copy()
    df_calc[COL_INDICE_PREV] = df_calc[COL_INDICE].shift(1)
    df_calc["Delta_Casos"] = df_calc[COL_CASOS].diff()
    df_calc["Delta_Indice"] = df_calc[COL_INDICE_PREV].diff()

    df_train = df_calc.dropna(subset=["Delta_Casos", "Delta_Indice"])
    if df_train.empty:
        return None, None

    try:
        X = df_train[["Delta_Indice"]].values
        y = df_train["Delta_Casos"].values
        modelo = LinearRegression(fit_intercept=True)
        modelo.fit(X, y)
        return modelo.intercept_, modelo.coef_[0]
    except Exception:
        return None, None

def calcular_modelo_b_completo(df):
    df[COL_EST_SIN] = 0.0
    df[COL_EST_CON] = 0.0

    if df is None or len(df) < 3:
        return df

    alpha, beta = calcular_coeficientes(df)
    if alpha is None:
        return df

    lista_sin = [0.0] * len(df)
    lista_con = [0.0] * len(df)
    
    # Recalcular deltas para la proyección
    df_calc = df.copy()
    df_calc[COL_INDICE_PREV] = df_calc[COL_INDICE].shift(1)
    
    for i in range(1, len(df)):
        casos_prev = df_calc.iloc[i - 1][COL_CASOS]
        ind_t1_actual = df_calc.iloc[i][COL_INDICE_PREV]
        ind_t1_prev = df_calc.iloc[i - 1][COL_INDICE_PREV]
        
        delta_ind = 0
        if pd.notna(ind_t1_actual) and pd.notna(ind_t1_prev):
            delta_ind = ind_t1_actual - ind_t1_prev
            
        est_sin = casos_prev + beta * delta_ind
        est_con = casos_prev + alpha + beta * delta_ind
        lista_sin[i] = est_sin
        lista_con[i] = est_con

    df[COL_EST_SIN] = lista_sin
    df[COL_EST_CON] = lista_con
    return df

def generar_plantilla():
    """Genera una plantilla de Excel vacía con las columnas requeridas."""
    ruta = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel", "*.xlsx")],
        title="Guardar Plantilla de Datos"
    )
    if not ruta:
        return

    try:
        # Crear DataFrame vacío con las columnas requeridas
        df_vacio = pd.DataFrame(columns=[
            "Numero de Semana Epidemiologica",
            "Periodo",
            "Indice",
            "Casos Reportados"
        ])
        
        # Guardar
        df_vacio.to_excel(ruta, index=False)
        messagebox.showinfo("Éxito", f"Plantilla guardada en:\n{ruta}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar la plantilla:\n{e}")
