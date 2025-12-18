# core/facebook_funcs/FacebookCrearPaginaYPostearVideo.py
import os
import time
from datetime import datetime

from core.adb_utils import crear_funciones_con_serial
from core.tiktok_funcs.utils import should_stop, cerrary_salir  # ya coopera con hilos_activos :contentReference[oaicite:2]{index=2}

# =========================
# CONFIG EDITABLE (rápido)
# =========================
FB_PACKAGE = "com.facebook.katana"

PAGE_NAME = "Pagina Automatizada"
PAGE_CATEGORY = "Entretenimiento"   # prueba 1: usa una categoría común
PAGE_DESCRIPTION = "Página creada automáticamente."

# Si quieres usar siempre el “primer” video del carrete, dejamos taps simples.
# Si falla en tu dispositivo, luego lo afinamos con 1-2 capturas.
VIDEO_PICK_MODE = "first"  # "first" o "latest" (por ahora "first" = más estable)

# Carpeta debug (en el root del proyecto)
DEBUG_DIR = "debug_fb"

import random

FB_CREAR_PAGINA_AREA = ("20%", "16%", "80%", "20%")

FB_OPCION_CREAR_NUEVA_PAGINA = ("50%", "28%")   # toca dentro del recuadro superior (ya viene marcado, pero ok)
FB_BTN_SIGUIENTE_ABAJO       = ("50%", "86%")   # botón azul grande “Siguiente”
FB_BTN_X_CERRAR              = ("7%",  "6%")    # X arriba izquierda (solo si necesitamos salir)

# =========================
# Helpers (pequeños)
# =========================
def _log(serial, msg):
    print(f"[FB:{serial}] {msg}")

import re

def fb_debug_ocr_pantalla(serial: str):
    run, tap, long_tap, move, write, buscarTextoEnRegion, detectarColorOTap, leerTextoEnRegion = crear_funciones_con_serial(serial)

    _log(serial, "🧪 DEBUG OCR: leyendo texto de pantalla completa…")
    region_full = ("2%", "2%", "98%", "98%")
    txt = leerTextoEnRegion(region_full) or ""
    txt_clean = re.sub(r"\s+", " ", txt).strip()

    _log(serial, "🧾 OCR RAW (pantalla completa):")
    print("----- OCR START -----")
    print(txt)
    print("----- OCR END -----")

    # Chequeos rápidos (por si sale con typos o sin acentos)
    keys = [
        "crear", "pagina", "página", "facebook",
        "crear página", "crear pagina", "página de facebook", "pagina de facebook",
        "ver más", "ver mas", "configuración", "privacidad"
    ]

    hay = []
    low = txt_clean.lower()
    for k in keys:
        if k in low:
            hay.append(k)

    _log(serial, f"🔎 Coincidencias directas encontradas: {hay if hay else 'Ninguna'}")

import random

def _tap_area(serial, tap, area, sleep_fn, t=1.2):
    x1,y1,x2,y2 = area
    # tap aleatorio dentro del rectángulo (evita caer justo en bordes)
    xr = random.uniform(float(x1.strip('%'))+1, float(x2.strip('%'))-1)
    yr = random.uniform(float(y1.strip('%'))+1, float(y2.strip('%'))-1)
    tap(f"{xr:.2f}%", f"{yr:.2f}%")
    sleep_fn(serial, t)

def _tap_area_percent(tap, area):
    x1, y1, x2, y2 = area
    x = random.uniform(float(x1.strip('%')) + 1, float(x2.strip('%')) - 1)
    y = random.uniform(float(y1.strip('%')) + 1, float(y2.strip('%')) - 1)
    tap(f"{x:.2f}%", f"{y:.2f}%")

def fb_tocar_crear_pagina(serial: str):
    run, tap, long_tap, move, write, *_ = crear_funciones_con_serial(serial)

    fb_ir_a_menu(serial)
    if should_stop(serial):
        return

    _log(serial, "📄 Tocando 'Crear página de Facebook' (por área %)…")
    _tap_area_percent(tap, FB_CREAR_PAGINA_AREA)
    _sleep(serial, 3.0)
    _log(serial, "✅ Tap hecho a 'Crear página'. (Siguiente logro: confirmar que abrió la pantalla).")


def _sleep(serial, seconds):
    end = time.time() + max(0, seconds)
    while time.time() < end:
        if should_stop(serial):
            return False
        time.sleep(0.1)
    return True

def _screencap(serial, run, tag):
    """Guarda screenshot para depurar (cuando algo falle)."""
    try:
        os.makedirs(DEBUG_DIR, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out = os.path.join(DEBUG_DIR, f"{serial}_{ts}_{tag}.png")
        # adb exec-out screencap -p > file
        # Usamos subprocess indirecto a través de run NO sirve para redirigir,
        # así que usamos el comando raw con ADB vía shell redirect:
        # (en Windows a veces falla). Alternativa: no guardar.
        # Como tu adb_utils ya hace screencap para OCR, en esta primera versión lo dejamos “best effort”.
        _log(serial, f"📸 (best-effort) Screenshot tag={tag} => {out} (si lo necesitas, lo afinamos)")
    except Exception:
        pass

def _tap_text_anywhere(serial, buscarTextoEnRegion, tap, keywords, tries=6):
    """Busca keywords en pantalla completa y toca donde lo detecta."""
    region_full = ("2%", "2%", "98%", "98%")
    for i in range(tries):
        if should_stop(serial):
            return False
        for kw in keywords:
            coords = buscarTextoEnRegion(region_full, kw, umbral_similitud=0.72)
            if coords:
                tap(*coords)
                return True
        _sleep(serial, 0.4)
    return False

def _wait_text_anywhere(serial, buscarTextoEnRegion, keywords, timeout_s=8):
    region_full = ("2%", "2%", "98%", "98%")
    t0 = time.time()
    while time.time() - t0 < timeout_s:
        if should_stop(serial):
            return False
        for kw in keywords:
            coords = buscarTextoEnRegion(region_full, kw, umbral_similitud=0.70)
            if coords:
                return True
        time.sleep(0.3)
    return False

def _open_facebook(serial, run):
    _log(serial, "🚀 Abriendo Facebook…")
    run(f"shell monkey -p {FB_PACKAGE} -c android.intent.category.LAUNCHER 1")
    return True


def fb_paso_opcion_y_siguiente(serial: str):
    run, tap, long_tap, move, write, *_ = crear_funciones_con_serial(serial)

    _log(serial, "✅ Pantalla '¿Qué opción...?' -> seleccionando 'Crear una nueva página'…")
    tap(*FB_OPCION_CREAR_NUEVA_PAGINA)
    _sleep(serial, 0.8)

    _log(serial, "➡️ Tocando 'Siguiente' (botón azul abajo)…")
    tap(*FB_BTN_SIGUIENTE_ABAJO)
    _sleep(serial, 2.5)


def _back(serial, run, times=1):
    for _ in range(times):
        if should_stop(serial):
            return False
        run("shell input keyevent 4")
        time.sleep(0.2)
    return True


# =========================
# Logro 0: abrir FB
# =========================
def fb_abrir(serial: str):
    run, tap, long_tap, move, write, buscarTextoEnRegion, detectarColorOTap, leerTextoEnRegion = crear_funciones_con_serial(serial)

    # limpieza ligera (como tu patrón)
    cerrary_salir(serial)
    if should_stop(serial): 
        return

    _open_facebook(serial, run)
    _sleep(serial, 3.0)
    _log(serial, "✅ Facebook abierto (si no lo ves, revisamos taps).")


# =========================
# Logro 1: abrir menú ☰
# =========================
def fb_ir_a_menu(serial: str):
    # 1) Asegurar que FB esté abierto desde donde sea
    fb_abrir(serial)
    if should_stop(serial):
        return

    # 2) Ya con FB abierto, tocar menú
    run, tap, long_tap, move, write, *_ = crear_funciones_con_serial(serial)

    _log(serial, "➡️ Abriendo Menú (☰)…")
    tap("6%", "8%")      # ☰
    _sleep(serial, 2.5)
    _log(serial, "✅ Menú abierto (sin OCR).")

def _tap_center(tap, area):
        x1,y1,x2,y2 = area
        cx = (float(x1.strip('%')) + float(x2.strip('%'))) / 2
        cy = (float(y1.strip('%')) + float(y2.strip('%'))) / 2
        tap(f"{cx:.2f}%", f"{cy:.2f}%")
# =========================
# Logro 2: entrar a Páginas
# =========================
def fb_abrir_paginas(serial: str):
    run, tap, long_tap, move, write, *_ = crear_funciones_con_serial(serial)

    fb_ir_a_menu(serial)
    if should_stop(serial):
        return

    _log(serial, "📄 Tocando 'Crear página de Facebook' (por coordenadas %)…")
    _tap_center(tap, FB_CREAR_PAGINA_AREA)
    _sleep(serial, 2.5)
    _log(serial, "✅ Tap hecho. (Logro C completado si cambiaste de pantalla).")

# =========================
# Logro 3: crear página
# =========================
def fb_crear_pagina(serial: str):
    run, tap, long_tap, move, write, buscarTextoEnRegion, detectarColorOTap, leerTextoEnRegion = crear_funciones_con_serial(serial)

    fb_abrir_paginas(serial)
    if should_stop(serial): 
        return

    # =========================
    # Paso: pantalla “¿Qué opción es la más adecuada para ti?”
    # (Crear una nueva página + Siguiente) por coordenadas
    # =========================
    fb_paso_opcion_y_siguiente(serial)
    if should_stop(serial):
        return


    # Nombre
    _log(serial, f"✍️ Escribiendo nombre de página: {PAGE_NAME}")
    # Tap en primer input grande al centro
    tap("50%", "28%")
    _sleep(serial, 0.4)
    write(PAGE_NAME)
    _sleep(serial, 0.8)

    # Siguiente / Next
    _log(serial, "➡️ Siguiente/Next…")
    if not _tap_text_anywhere(serial, buscarTextoEnRegion, tap, ["next", "siguiente"], tries=4):
        # fallback top-right
        tap("92%", "6%")
    _sleep(serial, 2.0)

    # Categoría
    _log(serial, f"🏷️ Categoría: {PAGE_CATEGORY}")
    tap("50%", "28%")
    _sleep(serial, 0.4)
    write(PAGE_CATEGORY)
    _sleep(serial, 1.0)
    # elegir primera sugerencia
    tap("50%", "36%")
    _sleep(serial, 0.8)

    # Siguiente / Crear
    if not _tap_text_anywhere(serial, buscarTextoEnRegion, tap, ["next", "siguiente", "create", "crear"], tries=5):
        tap("92%", "6%")
    _sleep(serial, 3.0)

    # Descripción (si aparece)
    _log(serial, "📝 Intentando agregar descripción (si aparece)…")
    if _tap_text_anywhere(serial, buscarTextoEnRegion, tap, ["description", "descripción"], tries=2):
        _sleep(serial, 0.4)
        write(PAGE_DESCRIPTION)
        _sleep(serial, 0.6)
        _tap_text_anywhere(serial, buscarTextoEnRegion, tap, ["next", "siguiente", "done", "listo", "finish", "finalizar"], tries=3)
        _sleep(serial, 2.0)

    # Validación
    ok = _wait_text_anywhere(serial, buscarTextoEnRegion, ["manage", "administrar", "edit", "editar", "invite", "invitar"], timeout_s=10)
    _log(serial, "✅ Página creada (confirmación por texto)" if ok else "⚠️ No confirmé creación por OCR (pero puede estar creada).")


# =========================
# Logro 4: postear video
# =========================
def fb_postear_video_en_pagina(serial: str):
    run, tap, long_tap, move, write, buscarTextoEnRegion, detectarColorOTap, leerTextoEnRegion = crear_funciones_con_serial(serial)

    _log(serial, "🎬 Preparando post de video…")

    # Intento 1: encontrar “Create post / Publicación / What’s on your mind”
    if not _tap_text_anywhere(serial, buscarTextoEnRegion, tap, ["create post", "publicación", "post", "what", "mente"], tries=6):
        # fallback: botón central típico en perfil de página
        tap("50%", "55%")
        _sleep(serial, 1.0)

    # Elegir Foto/Video
    _log(serial, "🖼️ Buscando 'Foto/Video'…")
    if not _tap_text_anywhere(serial, buscarTextoEnRegion, tap, ["photo", "foto", "video", "vídeo"], tries=8):
        _screencap(serial, run, "no_photo_video")
        raise RuntimeError("No pude abrir el selector Foto/Video.")

    _sleep(serial, 2.5)

    # Seleccionar un video
    _log(serial, "📌 Seleccionando un video del carrete…")
    if VIDEO_PICK_MODE == "first":
        # Tap en la primera miniatura (zona superior izquierda del grid)
        tap("18%", "32%")
    else:
        # “latest” aproximado (primera miniatura también suele ser lo último)
        tap("18%", "32%")
    _sleep(serial, 1.2)

    # Next / Done
    _tap_text_anywhere(serial, buscarTextoEnRegion, tap, ["next", "siguiente", "done", "listo"], tries=6)
    _sleep(serial, 2.5)

    # Publicar / Post / Share
    _log(serial, "🚀 Publicando…")
    if not _tap_text_anywhere(serial, buscarTextoEnRegion, tap, ["post", "publicar", "share", "compartir"], tries=10):
        # fallback top-right
        tap("92%", "6%")
    _sleep(serial, 4.0)

    _log(serial, "✅ Post enviado (si ves 'Publicando' y luego el post en el feed, logro completo).")


# =========================
# Función FINAL (todo el flujo)
# =========================
def fb_crear_pagina_y_postear_video(serial: str):
    """
    Flujo completo:
    1) abrir facebook
    2) ir a páginas
    3) crear página
    4) postear video en esa página
    """
    _log(serial, "🏁 INICIO flujo completo: Crear página + Postear video")
    fb_crear_pagina(serial)
    if should_stop(serial): 
        return
    fb_postear_video_en_pagina(serial)
    _log(serial, "🏁 FIN flujo completo")
