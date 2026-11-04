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
import urllib.parse
import time
import urllib.request
from datetime import datetime, timedelta, timezone

SITE_API = "https://asgardavilanutriciondeportiva.goatcounter.com/api/v0/"
DAYS = 30
LIMIT = 100  # máximo que admite la API por consulta
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "publisher", "stats.json")


def get(path, params, api_key):
    # GoatCounter limita a 4 peticiones por segundo
    time.sleep(0.5)
    url = SITE_API + path + "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={"Authorization": "Bearer " + api_key})
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


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
