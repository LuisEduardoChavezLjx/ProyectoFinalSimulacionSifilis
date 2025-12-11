# Documentación Técnica: Gestor de Datos y Proyecciones (`gestor_datos.py`)

## 1. Resumen del Componente
El módulo `gestor_datos.py` funciona como el sistema de administración de información (DBMS) del proyecto. Más allá de un simple editor de datos, este componente integra la lógica del **Modelo B (Dinámico)** en tiempo real, permitiendo a los investigadores observar cómo la adición o modificación de registros epidemiológicos altera instantáneamente las proyecciones y los coeficientes del modelo matemático.

## 2. Arquitectura y Diseño
El sistema implementa una arquitectura de **persistencia diferida** con procesamiento en memoria:

*   **Manipulación en Memoria (In-Memory Processing):** Utiliza un `DataFrame` de `pandas` como estructura de datos principal (`df_datos`). Todas las operaciones CRUD (Crear, Leer, Actualizar, Borrar) se realizan sobre esta estructura volátil para garantizar una respuesta inmediata de la interfaz.
*   **Sincronización con Archivos:** La persistencia se maneja explícitamente a través de funciones de lectura/escritura (`accion_abrir`, `accion_guardar`) que serializan el DataFrame a formato Excel (`.xlsx`), asegurando la integridad de la base de datos física.
*   **Recálculo Reactivo:** El sistema sigue un patrón reactivo; cualquier modificación en los datos dispara automáticamente el recálculo de los coeficientes del modelo predictivo ($\alpha, \beta$) y actualiza las columnas de estimación en la interfaz visual.

## 3. Funcionalidades Detalladas

### A. Gestión de Datos (CRUD)
Proporciona un formulario estructurado para el ingreso de variables críticas:
*   **Semana Epidemiológica:** Identificador temporal.
*   **Fecha:** Selección precisa mediante calendario (`tkcalendar`).
*   **Índice de Google ($x$):** Variable predictora.
*   **Casos Reales ($y$):** Variable objetivo.

El sistema incluye validación de tipos de datos y sugerencia automática de valores para el siguiente registro (e.g., autoincremento de semana), optimizando el flujo de trabajo de captura.

### B. Motor de Predicción en Tiempo Real
A diferencia de los modelos estáticos, este gestor evalúa la capacidad predictiva del modelo dinámicamente:
*   **Cálculo de Deltas:** Computa automáticamente las diferencias $\Delta Indice$ y $\Delta Casos$ internamente.
*   **Estimación Continua:** Para cada fila, calcula dos proyecciones retrospectivas ("Sin Intercepto" y "Con Intercepto") para que el usuario visualice el error del modelo histórico al instante.

### C. Manejo de "Cold Start" (Modelo de Referencia)
Una innovación clave es la capacidad de cargar un **Modelo de Referencia**.
*   *Problema:* Al iniciar una nueva vigilancia (e.g., año 2025), no hay suficientes datos históricos para entrenar un modelo estable (se requieren n > 3).
*   *Solución:* El sistema permite importar los coeficientes ($\alpha, \beta$) de un archivo histórico (e.g., 2024) para realizar predicciones en las primeras semanas del nuevo periodo, hasta que se acumule suficiente data propia.

### D. Proyección a Futuro
Incluye una función dedicada (`predecir_siguiente`) que toma los datos de la última semana registrada y, utilizando la tendencia actual del índice de búsqueda, estima los casos esperados para la semana entrante ($t+1$).

## 4. Relevancia para la Investigación (IEEE)
Este módulo es fundamental para la sección de **Metodología Experimental** del paper. Demuestra cómo el sistema mitiga el problema de la escasez de datos iniciales (Cold Start) y valida la hipótesis de que el modelo dinámico puede adaptarse a nuevas tendencias en tiempo real. La capacidad de visualizar la convergencia del modelo conforme se agregan datos refuerza la robustez de la propuesta matemática.
