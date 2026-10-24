# Modelado de la demanda de pasajeros en Colombia (2017-2026)

**Autor:** Luis Guevara  
**Programa:** Econometría II  
**Institución:** Universidad Nacional de Colombia  
**Fecha:** Octubre de 2026

---

## 1. Guía de inicio rápido

Esta sección presenta los pasos necesarios para configurar el entorno de trabajo y ejecutar correctamente el proyecto. Está dirigida a las personas que descarguen o clonen el repositorio por primera vez.

### 1.1. Requisitos previos

Antes de comenzar, asegúrese de tener instaladas las siguientes herramientas:

- **Anaconda o Miniconda:** para gestionar el entorno virtual de Python y sus dependencias.
- **Visual Studio Code (VS Code):** como editor de código y entorno de desarrollo.
- **Git:** herramienta opcional para clonar el repositorio desde la terminal.

### 1.2. Extensiones necesarias en Visual Studio Code

Para facilitar la ejecución del código, la inspección de los datos y la detección de errores, se recomienda instalar las siguientes extensiones desde el panel de extensiones de VS Code, accesible mediante `Ctrl + Shift + X`.

- **Python (Microsoft):** permite ejecutar scripts, seleccionar el intérprete y administrar las herramientas de desarrollo de Python.
- **Pylance (Microsoft):** facilita el análisis estático del código, la detección de errores y las sugerencias de programación.
- **Jupyter (Microsoft):** permite ejecutar y visualizar las celdas de código delimitadas mediante `# %%` dentro de los scripts.
- **Data Wrangler (Microsoft):** extensión opcional que facilita la inspección y transformación de conjuntos de datos tabulares, incluidos archivos CSV.
- **Rainbow CSV:** extensión opcional que mejora la lectura de archivos CSV mediante la diferenciación visual de sus columnas.

### 1.3. Configuración del entorno virtual

Abra una terminal integrada en VS Code desde la carpeta raíz del proyecto, donde se encuentra este archivo `README.md`.

Ejecute los siguientes comandos en el orden indicado.

**Paso 1. Crear el entorno de Conda**

El archivo `environment.yml` contiene la configuración del entorno y las dependencias declaradas para el proyecto.

```bash
conda env create -f environment.yml
```

**Paso 2. Activar el entorno**

```bash
conda activate poster_2017
```

**Paso 3. Instalar las dependencias adicionales**

Instale las bibliotecas de Python declaradas en el archivo `requirements.txt`.

```bash
pip install -r requirements.txt
```

**Paso 4. Instalar el navegador requerido para exportar el PDF**

Playwright utiliza Chromium para procesar el documento HTML y generar el archivo PDF.

```bash
playwright install chromium
```

Si alguno de estos comandos presenta errores, verifique que Conda esté instalado correctamente, que se encuentre en la carpeta raíz del proyecto y que los archivos de configuración estén disponibles.

### 1.4. Selección del intérprete de Python en VS Code

La selección del intérprete correcto es indispensable para que VS Code utilice las bibliotecas instaladas en el entorno del proyecto.

Siga estos pasos:

1. Abra la paleta de comandos mediante `Ctrl + Shift + P`. En macOS, utilice `Cmd + Shift + P`.
2. Escriba `Python: Select Interpreter`.
3. Seleccione el entorno de Conda denominado `poster_2017`.
4. Verifique que la ruta corresponda al intérprete del entorno creado. En Windows, puede presentar una estructura similar a la siguiente:

```text
...\anaconda3\envs\poster_2017\python.exe
```

Una vez seleccionado el intérprete, el entorno estará preparado para ejecutar los scripts del proyecto.

---

## 2. Pipeline de ejecución

El proyecto utiliza un flujo de procesamiento secuencial en el que los datos, los resultados estadísticos, las gráficas y los documentos finales se generan mediante scripts de Python.

**Regla fundamental:** los archivos HTML y JavaScript que contienen los resultados del póster se generan o actualizan a partir de los scripts de procesamiento. Por tanto, no deben modificarse manualmente cuando el cambio corresponda a resultados estadísticos, tablas o gráficas que puedan regenerarse automáticamente.

Para actualizar el proyecto, ejecute los scripts en el siguiente orden desde la terminal integrada de VS Code.

### 2.1. Limpieza y preparación de los datos

```bash
python 02_script/00_limpieza_data.py
```

Este script procesa los archivos CSV originales ubicados en `01_datos/raw/`, realiza las tareas de limpieza definidas en el código, verifica los valores faltantes y genera los archivos procesados en `01_datos/processed/`.

### 2.2. Desarrollo de la metodología y evaluación de modelos

```bash
python 02_script/01_paso_paso_para_hallar_modelo.py
```

Este script desarrolla el procedimiento metodológico, genera gráficas exploratorias, aplica las pruebas de estacionariedad ADF y KPSS, evalúa los cinco modelos candidatos y documenta la evolución del proceso de selección en la carpeta `03_resultados/`.

### 2.3. Estimación del modelo final

```bash
python 02_script/02_modelo_final.py
```

Este script estima el modelo seleccionado, identificado en la documentación del proyecto como SARIMAX complementado con GARCH. También genera las gráficas y tablas finales que se almacenan en `04_poster/img/`.

### 2.4. Actualización de los datos del póster

```bash
python 02_script/03_datos_poster.py
```

Este script extrae del modelo final las estadísticas y los resultados utilizados en el póster, incluidos el AIC, los coeficientes y los resultados de las pruebas estadísticas. Posteriormente, actualiza el archivo `04_poster/datos_poster.js`.

De esta manera, el contenido numérico del póster se mantiene vinculado a los resultados generados por el código.

### 2.5. Preparación de imágenes y generación del código QR

```bash
python 04_poster/preparar_imagenes.py
```

Este script prepara las imágenes utilizadas en el póster, recorta los márgenes blancos según la lógica implementada y genera el código QR del repositorio.

### 2.6. Exportación del póster a PDF

```bash
python 04_poster/exportar_pdf.py
```

Este script utiliza Playwright y Chromium para procesar el documento `poster.html` junto con sus recursos visuales y datos asociados, y exportar el resultado a un archivo PDF preparado para su impresión.

### 2.7. Visualización del resultado final

El proyecto ofrece dos formas principales de consultar el póster generado.

**Póster interactivo**

Abra el archivo `04_poster/poster.html` en un navegador web. También puede utilizar la extensión Live Server de VS Code para visualizarlo durante el desarrollo.

La interfaz incorpora las herramientas de interacción implementadas en el proyecto, entre ellas el acercamiento y alejamiento de la visualización y las anotaciones, si estas funciones se encuentran habilitadas en la versión actual.

**Póster en formato PDF**

Abra el archivo `04_poster/poster.pdf` para consultar la versión exportada, destinada a la impresión y distribución.

---

## 3. Estructura del proyecto

La organización de los directorios separa los datos originales, los datos procesados, los scripts de Python, los resultados estadísticos y los archivos necesarios para generar el póster.

```text
1_Poster_terminal_2017_2026/
|
|-- 01_datos/
|   |-- raw/                       # Datos originales
|   `-- processed/                 # Datos procesados
|
|-- 02_script/
|   |-- 00_limpieza_data.py
|   |-- 01_paso_paso_para_hallar_modelo.py
|   |-- 02_modelo_final.py
|   `-- 03_datos_poster.py
|
|-- 03_resultados/                 # Resultados y gráficas metodológicas
|
|-- 04_poster/
|   |-- img/                       # Gráficas y tablas originales
|   |-- img_poster/                # Imágenes preparadas para el póster
|   |-- preparar_imagenes.py       # Preparación de imágenes y código QR
|   |-- exportar_pdf.py            # Exportación del póster a PDF
|   |-- poster.html                # Documento principal del póster
|   `-- datos_poster.js            # Datos utilizados por el póster
|
|-- environment.yml                # Configuración del entorno Conda
|-- requirements.txt               # Dependencias adicionales de Python
`-- README.md                      # Documentación principal
```

Esta estructura representa la organización prevista del proyecto. Los nombres y las ubicaciones deben coincidir con los archivos existentes en el repositorio.

---

## 4. Documentación metodológica

### 4.1. Descripción del modelo

El proyecto tiene como objetivo modelar la serie mensual de pasajeros de la Terminal de Transporte de Bogotá durante el período 2017-2026 mediante técnicas de econometría de series de tiempo.

La estrategia metodológica se fundamenta en el enfoque de Box-Jenkins y contempla la transformación logarítmica de la variable de interés, la incorporación del número de despachos como variable exógena y el uso de variables indicadoras (*dummies*) para representar el choque estructural asociado con la pandemia de COVID-19.

El modelo final documentado corresponde a un modelo **SARIMAX(2,1,2)(0,1,1)₁₂**, complementado con un modelo **GARCH(1,1)** para representar la dinámica de la varianza condicional.

El componente SARIMAX permite modelar la dependencia temporal, la diferenciación regular y estacional, así como la relación con la variable exógena. Por su parte, el componente GARCH se utiliza para estudiar la dinámica de la volatilidad condicional de los errores.

La especificación definitiva, los supuestos de estimación y la interpretación de los parámetros deben verificarse con los scripts y los resultados estadísticos del modelo estimado.

### 4.2. Resultados principales

Los siguientes valores corresponden a los resultados reportados para la versión documentada del proyecto.

| Indicador | Resultado reportado |
|:--|--:|
| Criterio de información de Akaike (AIC) | -138.70 |
| Curtosis de los residuos | 3.33 |
| Prueba de Ljung-Box, rezago 6 | 0.1922 |
| Prueba ARCH | 0.1273 |
| Error porcentual absoluto medio (MAPE) en backtesting | 5.02 % |
| Pronóstico de pasajeros para diciembre de 2026 | Aproximadamente 1,84 millones |

**Consideraciones para la interpretación de los resultados:**

- **AIC:** permite comparar modelos estimados sobre una base de datos y una especificación de verosimilitud comparables. En igualdad de condiciones, un valor menor favorece al modelo con mejor equilibrio entre ajuste y complejidad.
- **Curtosis de los residuos:** el valor reportado de 3,33 se encuentra relativamente próximo al valor de referencia de 3 para una distribución normal cuando se utiliza la curtosis ordinaria de Pearson. Esta proximidad, por sí sola, no demuestra normalidad.
- **Prueba de Ljung-Box:** el resultado debe interpretarse según el tipo de estadístico reportado. Si corresponde al valor *p*, un resultado de 0,1922 no permite rechazar la hipótesis nula de ausencia de autocorrelación conjunta hasta el rezago evaluado al nivel de significancia del 5 %.
- **Prueba ARCH:** si 0,1273 corresponde al valor *p* de la prueba, no se rechaza la hipótesis nula de ausencia de efectos ARCH al nivel del 5 %. La conclusión debe confirmarse verificando el estadístico y el valor *p* generados por el código.
- **MAPE:** el valor reportado de 5,02 % resume el error porcentual absoluto medio del procedimiento de backtesting. Su interpretación depende del período de evaluación y del método de validación utilizados.
- **Pronóstico:** se reporta una proyección aproximada de 1,84 millones de pasajeros para diciembre de 2026. Este valor debe interpretarse como una estimación del modelo, no como un dato observado.

Los resultados deben actualizarse después de ejecutar el pipeline completo. Las cifras consignadas en esta sección no se consideran verificadas de manera independiente hasta contrastarlas con las salidas de la última ejecución.

---

## 5. Referencias bibliográficas

Las siguientes referencias corresponden a las obras metodológicas reportadas en el proyecto. Antes de la entrega académica definitiva, se recomienda completar y verificar los datos editoriales, los títulos exactos y los identificadores bibliográficos disponibles.

- Bollerslev, T. (1986). Generalized autoregressive conditional heteroskedasticity. *Journal of Econometrics, 31*(3), 307-327.

- Enders, W. (2014). *Applied econometric time series* (4.ª ed.). Wiley.

- Engle, R. F. (1982). Autoregressive conditional heteroscedasticity with estimates of the variance of United Kingdom inflation. *Econometrica, 50*(4), 987-1007.

- Guerrero, V. M. (2003). *Análisis estadístico de series de tiempo económicas*. La información editorial debe verificarse antes de completar la referencia.

- Hyndman, R. J., y Athanasopoulos, G. (2021). *Forecasting: Principles and practice* (3.ª ed.). OTexts. https://otexts.com/fpp3/

---

## 6. Reproducibilidad y mantenimiento

Para garantizar la reproducibilidad del análisis, se recomienda conservar los archivos originales, documentar las transformaciones aplicadas a los datos y ejecutar los scripts en el orden establecido.

Asimismo, conviene mantener actualizados los archivos de configuración del entorno, registrar las versiones de las bibliotecas utilizadas y conservar las salidas necesarias para verificar los resultados del modelo.

Antes de publicar una nueva versión del póster, compruebe que:

1. Los datos procesados corresponden a los archivos originales utilizados en el análisis.
2. Los resultados estadísticos provienen de la ejecución más reciente del modelo.
3. Las tablas, las gráficas y los valores incluidos en el póster coinciden con los archivos generados por los scripts.
4. El documento HTML se visualiza correctamente y sus recursos asociados están disponibles.
5. El archivo PDF se ha generado correctamente y conserva el diseño previsto para su impresión.
6. Las referencias bibliográficas están completas y verificadas.

Este procedimiento permite mantener la coherencia entre los datos, el análisis econométrico, los resultados reportados y la presentación final del proyecto.