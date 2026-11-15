/* Catálogo: carrusel de novedades (portada) y filtros por categoría (página de catálogo). */
(function () {
  "use strict";

  var AUTO_MS = 4000;     // tiempo entre pasos del carrusel
  var RESUME_MS = 8000;   // tiempo sin tocar el carrusel antes de que vuelva a moverse
  var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // ---------- Carrusel automático con scroll manual (dedo o ratón) ----------
  document.querySelectorAll("[data-carousel]").forEach(function (root) {
    var track = root.querySelector(".carousel__track");
    if (!track || track.children.length < 2) return;

    var timer = null;
    var resumeTimer = null;

    // Posición de una tarjeta dentro del carrusel (coordenadas del scroll, no de la página)
    function positionOf(item) {
      return item.getBoundingClientRect().left - track.getBoundingClientRect().left + track.scrollLeft;
    }

    // Siguiente tarjeta a la derecha; al llegar al final vuelve al principio
    function next() {
      var left = track.scrollLeft;
      var atEnd = left + track.clientWidth >= track.scrollWidth - 4;
      if (atEnd) {
        track.scrollTo({ left: 0, behavior: "smooth" });
        return;
      }
      for (var i = 0; i < track.children.length; i++) {
        var target = positionOf(track.children[i]);
        if (target > left + 4) {
          track.scrollTo({ left: target, behavior: "smooth" });
          return;
        }
      }
    }

    function start() {
      if (reduceMotion || timer) return;
      timer = setInterval(next, AUTO_MS);
    }

    function stop() {
      clearInterval(timer);
      timer = null;
    }

    // Si el visitante toca o hace scroll, el carrusel se queda quieto un rato
    function pauseForUser() {
      stop();
      clearTimeout(resumeTimer);
      resumeTimer = setTimeout(start, RESUME_MS);
    }

    ["pointerdown", "touchstart", "wheel", "keydown", "focusin"].forEach(function (name) {
      track.addEventListener(name, pauseForUser, { passive: true });
    });
    root.addEventListener("pointerenter", stop);
    root.addEventListener("pointerleave", function () { clearTimeout(resumeTimer); start(); });

    // No gastar movimiento si la pestaña no está visible
    document.addEventListener("visibilitychange", function () {
      if (document.hidden) stop(); else start();
    });

    start();
  });

  // ---------- Filtros por categoría ----------
  var filterButtons = document.querySelectorAll("[data-filter]");
  if (filterButtons.length) {
    var cards = document.querySelectorAll("#catalog-grid .product-card");
    var empty = document.getElementById("catalog-empty");

    filterButtons.forEach(function (button) {
      button.addEventListener("click", function () {
        var value = button.getAttribute("data-filter");
        var visible = 0;

        filterButtons.forEach(function (other) {
          var active = other === button;
          other.classList.toggle("is-active", active);
          other.setAttribute("aria-pressed", active ? "true" : "false");
        });

        cards.forEach(function (card) {
          var show = value === "all" || card.getAttribute("data-category") === value;
          card.hidden = !show;
          if (show) visible++;
        });

        if (empty) empty.hidden = visible > 0;
      });
    });
  }
})();
