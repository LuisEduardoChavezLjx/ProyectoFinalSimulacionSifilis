# Documentación Técnica: Módulos Auxiliares (`estilos.py` y `utilidades.py`)

## 1. Introducción
Para garantizar la mantenibilidad, consistencia visual y reutilización de código, el sistema se apoya en dos módulos transversales: `estilos.py` y `utilidades.py`. Estos archivos centralizan la configuración estética y la lógica de negocio repetitiva, siguiendo el principio de diseño DRY (Don't Repeat Yourself).

---

## 2. Módulo de Diseño: `estilos.py`

### Resumen
Este archivo actúa como el **Sistema de Diseño (Design System)** de la aplicación. Define la paleta de colores, tipografías y componentes gráficos reutilizables, asegurando que todas las ventanas del software mantengan una identidad visual coherente y profesional.

### Funcionalidades Clave

#### A. Paleta de Colores Centralizada
Define constantes globales para los colores, facilitando cambios de tema en toda la aplicación modificando una sola línea de código.
*   `COLOR_FONDO`: Fondo oscuro (#1e272e) para reducir fatiga visual.
*   `COLOR_ACCENT`: Azul brillante (#00a8ff) para acciones principales.
*   `COLOR_SUCCESS`, `COLOR_WARNING`, `COLOR_DANGER`: Colores semánticos para feedback de estado.

#### B. Componentes Reutilizables (Widgets)
En lugar de configurar cada botón individualmente en cada ventana, el módulo provee funciones factoría:
*   `crear_boton()`: Genera botones con estilos predefinidos (primary, success, danger) y efectos de *hover* automáticos.
*   `crear_card()`: Implementa contenedores visuales tipo "tarjeta" para agrupar información.
*   `aplicar_tema()`: Configura globalmente los estilos de `ttk` (como las tablas Treeview) para que coincidan con el tema oscuro.

---

## 3. Módulo de Lógica Compartida: `utilidades.py`

### Resumen
Este módulo encapsula la **Lógica de Negocio y Manipulación de Datos**. Contiene las funciones puras que realizan cálculos matemáticos, lectura/escritura de archivos y transformaciones de DataFrames. Al separar esta lógica de la interfaz gráfica, se facilita el testeo y la depuración.

### Funcionalidades Clave

#### A. Estandarización de Datos
Define constantes para los nombres de columnas (`COL_SEMANA`, `COL_INDICE`, etc.). Esto evita errores por "strings mágicos" y asegura que todos los modelos busquen las mismas columnas en el Excel.

#### B. Persistencia (I/O)
*   `leer_excel()`: Maneja la carga de archivos, incluyendo la validación de existencia, manejo de errores y normalización de nombres de columnas (mapeo de nombres antiguos a nuevos).
*   `guardar_excel()`: Centraliza el guardado, asegurando que no se exporten columnas temporales de cálculo interno.

#### C. Motor Matemático Compartido
Contiene el núcleo algorítmico utilizado tanto por el `gestor_datos.py` como por el `modelo_b.py`:
*   `calcular_coeficientes(df)`: Función pura que recibe un DataFrame y retorna los coeficientes $\alpha$ y $\beta$ usando regresión lineal sobre deltas.
*   `calcular_modelo_b_completo(df)`: Orquesta el proceso completo: cálculo de deltas -> regresión -> reconstrucción de series estimadas.

## 4. Relevancia para la Ingeniería de Software (IEEE)
La inclusión de estos módulos demuestra buenas prácticas de ingeniería de software en el desarrollo de simulaciones científicas:
1.  **Modularidad:** Separa la presentación (`estilos.py`) de la lógica (`utilidades.py`) y de la orquestación (`menu_principal.py`).
2.  **Robustez:** La centralización de la lectura de datos en `utilidades.py` reduce la probabilidad de errores al procesar archivos con formatos ligeramente distintos.
3.  **Escalabilidad:** Facilitan la adición de nuevos modelos o ventanas sin duplicar código base.
