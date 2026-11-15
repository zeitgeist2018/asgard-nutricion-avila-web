/* Catálogo: carrusel de novedades (portada) y filtros por categoría (página de catálogo). */
(function () {
  "use strict";

  var AUTO_MS = 4000;     // tiempo entre pasos del carrusel
  var RESUME_MS = 8000;   // tiempo sin tocar el carrusel antes de que vuelva a moverse
  var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // ---------- Carrusel automático con scroll manual (dedo o ratón) ----------
  document.querySelectorAll("[data-carousel]").forEach(function (root) {
    var track = root.querySelector(".carousel__track");
    var dotsBox = root.nextElementSibling && root.nextElementSibling.hasAttribute("data-carousel-dots")
      ? root.nextElementSibling
      : null;
    if (!track || track.children.length < 2) {
      root.classList.add("is-static");   // con pocas tarjetas no hacen falta flechas ni puntos
      return;
    }

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

    // Flechas: avanzan o retroceden una tarjeta; en los extremos dan la vuelta
    function stepBy(direction) {
      var step = positionOf(track.children[1]) - positionOf(track.children[0]);
      var max = track.scrollWidth - track.clientWidth;
      var target;
      if (direction > 0 && track.scrollLeft >= max - 4) target = 0;
      else if (direction < 0 && track.scrollLeft <= 4) target = max;
      else target = Math.min(max, Math.max(0, track.scrollLeft + direction * step));
      track.scrollTo({ left: target, behavior: "smooth" });
    }

    var prevButton = root.querySelector("[data-carousel-prev]");
    var nextButton = root.querySelector("[data-carousel-next]");
    if (prevButton) prevButton.addEventListener("click", function () { pauseForUser(); stepBy(-1); });
    if (nextButton) nextButton.addEventListener("click", function () { pauseForUser(); stepBy(1); });

    // Puntos: uno por tarjeta; marcan la tarjeta visible y permiten ir directamente a ella
    var dots = [];
    if (dotsBox) {
      Array.prototype.forEach.call(track.children, function (item, index) {
        var dot = document.createElement("button");
        dot.type = "button";
        dot.className = "carousel__dot";
        dot.setAttribute("aria-label", "Ver el producto " + (index + 1));
        dot.addEventListener("click", function () {
          pauseForUser();
          track.scrollTo({ left: positionOf(item), behavior: "smooth" });
        });
        dotsBox.appendChild(dot);
        dots.push(dot);
      });
    }

    function updateDots() {
      var current = 0;
      for (var i = 0; i < track.children.length; i++) {
        if (positionOf(track.children[i]) <= track.scrollLeft + 8) current = i;
      }
      dots.forEach(function (dot, index) {
        dot.setAttribute("aria-current", index === current ? "true" : "false");
      });
    }
    track.addEventListener("scroll", updateDots, { passive: true });
    window.addEventListener("resize", updateDots);
    updateDots();

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

  // ---------- Ficha completa del producto en una ventana emergente ----------
  var modal = document.getElementById("product-modal");
  if (modal) {
    var closeButton = modal.querySelector(".product-modal__close");
    var openedFrom = null;   // tarjeta que abrió la ventana (para devolverle el foco)

    function fillModal(card) {
      var media = card.querySelector(".product-card__media");
      var meta = card.querySelector(".product-card__body");
      var title = card.querySelector(".product-card__title");
      var prices = card.querySelector(".product-card__prices");
      var description = card.getAttribute("data-description") || "";

      var mediaBox = document.getElementById("product-modal-media");
      mediaBox.innerHTML = media ? media.innerHTML : "";

      var metaBox = document.getElementById("product-modal-meta");
      metaBox.innerHTML = "";
      if (meta) {
        meta.querySelectorAll(".product-card__cat, .product-card__brand").forEach(function (node) {
          metaBox.appendChild(node.cloneNode(true));
        });
      }

      document.getElementById("product-modal-title").textContent = title ? title.textContent : "";

      var descBox = document.getElementById("product-modal-desc");
      descBox.textContent = description;
      descBox.hidden = !description;

      var pricesBox = document.getElementById("product-modal-prices");
      pricesBox.innerHTML = prices ? prices.innerHTML : "";
    }

    var CLOSE_MS = 250;      // duración de la animación de cierre (igual que en el CSS)
    var closeTimer = null;

    function openModal(card) {
      clearTimeout(closeTimer);
      openedFrom = card;
      fillModal(card);
      modal.hidden = false;
      document.body.style.overflow = "hidden";
      // Forzar un repintado para que la transición de entrada parta del estado inicial
      void modal.offsetWidth;
      modal.classList.add("is-open");
      closeButton.focus();
    }

    function closeModal() {
      if (!modal.classList.contains("is-open")) return;
      modal.classList.remove("is-open");
      document.body.style.overflow = "";
      if (openedFrom) openedFrom.focus();
      openedFrom = null;
      // Se oculta cuando termina la animación de salida
      closeTimer = setTimeout(function () {
        modal.hidden = true;
      }, CLOSE_MS);
    }

    // Pulsar la tarjeta abre la ficha; los enlaces (p. ej. WhatsApp) siguen funcionando solos
    document.addEventListener("click", function (event) {
      var card = event.target.closest(".product-card");
      if (!card || event.target.closest("a")) return;
      openModal(card);
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") {
        closeModal();
        return;
      }
      if ((event.key === "Enter" || event.key === " ") && event.target.classList &&
          event.target.classList.contains("product-card")) {
        event.preventDefault();
        openModal(event.target);
      }
    });

    modal.addEventListener("click", function (event) {
      if (event.target.hasAttribute("data-close")) closeModal();
    });
  }
})();
