# Asgard Nutrición Deportiva — Sitio web

## Estructura del proyecto

```
index.html              → Página de inicio
blog.html                → Listado de todas las entradas del blog
blog/                    → Una página HTML por cada entrada del blog
css/
  variables.css          → Paleta de color, tipografía, espaciados (edita aquí el estilo global)
  base.css                → Reset y tipografía base
  layout.css              → Cabecera, navegación, pie de página, contenedores
  components.css          → Tarjetas, botones, divisores, etc. (reutilizables)
  pages.css               → Estilos propios del hero, la cabecera de blog y el artículo
js/
  main.js                 → Inyecta la cabecera/pie en todas las páginas y controla el menú móvil
images/                   → Imágenes del sitio (logo + fotos de cada entrada)
```

## Añadir una página nueva en el futuro

1. Crea el nuevo archivo `.html` en la raíz (copia `blog.html` como
   plantilla, por ejemplo) y enlaza las 5 hojas de estilo y
   `js/main.js` igual que en las páginas existentes.
2. En el `<body>`, define `data-root="."` y un `data-page` propio,
   por ejemplo `data-page="tienda"`.
3. Añade una línea nueva al array `navLinks` en `js/main.js`:
   ```js
   { href: root + "/tienda.html", label: "Tienda", page: "tienda" }
   ```
   Ese enlace aparecerá automáticamente en el menú de **todas** las
   páginas del sitio, sin tener que tocar cada `<header>` a mano.

## Fuente tipográfica

El sitio usa **Caudex** (Google Fonts), cargada por CDN en el
`<head>` de cada página. Si prefieres alojarla localmente, descarga
los archivos `.woff2` de Caudex y sustituye el `<link>` de Google
Fonts por una regla `@font-face` en `css/variables.css` o
`css/base.css`.
