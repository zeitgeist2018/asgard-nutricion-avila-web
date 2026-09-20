#!/usr/bin/env bash
# =========================================================
# download-images.sh
#
# Descarga las imágenes originales del blog de Asgard Nutrición
# Deportiva y las guarda en la carpeta images/ del proyecto con
# los nombres que ya usan las páginas HTML.
#
# Uso:
#   1) Coloca este script en la raíz del proyecto (junto a index.html)
#   2) Dale permisos de ejecución:  chmod +x download-images.sh
#   3) Ejecútalo:                   ./download-images.sh
#
# Requiere tener "curl" instalado (viene por defecto en macOS y
# en la mayoría de distribuciones de Linux; en Windows puedes
# usar Git Bash o WSL).
# =========================================================

set -e

DEST="images"
mkdir -p "$DEST"

download () {
  local url="$1"
  local out="$2"
  echo "Descargando $out ..."
  curl -L --fail --silent --show-error "$url" -o "$DEST/$out"
}

# Logo de la tienda (usado en la cabecera de todas las páginas)
download "https://asgardnutriciondeportivaavila.com/wp-content/uploads/2026/07/cropped-WhatsApp-Image-2026-06-19-at-5.26.44-AM.jpeg" "logo.jpg"

# Imágenes de las entradas del blog
download "https://asgardnutriciondeportivaavila.com/wp-content/uploads/2026/07/1000612808-1024x768.jpg" "post-357-glutamina.jpg"
download "https://asgardnutriciondeportivaavila.com/wp-content/uploads/2026/07/1000605452-1024x702.jpg" "post-332-ashwagandha.jpg"
download "https://asgardnutriciondeportivaavila.com/wp-content/uploads/2026/07/1000552674-802x1024.jpg" "post-323-motivacion.jpg"
download "https://asgardnutriciondeportivaavila.com/wp-content/uploads/2026/06/1000597033-1024x466.jpg" "post-315-recuerdo.jpg"
download "https://asgardnutriciondeportivaavila.com/wp-content/uploads/2026/06/1000578686-1024x1024.png" "post-300-realidad.png"
download "https://asgardnutriciondeportivaavila.com/wp-content/uploads/2026/06/1000589434-1024x465.jpg" "post-293-diferenciamos.jpg"

# Imágenes de producto (sección "Nuestros productos" de la home)
download "https://asgardnutriciondeportivaavila.com/wp-content/uploads/2026/05/UK-ABEPerformanceEnergyDrink330ml12x330ml-GrapeSoda.png" "product-abe-energy-drink.png"
download "https://asgardnutriciondeportivaavila.com/wp-content/uploads/2026/05/ultra-zmax.png" "product-ultra-zma.png"
download "https://asgardnutriciondeportivaavila.com/wp-content/uploads/2026/05/prime-v-ts8.png" "product-prime-vts8.png"
download "https://asgardnutriciondeportivaavila.com/wp-content/uploads/2026/05/omega-3-100-perlas.png" "product-omega-3.png"
download "https://asgardnutriciondeportivaavila.com/wp-content/uploads/2026/05/Mockup-90-ISO-2kg-Chocolate-blanco-1536x1536.png.webp" "product-iso-90-choco-blanco.webp"
download "https://asgardnutriciondeportivaavila.com/wp-content/uploads/2026/05/Mockup-80-WHEY-ESSENTIAL-2kg-Kic-choco-1536x1536.png.webp" "product-whey-essential.webp"
download "https://asgardnutriciondeportivaavila.com/wp-content/uploads/2026/05/isolate-pro-zero-1-kg-caramelo.png" "product-isolate-pro-zero.png"
download "https://asgardnutriciondeportivaavila.com/wp-content/uploads/2026/05/essence-pro-whey-1-kg-chocolate-con-leche.png" "product-essence-pro-whey.png"
download "https://asgardnutriciondeportivaavila.com/wp-content/uploads/2026/05/creatine-gummies.png" "product-creatine-gummies.png"
download "https://asgardnutriciondeportivaavila.com/wp-content/uploads/2026/05/creatine-clonapure.png" "product-creatine-clonapure.png"
download "https://asgardnutriciondeportivaavila.com/wp-content/uploads/2026/05/boogieman-300-gr-1674558261-big.webp" "product-boogieman.webp"
download "https://asgardnutriciondeportivaavila.com/wp-content/uploads/2026/05/artiflex-vitobest.webp" "product-artiflex.webp"
download "https://asgardnutriciondeportivaavila.com/wp-content/uploads/2026/05/anabol-testo-booster-limonada-rosa-240gr.png" "product-anabol-testo-booster.png"
download "https://asgardnutriciondeportivaavila.com/wp-content/uploads/2026/05/ABEUltimatePre-Workout375g-CandyIceBlast_54770520-adae-4f8d-8387-0ae3254e0f92.webp" "product-abe-preworkout.webp"
download "https://asgardnutriciondeportivaavila.com/wp-content/uploads/2026/05/8594159531093-1.png" "product-misc-1.png"
download "https://asgardnutriciondeportivaavila.com/wp-content/uploads/2026/05/1064885868_1dad70fa-adb3-440d-95c2-c1c16472b463.png" "product-misc-2.png"

# Logos de marcas (sección "Marcas de confianza" de la home)
download "https://asgardnutriciondeportivaavila.com/wp-content/uploads/2026/05/Logo_01.png" "brand-logo-01.png"
download "https://asgardnutriciondeportivaavila.com/wp-content/uploads/2026/05/Logo_02.png" "brand-logo-02.png"
download "https://asgardnutriciondeportivaavila.com/wp-content/uploads/2026/05/Logo_03.png" "brand-logo-03.png"
download "https://asgardnutriciondeportivaavila.com/wp-content/uploads/2026/05/Logo_04.png" "brand-logo-04.png"

echo ""
echo "Listo. Se han descargado las imágenes en la carpeta '$DEST/'."
echo "Nota: la entrada 'La secta del arroz y pollo' no tenía imagen"
echo "en el sitio original, por eso no se descarga ninguna para ella;"
echo "la página usa en su lugar un panel decorativo en CSS."
