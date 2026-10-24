# %% [BLOQUE 1] IMPORTACIÓN DE PAQUETES Y CONFIGURACIÓN
# ==========================================================
# En este bloque importamos las librerías necesarias y definimos
# las rutas relativas. Usamos 'pathlib' porque es la mejor práctica
# para que el código funcione en cualquier computadora (Windows/Mac/Linux).
# ==========================================================

# 'Path' nos permite manejar rutas de archivos de forma independiente al sistema operativo.
from pathlib import Path

# 'pandas' es la librería estándar para manipulación de datos tabulares.
import pandas as pd

# 'numpy' nos ayuda con operaciones matemáticas (aunque en este script es opcional, es buena práctica tenerla).
import numpy as np

# 'matplotlib.pyplot' nos permite crear las gráficas de la serie de tiempo.
import matplotlib.pyplot as plt

# 'seaborn' mejora el estilo visual de las gráficas de matplotlib.
import seaborn as sns

# Configuramos el estilo de las gráficas para que se vean profesionales.
sns.set_theme(style="whitegrid", palette="deep")
plt.rcParams.update({'font.size': 10, 'figure.dpi': 120})

# --- CONFIGURACIÓN DE RUTAS RELATIVAS ---
# BASE_DIR: Obtiene la ruta de la carpeta raíz del proyecto.
# Como este script está en '02_script', subimos un nivel con '.parent'.
BASE_DIR = Path(__file__).resolve().parent.parent

# DATA_RAW: Ruta donde está el archivo CSV original.
DATA_RAW = BASE_DIR / "01_datos" / "raw" / "datal_2017_2026.csv"

# DATA_PROC: Carpeta donde guardaremos la base de datos limpia.
DATA_PROC = BASE_DIR / "01_datos" / "processed"

# FIG_DIR: Carpeta donde guardaremos las gráficas generadas.
FIG_DIR = BASE_DIR / "03_resultados" / "figuras"

# Crear la carpeta 'processed' si no existe (parents=True crea la ruta completa).
DATA_PROC.mkdir(parents=True, exist_ok=True)

# Crear la carpeta 'figuras' si no existe.
FIG_DIR.mkdir(parents=True, exist_ok=True)


# %% [BLOQUE 2] CARGA Y DIAGNÓSTICO DE DATOS
# ==========================================================
# Aquí leemos el archivo CSV y hacemos una inspección inicial.
# ==========================================================
print("="*70)
print("PASO 1: CARGA Y DIAGNÓSTICO DE DATOS")
print("="*70)

# Leemos el archivo CSV usando pandas.
# 'parse_dates=["fecha"]' le dice a pandas que la columna 'fecha' es de tipo fecha,
# así no tenemos que convertirla manualmente después.
df = pd.read_csv(DATA_RAW, parse_dates=["fecha"])

# Imprimimos las primeras 5 filas para verificar que todo se cargó bien.
print("\n--- Primeras 5 filas del CSV original ---")
print(df.head())

# Imprimimos la información general del dataframe (tipos de datos, cantidad de filas).
print("\n--- Información del DataFrame ---")
df.info()


# %% [BLOQUE 3] LIMPIEZA Y PREPARACIÓN DE LA FECHA
# ==========================================================
# Queremos que el índice sea estrictamente mensual (año-mes).
# Para ello, convertimos la fecha al primer día de cada mes.
# ==========================================================
print("\n" + "="*70)
print("PASO 2: LIMPIEZA DE LA FECHA (FRECUENCIA MENSUAL)")
print("="*70)

# Aseguramos que la columna 'fecha' sea de tipo datetime.
# Aunque ya lo hicimos en read_csv, esta línea es un seguro.
df["fecha"] = pd.to_datetime(df["fecha"])

# Convertimos la fecha al primer día del mes (Month Start).
# Por ejemplo: 2022-03-15 -> 2022-03-01.
# Esto es crucial para que pandas entienda que la serie es mensual.
df["fecha"] = df["fecha"].dt.to_period("M").dt.to_timestamp()

# Establecemos la columna 'fecha' como el índice del DataFrame.
# Esto es fundamental para series de tiempo en pandas.
df = df.set_index("fecha")

# Ordenamos el DataFrame por fecha (por seguridad, por si el CSV está desordenado).
df = df.sort_index()

# Verificamos si hay meses faltantes. 'asfreq("MS")' crea un índice continuo mensual.
# Si un mes no existe en el CSV, se rellenará con NaN.
df = df.asfreq("MS")

# Verificamos cuántos valores nulos hay después de la alineación.
nulos = df.isnull().sum()
print(f"\n--- Diagnóstico de valores nulos ---")
print(nulos)

# Si hay valores nulos (meses faltantes), los rellenamos con 0 (asumiendo que no hubo viajes).
if nulos.sum() > 0:
    print("\n Se encontraron meses sin datos. Se rellenarán con 0.")
    df = df.fillna(0)
else:
    print("\n No hay valores nulos. La serie está completa.")

# Mostramos las primeras filas de la base limpia.
print("\n--- Primeras 5 filas de la base limpia ---")
print(df.head())

# Mostramos la última fila para verificar el rango temporal.
print("\n--- Última fila de la base limpia ---")
print(df.tail(1))


# %% [BLOQUE 4] VISUALIZACIÓN EXPLORATORIA
# ==========================================================
# Graficamos las dos series (pasajeros y despachos) para observar
# la tendencia, los picos y el desplome de 2020 (pandemia).
# ==========================================================
print("\n" + "="*70)
print("PASO 3: VISUALIZACIÓN EXPLORATORIA")
print("="*70)

# Creamos una figura de 2 subgráficos (uno para pasajeros, otro para despachos).
fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

# Subgráfico 1: Pasajeros
# Ploteamos la serie de pasajeros en color azul.
axes[0].plot(df.index, df["pasajeros"], color="#1a237e", linewidth=2)
# Título del subgráfico.
axes[0].set_title("Serie Histórica: Pasajeros (2017 - 2026)", fontweight="bold")
# Etiqueta del eje Y.
axes[0].set_ylabel("Pasajeros")

# Subgráfico 2: Despachos
# Ploteamos la serie de despachos en color naranja.
axes[1].plot(df.index, df["despachos"], color="#ff7f0e", linewidth=2)
# Título del subgráfico.
axes[1].set_title("Serie Histórica: Despachos (2017 - 2026)", fontweight="bold")
# Etiqueta del eje Y.
axes[1].set_ylabel("Despachos")
# Etiqueta del eje X.
axes[1].set_xlabel("Fecha")

# Ajustamos el layout para que no se solapen los títulos.
plt.tight_layout()

# Guardamos la gráfica en la carpeta de figuras.
plt.savefig(FIG_DIR / "01_serie_original.png", dpi=150)

# Mostramos la gráfica en pantalla.
plt.show()


# %% [BLOQUE 5] GUARDADO DE LA BASE LIMPIA
# ==========================================================
# Guardamos el DataFrame limpio en la carpeta 'processed' para
# usarlo en los siguientes pasos (modelado Box-Jenkins).
# ==========================================================
print("\n" + "="*70)
print("PASO 4: GUARDADO DE LA BASE LIMPIA")
print("="*70)

# Definimos la ruta de salida.
ruta_salida = DATA_PROC / "serie_limpia_2017_2026.csv"

# Guardamos el DataFrame en CSV.
# 'index=True' guarda el índice (la fecha), lo cual es crucial para series de tiempo.
df.to_csv(ruta_salida, index=True)

# Confirmamos al usuario que el archivo se guardó correctamente.
print(f"\n Base de datos limpia guardada en: {ruta_salida}")
print(f"   Total de observaciones mensuales: {len(df)}")
print(f"   Rango de fechas: {df.index.min().strftime('%Y-%m')} a {df.index.max().strftime('%Y-%m')}")