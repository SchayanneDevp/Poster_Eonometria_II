# Modelado de la demanda de pasajeros en Colombia (2017-2026)

**Autor:** Luis Guevara  
**Programa:** Econometría II  
**Institución:** Universidad Nacional de Colombia  
**Fecha:** Octubre de 2026

---

## 1. Descripción del proyecto

Este proyecto tiene como objetivo modelar y pronosticar la serie de tiempo mensual de pasajeros que salen de la Terminal de Transporte de Bogotá durante el periodo 2017-2026. Para ello, se aplica la metodología Box-Jenkins (Guerrero, 2003; Enders, 2014), complementada con transformaciones logarítmicas, variables exógenas (despachos de buses) y modelos de heterocedasticidad condicional autorregresiva generalizada (GARCH), con el propósito de analizar y modelar el comportamiento de la varianza.

El repositorio contiene el código fuente, las bases de datos procesadas, los resultados gráficos y un póster interactivo que resume los principales hallazgos del análisis.

## 2. Motivación económica

La serie analizada representa el flujo de pasajeros que salen de Bogotá por transporte terrestre intermunicipal. Este indicador puede utilizarse como una aproximación a la actividad económica y a la movilidad regional, dado que refleja parte de la demanda de transporte entre diferentes regiones del país.

La caída abrupta observada en 2020, asociada con la pandemia por COVID-19 y las restricciones de movilidad, evidencia la importancia de utilizar modelos capaces de representar cambios atípicos y posibles alteraciones estructurales en las series económicas. El análisis busca generar pronósticos que puedan contribuir a la planificación de las operaciones logísticas y de la infraestructura de transporte.

## 3. Estructura del proyecto

El repositorio está organizado de la siguiente manera:

```text
1_Poster_terminal_2017_2026/
│
├── 01_datos/
│   ├── raw/
│   │   └── datal_2017_2026.csv
│   └── processed/
│       └── serie_limpia_2017_2026.csv
│
├── 02_script/
│   ├── 00_limpieza_data.py
│   ├── 01_paso_paso_para_hallar_modelo.py
│   └── 02_modelo_final.py
│
├── 03_resultados/
│   └── historia/
│
├── 04_poster/
│   ├── img/
│   │   ├── graficas/
│   │   └── tablas/
│   ├── index.html
│   ├── styles.css
│   └── script.js
│
├── environment.yml
├── requirements.txt
├── README.md
└── INSTRUCCIONES.md
```

La carpeta `01_datos/raw/` contiene los datos originales, mientras que `01_datos/processed/` almacena los datos preparados para el análisis. La carpeta `02_script/` reúne los programas de limpieza, modelado y generación de resultados. Por su parte, `03_resultados/` contiene las gráficas generadas durante el proceso de modelado y `04_poster/` reúne los archivos necesarios para visualizar el póster interactivo.

## 4. Requisitos previos

Para ejecutar el proyecto, se requieren las siguientes herramientas:

- Python 3.11 con el gestor de paquetes `pip`.
- Anaconda o Miniconda para administrar el entorno virtual.
- Visual Studio Code como editor de código recomendado.
- Las extensiones Python, Pylance y Jupyter para Visual Studio Code.
- Git, de manera opcional, para clonar el repositorio.

Las dependencias de Python se especifican en el archivo `requirements.txt` e incluyen las siguientes bibliotecas:

- `pandas`
- `numpy`
- `matplotlib`
- `seaborn`
- `statsmodels`
- `scipy`
- `arch`
- `pmdarima`
- `tabulate`

## 5. Instalación y ejecución

### 5.1. Clonar el repositorio

Abra una terminal y ejecute los siguientes comandos:

```bash
git clone <URL_DEL_REPOSITORIO>
cd 1_Poster_terminal_2017_2026
```

Sustituya `<URL_DEL_REPOSITORIO>` por la dirección real del repositorio.

### 5.2. Crear el entorno de Conda

Ejecute el siguiente comando desde el directorio raíz del proyecto:

```bash
conda env create -f environment.yml
```

### 5.3. Activar el entorno

Active el entorno definido en el archivo `environment.yml`:

```bash
conda activate poster_2017
```

### 5.4. Instalar las dependencias

Instale las bibliotecas especificadas en el archivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 5.5. Ejecutar el análisis

Para ejecutar el proceso de modelado y generar las gráficas, tablas y resultados correspondientes, utilice:

```bash
python 02_script/01_paso_paso_para_hallar_modelo.py
```

### 5.6. Visualizar el póster

Abra el archivo `04_poster/index.html` en un navegador web para consultar el póster interactivo. Las funcionalidades de visualización dependerán de la implementación de los archivos `styles.css` y `script.js`.

## 6. Descripción de los scripts

### 6.1. Script de limpieza y preparación

**Archivo:** `00_limpieza_data.py`

Este script carga el archivo CSV original, transforma la columna de fecha y prepara el índice temporal con frecuencia mensual (`MS`). También verifica la presencia de valores nulos y guarda los datos preparados en la carpeta `01_datos/processed/`.

### 6.2. Script de desarrollo metodológico

**Archivo:** `01_paso_paso_para_hallar_modelo.py`

Este programa documenta las etapas del análisis de la serie de tiempo. Entre sus funciones se encuentran:

- Generación de gráficas de la serie histórica.
- Construcción de las funciones de autocorrelación (FAC) y autocorrelación parcial (FACP).
- Aplicación de pruebas de raíz unitaria, incluidas las pruebas ADF y KPSS.
- Estimación y comparación de modelos SARIMA y SARIMAX.
- Evaluación de transformaciones logarítmicas y variables indicadoras de intervención.
- Incorporación de la variable exógena correspondiente a los despachos de buses.
- Evaluación de modelos GARCH para estudiar la dinámica de la varianza condicional.
- Diagnóstico de los residuos y evaluación del modelo seleccionado.
- Generación de pronósticos y evaluación mediante *backtesting*.

Según la descripción del proyecto, el script también genera documentación sobre las etapas del proceso de modelado.

### 6.3. Script del modelo final

**Archivo:** `02_modelo_final.py`

Este script está destinado a generar los recursos gráficos y tabulares del póster web, incluidos los coeficientes estimados, las pruebas de diagnóstico y los resultados del pronóstico final.

## 7. Resultados principales

De acuerdo con los resultados reportados en el proyecto, el modelo seleccionado es un **SARIMAX(2,1,2)(0,1,1,12)**, estimado con transformación logarítmica, una variable exógena correspondiente a los despachos de buses y variables indicadoras de intervención para determinados periodos. Adicionalmente, se reporta la estimación de un modelo GARCH(1,1) para analizar la heterocedasticidad condicional.

### 7.1. Especificación del modelo

La especificación reportada incorpora los siguientes componentes:

- **Componente no estacional:** SARIMAX(2,1,2).
- **Componente estacional:** (0,1,1,12), con periodicidad anual para datos mensuales.
- **Transformación:** logaritmo de la variable de pasajeros.
- **Variable exógena:** despachos de buses.
- **Variables de intervención:** indicadores asociados con la pandemia de 2020 y diciembre de 2019 y 2020.
- **Modelo complementario de varianza:** GARCH(1,1).

### 7.2. Indicadores reportados

| Indicador | Resultado reportado |
|---|---:|
| Criterio de información de Akaike (AIC) | -138.70 |
| Prueba de Ljung-Box, rezago 6 | 0.1922 |
| Prueba ARCH | 0.1273 |
| Curtosis | 3.33 |
| Error porcentual absoluto medio (MAPE) del *backtesting* | 5,02 % |

Estos valores corresponden a los resultados descritos en el proyecto y deben interpretarse de acuerdo con la definición de cada estadístico, sus hipótesis y el procedimiento de evaluación utilizado.

En particular, es necesario verificar si los valores de Ljung-Box y ARCH corresponden a estadísticos de prueba o valores *p*. La interpretación de los resultados cambia según esta distinción.

### 7.3. Pronóstico

El proyecto reporta un pronóstico a diez meses y una proyección aproximada de 1,84 millones de pasajeros para diciembre de 2026. Este resultado pretende representar el comportamiento estacional de la demanda de transporte terrestre al final del año.

La proyección debe interpretarse como una estimación condicionada a la especificación del modelo, a la información disponible y a los valores futuros utilizados para la variable exógena de despachos. Su precisión debe evaluarse mediante los resultados del *backtesting* y, cuando corresponda, mediante intervalos de predicción.

## 8. Conclusiones

1. La transformación logarítmica se incorporó para modelar la serie en una escala que puede reducir la variación relativa y facilitar el análisis de la tendencia y la estacionalidad. Su efectividad debe verificarse mediante el análisis de los residuos y de la estabilidad de la varianza.

2. La inclusión de los despachos de buses como variable exógena busca representar la relación entre la oferta de servicios de transporte y la cantidad de pasajeros movilizados. La contribución de esta variable debe evaluarse mediante pruebas de significancia, comparación de modelos y validación predictiva fuera de muestra.

3. El modelo GARCH(1,1) se incluyó para estudiar la posible heterocedasticidad condicional. Su utilidad debe establecerse a partir del diagnóstico de los residuos y de las pruebas correspondientes, sin asumir que su incorporación garantiza por sí sola el cumplimiento de los supuestos del modelo.

4. El *backtesting* reporta un MAPE del 5,02 %. Este resultado constituye una medida de error predictivo para el periodo evaluado. Su interpretación depende de la longitud del periodo de prueba, del procedimiento de generación de los pronósticos y de la existencia de valores iguales o cercanos a cero.

5. La proyección de pasajeros para diciembre de 2026 debe considerarse una estimación del modelo y no un resultado observado. Para valorar su confiabilidad, es necesario documentar la información disponible en la fecha de estimación, los supuestos sobre los despachos futuros y los intervalos de predicción.

## 9. Referencias bibliográficas

Bollerslev, T. (1986). Generalized autoregressive conditional heteroskedasticity. *Journal of Econometrics, 31*(3), 307–327.

Enders, W. (2014). *Applied econometric time series* (4th ed.). Wiley.

Engle, R. F. (1982). Autoregressive conditional heteroscedasticity with estimates of the variance of United Kingdom inflation. *Econometrica, 50*(4), 987–1007.

Guerrero, V. M. (2003). *Análisis estadístico de series de tiempo económicas*. Thomson.

Hyndman, R. J., & Athanasopoulos, G. (2021). *Forecasting: Principles and practice* (3rd ed.). OTexts. https://otexts.com/fpp3/

Kwiatkowski, D., Phillips, P. C. B., Schmidt, P., & Shin, Y. (1992). Testing the null hypothesis of stationarity against the alternative of a unit root. *Journal of Econometrics, 54*(1–3), 159–178.