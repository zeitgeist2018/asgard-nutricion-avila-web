# Asgard Nutrición Deportiva — Sitio web

Sitio estático (HTML, CSS y JavaScript mínimo), publicado en GitHub
Pages, con un blog que se genera automáticamente a partir de
archivos Markdown. Pensado para que alguien sin conocimientos
técnicos pueda publicar una entrada nueva desde el móvil, sin
comandos ni servidores, y para que el resultado tenga buen SEO.

## Cómo funciona (visión general)

```
Hermano escribe la entrada        →  App "Publicar en Asgard"
en la app del móvil                  (publisher/)
                                          │
                                          │ crea blog/xxx.md
                                          │ vía API de GitHub
                                          ▼
                                   Rama "master" del repositorio
                                   (código fuente + entradas .md)
                                          │
                                          │ dispara automáticamente
                                          ▼
                                   GitHub Actions
                                   (.github/workflows/deploy.yml)
                                          │
                                          │ ejecuta build_site.py:
                                          │ .md → HTML real, con SEO
                                          ▼
                                   Rama "gh-pages"
                                   (solo HTML/CSS/JS ya construidos)
                                          │
                                          ▼
                                   Sitio publicado
                                   (tu dominio propio)
```

Dos ramas, cada una con su función:
- **`master`** — el código fuente: plantillas, estilos, la app de
  publicar, y las entradas en `blog/*.md`. Aquí es donde se añade
  contenido nuevo.
- **`gh-pages`** — el sitio ya construido, en HTML puro. GitHub
  Pages sirve el contenido de esta rama. **No se edita a mano**:
  la genera GitHub Actions automáticamente en cada cambio en `master`.

## Por qué así (y no con JavaScript cargando el blog al vuelo)

Una versión anterior de este proyecto cargaba las entradas con
JavaScript en el propio navegador de cada visitante. Es más simple
de montar, pero tiene un problema real para una tienda que vive del
boca a boca: los enlaces compartidos en WhatsApp o Facebook no
generan vista previa (esas apps no ejecutan JavaScript), y Google
tarda más e indexa peor ese tipo de contenido. Por eso ahora cada
entrada se convierte en una página HTML normal y corriente, ya
escrita, con su título, su descripción y su URL propia — antes de
que nadie la visite.

## Dominio: gratuito de GitHub Pages, o propio

Al principio de `build_site.py` hay un interruptor:

```python
USE_CUSTOM_DOMAIN = False
```

- **`False`** (como está ahora) → el sitio se genera para
  `https://zeitgeist2018.github.io/asgard-nutricion-avila-web/`, la
  URL gratuita de GitHub. Como esa URL vive en una subcarpeta (no en
  la raíz del dominio), el build reescribe automáticamente todas las
  rutas del sitio (`/css/...`, `/blog/...`, etc.) para que incluyan
  ese prefijo — si no lo hiciera, nada cargaría, igual que pasa al
  previsualizar con un servidor que no sirve desde la raíz correcta.
- **`True`** → el sitio se genera para el dominio propio de
  `SITE_URL` (más abajo en el mismo archivo), sin ningún prefijo, y
  se copia el archivo `CNAME` para que GitHub Pages sepa servir ese
  dominio.

Cuando el dominio propio esté listo, solo hay que cambiar esa línea
a `True` (y comprobar que `SITE_URL` y `CNAME` tienen el dominio
correcto) y volver a construir el sitio — no hace falta tocar nada
más.

## Configuración inicial (una sola vez)

1. **Verifica que el repositorio existe** con dos ramas: `master`
   (con todo este contenido) y `gh-pages` (puede empezar vacía;
   Actions la rellena sola en el primer build).
2. **Activa GitHub Pages** desde el repositorio: Settings → Pages →
   Source → "Deploy from a branch" → rama `gh-pages`, carpeta `/`.
3. **Sobre el dominio** — ahora mismo el sitio está configurado para
   la URL gratuita de GitHub Pages (`USE_CUSTOM_DOMAIN = False` en
   `build_site.py`). Cuando quieras pasar al dominio propio, ve a la
   sección "Dominio: gratuito de GitHub Pages, o propio" de este
   mismo README.
4. **No hace falta tocar nada más** para que el build funcione: el
   workflow de GitHub Actions usa un permiso que GitHub concede
   automáticamente (`GITHUB_TOKEN`), no hay que crear ningún secreto
   para publicar el sitio.

## Configurar la app "Publicar en Asgard" (una sola vez, en el móvil del hermano)

La app vive en `/publisher/` dentro del propio sitio, así que en
cuanto el sitio esté publicado estará disponible en
`https://tu-dominio/publisher/`.

1. Abre esa dirección en el móvil con Chrome (Android).
2. Menú del navegador → **"Añadir a pantalla de inicio"** /
   "Instalar app". Quedará como un icono más, se abre a pantalla
   completa como cualquier app.
3. La primera vez pedirá los ajustes de conexión con GitHub:
   - **Usuario/organización**: `zeitgeist2018`
   - **Repositorio**: `asgard-nutricion-avila-web`
   - **Rama**: `master`
   - **Token de acceso**: hay que crearlo una vez en GitHub —
     Settings (de tu cuenta) → Developer settings → Fine-grained
     personal access tokens → Generate new token. Dale acceso
     **solo a este repositorio** y el permiso
     **Contents: Read and write** (ningún otro). Cópialo y pégalo
     en la app.
4. Guardar ajustes. Ya está — a partir de aquí, publicar es rellenar
   el título y el texto, y pulsar "Publicar entrada".

**Sobre la seguridad del token:** se guarda únicamente en el
almacenamiento privado de ese navegador/teléfono, y solo se usa para
hablar directamente con `api.github.com` desde el propio dispositivo
— nunca pasa por ningún servidor intermedio ni queda en ningún
código visible. Al estar limitado a un solo repositorio y solo con
permiso de lectura/escritura de contenido, si el token se filtrara
alguna vez, el daño posible quedaría limitado a ese repositorio.

## Qué pasa cuando se publica una entrada

1. La app crea `blog/tu-titulo.md` (y la foto en `images/`, si la
   hay) directamente en la rama `master`, vía la API de GitHub.
2. Eso dispara automáticamente el workflow de GitHub Actions.
3. En menos de un minuto, la Action reconstruye el sitio entero y lo
   publica en `gh-pages`.
4. La entrada ya está online, con su propia URL
   (`/blog/tu-titulo/`), indexable por Google y con vista previa
   correcta al compartirla.

Puedes ver el progreso de cada publicación en la pestaña **Actions**
del repositorio en GitHub.

## Añadir una entrada a mano (alternativa a la app)

Sigue funcionando exactamente igual que crear el archivo desde la
app: crea `blog/tu-titulo.md` en la rama `master` con este formato:

```markdown
---
title: "Título de la entrada"
date: "2026-08-01"
author: "Israel Lobo Martín"
image: "images/tu-foto.jpg"
excerpt: "Resumen corto que aparece en la tarjeta."
---

Contenido en Markdown normal: párrafos, **negrita**, *cursiva*,
## subtítulos, enlaces [texto](url)...
```

El campo `image` es opcional. En cuanto se suba a `master`, aparece
sola en el sitio en menos de un minuto.

## Ver el sitio en local mientras se edita

```
pip install markdown
python build_site.py
```

Esto genera una carpeta `dist/` con el sitio completo ya construido.
Ábrela con un servidor local para verla:

```
cd dist
python -m http.server 8000
```

y visita `http://localhost:8000`. La carpeta `dist/` no se sube al
repositorio (está en `.gitignore`) — la genera GitHub Actions cada
vez.

## Estructura del proyecto

```
.github/workflows/deploy.yml  → El build automático (GitHub Actions)
build_site.py                  → Genera dist/ a partir de todo lo demás
requirements.txt                → Dependencia de Python para el build
CNAME                           → Dominio propio para GitHub Pages
.nojekyll                       → Evita que GitHub procese el sitio con Jekyll
index.html, blog.html          → Plantillas de la home y el listado del blog
templates/post_template.html   → Plantilla de una entrada individual
blog/*.md                       → Las entradas del blog (código fuente)
publisher/                      → La app para publicar desde el móvil
css/                             → Estilos (paleta, tipografía, componentes)
js/main.js                      → Solo el menú móvil (lo demás ya es HTML fijo)
images/                         → Todas las imágenes del sitio
download-images.sh / .py       → Descargan las imágenes reales del sitio original
```

## Imágenes de muestra

Las imágenes de `images/` son de sustitución temporal. Para poner
las reales del sitio original:

```
python download_images.py
```

o, en macOS/Linux: `chmod +x download-images.sh && ./download-images.sh`

## Colores y tipografía

Paleta sencilla: negro casi puro de fondo, blanco casi puro para el
texto, y un único color de acento (dorado). Todo se controla desde
`css/variables.css`. Tipografía **Caudex** en todo el sitio.

## Añadir una página nueva (no de blog) en el futuro

1. Crea el nuevo archivo `.html` en la raíz y enlaza las 5 hojas de
   estilo igual que `blog.html`.
2. Usa las funciones `render_header(...)` / `render_footer(...)` de
   `build_site.py` si quieres que también pase por el build (con
   cabecera/pie ya escritos), o simplemente escribe el HTML de
   cabecera/pie a mano copiándolo de una página ya generada.
3. Añade el enlace en `render_header()` dentro de `build_site.py`
   para que aparezca en el menú de todas las páginas.
