# Documentación: Módulo de Consulta de Datos Externos

**Fecha de Actualización:** 04 de Diciembre de 2025
**Archivo Relacionado:** `menu_principal.py`

## 1. Descripción General
Se ha incorporado una nueva sección denominada **"Consultar Datos"** en el panel lateral izquierdo del Menú Principal. Este módulo tiene como objetivo facilitar la adquisición de los datos primarios necesarios para alimentar los modelos matemáticos del proyecto (Modelo A y Modelo B).

## 2. Funcionalidades Implementadas

### A. Selector Dinámico de Google Trends
Esta función permite al usuario generar consultas personalizadas a la herramienta Google Trends directamente desde la aplicación.

*   **Cómo funciona:**
    1.  Al hacer clic en el botón **"Google Trends"**, se abre una ventana emergente.
    2.  El usuario selecciona una **Fecha de Inicio** y una **Fecha de Fin** utilizando un calendario visual interactivo.
    3.  El sistema valida que:
        *   La fecha final no sea posterior al día actual (evitando errores de predicción futura inexistente).
        *   La fecha de inicio sea anterior a la fecha final.
    4.  Al confirmar, el sistema construye automáticamente una URL con los parámetros precisos:
        *   **Término de búsqueda:** `/m/074m2` (Identificador de entidad para "Sífilis").
        *   **Geolocalización:** `MX` (México).
        *   **Rango de fechas:** El intervalo seleccionado por el usuario.
    5.  Se abre el navegador web predeterminado con los resultados listos para descargar.

### B. Acceso al Boletín Epidemiológico
Un acceso directo al repositorio oficial de la Secretaría de Salud.

*   **Cómo funciona:**
    *   El botón **"Boletín Epidemiológico"** redirige inmediatamente al usuario a la página del Sistema Nacional de Vigilancia Epidemiológica (SINAVE), donde se publican los reportes semanales de casos nuevos.

## 3. Importancia para el Proyecto

Este cambio es crítico para el flujo de trabajo de la **Epidemiología Digital** por las siguientes razones:

1.  **Estandarización de la Búsqueda:**
    *   Para que el modelo matemático funcione, es vital que siempre se busque el *mismo término* ("Sífilis" como enfermedad, no como palabra clave genérica) y en la *misma región*. El botón automatiza esto, eliminando el error humano de buscar términos incorrectos que alterarían el "Índice de Google" ($x$).

2.  **Agilidad en la Actualización de Datos:**
    *   Los modelos A y B dependen de datos frescos. Facilitar el acceso a las fuentes originales reduce el tiempo que el investigador tarda en actualizar el Excel `Sifilis.xlsx` semana tras semana.

3.  **Sincronización Temporal:**
    *   Al permitir seleccionar el rango de fechas exacto, el usuario puede alinear perfectamente los datos de Google Trends con las Semanas Epidemiológicas que está analizando en el Boletín, asegurando que la correlación ($R^2$) sea válida.

## 4. Tecnologías Utilizadas
*   **`tkcalendar`**: Para la implementación de los widgets de calendario (`DateEntry`), ofreciendo una interfaz gráfica intuitiva y profesional.
*   **`webbrowser`**: Para la gestión de la apertura de enlaces externos en el navegador del sistema operativo.
*   **`datetime`**: Para la lógica de validación y formateo de fechas en la construcción de la URL.
