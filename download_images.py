#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
download_images.py

Descarga las imagenes originales del blog de Asgard Nutricion Deportiva
y las guarda en la carpeta images/ del proyecto con los nombres que ya
usan las paginas HTML.

Funciona en Windows, macOS y Linux: solo necesita Python (version 3),
sin instalar ninguna libreria adicional.

Como usarlo en Windows:
  1) Instala Python si no lo tienes: https://www.python.org/downloads/
     (durante la instalacion, marca la casilla "Add Python to PATH")
  2) Abre la carpeta del proyecto, haz Shift + clic derecho dentro de
     ella y elige "Abrir ventana de PowerShell aqui" (o "Abrir en
     Terminal").
  3) Ejecuta:
        python download_images.py
     (si "python" no funciona, prueba con "py download_images.py")

Como usarlo en macOS / Linux:
  1) Abre una terminal en la carpeta del proyecto.
  2) Ejecuta:
        python3 download_images.py
"""

import os
import urllib.request
import urllib.error

DEST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")

FILES = [
    # (URL original, nombre de archivo local)
    ("https://asgardnutriciondeportivaavila.com/wp-content/uploads/2026/07/cropped-WhatsApp-Image-2026-06-19-at-5.26.44-AM.jpeg", "logo.jpg"),
    ("https://asgardnutriciondeportivaavila.com/wp-content/uploads/2026/07/1000612808-1024x768.jpg", "post-357-glutamina.jpg"),
    ("https://asgardnutriciondeportivaavila.com/wp-content/uploads/2026/07/1000605452-1024x702.jpg", "post-332-ashwagandha.jpg"),
    ("https://asgardnutriciondeportivaavila.com/wp-content/uploads/2026/07/1000552674-802x1024.jpg", "post-323-motivacion.jpg"),
    ("https://asgardnutriciondeportivaavila.com/wp-content/uploads/2026/06/1000597033-1024x466.jpg", "post-315-recuerdo.jpg"),
    ("https://asgardnutriciondeportivaavila.com/wp-content/uploads/2026/06/1000578686-1024x1024.png", "post-300-realidad.png"),
    ("https://asgardnutriciondeportivaavila.com/wp-content/uploads/2026/06/1000589434-1024x465.jpg", "post-293-diferenciamos.jpg"),

    # Imagenes de producto (seccion "Nuestros productos" de la home)
    ("https://asgardnutriciondeportivaavila.com/wp-content/uploads/2026/05/UK-ABEPerformanceEnergyDrink330ml12x330ml-GrapeSoda.png", "product-abe-energy-drink.png"),
    ("https://asgardnutriciondeportivaavila.com/wp-content/uploads/2026/05/ultra-zmax.png", "product-ultra-zma.png"),
    ("https://asgardnutriciondeportivaavila.com/wp-content/uploads/2026/05/prime-v-ts8.png", "product-prime-vts8.png"),
    ("https://asgardnutriciondeportivaavila.com/wp-content/uploads/2026/05/omega-3-100-perlas.png", "product-omega-3.png"),
    ("https://asgardnutriciondeportivaavila.com/wp-content/uploads/2026/05/Mockup-90-ISO-2kg-Chocolate-blanco-1536x1536.png.webp", "product-iso-90-choco-blanco.webp"),
    ("https://asgardnutriciondeportivaavila.com/wp-content/uploads/2026/05/Mockup-80-WHEY-ESSENTIAL-2kg-Kic-choco-1536x1536.png.webp", "product-whey-essential.webp"),
    ("https://asgardnutriciondeportivaavila.com/wp-content/uploads/2026/05/isolate-pro-zero-1-kg-caramelo.png", "product-isolate-pro-zero.png"),
    ("https://asgardnutriciondeportivaavila.com/wp-content/uploads/2026/05/essence-pro-whey-1-kg-chocolate-con-leche.png", "product-essence-pro-whey.png"),
    ("https://asgardnutriciondeportivaavila.com/wp-content/uploads/2026/05/creatine-gummies.png", "product-creatine-gummies.png"),
    ("https://asgardnutriciondeportivaavila.com/wp-content/uploads/2026/05/creatine-clonapure.png", "product-creatine-clonapure.png"),
    ("https://asgardnutriciondeportivaavila.com/wp-content/uploads/2026/05/boogieman-300-gr-1674558261-big.webp", "product-boogieman.webp"),
    ("https://asgardnutriciondeportivaavila.com/wp-content/uploads/2026/05/artiflex-vitobest.webp", "product-artiflex.webp"),
    ("https://asgardnutriciondeportivaavila.com/wp-content/uploads/2026/05/anabol-testo-booster-limonada-rosa-240gr.png", "product-anabol-testo-booster.png"),
    ("https://asgardnutriciondeportivaavila.com/wp-content/uploads/2026/05/ABEUltimatePre-Workout375g-CandyIceBlast_54770520-adae-4f8d-8387-0ae3254e0f92.webp", "product-abe-preworkout.webp"),
    ("https://asgardnutriciondeportivaavila.com/wp-content/uploads/2026/05/8594159531093-1.png", "product-misc-1.png"),
    ("https://asgardnutriciondeportivaavila.com/wp-content/uploads/2026/05/1064885868_1dad70fa-adb3-440d-95c2-c1c16472b463.png", "product-misc-2.png"),

    # Logos de marcas (seccion "Marcas de confianza" de la home)
    ("https://asgardnutriciondeportivaavila.com/wp-content/uploads/2026/05/Logo_01.png", "brand-logo-01.png"),
    ("https://asgardnutriciondeportivaavila.com/wp-content/uploads/2026/05/Logo_02.png", "brand-logo-02.png"),
    ("https://asgardnutriciondeportivaavila.com/wp-content/uploads/2026/05/Logo_03.png", "brand-logo-03.png"),
    ("https://asgardnutriciondeportivaavila.com/wp-content/uploads/2026/05/Logo_04.png", "brand-logo-04.png"),
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; AsgardImageDownloader/1.0)"
}


def download(url, filename):
    dest_path = os.path.join(DEST, filename)
    print(f"Descargando {filename} ...")
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=20) as response, open(dest_path, "wb") as out_file:
            out_file.write(response.read())
        print(f"  OK -> {dest_path}")
        return True
    except urllib.error.URLError as e:
        print(f"  ERROR al descargar {filename}: {e}")
        return False


def main():
    os.makedirs(DEST, exist_ok=True)
    print(f"Guardando imagenes en: {DEST}\n")

    ok = 0
    for url, filename in FILES:
        if download(url, filename):
            ok += 1

    print(f"\nListo: {ok} de {len(FILES)} imagenes descargadas correctamente.")
    print("Nota: la entrada 'La secta del arroz y pollo' no tenia imagen")
    print("en el sitio original, por eso no se descarga ninguna para ella;")
    print("la pagina usa en su lugar un panel decorativo en CSS.")


if __name__ == "__main__":
    main()
