# Documentación Técnica del Sistema de Epidemiología Digital

Este documento detalla el funcionamiento, lógica y dependencias de los componentes principales del sistema.

## 1. Archivo: `menu_principal.py`

### Descripción General
Es el punto de entrada de la aplicación. Proporciona una interfaz gráfica (GUI) principal que permite al usuario navegar entre los diferentes módulos del sistema (Gestor de Datos, Modelo A, Modelo B y Corrección Modelo B).

### Funcionalidades
*   **Interfaz Gráfica Principal:** Ventana maximizada con botones de navegación claros.
*   **Selección de Archivo de Datos:** Permite al usuario seleccionar un archivo Excel (`.xlsx` o `.xls`) que servirá como fuente de datos para los modelos A y B. La ruta del archivo se almacena en una variable global `RUTA_EXCEL`.
*   **Ejecución de Módulos:** Lanza otros scripts de Python (`subprocess`) pasando, si es necesario, la ruta del archivo Excel seleccionado como argumento de línea de comandos.
*   **Marco Teórico:** Incluye una sección informativa ("Presentación y Marco Teórico") que explica el contexto, objetivos y metodología del proyecto.

### Lógica de Implementación
*   Usa `tkinter` para la GUI.
*   La función `ejecutar_script` utiliza `subprocess.Popen` para abrir los otros archivos `.py` en procesos separados. Esto permite que cada módulo funcione de manera independiente pero iniciado desde un punto central.
*   Gestiona la ruta del archivo Excel globalmente para pasarla a los submódulos.

### Librerías Utilizadas
*   `tkinter`: Para la interfaz gráfica (ventanas, botones, etiquetas, cuadros de diálogo).
*   `subprocess`: Para ejecutar otros scripts de Python.
*   `sys`: Para obtener el ejecutable de Python actual.
*   `os`: Para verificar la existencia de archivos.

---

## 2. Archivo: `modelo_a.py`

### Descripción General
Implementa el **Modelo A (Correlacional)**. Su objetivo es analizar la relación estadística entre el índice de búsquedas de Google (variable independiente) y los casos reportados de sífilis (variable dependiente).

### Funcionalidades
*   **Carga de Datos:** Lee el archivo Excel seleccionado.
*   **Análisis Estadístico:** Calcula la regresión lineal simple entre el índice de Google de la semana anterior ($t-1$) y los casos actuales ($t$).
*   **Métricas:** Muestra la Pendiente ($\beta$), Intercepto ($\alpha$), Coeficiente de Correlación de Pearson ($r$) y el Coeficiente de Determinación ($R^2$).
*   **Visualización:** Genera un gráfico de dispersión con la línea de tendencia ajustada.
*   **Interpretación:** Proporciona una conclusión automática basada en el valor de $R^2$ para determinar si existe una relación lineal significativa.

### Lógica de Implementación
*   Utiliza `pandas` para manipular los datos.
*   Calcula la columna `Indice_t_1` (lag de 1 semana) si no existe.
*   Usa `sklearn.linear_model.LinearRegression` para ajustar el modelo $y = \alpha + \beta x$.
*   Calcula $R^2$ y correlación usando `numpy`.
*   La interfaz gráfica muestra los resultados numéricos y permite abrir una ventana secundaria con el gráfico de `matplotlib`.

### Librerías Utilizadas
*   `tkinter`: GUI.
*   `pandas`: Manipulación y análisis de datos.
*   `numpy`: Cálculos numéricos (correlación).
*   `sklearn` (`scikit-learn`): Modelo de Regresión Lineal.
*   `matplotlib`: Generación de gráficos.
*   `os`, `sys`: Gestión de sistema y argumentos.

---

## 3. Archivo: `modelo_b.py`

### Descripción General
Implementa el **Modelo B (Predictivo Dinámico)**. Este modelo se centra en predecir los casos futuros basándose en los *cambios* (deltas) de las búsquedas, en lugar de los valores absolutos.

### Funcionalidades
*   **Cálculo de Deltas:** Calcula la diferencia semana a semana de los casos ($\Delta Casos$) y del índice de Google ($\Delta Indice$).
*   **Entrenamiento:** Ajusta una regresión lineal sobre estas diferencias: $\Delta Casos \approx \beta \cdot \Delta Indice$.
*   **Predicción:** Genera dos líneas de estimación:
    1.  **Sin Intercepto:** Asume que si no hay cambio en búsquedas, no hay cambio base en casos (más allá de la tendencia).
    2.  **Con Intercepto:** Incluye un término constante de ajuste.
*   **Proyección Futura:** Permite predecir los casos de la *siguiente semana* basándose en los últimos datos disponibles.
*   **Visualización:** Gráfica de serie temporal comparando los casos reales con las estimaciones del modelo.

### Lógica de Implementación
*   Calcula diferencias usando `df.diff()`.
*   Entrena el modelo usando solo las filas donde existen ambos deltas.
*   Reconstruye la serie temporal de casos estimados sumando el cambio predicho a los casos de la semana anterior: $Casos_t = Casos_{t-1} + \Delta Estimado$.
*   Incluye manejo de errores para asegurar que haya suficientes datos para el cálculo.

### Librerías Utilizadas
*   `tkinter`: GUI.
*   `pandas`: Manipulación de datos y series temporales.
*   `numpy`: Operaciones numéricas.
*   `sklearn`: Regresión Lineal.
*   `matplotlib`: Gráficos de series temporales interactivos.
*   `tkcalendar`: Widget de calendario para selección de fechas (aunque se usa más en el gestor, se importa aquí por consistencia o reutilización).
*   `os`, `sys`, `datetime`.

---

## 4. Archivo: `gestor_datos.py`

### Descripción General
Es el módulo de administración de la base de datos (CRUD). Permite al usuario ver, agregar, editar y eliminar registros del archivo Excel directamente desde la aplicación. Además, integra la lógica del Modelo B para mostrar proyecciones en tiempo real conforme se agregan datos.

### Funcionalidades
*   **CRUD Completo:** Crear, Leer, Actualizar y Borrar registros epidemiológicos.
*   **Tabla Interactiva:** Muestra los datos en una tabla (`Treeview`) incluyendo las columnas calculadas de estimación.
*   **Persistencia:** Guarda los cambios automáticamente en el archivo Excel.
*   **Predicción Integrada:** Al igual que `modelo_b.py`, calcula y muestra proyecciones futuras basadas en los datos actuales.
*   **Formulario de Entrada:** Campos para ingresar Semana, Fecha, Índice y Casos, con sugerencia automática para el siguiente registro.

### Lógica de Implementación
*   Mantiene un `DataFrame` de `pandas` en memoria (`df_datos`) que se sincroniza con el archivo Excel.
*   Cada vez que se modifica la tabla (agregar/editar/borrar), se recalcula el Modelo B completo para actualizar las columnas de estimación (`Est. SIN Intercepto`, `Est. CON Intercepto`).
*   Usa `tkcalendar` para facilitar la entrada de fechas.

### Librerías Utilizadas
*   `tkinter`: GUI y widgets (Treeview).
*   `pandas`: Manejo de la base de datos en memoria.
*   `tkcalendar`: Selección de fechas.
*   `sklearn`: Para recalcular el modelo predictivo en tiempo real.
*   `numpy`, `os`, `datetime`.
