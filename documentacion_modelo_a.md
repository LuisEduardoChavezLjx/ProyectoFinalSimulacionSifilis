# Documentación Técnica: Modelo A - Análisis Correlacional (`modelo_a.py`)

## 1. Resumen del Componente
El módulo `modelo_a.py` implementa el **Análisis Estadístico Estático** del sistema. Su objetivo principal no es la predicción futura, sino la **validación de hipótesis**. Examina la existencia y fuerza de una relación lineal entre el interés de búsqueda en Google (variable independiente $x$) y los casos confirmados de sífilis (variable dependiente $y$), utilizando un enfoque de regresión clásica.

## 2. Arquitectura y Diseño
Este componente opera como un script de análisis de datos independiente, invocado por el orquestador principal. Su arquitectura se basa en el stack científico de Python:

*   **Procesamiento de Datos:** Utiliza `pandas` para la manipulación tabular y `numpy` para cálculos vectoriales.
*   **Motor Estadístico:** Emplea `scikit-learn` (`LinearRegression`) para el ajuste del modelo matemático.
*   **Visualización:** Integra `matplotlib` embebido en `tkinter` (vía `FigureCanvasTkAgg`) para generar gráficos interactivos dentro de la aplicación de escritorio.

## 3. Funcionalidades Detalladas

### A. Ingesta y Preprocesamiento de Datos
El módulo recibe la ruta del archivo de datos como argumento de línea de comandos (`sys.argv`), permitiendo su integración fluida con el `menu_principal.py`.
*   **Generación de Lags (Retardos):** Una característica crítica es la transformación temporal de los datos. El sistema calcula automáticamente la columna `Indice_t_1` (valor de búsqueda de la semana anterior), alineando la causa (búsqueda) con el efecto (reporte clínico) para simular el retraso natural en la atención médica.
*   **Limpieza:** Filtra automáticamente registros nulos o semanas iniciales sin historial previo, asegurando la robustez del cálculo.

### B. Análisis de Regresión Lineal Simple
Ejecuta el ajuste del modelo $y = \alpha + \beta x + \epsilon$, calculando métricas clave para la interpretación científica:
*   **Pendiente ($\beta$):** Cuantifica la sensibilidad de los casos ante cambios en las búsquedas.
*   **Intercepto ($\alpha$):** Representa la línea base de casos no explicados por las búsquedas.
*   **Coeficiente de Correlación de Pearson ($r$):** Mide la dirección y fuerza de la asociación lineal.
*   **Coeficiente de Determinación ($R^2$):** Métrica fundamental que indica qué porcentaje de la variabilidad de los casos es explicada por el modelo.

### C. Visualización e Interpretación
*   **Gráfico de Dispersión:** Genera un plot XY donde cada punto es una semana epidemiológica. Superpone la recta de regresión ajustada para visualizar la tendencia.
*   **Interpretación Automática:** El sistema evalúa el valor de $R^2$ y genera una conclusión en lenguaje natural (e.g., "NO existe relación lineal significativa"), ayudando al investigador a descartar falsos positivos rápidamente.

## 4. Relevancia para la Investigación (IEEE)
En el marco del estudio, el `modelo_a.py` cumple una función de **control y validación**. Antes de aplicar modelos predictivos complejos (como el Modelo B), es necesario establecer si existe una correlación base. Este módulo permite demostrar formalmente si las búsquedas de Google son un proxy válido para la vigilancia epidemiológica en un contexto estático, o si es necesario recurrir a modelos dinámicos de tendencias (Deltas) debido a la no-estacionariedad de los datos.
