# -*- coding: utf-8 -*-
# ============================================================================
# EXPORTADOR DE PÓSTER A PDF
# ============================================================================
"""
Este script toma el archivo `poster.html` y lo convierte en un PDF de alta 
resolución utilizando Playwright (un navegador Chromium automatizado).

Tamaño del lienzo: 3200x1800 px (equivale a 33.3 x 18.75 pulgadas).
Nota: La diagonal es de 38.3 in, lo que cabe perfecto en el límite de 40 in 
para impresión de pósteres.

Requisitos previos:
    pip install playwright
    python -m playwright install chromium
"""

# %% ============================================================================
# 1. IMPORTACIÓN DE LIBRERÍAS Y CONFIGURACIÓN
# ============================================================================
from pathlib import Path
from playwright.sync_api import sync_playwright

# Ruta base donde se encuentra este script
AQUI = Path(__file__).resolve().parent
RUTA_HTML = AQUI / "poster.html"
RUTA_PDF = AQUI / "poster.pdf"


# %% ============================================================================
# 2. PROCESO DE EXPORTACIÓN
# ============================================================================
"""
Abrimos el navegador en modo "headless" (invisible), cargamos el HTML, 
le damos un segundo y medio para que carguen las fuentes e imágenes, 
cambiamos a modo "print" (para que respete los estilos @media print de tu CSS) 
y finalmente guardamos el PDF.
"""
with sync_playwright() as p:
    # Iniciar navegador y crear una página con el tamaño exacto del póster
    nav = p.chromium.launch()
    pg = nav.new_page(viewport={"width": 3200, "height": 1800})
    
    # Abrir el archivo HTML local
    pg.goto(RUTA_HTML.as_uri())
    
    # Esperar 1.5 segundos para asegurar que todas las imágenes (PNG, QR) carguen bien
    pg.wait_for_timeout(1500)
    
    # Emular los estilos de impresión
    pg.emulate_media(media="print")
    
    # Generar el PDF con el tamaño exacto, fondo incluido y solo 1 página
    pg.pdf(
        path=str(RUTA_PDF), 
        width="3200px", 
        height="1800px", 
        print_background=True, 
        page_ranges="1"
    )
    
    # Cerrar el navegador
    nav.close()

print("PDF ->", RUTA_PDF)