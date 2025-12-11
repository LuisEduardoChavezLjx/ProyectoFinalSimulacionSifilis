# Documentación Técnica: Modelo B - Predictivo Dinámico (`modelo_b.py`)

## 1. Resumen del Componente
El módulo `modelo_b.py` implementa el **Modelo Dinámico de Tendencias**, el motor predictivo avanzado del sistema. A diferencia del Modelo A, que busca correlaciones estáticas, este componente se centra en la **predicción temporal** basada en tasas de cambio (Deltas). Su hipótesis fundamental es que un cambio brusco en el interés de búsqueda ($\Delta Indice$) precede y predice un cambio proporcional en los casos clínicos ($\Delta Casos$) para la semana siguiente.

## 2. Arquitectura y Diseño
Este módulo combina capacidades de gestión de datos (CRUD) con análisis predictivo en tiempo real.
*   **Motor de Cálculo Diferencial:** Transforma las series temporales absolutas en series de diferencias finitas (Deltas) para eliminar la no-estacionariedad y capturar tendencias a corto plazo.
*   **Persistencia y Estado:** Al igual que el gestor de datos, mantiene un estado local sincronizado con el archivo Excel, permitiendo agregar nuevas observaciones y recalcular el modelo instantáneamente.
*   **Visualización Interactiva:** Utiliza `matplotlib` con interactividad avanzada (cursores y tooltips) para comparar visualmente la serie real contra las estimaciones del modelo.

## 3. Funcionalidades Detalladas

### A. Transformación de Datos (Cálculo de Deltas)
El núcleo del algoritmo reside en la función `calcular_modelo_b_completo`.
1.  **Generación de Lags:** Alinea el índice de búsqueda de la semana anterior ($t-1$) con los casos actuales ($t$).
2.  **Diferenciación:** Calcula los cambios semana a semana:
    *   $\Delta Indice = Indice_{t-1} - Indice_{t-2}$
    *   $\Delta Casos = Casos_{t} - Casos_{t-1}$

### B. Entrenamiento del Modelo
Ajusta una regresión lineal sobre las diferencias:
$$ \Delta Casos \approx \alpha + \beta \cdot \Delta Indice $$
*   **$\beta$ (Sensibilidad):** Indica cuántos casos adicionales se esperan por cada punto de aumento en el interés de búsqueda.
*   **$\alpha$ (Intercepto/Drift):** Captura la tendencia base de aumento o disminución de casos independiente de las búsquedas.

### C. Reconstrucción y Predicción (Backtesting)
Una vez obtenidos los coeficientes, el sistema reconstruye la serie temporal para validar el modelo:
$$ CasosEstimados_{t} = CasosReales_{t-1} + (\alpha + \beta \cdot \Delta Indice) $$
Esto permite generar dos líneas de estimación:
1.  **Estimación SIN Intercepto:** Asume que si no hay cambio en búsquedas, los casos se mantienen estables.
2.  **Estimación CON Intercepto:** Incorpora la tendencia subyacente (drift) de la epidemia.

### D. Proyección a Futuro ($t+1$)
Utiliza los datos de la última semana registrada para pronosticar el futuro inmediato:
*   Toma los casos reales de la última semana como base.
*   Calcula el cambio reciente en el interés de búsqueda.
*   Aplica la fórmula del modelo para proyectar los casos de la siguiente semana, proporcionando una herramienta de alerta temprana.

## 4. Relevancia para la Investigación (IEEE)
El `modelo_b.py` representa la contribución principal del estudio en términos de **utilidad práctica**. Demuestra que, aunque la correlación estática (Modelo A) sea débil, la información contenida en la *variación* de las búsquedas digitales puede ser explotada para mejorar la precisión de los pronósticos a corto plazo. La visualización de "Reales vs. Estimados" permite validar gráficamente la capacidad del modelo para anticipar picos epidémicos, un elemento central en la discusión de resultados del paper.
