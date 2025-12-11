# Documentación Técnica: Módulo de Interfaz Principal (`menu_principal.py`)

## 1. Resumen del Componente
El archivo `menu_principal.py` constituye el núcleo de orquestación del *Sistema de Epidemiología Digital*. Su propósito fundamental es proveer una interfaz gráfica unificada que integre los diversos modelos de simulación y herramientas de gestión de datos del proyecto. Actúa como el punto de entrada (entry point) de la aplicación, facilitando la interacción del usuario con los algoritmos matemáticos subyacentes sin necesidad de manipulación directa de código.

## 2. Arquitectura y Diseño
El módulo está construido sobre la librería estándar `tkinter` de Python, siguiendo un patrón de diseño orientado a eventos. La arquitectura se caracteriza por el desacoplamiento entre la interfaz de usuario y la lógica de negocio:

*   **Orquestador de Procesos:** El menú principal no ejecuta los cálculos intensivos. En su lugar, actúa como un *dispatcher* que instancia procesos independientes para cada submódulo (`modelo_a.py`, `modelo_b.py`, `gestor_datos.py`) utilizando la librería `subprocess`. Esto asegura que la estabilidad de la interfaz no se vea comprometida por la ejecución de los modelos matemáticos.
*   **Gestión de Estado Global:** Implementa un mecanismo de inyección de dependencias simple. La ruta del conjunto de datos (archivo Excel) se selecciona una única vez en este módulo y se propaga automáticamente a los subsistemas de predicción. Esto garantiza la consistencia de los datos en todos los experimentos de la simulación.

## 3. Funcionalidades Detalladas

### A. Configuración del Entorno de Simulación
El módulo permite la carga inicial de la base de datos epidemiológica. Mediante el uso de `filedialog`, el usuario selecciona el archivo fuente (`.xlsx`), cuya ruta es validada y almacenada en memoria (`RUTA_EXCEL`). Esta funcionalidad es crítica para asegurar que tanto el modelo correlacional como el predictivo operen sobre el mismo *dataset*.

### B. Módulo Educativo (Marco Teórico)
Integra una sección de "Presentación y Marco Teórico" que contextualiza la simulación. A través de una ventana secundaria, expone los fundamentos matemáticos de los modelos utilizados:
*   **Modelo A:** Explica la Regresión Lineal Simple y el Coeficiente de Pearson para el análisis estático.
*   **Modelo B:** Detalla el modelo dinámico basado en "Deltas" (cambios) y la fórmula de predicción $Casos(t) = Casos(t-1) + \beta \cdot \Delta Indice$.

### C. Ejecución de Modelos
Proporciona controles directos para lanzar las simulaciones:
1.  **Gestión de Datos:** Abre la herramienta CRUD para la manipulación en tiempo real de los registros.
2.  **Modelo A (Correlacional):** Ejecuta el análisis estadístico para evaluar la relación lineal entre búsquedas y casos.
3.  **Modelo B (Predictivo):** Inicia el modelo de tendencias para proyectar escenarios futuros.

### D. Descarga de Plantilla
Se incluye una funcionalidad para descargar una plantilla preformateada del archivo de datos (`plantilla_sifilis.xlsx`). Esta característica es fundamental para garantizar la integridad de los datos de entrada, proporcionando al usuario un esquema estandarizado con las columnas requeridas ('Semana', 'Casos', 'Busquedas') para el correcto funcionamiento de los algoritmos de predicción.

## 4. Relevancia para la Investigación (IEEE)
En el contexto del documento IEEE, este componente es esencial para demostrar la **usabilidad y reproducibilidad** del sistema propuesto. La centralización de la ejecución permite realizar pruebas comparativas rápidas entre los distintos modelos matemáticos, facilitando la validación de la hipótesis sobre la relación entre el comportamiento digital y la epidemiología real de la sífilis en México.
