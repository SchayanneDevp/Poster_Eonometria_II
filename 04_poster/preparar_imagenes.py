# -*- coding: utf-8 -*-
# ============================================================================
# SCRIPT DE DISEÑO DEL PÓSTER (RECORTE DE IMÁGENES Y GENERACIÓN DE QR)
# ============================================================================
"""
Este script se encarga exclusivamente del diseño visual de los recursos.
NO modifica las imágenes originales (img/) ni el modelo estadístico.

Sus dos funciones principales son:
1. Recortar los márgenes blancos sobrantes de cada PNG y guardarlos en 
   `img_poster/` para que se vean más grandes y limpios en el póster.
2. Generar el código QR que apunta al repositorio de GitHub.

Requisitos:
    pip install pillow "qrcode[pil]"
"""

# %% ============================================================================
# 1. IMPORTACIÓN DE LIBRERÍAS Y CONFIGURACIÓN INICIAL
# ============================================================================
from pathlib import Path
from PIL import Image, ImageChops

# Rutas y parámetros
AQUI = Path(__file__).resolve().parent
URL = "https://github.com/SchayanneDevp/Poster_Eonometria_II"
PAD = 14   # Píxeles de aire (padding) alrededor de cada imagen recortada


# %% ============================================================================
# 2. RECORTE AUTOMÁTICO DE IMÁGENES (Eliminar márgenes blancos)
# ============================================================================
"""
Recorremos las carpetas de gráficas y tablas. Para cada imagen, detectamos 
el área no blanca (bounding box) y recortamos el resto. Luego añadimos un 
pequeño margen uniforme (PAD) para que las imágenes no queden pegadas al borde.
"""
n = 0  # Contador de imágenes procesadas

for sub in ("graficas", "tablas"):
    # Crear la carpeta de destino si no existe
    dst = AQUI / "img_poster" / sub
    dst.mkdir(parents=True, exist_ok=True)
    
    # Procesar cada archivo PNG de la carpeta original
    for f in sorted((AQUI / "img" / sub).glob("*.png")):
        im = Image.open(f).convert("RGB")
        
        # Detectar el área que contiene la imagen (diferencia con el fondo blanco)
        caja = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255))).getbbox()
        
        # Si se detectó un área con contenido, recortar
        if caja:
            im = im.crop(caja)
            
        # Crear un lienzo nuevo un poco más grande y pegar la imagen en el centro
        lienzo = Image.new("RGB", (im.width + 2 * PAD, im.height + 2 * PAD), (255, 255, 255))
        lienzo.paste(im, (PAD, PAD))
        
        # Guardar la imagen procesada
        lienzo.save(dst / f.name)
        n += 1

print(f"{n} imágenes recortadas en img_poster/")


# %% ============================================================================
# 3. GENERACIÓN DEL CÓDIGO QR DEL REPOSITORIO
# ============================================================================
"""
Intentamos generar un código QR con la URL del repositorio. Si la librería 
`qrcode` no está instalada, mostramos un mensaje amigable en lugar de 
romper la ejecución del script.
"""
try:
    import qrcode
    qr_path = AQUI / "qr_github.png"
    qrcode.make(URL, box_size=10, border=2).save(qr_path)
    print("QR ->", qr_path)
except Exception as e:
    print("QR no generado (pip install qrcode[pil]):", e)