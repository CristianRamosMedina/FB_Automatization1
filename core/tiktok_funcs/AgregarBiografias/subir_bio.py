import time
import subprocess
import pyperclip  # pip install pyperclip

from core.tiktok_funcs.utils import crear_funciones_con_serial, should_stop


def _escribir_texto_otg(serial: str, text: str):
    """
    Usa scrcpy con sincronización de portapapeles para enviar texto con emojis/saltos de línea.
    """
    from core.paths import SCRCPY_PATH

    # Copiar el texto al portapapeles de la PC
    pyperclip.copy(text)

    # Lanzar scrcpy con clipboard autosync (sin audio/ventana)
    proc = subprocess.Popen(
        [SCRCPY_PATH, "-s", serial, "--no-audio", "--no-display", "--clipboard-autosync"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    # Esperar que scrcpy sincronice el portapapeles con Android
    time.sleep(2)

    # Simular "Pegar" en Android (KEYCODE_PASTE = 279)
    subprocess.run(
        ["adb", "-s", serial, "shell", "input", "keyevent", "279"],
        check=True
    )

    # Cerrar scrcpy
    proc.terminate()
    proc.wait()
    time.sleep(0.5)


def subir_biografia(serial: str, bio_text: str) -> bool:
    """
    Cambia la biografía en TikTok con scrcpy clipboard-sync + adb paste.
    """
    run, tap, long_tap, move, write, buscarTextoEnRegion, detectarColorOTap, leerTextoEnRegion = crear_funciones_con_serial(serial)

    try:
        if should_stop(serial):
            return False

        # Ir al perfil
        tap("90%", "93%")
        time.sleep(1.2)

        # Edit profile
        coords = buscarTextoEnRegion(("469", "304", "616", "377"), "Edit", umbral_similitud=0.65)
        if coords:
            tap(*coords)
        else:
            tap("50%", "80%")  # fallback
        time.sleep(1.2)

        # Bio field
        coords = buscarTextoEnRegion(("40", "962", "158", "1048"), "Bio", umbral_similitud=0.65)
        if not coords:
            print(f"⚠️ [{serial}] No encontré campo Bio")
            return False
        tap(*coords)
        time.sleep(0.6)

        # Borrar contenido actual
        run("shell input keyevent 123")  # ir al final
        for _ in range(100):
            run("shell input keyevent 67")  # borrar
        time.sleep(0.3)

        # Escribir nueva bio con emojis
        _escribir_texto_otg(serial, bio_text)

        # Guardar
        coords = buscarTextoEnRegion(("893", "114", "1047", "185"), "Save", umbral_similitud=0.65)
        if coords:
            tap(*coords)
        else:
            tap("92%", "8%")
        time.sleep(1.0)

        print(f"✅ [{serial}] Bio actualizada con emojis y saltos de línea")
        return True

    except Exception as e:
        print(f"💥 [{serial}] Error en subir_biografia: {e}")
        return False

