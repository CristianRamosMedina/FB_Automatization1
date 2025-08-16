from adb_utils import crear_funciones_con_serial,cerrary_salir
import time


def ejecutar_gestos(serial):
    try:
        run, tap, long_tap, move, write, buscarTextoEnRegion, detectarColorOTap = crear_funciones_con_serial(serial)
        run("shell input keyevent 224")  # Encender pantalla
        time.sleep(1)
        move("50%","68%","50%","20%")
        time.sleep(1)

        print(f"\n🚀 Abriendo TikTok en {serial}...")
        run("shell monkey -p com.zhiliaoapp.musically -c android.intent.category.LAUNCHER 1")
        time.sleep(5)
        tap("50%", "90.34%")
        time.sleep(4)

        tap("8.85%","90.87%")
        tap("79.17%", "80.26%")
        time.sleep(0.8)
        
        
        tap("50%", "6.4%")
        time.sleep(0.4)
        coords1 = buscarTextoEnRegion(("25.29%", "8.19%", "85.71%", "85.94%"), "Camera", umbral_similitud=0.9)
        if coords1:
            tap(*coords1)
            time.sleep(0.4) 
        else:
            print("\n No se pudo encontrar Camera")
            tap("50%", "6.4%")
            time.sleep(0.4)    
        tap("50%", "6.4%")                   
        coords2 = buscarTextoEnRegion(("25.29%", "8.19%", "85.71%", "85.94%"), "Camera", umbral_similitud=0.8)
        if coords2:
            tap(*coords2)
            time.sleep(0.4) 
        else:
            print("\n No se pudo encontrar Camera")
            tap("50%", "6.4%")
            time.sleep(0.4)           
        tap("50%", "6.4%")
        coords3 = buscarTextoEnRegion(("25.29%", "8.19%", "85.71%", "85.94%"), "Camera", umbral_similitud=0.6)
        if coords3:
            tap(*coords3)
            time.sleep(0.4) 
        else:
            print("\n No se pudo encontrar Camera")
            tap("50%", "6.4%")
            time.sleep(0.4)           
        
        
        
        
        
        time.sleep(2)
        
        
        
        
        
        region_checkbox = ("0%","85.5%","50%","100%")
    
        # Detectar color rojo y si no está, tapear en el círculo
        detectarColorOTap(
            color_objetivo="#E94F64",   # rojo del check
            region=region_checkbox,     
            tolerancia=30,              # margen de variación del rojo
            tap_si_no=("6%","90.125%"),    # coordenadas aproximadas del círculo
            muestreo=64,
            exigir_pixeles=3
        )
        
        
        
        # Gestos de taps
        secuencias = [
            ("61.48%", "63.68%"), ("28.70%", "63.68%"), ("94.72%", "47.91%"),
            ("61.48%", "47.91%"), ("28.70%", "47.91%"), ("94.72%", "32.56%"),
            ("61.48%", "32.56%"), ("28.70%", "32.56%"), ("94.72%", "16.92%"),
            ("61.48%", "16.92%"), ("28.70%", "16.92%")
        ]
        
        for pos in secuencias:
            tap(*pos)
            time.sleep(0.3)

        # Botón Next
        coords = buscarTextoEnRegion(("2.50%", "75.98%", "98.70%", "93.76%"), "Next")
        tap(*coords) if coords else tap("74.54%", "90.17%")

        time.sleep(4)
        coords = buscarTextoEnRegion(("5.74%", "5.30%", "98.70%", "13.12%"), "♪")
        if coords:
            tap(*coords)
        else:
            print("\n no se pudo ")
            tap("50%", "10.37%")

        time.sleep(0.9)
        tap("92.69%", "52.02%")
        time.sleep(1)

        if serial.startswith("R8YY602XW7Y"):
            write("Being a Girl jonica")
        else:
            write("wash favsoundds")

        run("shell input keyevent 66")
        time.sleep(6)
        long_tap("87.68%", "50.68%")
        time.sleep(2.3)
        tap("50.46%", "29.19%")
        time.sleep(2)
        print("\n Musica hecha")

        coords = buscarTextoEnRegion(("2.50%", "75.98%", "98.70%", "93.76%"), "Next")
        tap(*coords) if coords else tap("75.71%", "92.22%")
        time.sleep(2)
        tap("50%", "33%")
        tap("50%", "33%")
        print("Escribiendo Post")
        time.sleep(0.4)

        if serial.startswith("R8YY602XW7Y"):
            write("#women #health #healthy #bloating #bloated ")
        else:
            write("#hairgrowth #beaty #fy #hairgrowthtips ")

        time.sleep(0.9)
        coords = buscarTextoEnRegion(("1%", "0%", "100%", "100%"), "Post")
        tap(*coords) if coords else long_tap("91.76%", "6.88%")

        print("\n🎉🍾End 🎉🍾")

        # --- Esperar a que aparezca "posted" ---
        print("⌛ Esperando a que aparezca 'posted'...")
        start_time = time.time()
        while time.time() - start_time < 70:
            if buscarTextoEnRegion(("0%", "0%", "100%", "100%"), "posted", umbral_similitud=0.6):
                print("✅ 'posted' detectado, flujo finalizado correctamente.")
                return
            time.sleep(0.3)

        # Si no apareció → forzar error para que vaya al except
        raise Exception("'posted' no detectado en 40s")

    except Exception as e:
        print(f"❌ Error en ejecutar_gestos: {e}")
        cerrary_salir(serial)
        ejecutar_gestos(serial)
