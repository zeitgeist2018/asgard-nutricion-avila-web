#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
serve_local.py

Sirve la web en http://localhost:8000 para probarla en el navegador.
Cada vez que cambia un fichero del proyecto, vuelve a construir el sitio
(en .local-site/, sin tocar dist/). Basta con recargar la página
(Ctrl+F5) para ver los cambios.

    python serve_local.py

Para parar el servidor: Ctrl+C.
"""

import http.server
import os
import shutil
import subprocess
import sys
import threading
import time
import urllib.parse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_DIR = os.path.join(BASE_DIR, ".local-site")
PORT = 8000
IGNORED = {".git", ".idea", "dist", ".local-site", "__pycache__"}

current = {"dir": None}   # carpeta con la última versión construida
lock = threading.Lock()


def build(target):
    env = dict(os.environ, ASGARD_DIST_DIR=target, PYTHONIOENCODING="utf-8")
    result = subprocess.run(
        [sys.executable, "build_site.py"],
        cwd=BASE_DIR, env=env, capture_output=True, text=True, encoding="utf-8",
    )
    if result.returncode != 0:
        # Se mantiene la versión anterior hasta que el error se corrija
        print("Error al construir el sitio:\n" + result.stderr, flush=True)
        return False
    return True


def rebuild():
    os.makedirs(LOCAL_DIR, exist_ok=True)
    target = os.path.join(LOCAL_DIR, "site-" + str(int(time.time() * 1000)))
    if not build(target):
        return
    with lock:
        old = current["dir"]
        current["dir"] = target
    print("[" + time.strftime("%H:%M:%S") + "] Web reconstruida. Recarga la página.", flush=True)
    if old:
        shutil.rmtree(old, ignore_errors=True)


class Handler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        with lock:
            root = current["dir"]
        clean = urllib.parse.unquote(path.split("?", 1)[0].split("#", 1)[0])
        parts = [p for p in clean.split("/") if p not in ("", ".", "..")]
        full = os.path.join(root, *parts)
        if os.path.isdir(full):
            full = os.path.join(full, "index.html")
        return full

    def log_message(self, format, *args):
        pass  # sin una línea por cada petición


def snapshot():
    state = {}
    for folder, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if d not in IGNORED]
        for name in files:
            path = os.path.join(folder, name)
            try:
                state[path] = os.path.getmtime(path)
            except OSError:
                pass
    return state


def watch():
    last = snapshot()
    while True:
        time.sleep(1)
        now = snapshot()
        if now != last:
            last = now
            rebuild()


if __name__ == "__main__":
    rebuild()
    threading.Thread(target=watch, daemon=True).start()
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print("Abre http://localhost:" + str(PORT) + " en Chrome. Ctrl+C para parar.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Servidor parado.")
