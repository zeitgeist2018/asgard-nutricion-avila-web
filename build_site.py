#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_site.py

Construye el sitio estático final en dist/ a partir de:
  - las plantillas index.html, blog.html, templates/post_template.html
  - las entradas del blog en blog/*.md
  - los assets estáticos (css/, js/, images/, publisher/)

Se ejecuta automáticamente en GitHub Actions en cada push a la rama
"main" (ver .github/workflows/deploy.yml). No hace falta ejecutarlo
a mano en el uso normal, pero también funciona en local:

    pip install markdown
    python build_site.py

El resultado queda en dist/, listo para publicarse tal cual.
"""

import html
import json
import os
import re
import shutil
import urllib.parse
from datetime import datetime, timezone

import markdown

# --------------------------------------------------------------------
# Configuración del sitio.
#
# Cambia USE_CUSTOM_DOMAIN a True cuando el dominio propio esté listo
# (y ajusta la URL de abajo si es distinta de la actual). Con False,
# el sitio se genera para la URL gratuita de GitHub Pages, que vive
# bajo una subcarpeta con el nombre del repositorio — por eso también
# hace falta BASE_PATH, para que todas las rutas absolutas (/css/...,
# /blog/...) se reescriban con ese prefijo y no rompan al cargar.
# --------------------------------------------------------------------
USE_CUSTOM_DOMAIN = True

if USE_CUSTOM_DOMAIN:
    SITE_URL = "https://asgardavilanutriciondeportiva.com"
    BASE_PATH = ""
else:
    SITE_URL = "https://zeitgeist2018.github.io/asgard-nutricion-avila-web"
    BASE_PATH = "/asgard-nutricion-avila-web"

SITE_NAME = "Asgard Nutrición Deportiva"

# Imágenes para las vistas previas (WhatsApp, Google, redes)
LOGO_IMAGE = f"{SITE_URL}/images/logo.jpg"
SHARE_IMAGE = f"{SITE_URL}/images/share.jpg"  # 1200x630

# Datos de la tienda para los datos estructurados (JSON-LD) de la portada.
# Lo que quede vacío no se publica. Google usa la dirección para la ficha local.
BUSINESS = {
    "telephone": "+34683584356",
    "instagram": "https://www.instagram.com/asgardnutricionavila",
    "streetAddress": "Pl. Sta. Ana, 2",
    "postalCode": "05001",
    "addressLocality": "Ávila",
    "addressRegion": "Castilla y León",
    "addressCountry": "ES",
    # Horario de Google Maps. Domingo cerrado: no se incluye.
    "openingHours": [
        "Mo-Fr 10:30-14:00",
        "Mo-Fr 17:00-20:00",
        "Sa 11:00-13:30",
    ],
    "latitude": 40.656396,
    "longitude": -4.689563,
    # Enlace de la ficha de Google Maps (desde ahí se pulsa "Escribir una reseña").
    # Si está vacío, no se muestra el enlace.
    "reviewUrl": "https://maps.app.goo.gl/CyCavWFksUik9Vn6A",
}
DEFAULT_AUTHOR = "Israel Lobo Martín"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BLOG_DIR = os.path.join(BASE_DIR, "blog")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
# Carpeta de salida. serve_local.py la cambia para probar en el navegador sin tocar dist/.
DIST_DIR = os.environ.get("ASGARD_DIST_DIR") or os.path.join(BASE_DIR, "dist")

MESES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]


# --------------------------------------------------------------------
# Utilidades
# --------------------------------------------------------------------

def parse_frontmatter(raw):
    """Igual que en js/blog.js (ya retirado): separa '---\\n...\\n---' del cuerpo."""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", raw, re.S)
    if not match:
        return {}, raw.strip()
    block, body = match.groups()
    data = {}
    for line in block.split("\n"):
        m = re.match(r"^([a-zA-Z0-9_]+)\s*:\s*(.*)$", line)
        if not m:
            continue
        key, value = m.group(1), m.group(2).strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        value = value.replace('\\"', '"')
        data[key] = value
    return data, body.strip()


def format_date_es(iso):
    try:
        d = datetime.strptime(iso, "%Y-%m-%d")
    except (ValueError, TypeError):
        return iso or ""
    return f"{d.day} de {MESES[d.month - 1]} de {d.year}"


def truncate(text, n):
    text = text or ""
    if len(text) <= n:
        return text
    return text[:n].rsplit(" ", 1)[0] + "…"


def esc(text):
    """Escapa para usar dentro de atributos/texto HTML."""
    return html.escape(text or "", quote=True)


SHIELD_SVG = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3" '
    'aria-hidden="true"><path d="M12 21c-4-2-8-5-8-10V5l8-3 8 3v6c0 5-4 8-8 10Z" '
    'stroke-linejoin="round"/></svg>'
)


# --------------------------------------------------------------------
# Carga de entradas
# --------------------------------------------------------------------

def load_posts():
    posts = []
    if not os.path.isdir(BLOG_DIR):
        return posts
    for filename in sorted(os.listdir(BLOG_DIR)):
        if not filename.lower().endswith(".md"):
            continue
        path = os.path.join(BLOG_DIR, filename)
        with open(path, encoding="utf-8") as f:
            raw = f.read()
        data, body_md = parse_frontmatter(raw)
        # Borradores: se guardan en el repo (y se ven en el panel) pero no se publican
        if data.get("draft", "").lower() == "true":
            continue
        slug = filename[:-3]
        body_html = markdown.markdown(body_md, extensions=["extra", "sane_lists"])
        posts.append({
            "slug": slug,
            "title": data.get("title", slug),
            "date": data.get("date", ""),
            "author": data.get("author", DEFAULT_AUTHOR),
            "image": data.get("image", ""),
            "excerpt": data.get("excerpt", ""),
            "body_html": body_html,
        })
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts


# --------------------------------------------------------------------
# Cabecera y pie de página (antes se inyectaban con JS; ahora son
# HTML real escrito en cada página para que los rastreadores lo vean
# sin ejecutar nada).
# --------------------------------------------------------------------

def render_header(active_page):
    def nav_link(href, label, page_id):
        current = ' aria-current="page"' if page_id == active_page else ""
        return f'<li><a class="main-nav__link" href="{href}"{current}>{label}</a></li>'

    instagram_icon = (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true">'
        '<rect x="3" y="3" width="18" height="18" rx="5"/>'
        '<circle cx="12" cy="12" r="4.2"/>'
        '<circle cx="17.2" cy="6.8" r="0.9" fill="currentColor" stroke="none"/>'
        '</svg>'
    )
    instagram_link = (
        '<li><a class="main-nav__icon-link" href="https://www.instagram.com/asgardnutricionavila" '
        'target="_blank" rel="noopener noreferrer" aria-label="Instagram de Asgard Nutrición Deportiva">'
        + instagram_icon + '</a></li>'
    )

    nav_items = (
        nav_link("/index.html", "Inicio", "inicio")
        + nav_link("/blog.html", "Blog", "blog")
        + nav_link("/catalogo.html", "Catálogo", "catalogo")
        + instagram_link
    )

    return f'''<header class="site-header" id="site-header">
    <div class="container site-header__inner">
      <a class="brand" href="/index.html" aria-label="Ir a la página de inicio de Asgard Nutrición Deportiva">
        <img class="brand__mark" src="/images/logo.jpg" alt="" width="42" height="42">
        <span class="brand__name">Asgard<span>Nutrición Deportiva</span></span>
      </a>
      <nav class="main-nav" id="main-nav" aria-label="Navegación principal">
        <ul class="main-nav__list">{nav_items}</ul>
      </nav>
      <button class="nav-toggle" id="nav-toggle" aria-expanded="false" aria-controls="main-nav" aria-label="Abrir menú de navegación">
        <span class="nav-toggle__bar nav-toggle__bar--top"></span>
        <span class="nav-toggle__bar nav-toggle__bar--mid"></span>
        <span class="nav-toggle__bar nav-toggle__bar--bottom"></span>
      </button>
    </div>
  </header>'''


def render_footer():
    year = datetime.now().year
    return f'''<footer class="site-footer" id="site-footer">
    <div class="container site-footer__inner">
      <svg class="site-footer__rune" viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
        <path d="M24 4v40M24 4l-10 10M24 4l10 10M24 44l-10-10M24 44l10-10M10 24h28" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <p class="site-footer__brand">Asgard Nutrición Deportiva</p>
      <p class="site-footer__tagline">Nutrición deportiva y asesoramiento con la firmeza de la vieja guardia.</p>
      <nav class="site-footer__nav" aria-label="Enlaces del pie de página">
        <a href="/index.html">Inicio</a>
        <a href="/blog.html">Blog</a>
      </nav>
      <p class="site-footer__meta">© {year} Asgard Nutrición Deportiva</p>
    </div>
  </footer>'''


def render_whatsapp_button():
    whatsapp_url = (
        "https://api.whatsapp.com/send/?phone=34683584356&text=Hola,%20me%20"
        "gustar%C3%ADa%20saber%20qu%C3%A9%20catalogo%20de%20prote%C3%ADnas%20ten%C3%A9is"
    )
    icon = (
        '<svg viewBox="0 0 32 32" fill="currentColor" aria-hidden="true">'
        '<path d="M16.001 3C9.106 3 3.5 8.605 3.5 15.5c0 2.385.664 4.615 1.816 6.52L3 29l7.163-2.263A12.44 '
        '12.44 0 0 0 16 28.999C22.895 29 28.5 23.394 28.5 16.5S22.895 4 16.001 3Zm7.06 17.94c-.302.85-1.51 '
        '1.56-2.47 1.77-.66.14-1.52.25-4.42-.95-3.71-1.53-6.1-5.28-6.29-5.53-.18-.25-1.5-2-1.5-3.82 '
        '0-1.82.95-2.71 1.29-3.08.3-.32.66-.4.88-.4.22 0 .44 0 .63.01.2.01.47-.08.74.56.28.66.94 2.29 '
        '1.02 2.46.08.17.13.37.03.6-.1.23-.15.37-.3.56-.15.19-.31.43-.44.58-.15.16-.31.34-.13.66.18.32 '
        '.79 1.3 1.7 2.11 1.17 1.04 2.15 1.37 2.47 1.52.32.15.51.13.7-.08.19-.21.81-.95 1.03-1.28.22-.32 '
        '.44-.27.74-.16.3.11 1.9.9 2.22 1.06.32.16.53.24.61.38.08.13.08.76-.22 1.6Z"/>'
        '</svg>'
    )
    return (
        f'<a class="whatsapp-float" href="{whatsapp_url}" target="_blank" '
        'rel="noopener noreferrer" aria-label="Escríbenos por WhatsApp">'
        + icon + '</a>'
    )


# --------------------------------------------------------------------
# Tarjetas de entrada (home y listado del blog)
# --------------------------------------------------------------------

def render_card(post):
    href = f"/blog/{post['slug']}/"
    date_label = format_date_es(post["date"])
    excerpt = esc(truncate(post["excerpt"], 160))
    title = esc(post["title"])

    if post["image"]:
        media = (
            f'<a class="post-card__media" href="{href}" tabindex="-1">'
            f'<img src="/{post["image"]}" alt="{title}" loading="lazy"></a>'
        )
    else:
        media = f'<div class="post-card__media post-card__media--fallback">{SHIELD_SVG}</div>'

    return (
        '<article class="post-card">'
        + media
        + '<div class="post-card__body">'
        + f'<span class="post-card__date">{date_label}</span>'
        + f'<h3 class="post-card__title"><a href="{href}">{title}</a></h3>'
        + f'<p class="post-card__excerpt">{excerpt}</p>'
        + '<span class="post-card__link">Leer más →</span>'
        + "</div></article>"
    )


# --------------------------------------------------------------------
# Páginas
# --------------------------------------------------------------------

def render_placeholder_page(template_text, active_page, extra_replacements):
    out = template_text.replace("<!--HEADER-->", render_header(active_page))
    out = out.replace("<!--FOOTER-->", render_footer())
    out = out.replace("{{SITE_URL}}", SITE_URL)
    for key, value in extra_replacements.items():
        out = out.replace(key, value)
    # Botón flotante de WhatsApp en todas las páginas
    out = out.replace("</body>", render_whatsapp_button() + "\n</body>")
    return out


def json_ld_script(data):
    """Envuelve datos JSON-LD en la etiqueta <script> que leen los buscadores."""
    return '<script type="application/ld+json">\n' + json.dumps(data, ensure_ascii=False, indent=2) + "\n</script>"


def organization_json_ld():
    return {
        "@type": "Organization",
        "name": SITE_NAME,
        "url": f"{SITE_URL}/",
        "logo": {"@type": "ImageObject", "url": LOGO_IMAGE},
    }


def store_json_ld():
    """Ficha de la tienda y del sitio web (solo en la portada)."""
    address = {
        "@type": "PostalAddress",
        "addressLocality": BUSINESS["addressLocality"],
        "addressRegion": BUSINESS["addressRegion"],
        "addressCountry": BUSINESS["addressCountry"],
    }
    if BUSINESS["streetAddress"]:
        address["streetAddress"] = BUSINESS["streetAddress"]
    if BUSINESS["postalCode"]:
        address["postalCode"] = BUSINESS["postalCode"]

    store = {
        "@context": "https://schema.org",
        "@type": "Store",
        "@id": f"{SITE_URL}/#store",
        "name": SITE_NAME,
        "url": f"{SITE_URL}/",
        "logo": LOGO_IMAGE,
        "image": SHARE_IMAGE,
        "address": address,
        "sameAs": [BUSINESS["instagram"]],
    }
    if BUSINESS["telephone"]:
        store["telephone"] = BUSINESS["telephone"]
    if BUSINESS["openingHours"]:
        store["openingHours"] = BUSINESS["openingHours"]
    if BUSINESS["latitude"] and BUSINESS["longitude"]:
        store["geo"] = {
            "@type": "GeoCoordinates",
            "latitude": BUSINESS["latitude"],
            "longitude": BUSINESS["longitude"],
        }

    website = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "@id": f"{SITE_URL}/#website",
        "name": SITE_NAME,
        "url": f"{SITE_URL}/",
        "inLanguage": "es-ES",
    }
    return [website, store]


def blog_json_ld(posts):
    """Listado del blog: cada entrada publicada como BlogPosting."""
    return {
        "@context": "https://schema.org",
        "@type": "Blog",
        "name": "Blog de " + SITE_NAME,
        "url": f"{SITE_URL}/blog.html",
        "inLanguage": "es-ES",
        "publisher": organization_json_ld(),
        "blogPost": [
            {
                "@type": "BlogPosting",
                "headline": p["title"],
                "url": f"{SITE_URL}/blog/{p['slug']}/",
                "datePublished": p["date"],
            }
            for p in posts
        ],
    }


def breadcrumb_json_ld(title, canonical):
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Inicio", "item": f"{SITE_URL}/"},
            {"@type": "ListItem", "position": 2, "name": "Blog", "item": f"{SITE_URL}/blog.html"},
            {"@type": "ListItem", "position": 3, "name": title, "item": canonical},
        ],
    }


# --------------------------------------------------------------------
# Catálogo de productos (se gestiona desde el panel de administración)
# --------------------------------------------------------------------

CATALOG_FILE = os.path.join(BASE_DIR, "catalogo", "catalogo.json")
CAROUSEL_LIMIT = 12  # productos que muestra el carrusel de la portada
WHATSAPP_NUMBER = BUSINESS["telephone"].lstrip("+")


def load_catalog():
    """Devuelve (categorias, productos). Los productos salen primero los más recientes."""
    if not os.path.isfile(CATALOG_FILE):
        return [], []
    with open(CATALOG_FILE, encoding="utf-8") as f:
        data = json.load(f)

    categories = data.get("categorias", [])
    names = {c["id"]: c["nombre"] for c in categories}
    brands = {m["id"]: m["nombre"] for m in data.get("marcas", [])}
    products = []
    for p in data.get("productos", []):
        products.append({
            "id": p["id"],
            "titulo": p.get("titulo", ""),
            "descripcion": p.get("descripcion", ""),
            "categoria": p.get("categoria", ""),
            "categoriaNombre": names.get(p.get("categoria", ""), ""),
            "marcaNombre": brands.get(p.get("marca", ""), ""),
            "precioOriginal": p.get("precioOriginal"),
            "precioReal": p.get("precioReal"),
            "imagen": p.get("imagen", ""),
            "creado": p.get("creado", ""),
        })
    products.sort(key=lambda p: p["creado"], reverse=True)
    return categories, products


def format_price(value):
    """Precio en formato español: 1.234,50 €"""
    text = f"{float(value):,.2f}"  # 1,234.50 (formato inglés)
    return text.replace(",", "§").replace(".", ",").replace("§", ".") + " €"


def whatsapp_question_url(product_title):
    """Enlace a WhatsApp con un mensaje ya escrito sobre ese producto."""
    text = f"Hola, me interesa el producto «{product_title}». ¿Me dices el precio?"
    return f"https://wa.me/{WHATSAPP_NUMBER}?text={urllib.parse.quote(text)}"


def product_card(p, with_description=False):
    if p["imagen"]:
        media = f'<img src="/{esc(p["imagen"])}" alt="{esc(p["titulo"])}" loading="lazy">'
    else:
        media = '<span class="product-card__placeholder">Sin foto</span>'

    prices = []
    if p["precioOriginal"] is not None:
        prices.append(f'<s class="product-card__old">{format_price(p["precioOriginal"])}</s>')
    if p["precioReal"] is not None:
        prices.append(f'<span class="product-card__real">{format_price(p["precioReal"])}</span>')
    else:
        prices.append(
            f'<a class="product-card__ask" href="{esc(whatsapp_question_url(p["titulo"]))}" '
            'target="_blank" rel="noopener noreferrer">Consulta el precio con nosotros</a>'
        )

    category = f'<span class="product-card__cat">{esc(p["categoriaNombre"])}</span>' if p["categoriaNombre"] else ""
    if p["marcaNombre"]:
        category += f'<span class="product-card__brand">{esc(p["marcaNombre"])}</span>'
    description = ""
    if with_description and p["descripcion"]:
        description = f'<p class="product-card__desc">{esc(p["descripcion"])}</p>'

    return (
        f'<article class="product-card" data-category="{esc(p["categoria"])}">'
        f'<div class="product-card__media">{media}</div>'
        '<div class="product-card__body">'
        + category
        + f'<h3 class="product-card__title">{esc(p["titulo"])}</h3>'
        + description
        + '<div class="product-card__prices">' + "".join(prices) + "</div>"
        + "</div></article>"
    )


def catalog_carousel_html(products):
    """Carrusel de novedades para la portada (vacío si no hay productos)."""
    if not products:
        return ""
    items = "".join(f"<li>{product_card(p)}</li>" for p in products[:CAROUSEL_LIMIT])
    return (
        '<section class="section section--alt" id="novedades">'
        '<div class="container">'
        '<div class="section__head"><p class="eyebrow">Catálogo</p><h2>Últimas incorporaciones</h2></div>'
        '<div class="carousel" data-carousel>'
        '<ul class="carousel__track" aria-label="Productos del catálogo">' + items + "</ul>"
        "</div>"
        '<div class="carousel__footer"><a class="btn btn--primary" href="/catalogo.html">Ver todo el catálogo</a></div>'
        "</div></section>"
    )


def build_catalog_page(categories, products):
    with open(os.path.join(BASE_DIR, "catalogo.html"), encoding="utf-8") as f:
        template = f.read()
    filters = ['<button type="button" class="chip-filter is-active" data-filter="all" aria-pressed="true">Todos</button>']
    for c in categories:
        filters.append(
            f'<button type="button" class="chip-filter" data-filter="{esc(c["id"])}" aria-pressed="false">'
            f'{esc(c["nombre"])}</button>'
        )
    grid = "".join(product_card(p, with_description=True) for p in products)
    html_out = render_placeholder_page(template, "catalogo", {
        "<!--CATALOG_FILTERS-->": "".join(filters),
        "<!--CATALOG_GRID-->": grid or '<p class="catalog-empty">Todavía no hay productos en el catálogo.</p>',
    })
    write_file(os.path.join(DIST_DIR, "catalogo.html"), html_out)


def review_link_html():
    """Enlace para dejar una reseña en Google. Vacío si no hay enlace configurado."""
    if not BUSINESS["reviewUrl"]:
        return ""
    return (
        '<p class="hero__review"><a href="' + esc(BUSINESS["reviewUrl"]) + '" '
        'target="_blank" rel="noopener noreferrer">¿Te ha gustado? Deja una reseña en Google ★</a></p>'
    )


def build_home(posts, products):
    with open(os.path.join(BASE_DIR, "index.html"), encoding="utf-8") as f:
        template = f.read()
    cards = "".join(render_card(p) for p in posts[:3]) or (
        '<p style="color: var(--color-text-muted);">Todavía no hay entradas publicadas.</p>'
    )
    html_out = render_placeholder_page(template, "inicio", {
        "<!--LATEST_POSTS-->": cards,
        "<!--JSON_LD-->": json_ld_script(store_json_ld()),
        "<!--REVIEW_LINK-->": review_link_html(),
        "<!--CATALOG_CAROUSEL-->": catalog_carousel_html(products),
    })
    write_file(os.path.join(DIST_DIR, "index.html"), html_out)


def build_blog_listing(posts):
    with open(os.path.join(BASE_DIR, "blog.html"), encoding="utf-8") as f:
        template = f.read()
    cards = "".join(render_card(p) for p in posts) or (
        '<p style="color: var(--color-text-muted);">Todavía no hay entradas publicadas.</p>'
    )
    html_out = render_placeholder_page(template, "blog", {
        "<!--BLOG_GRID-->": cards,
        "<!--JSON_LD-->": json_ld_script(blog_json_ld(posts)),
    })
    write_file(os.path.join(DIST_DIR, "blog.html"), html_out)


def build_post_pages(posts):
    with open(os.path.join(TEMPLATES_DIR, "post_template.html"), encoding="utf-8") as f:
        template = f.read()

    for post in posts:
        canonical = f"{SITE_URL}/blog/{post['slug']}/"
        title = esc(post["title"])
        description = esc(truncate(post["excerpt"], 155))
        date_label = format_date_es(post["date"])
        author = esc(post["author"])

        if post["image"]:
            image_url = f"{SITE_URL}/{post['image']}"
            cover_html = (
                f'<figure class="article-cover"><img src="/{post["image"]}" alt="{title}" loading="lazy"></figure>'
            )
            og_image = f'<meta property="og:image" content="{image_url}">'
            twitter_image = f'<meta name="twitter:image" content="{image_url}">'
            twitter_card_type = "summary_large_image"
        else:
            cover_html = (
                '<div class="decorative-panel" role="img" aria-label="Motivo ornamental vikingo">'
                + SHIELD_SVG + "</div>"
            )
            # Sin foto propia, la vista previa usa la imagen de marca (1200x630)
            og_image = f'<meta property="og:image" content="{SHARE_IMAGE}">'
            twitter_image = f'<meta name="twitter:image" content="{SHARE_IMAGE}">'
            twitter_card_type = "summary_large_image"

        article = {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": post["title"],
            "description": truncate(post["excerpt"], 155),
            "datePublished": post["date"],
            "dateModified": post["date"],
            "author": {"@type": "Person", "name": post["author"]},
            "publisher": organization_json_ld(),
            "mainEntityOfPage": canonical,
            "image": f"{SITE_URL}/{post['image']}" if post["image"] else SHARE_IMAGE,
            "inLanguage": "es-ES",
        }
        # Lista de datos: la entrada y la ruta de navegación (el template ya pone la etiqueta <script>)
        json_ld = json.dumps([article, breadcrumb_json_ld(post["title"], canonical)],
                             ensure_ascii=False, indent=2)

        page = template
        replacements = {
            "{{TITLE}}": title,
            "{{DESCRIPTION}}": description,
            "{{CANONICAL_URL}}": canonical,
            "{{DATE_ISO}}": post["date"],
            "{{DATE_LABEL}}": date_label,
            "{{AUTHOR}}": author,
            "{{OG_IMAGE}}": og_image,
            "{{TWITTER_IMAGE}}": twitter_image,
            "{{TWITTER_CARD_TYPE}}": twitter_card_type,
            "{{JSON_LD}}": json_ld,
            "{{COVER_HTML}}": cover_html,
            "{{BODY_HTML}}": post["body_html"],
        }
        page = render_placeholder_page(page, "blog", replacements)
        write_file(os.path.join(DIST_DIR, "blog", post["slug"], "index.html"), page)


# --------------------------------------------------------------------
# Sitemap y robots.txt
# --------------------------------------------------------------------

def build_sitemap(posts):
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    # La portada y el listado cambian cuando se publica una entrada: usan la fecha de la más reciente
    latest = max((p["date"] for p in posts if p["date"]), default=today)

    entries = [
        f"  <url><loc>{esc(SITE_URL)}/</loc><lastmod>{latest}</lastmod></url>",
        f"  <url><loc>{esc(SITE_URL)}/blog.html</loc><lastmod>{latest}</lastmod></url>",
        f"  <url><loc>{esc(SITE_URL)}/catalogo.html</loc><lastmod>{latest}</lastmod></url>",
    ]
    for p in posts:
        images = ""
        if p["image"]:
            images = (
                f"<image:image><image:loc>{esc(SITE_URL + '/' + p['image'])}</image:loc>"
                f"<image:caption>{esc(p['title'])}</image:caption></image:image>"
            )
        entries.append(
            f"  <url><loc>{esc(SITE_URL + '/blog/' + p['slug'] + '/')}</loc>"
            f"<lastmod>{p['date'] or latest}</lastmod>{images}</url>"
        )

    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n'
        + "\n".join(entries) + "\n</urlset>\n"
    )
    write_file(os.path.join(DIST_DIR, "sitemap.xml"), sitemap)

    robots = f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n"
    write_file(os.path.join(DIST_DIR, "robots.txt"), robots)


# --------------------------------------------------------------------
# Copia de assets estáticos
# --------------------------------------------------------------------

def copy_static_assets():
    for folder in ("css", "js", "images", "publisher"):
        src = os.path.join(BASE_DIR, folder)
        if os.path.isdir(src):
            shutil.copytree(src, os.path.join(DIST_DIR, folder))

    # Dominio propio para GitHub Pages: solo se copia el CNAME cuando
    # está en uso, para no confundir a GitHub Pages con un dominio que
    # todavía no está configurado en el DNS.
    if USE_CUSTOM_DOMAIN:
        cname_path = os.path.join(BASE_DIR, "CNAME")
        if os.path.isfile(cname_path):
            shutil.copy(cname_path, os.path.join(DIST_DIR, "CNAME"))

    # Evita que GitHub procese el sitio publicado con Jekyll
    open(os.path.join(DIST_DIR, ".nojekyll"), "w").close()


def apply_base_path(dist_dir, base_path):
    """Antepone base_path a toda ruta absoluta del sitio (/css/..., /blog/...,
    /images/..., /publisher/...) en cada archivo generado. No hace nada si
    base_path está vacío (caso del dominio propio, servido desde la raíz)."""
    if not base_path:
        return

    pattern = re.compile(
        r'"(/(?:css|js|images|blog|publisher)(?:/[^"]*)?|/(?:index|blog)\.html)"'
    )

    for root, _dirs, files in os.walk(dist_dir):
        for filename in files:
            if not filename.endswith((".html", ".webmanifest")):
                continue
            path = os.path.join(root, filename)
            with open(path, encoding="utf-8") as f:
                content = f.read()
            new_content = pattern.sub(
                lambda m: '"' + base_path + m.group(1) + '"', content
            )
            if new_content != content:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(new_content)


# --------------------------------------------------------------------

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def build_404():
    """Página de error propia. GitHub Pages la sirve cuando una URL no existe."""
    with open(os.path.join(BASE_DIR, "404.html"), encoding="utf-8") as f:
        template = f.read()
    write_file(os.path.join(DIST_DIR, "404.html"), render_placeholder_page(template, None, {}))


def main():
    if os.path.isdir(DIST_DIR):
        shutil.rmtree(DIST_DIR)
    os.makedirs(DIST_DIR, exist_ok=True)

    posts = load_posts()
    print(f"Entradas encontradas: {len(posts)}")
    for p in posts:
        print(f"  - {p['date']} | {p['title']}")

    categories, products = load_catalog()
    print(f"Productos en el catálogo: {len(products)}")

    build_home(posts, products)
    build_catalog_page(categories, products)
    build_blog_listing(posts)
    build_post_pages(posts)
    build_sitemap(posts)
    build_404()
    copy_static_assets()
    apply_base_path(DIST_DIR, BASE_PATH)

    domain_msg = "dominio propio" if USE_CUSTOM_DOMAIN else f"GitHub Pages (subcarpeta {BASE_PATH})"
    print(f"\nListo. Sitio generado en {DIST_DIR} para: {domain_msg}")


if __name__ == "__main__":
    main()
