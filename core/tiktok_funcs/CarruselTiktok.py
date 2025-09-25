# core/tiktok_funcs/CarruselTiktok.py
from core.adb_utils import crear_funciones_con_serial
import time
from .utils import cerrary_salir, should_stop

def _sleep_coop(serial: str, total_seg: float, slice_seg: float = 0.2) -> bool:
    """Espera cooperativa. Devuelve True si se pidió detener durante la espera."""
    fin = time.time() + max(0.0, total_seg)
    while time.time() < fin:
        if should_stop(serial):
            return True
        time.sleep(min(slice_seg, fin - time.time()))
    return False

def _esperar_texto(serial: str, buscarTextoEnRegion, texto: str, region, timeout=70, umbral=0.6) -> bool:
    """Espera cooperativa a que aparezca un texto por OCR."""
    start = time.time()
    while time.time() - start < timeout:
        if should_stop(serial):
            return False
        if buscarTextoEnRegion(region, texto, umbral_similitud=umbral):
            return True
        time.sleep(0.3)
    return False

def ejecutar_gestos(serial: str):
    """
    Reintenta indefinidamente hasta detectar 'posted' o hasta que should_stop(serial) sea True.
    Sin recursión.
    """
    run, tap, long_tap, move, write, buscarTextoEnRegion, detectarColorOTap ,leerTextoEnRegion = crear_funciones_con_serial(serial)
    intento = 0
    backoff = 1.0  # crecerá suavemente en errores consecutivos

    while True:
        if should_stop(serial):
            print(f"⏹ [{serial}] Stop solicitado. Salgo de ejecutar_gestos.")
            return

        intento += 1
        try:
            print(f"\n🚀 [{serial}] Iniciando flujo de publicación (intento #{intento})")

            # Encender y “desbloquear”
            run("shell input keyevent 224")
            if _sleep_coop(serial, 1): return
            move("50%","68%","50%","20%")
            if _sleep_coop(serial, 1): return

            # Abrir TikTok
            run("shell monkey -p com.zhiliaoapp.musically -c android.intent.category.LAUNCHER 1")
            if _sleep_coop(serial, 5): return

            tap("50%", "90.34%"); _sleep_coop(serial, 4)
            tap("8.85%","90.87%"); tap("79.17%", "80.26%"); _sleep_coop(serial, 0.8)

            # Entrar a Camera (varios umbrales)
            tap("50%", "6.4%"); _sleep_coop(serial, 0.4)
            for umbral in (0.9, 0.8, 0.6):
                if should_stop(serial): return
                coords = buscarTextoEnRegion(("25.29%", "8.19%", "85.71%", "85.94%"), "Camera", umbral_similitud=umbral)
                if coords:
                    tap(*coords); _sleep_coop(serial, 0.4)
                    break
                else:
                    print(f"⚠️ [{serial}] 'Camera' no visible con umbral {umbral}. Reintentando tap en barra…")
                    tap("50%", "6.4%"); _sleep_coop(serial, 0.4)

            if _sleep_coop(serial, 2): return

            # Check rojo (si aplica)
            detectarColorOTap(
                color_objetivo="#E94F64",
                region=("0%","85.5%","50%","100%"),
                tolerancia=30,
                tap_si_no=("6%","90.125%"),
                muestreo=64,
                exigir_pixeles=3
            )

            # Taps de rejilla
            secuencias = [
                ("61.48%", "63.68%"), ("28.70%", "63.68%"), ("94.72%", "47.91%"),
                ("61.48%", "47.91%"), ("28.70%", "47.91%"), ("94.72%", "32.56%"),
                ("61.48%", "32.56%"), ("28.70%", "32.56%"), ("94.72%", "16.92%"),
                ("61.48%", "16.92%"), ("28.70%", "16.92%")
            ]
            for pos in secuencias:
                if should_stop(serial): return
                tap(*pos); _sleep_coop(serial, 0.3)

            # Next
            coords = buscarTextoEnRegion(("2.50%", "75.98%", "98.70%", "93.76%"), "Next")
            tap(*coords) if coords else tap("74.54%", "90.17%")
            if _sleep_coop(serial, 4): return

            # Nota musical
            coords = buscarTextoEnRegion(("5.74%", "5.30%", "98.70%", "13.12%"), "♪")
            tap(*coords) if coords else tap("50%", "10.37%")
            if _sleep_coop(serial, 0.9): return

            tap("92.69%", "52.02%"); _sleep_coop(serial, 1)
            write("passport junkie" if serial.startswith("R8YY602XW7Y") else "passport junkie")
            run("shell input keyevent 66")  # Enter
            if _sleep_coop(serial, 6): return

            long_tap("87.68%", "50.68%"); _sleep_coop(serial, 2.3)
            tap("50.46%", "29.19%"); _sleep_coop(serial, 2)
            print(f"🎵 [{serial}] Música aplicada")

            # Next
            coords = buscarTextoEnRegion(("2.50%", "75.98%", "98.70%", "93.76%"), "Next")
            tap(*coords) if coords else tap("75.71%", "92.22%")
            if _sleep_coop(serial, 2): return

            # Escribir post
            tap("50%", "33%"); tap("50%", "33%"); _sleep_coop(serial, 0.4)
            write("Believe me when i say... #prettygirls #blackwoman" if serial.startswith("R8YY602XW7Y")
                  else "Believe me when i say... #prettygirls #blackwoman")
            if _sleep_coop(serial, 0.9): return
        
            time.sleep(2)
            tap("79.16%","96.93%") # hagia abajo
            time.sleep(2)
                
            tap("73.75%", "90.68%")
            tap(*coords) if coords else long_tap("91.76%", "6.88%")
            print(f"🎉🍾 [{serial}] Publicando…")

            time.sleep(0.6)
            # Esperar 'posted'
            ok = _esperar_texto(
                serial,
                buscarTextoEnRegion,
                "Post",
                region=("0%", "0%", "100%", "8.5%"),
                timeout=70,
                umbral=0.6
            )
            if ok:
                print(f"✅ [{serial}] 'post' detectado. Flujo finalizado correctamente.")
                return

            # Forzar reintento si no apareció
            raise Exception("'post' no detectado en 70s")

        except Exception as e:
            print(f"❌ [{serial}] Error en ejecutar_gestos (intento #{intento}): {e}")
            cerrary_salir(serial)

            if should_stop(serial):
                print(f"⏹ [{serial}] Stop tras error. Saliendo.")
                return

            # Backoff suave y seguir intentando infinitamente
            backoff = min(10.0, backoff + 1.0)  # crece hasta 10s
            print(f"🔁 [{serial}] Reintentando en {backoff:.1f}s… (intentos infinitos)")
            if _sleep_coop(serial, backoff):  # si piden stop durante el backoff, salimos
                return
            # loop continúa (retry infinito)
