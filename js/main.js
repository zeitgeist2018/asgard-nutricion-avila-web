/* =========================================================
   MAIN.JS
   Inyecta la cabecera y el pie de página en cada página del
   sitio a partir de una única plantilla, para que añadir o
   renombrar páginas en el futuro solo implique editar este
   archivo una vez.

   Cada página debe definir en su <body>:
     data-root="."      -> páginas en la raíz (index.html, blog.html)
     data-root=".."      -> páginas dentro de /blog/
     data-page="inicio"  -> identificador de la página actual,
                            usado para resaltar el enlace activo
   ========================================================= */

(function () {
  "use strict";

  var body = document.body;
  var root = body.getAttribute("data-root") || ".";
  var currentPage = body.getAttribute("data-page") || "";

  /* Enlaces de navegación principal.
     Para añadir una página nueva en el futuro, agrega aquí
     una entrada { href, label, page } y aparecerá en todo
     el sitio automáticamente. */
  var navLinks = [
    { href: root + "/index.html", label: "Inicio", page: "inicio" },
    { href: root + "/blog.html", label: "Blog", page: "blog" },
  ];

  var year = new Date().getFullYear();

  function buildNav() {
    return navLinks
      .map(function (link) {
        var current = link.page === currentPage ? ' aria-current="page"' : "";
        return (
          '<li><a class="main-nav__link" href="' +
          link.href +
          '"' +
          current +
          ">" +
          link.label +
          "</a></li>"
        );
      })
      .join("");
  }

  var headerHTML =
    '<div class="container site-header__inner">' +
    '<a class="brand" href="' +
    root +
    '/index.html" aria-label="Ir a la página de inicio de Asgard Nutrición Deportiva">' +
    '<img class="brand__mark" src="' +
    root +
    '/images/logo.jpg" alt="" width="42" height="42">' +
    '<span class="brand__name">Asgard<span>Nutrición Deportiva</span></span>' +
    "</a>" +
    '<nav class="main-nav" id="main-nav" aria-label="Navegación principal">' +
    '<ul class="main-nav__list">' +
    buildNav() +
    "</ul>" +
    "</nav>" +
    '<button class="nav-toggle" id="nav-toggle" aria-expanded="false" aria-controls="main-nav" aria-label="Abrir menú de navegación">' +
    '<span class="nav-toggle__bar nav-toggle__bar--top"></span>' +
    '<span class="nav-toggle__bar nav-toggle__bar--mid"></span>' +
    '<span class="nav-toggle__bar nav-toggle__bar--bottom"></span>' +
    "</button>" +
    "</div>";

  var footerHTML =
    '<div class="container site-footer__inner">' +
    '<svg class="site-footer__rune" viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">' +
    '<path d="M24 4v40M24 4l-10 10M24 4l10 10M24 44l-10-10M24 44l10-10M10 24h28" stroke-linecap="round" stroke-linejoin="round"/>' +
    "</svg>" +
    '<p class="site-footer__brand">Asgard Nutrición Deportiva</p>' +
    '<p class="site-footer__tagline">Nutrición deportiva y asesoramiento con la firmeza de la vieja guardia.</p>' +
    '<nav class="site-footer__nav" aria-label="Enlaces del pie de página">' +
    '<a href="' +
    root +
    '/index.html">Inicio</a>' +
    '<a href="' +
    root +
    '/blog.html">Blog</a>' +
    "</nav>" +
    '<p class="site-footer__meta">© ' +
    year +
    " Asgard Nutrición Deportiva</p>" +
    "</div>";

  var headerMount = document.getElementById("site-header");
  var footerMount = document.getElementById("site-footer");

  if (headerMount) {
    headerMount.innerHTML = headerHTML;
  }
  if (footerMount) {
    footerMount.innerHTML = footerHTML;
  }

  var toggle = document.getElementById("nav-toggle");
  var nav = document.getElementById("main-nav");

  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var isOpen = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", String(isOpen));
      toggle.setAttribute(
        "aria-label",
        isOpen ? "Cerrar menú de navegación" : "Abrir menú de navegación"
      );
    });

    nav.addEventListener("click", function (event) {
      if (event.target.closest("a")) {
        nav.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
        toggle.setAttribute("aria-label", "Abrir menú de navegación");
      }
    });
  }
})();
