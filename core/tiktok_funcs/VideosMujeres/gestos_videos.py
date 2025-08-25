import time, random
from core.adb_utils import crear_funciones_con_serial
from ..utils import ejecteg, cerrary_salir, should_stop
from ..CarruselTiktok import _sleep_coop

def _esperar_texto(serial, buscarTextoEnRegion, texto, region, timeout=40, umbral=0.6, interval=1.0):
    """
    Espera hasta que aparezca 'texto' en pantalla en un tiempo máximo.
    Devuelve True si se detectó, False si no.
    """
    fin = time.time() + timeout
    while time.time() < fin:
        if should_stop(serial):
            return False
        coords = buscarTextoEnRegion(region, texto, umbral_similitud=umbral)
        if coords:
            return True
        time.sleep(interval)
    return False


def gestos_videos(serial):
    run, tap, long_tap, move, write, buscarTextoEnRegion, detectarColorOTap, leerTextoEnRegion = crear_funciones_con_serial(serial)

    intento = 0
    backoff = 1.0

    while True:  # retry infinito hasta que logre detectar "posted"
        try:
            intento += 1
            stickerMood = random.randint(1, 3)
            print(f"\n🎵 Seleccionando música para el sticker: {stickerMood}")
            run("shell input keyevent 224")  # Encender pantalla
            time.sleep(1)
            move("50%","68%","50%","20%")
            time.sleep(1)

            ejecteg(serial)

            print(f"\n🚀 Abriendo TikTok en {serial}...")
            run("shell monkey -p com.zhiliaoapp.musically -c android.intent.category.LAUNCHER 1")

            time.sleep(5)
            tap("50%", "90.34%")
            time.sleep(4)
            tap("8.85%","90.87%")
            tap("79.17%", "80.26%")
            time.sleep(0.8)
            tap("50%", "6.4%")
            time.sleep(0.6)

            coords = buscarTextoEnRegion(("25.29%", "8.19%", "85.71%", "85.94%"), "Videos", umbral_similitud=0.7)
            if coords:
                tap(*coords)
            else:
                coords = buscarTextoEnRegion(("25.29%", "8.19%", "85.71%", "85.94%"), "Videos", umbral_similitud=0.6)
                if coords:
                    tap(*coords)
                else:
                    coords = buscarTextoEnRegion(("25.29%", "8.19%", "85.71%", "85.94%"), "Videos", umbral_similitud=0.3)
                    if coords:
                        tap(*coords)
                    else:
                        print("No se encontró 'Camera' en pantalla, tocando en el centro")

            tap("50%", "6.4%")
            time.sleep(0.6)
            coords = buscarTextoEnRegion(("25.29%", "8.19%", "85.71%", "85.94%"), "Videos", umbral_similitud=0.7)
            if coords:
                tap(*coords)
            else:
                coords = buscarTextoEnRegion(("25.29%", "8.19%", "85.71%", "85.94%"), "Videos", umbral_similitud=0.6)
                if coords:
                    tap(*coords)
                else:
                    coords = buscarTextoEnRegion(("25.29%", "8.19%", "85.71%", "85.94%"), "Videos", umbral_similitud=0.3)
                    if coords:
                        tap(*coords)
                    else:
                        print("No se encontró 'Camera' en pantalla, tocando en el centro")

            time.sleep(1.6)
            tap("61.48%", "16.92%"); time.sleep(0.6)
            tap("28.70%", "16.92%"); time.sleep(0.6)

            coords = buscarTextoEnRegion(("2.50%", "75.98%", "98.70%", "93.76%"), "Next")
            if coords:
                tap(*coords)
            else:
                tap("74.54%", "90.17%")

            time.sleep(4)
            ############# Musica
            coords = buscarTextoEnRegion(("5.74%", "5.30%", "98.70%", "13.12%"), "Sound")
            if coords:
                tap(*coords)
            else:
                print("\n No musica encontrada, tocando en el centro")
                tap("50%", "10.6%")

            time.sleep(0.9)
            tap("92.69%", "52.02%")
            time.sleep(1)

            switch_musica = {
                1: "Make America Great Again - Brian Kelley",
                2: "There She Goes - Cyril Riley & idkxlcfzmk4 & MOONLGHT",
                3: "Boundless Worship - Josue Novais Piano Worship"
            }
            music = switch_musica.get(stickerMood)
            print(f"\n🎵 Música seleccionada: {music}")
            time.sleep(0.6)
            write(str(music))
            run("shell input keyevent 66")  # Enter

            time.sleep(6)
            long_tap("87.68%", "50.68%")

            time.sleep(2.3)
            tap("50.46%", "29.19%")

            time.sleep(2)
            tap("95%","18.5%")
            time.sleep(0.5)
            coords = buscarTextoEnRegion(("0%", "60%", "90%", "93%"), "Post")
            if coords:
                run("shell input keyevent 4")  # Back
                time.sleep(1)
                tap("95%", "25%")
            else:
                print("\n No se encontró 'Share'")

            time.sleep(2.5)
            move("95%","89.5%","5%","89.5%",1000)
            time.sleep(1.6)
            coords= buscarTextoEnRegion(("2.50%", "75.98%", "98.70%", "85.76%"), "Overlay",umbral_similitud=0.6)
            if coords:
                tap(*coords)
            else:
                time.sleep(1.6)
                move("95%","89.5%","9%","89.5%",1000)
                time.sleep(1.6)
                coords= buscarTextoEnRegion(("2.50%", "75.98%", "98.70%", "85.76%"), "Overlay", umbral_similitud=0.5)
                if coords:
                    tap(*coords)
                else:
                    move("95%","89.5%","9%","89.5%",1000)
                    time.sleep(1.6)
                    if serial.startswith("R8YY602WSYX"):
                        tap("16.2%", "89.5%")
                    else:
                        tap("1.14%", "90%")
                        time.sleep(1)
                    
                    #if buscarTextoEnRegion(("2.50%","46.25%","85.15%","55.7%"),"Detect"):
                     #   run("shell input keyevent 4")  # Back
                      #  time.sleep(1)
                       # tap("16.2%", "89.5%")
                    #else:
                     #   print("\n No se encontró 'overlay' en pantalla, tocando en el centro")

            time.sleep(1.6)
            tap("50%", "6.4%")
            time.sleep(0.6)
            coords = buscarTextoEnRegion(("25.29%", "8.19%", "85.71%", "85.94%"), "Camera", umbral_similitud=0.7)
            if coords:
                tap(*coords)
            else:
                coords = buscarTextoEnRegion(("25.29%", "8.19%", "85.71%", "85.94%"), "Camera", umbral_similitud=0.6)
                if coords:
                    tap(*coords)
                else:
                    coords = buscarTextoEnRegion(("25.29%", "8.19%", "85.71%", "85.94%"), "Camera", umbral_similitud=0.3)
                    if coords:
                        tap(*coords)
                    else:
                        print("No se encontró 'Camera' en pantalla, tocando en el centro")

            time.sleep(1.6)
            switch_tap_sticker = {
                3: ("61.48%", "16.92%"),
                2: ("94.72%", "16.92%"),
                1: ("28.70%", "32.56%")
            }
            tap(*switch_tap_sticker.get(stickerMood))
            time.sleep(0.5)

            coords = buscarTextoEnRegion(("2.50%", "75.98%", "98.70%", "93.76%"), "Next")
            if coords:
                tap(*coords)
            else:
                tap("74.54%", "90.17%")
            time.sleep(1)
            print("Estirando sticker")
            move("99.5%", "72%","99.8%","72%", duration=2000)
            time.sleep(1)
            tap("95.29%", "5.50%")
            time.sleep(1.2)

            caption= random.choice([
                "#MAGA #Trump2024 #TrumpTrain #AmericaFirst #Patriot",  
                "#TrumpSupporter #MakeAmericaGreatAgain #RedWave #SaveAmerica #KAG",  
                "#Conservative #ProTrump #Freedom #USA #PatriotsUnite",  
                "#TrumpWon #AmericaStrong #SupportTrump #Election2024 #PatriotPride",  
                "#Republican #AmericanPride #StandWithTrump #GodBlessTheUSA",  
                "#TrumpForever #BackTheBlue #LoveUSA #ProFreedom #MAGA2024"
            ])

            tap("19.96%", "11%")
            time.sleep(0.4)
            write(caption)
            time.sleep(1.2)

            long_tap("90%", "5.375%")
          
            # ✅ Esperar que aparezca "posted"
            ok = _esperar_texto(
                serial,
                buscarTextoEnRegion,
                "posted",
                region=("0%", "0%", "100%", "30%"),
                timeout=70,
                umbral=0.6
            )
            if ok:
                print(f"✅ [{serial}] 'posted' detectado. Flujo finalizado correctamente.")
                return

            # Si no apareció "posted" en el timeout → error forzado
            raise Exception("'posted' no detectado en 70s")

        except Exception as e:
            print(f"❌ [{serial}] Error en ejecutar_gestos (intento #{intento}): {e}")
            cerrary_salir(serial)

            if should_stop(serial):
                print(f"⏹ [{serial}] Stop tras error. Saliendo.")
                return

            # 🔁 Reintento infinito con backoff suave
            backoff = min(10.0, backoff + 1.0)  # crece hasta 10s
            print(f"🔁 [{serial}] Reintentando en {backoff:.1f}s… (intentos infinitos)")
            if _sleep_coop(serial, backoff):  # si piden stop durante backoff, salir
                return
            # loop continúa
