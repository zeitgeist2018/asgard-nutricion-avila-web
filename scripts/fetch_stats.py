#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_stats.py

Descarga las estadísticas de GoatCounter de los últimos días y las
guarda en publisher/stats.json, que lee el panel de administración.

Lo ejecuta GitHub Actions cada día (ver .github/workflows/stats.yml).
Necesita la variable de entorno GOATCOUNTER_API_KEY, que debe estar
guardada como secreto del repositorio y nunca escrita en un fichero.

Solo se guardan visitas agregadas por página, país, navegador y
sistema. No se guarda nada que identifique a una persona.
"""

import json
import os
import sys
import urllib.error
import urllib.parse
import time
import urllib.request
from datetime import datetime, timedelta, timezone

SITE_API = "https://asgardavilanutriciondeportiva.goatcounter.com/api/v0/"
DAYS = 30
LIMIT = 100  # máximo que admite la API por consulta
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "publisher", "stats.json")

REQUEST_TIMEOUT = 20      # segundos máximos por petición; sin esto una conexión puede colgarse
ATTEMPTS = 4              # intentos por petición (el primero incluido)
BACKOFF_SECONDS = 5       # espera inicial entre intentos; se duplica en cada reintento
RETRY_AFTER_CAP = 60      # tope a la espera que pida la API con Retry-After


def log(message):
    print(message, file=sys.stderr, flush=True)


def get_once(url, api_key):
    request = urllib.request.Request(url, headers={"Authorization": "Bearer " + api_key})
    with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
        return json.loads(response.read().decode("utf-8"))


def get(path, params, api_key):
    # GoatCounter limita a 4 peticiones por segundo
    time.sleep(0.5)
    url = SITE_API + path + "?" + urllib.parse.urlencode(params)
    delay = BACKOFF_SECONDS
    for attempt in range(1, ATTEMPTS + 1):
        try:
            return get_once(url, api_key)
        except urllib.error.HTTPError as err:
            # Errores de la propia petición (clave, ruta…) no se arreglan reintentando
            if err.code not in (408, 429) and err.code < 500:
                raise
            wait = delay
            retry_after = err.headers.get("Retry-After", "") if err.headers else ""
            if retry_after.isdigit():
                wait = min(int(retry_after), RETRY_AFTER_CAP)
            reason = "HTTP %d" % err.code
        except (urllib.error.URLError, TimeoutError, OSError) as err:
            # Tiempo agotado o conexión caída: se reintenta
            wait = delay
            reason = "timeout o red (%s)" % err
        if attempt == ATTEMPTS:
            raise RuntimeError("GoatCounter no responde tras %d intentos: %s" % (ATTEMPTS, path))
        log("Intento %d/%d de %s falló (%s). Reintento en %ds." % (attempt, ATTEMPTS, path, reason, wait))
        time.sleep(wait)
        delay *= 2


def breakdown(stats, api_key, start, end):
    """Pide un desglose (locations, browsers, systems) y devuelve nombre y visitas."""
    data = get("stats/" + stats, {"start": start, "end": end, "limit": LIMIT}, api_key)
    return [{"name": item.get("name") or "Desconocido", "count": item.get("count", 0)}
            for item in data.get("stats", [])]


def main():
    api_key = os.environ.get("GOATCOUNTER_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("Falta la variable GOATCOUNTER_API_KEY.")

    now = datetime.now(timezone.utc)
    start = (now - timedelta(days=DAYS)).strftime("%Y-%m-%d")
    end = now.strftime("%Y-%m-%d")

    total = get("stats/total", {"start": start, "end": end}, api_key)
    hits = get("stats/hits", {"start": start, "end": end, "limit": LIMIT}, api_key)

    data = {
        "updated": now.isoformat(timespec="seconds"),
        "start": start,
        "end": end,
        "days": DAYS,
        "total": total.get("total", 0),
        "daily": [{"day": day["day"], "count": day.get("daily", 0)} for day in total.get("stats", [])],
        "pages": [
            {"title": hit.get("title") or hit.get("path"), "path": hit.get("path"), "count": hit.get("count", 0)}
            for hit in hits.get("hits", [])
            if not hit.get("event")
        ],
        "locations": breakdown("locations", api_key, start, end),
        "browsers": breakdown("browsers", api_key, start, end),
        "systems": breakdown("systems", api_key, start, end),
    }

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("Estadísticas guardadas en", os.path.normpath(OUTPUT))


if __name__ == "__main__":
    main()
