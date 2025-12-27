# core/facebook_funcs/FacebookCrearPaginaYPostearVideo.py
import time
from core.adb_utils import crear_funciones_con_serial
from core.tiktok_funcs.utils import should_stop, cerrary_salir

# =========================
# CONFIG
# =========================
FB_PACKAGE = "com.facebook.katana"

OCR_REGION_FULL = ("5%", "5%", "95%", "95%")
OCR_REGION_NOMBRE = ("5%", "10%", "95%", "25%")  # donde está el nombre
OCR_REGION_CREATE_NEW = ("10%", "10%", "90%", "50%")


# =========================
# HELPERS
# =========================
def _log(serial, msg):
    print(f"[FB:{serial}] {msg}")

def _sleep(serial, s):
    end = time.time() + s
    while time.time() < end:
        if should_stop(serial):
            return False
        time.sleep(0.1)
    return True

# =========================
# ABRIR FACEBOOK
# =========================
def fb_abrir(serial):
    run, *_ = crear_funciones_con_serial(serial)
    cerrary_salir(serial)

    _log(serial, "🚀 Abriendo Facebook")
    run(f"shell monkey -p {FB_PACKAGE} -c android.intent.category.LAUNCHER 1")
    _sleep(serial, 5)

# =========================
# MENÚ ☰
# =========================
def tap_menu_icono(serial):
    _, tap, *_ = crear_funciones_con_serial(serial)
    _log(serial, "☰ Tap menú (zona fija)")
    tap("95%", "8%")
    _sleep(serial, 2)

# =========================
# TEST OCR NOMBRE PERFIL
# =========================
def test_ocr_nombre(serial):
    _, _, _, _, _, buscarTextoEnRegion, *_ = crear_funciones_con_serial(serial)

    _log(serial, "🧪 TEST OCR: buscando nombre del perfil")

    coords = buscarTextoEnRegion(
        OCR_REGION_NOMBRE,
        "Diamond"
    )

    _log(serial, f"🧪 OCR resultado: {coords} | type={type(coords)}")

    if coords:
        _log(serial, "✅ OCR SÍ lee el nombre del perfil")
    else:
        _log(serial, "❌ OCR NO lee el nombre del perfil")

# =========================
# TAP CREATE PAGE RELATIVO AL NOMBRE
# =========================
def tap_create_page_desde_nombre(serial):
    _, tap, *_ = crear_funciones_con_serial(serial)
    _, _, _, _, _, buscarTextoEnRegion, *_ = crear_funciones_con_serial(serial)

    coords = buscarTextoEnRegion(OCR_REGION_NOMBRE, "Diamond")

    if not coords:
        _log(serial, "❌ No se detectó el nombre del perfil")
        return False

    x, y = coords

    # Ajuste relativo: Create Facebook Page justo debajo del nombre
    y_create_page = y + 120  # píxeles, ajustar según resolución

    _log(serial, f"📍 Tap Create Page relativo a nombre ({x}, {y_create_page})")
    tap(x, y_create_page)
    _sleep(serial, 2)

    return True

# =========================
# TAP "CREATE A NEW PAGE" CON OCR
# =========================
def tap_create_new_page(serial):
    _, tap, *_ = crear_funciones_con_serial(serial)
    _, _, _, _, _, buscarTextoEnRegion, *_ = crear_funciones_con_serial(serial)

    coords = buscarTextoEnRegion(OCR_REGION_CREATE_NEW, "Create a new Page")

    if coords:
        _log(serial, f"✅ OCR detectó 'Create a new Page' en {coords} | type={type(coords)}")
        x, y = coords
        _log(serial, f"📍 Tap 'Create a new Page' en ({x}, {y})")
        tap(x, y)
        _sleep(serial, 2)
        return True
    else:
        _log(serial, "❌ OCR NO detectó 'Create a new Page'")
        _log(serial, f"   - Revisar región OCR: {OCR_REGION_CREATE_NEW}")
        return False

# =========================
# TEST GENERAL
# =========================
def fb_test_ocr(serial):
    _log(serial, "🏁 INICIO TEST OCR FACEBOOK")

    fb_abrir(serial)
    if should_stop(serial):
        return

    tap_menu_icono(serial)
    if should_stop(serial):
        return

    test_ocr_nombre(serial)

    # Tap Create Facebook Page relativo al nombre
    tap_create_page_desde_nombre(serial)

    # Intentar tap "Create a new Page" usando OCR
    tap_create_new_page(serial)

    _log(serial, "🏁 FIN TEST OCR FACEBOOK")

# =========================
# FUNCIÓN MAIN
# =========================
def fb_crear_pagina_y_postear_video(serial):
    fb_test_ocr(serial)
