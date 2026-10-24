# -*- coding: utf-8 -*-
# ============================================================================
# 03_datos_poster.py -- GENERADOR DE DATOS PARA EL PÓSTER
# ============================================================================
"""
Este script NO modifica el modelo original. Su función es ejecutar 
`02_modelo_final.py` en un entorno aislado (leyendo sus variables) y 
extraer los resultados reales del modelo (estimaciones, pruebas, pronósticos)
para exportarlos a `04_poster/datos_poster.js`.

Así, el póster HTML siempre mostrará números coherentes con el modelo,
evitando datos escritos a mano que se desactualicen.
"""

# %% ============================================================================
# 1. IMPORTACIÓN DE LIBRERÍAS
# ============================================================================
from pathlib import Path
import json
import io
import contextlib

import numpy as np
import pandas as pd


# %% ============================================================================
# 2. CONFIGURACIÓN DE RUTAS
# ============================================================================
# Ruta raíz del proyecto y rutas de los archivos clave
RAIZ = Path(__file__).resolve().parent.parent
MODELO = Path(__file__).resolve().parent / "02_modelo_final.py"
SALIDA = RAIZ / "04_poster" / "datos_poster.js"


# %% ============================================================================
# 3. EJECUCIÓN DEL MODELO EN ENTORNO AISLADO
# ============================================================================
"""
Ejecutamos `02_modelo_final.py` sin modificar el archivo original.
Usamos un diccionario `ns` (namespace) para capturar todas las variables
que se crean durante la ejecución del modelo. 
Se redirige la salida estándar (stdout) para evitar que los prints del 
modelo ensucien la consola de este script.
"""
ns = {"__file__": str(MODELO), "__name__": "modelo_final"}

with contextlib.redirect_stdout(io.StringIO()):
    exec(compile(MODELO.read_text(encoding="utf-8"), str(MODELO), "exec"), ns)


# %% ============================================================================
# 4. EXTRACCIÓN DE RESULTADOS DEL MODELO
# ============================================================================
# Extraemos las variables clave desde el namespace generado
e = ns["estimacion"]
y = ns["pasajeros"]
ic = ns["intervalos"]
pron = ns["pron_nivel"]


# %% ============================================================================
# 5. CONSTRUCCIÓN DEL DICCIONARIO DE DATOS (JSON)
# ============================================================================
"""
Estructuramos todos los resultados en un único diccionario `D` 
que luego será exportado como un archivo JS. 
Se redondean los valores flotantes para evitar decimales infinitos.
"""
D = {
    # --- Metadatos básicos ---
    "T": int(len(y)),
    "inicio": f"{y.index[0]:%Y-%m}",
    "fin": f"{y.index[-1]:%Y-%m}",

    # --- Métricas de ajuste ---
    "aic": round(float(e.aic), 2),
    "bic": round(float(e.bic), 2),
    "loglik": round(float(e.llf), 2),

    # --- Parámetros estimados ---
    "params": [
        {
            "n": k,
            "c": float(e.params[k]),
            "se": float(e.bse[k]),
            "p": float(e.pvalues[k])
        }
        for k in e.params.index
    ],

    # --- Tablas de pruebas y modelos candidatos ---
    "pruebas": ns["tabla_pruebas"].to_dict("records"),
    "candidatos": ns["tabla_cand"].to_dict("records"),

    # --- Back-testing (MAPE) ---
    "mape_backtest": float(ns["mape"]) if "mape" in ns else None,

    # --- Raíces del modelo (para validación de estabilidad) ---
    "raiz_ar_min": float(np.abs(e.arroots).min()),
    "raiz_ma_min": float(np.abs(e.maroots).min()),

    # --- Pronósticos con intervalos de confianza ---
    "pronostico": [
        {
            "mes": f"{t:%b-%Y}",
            "v": float(pron[t]),
            "li": float(ic.loc[t].iloc[0]),
            "ls": float(ic.loc[t].iloc[1])
        }
        for t in pron.index
    ],
}


# %% ============================================================================
# 6. EXPORTACIÓN A JAVASCRIPT
# ============================================================================
"""
Guardamos el diccionario como un archivo `.js` con la sintaxis:
`const datosPoster = { ... };`
"""
js_content = "const datosPoster = " + json.dumps(D, ensure_ascii=False) + ";"
SALIDA.write_text(js_content, encoding="utf-8")

print("OK ->", SALIDA)