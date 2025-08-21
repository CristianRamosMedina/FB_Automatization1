from ..adb_utils import crear_funciones_con_serial, procesar_celular,guardar_dispositivos
import random, time, subprocess,json
from .utils import ejecteg, switchAccount,cargar_videos
import os, shutil, subprocess
from .TiktokCuentaScan import actualizar_estado_cuenta,stop_requested,_sleep
from core.paths import ADB_PATH

# Ruta local donde tienes los videos
BASE_VIDEOS_PATH = r"C:\Users\Acer\Documents\Carrusel\ImagenesCrudas\Videos"
USADOS_VIDEOS_PATH = os.path.join(BASE_VIDEOS_PATH, "videosUsados")

# Ruta en el dispositivo (Samsung A06)
DEVICE_VIDEOS_DIR = "/sdcard/DCIM/Video"

ADB_PATH = r"C:\Users\Acer\Documents\platform-tools-latest-windows\platform-tools\adb.exe"

# 📌 Asignación de celulares a carpetas de videos
ASIGNACION_VIDEOS = {
    "R8YY602WSYX": "Asian 2",   # cell1
    "R8YY602XA3R": "Australian Woman",     # cell2
}

def forzar_indexado(serial, carpeta="DCIM/Video"):
    try:
        run_adb(serial, "shell", "am", "broadcast",
                "-a", "android.intent.action.MEDIA_SCANNER_SCAN_FILE",
                "-d", f"file:///sdcard/{carpeta}")
        print(f"📂 Indexado forzado en {serial} → {carpeta}")
    except Exception as e:
        print(f"⚠️ Error indexando {carpeta} en {serial}: {e}")


def run_adb(serial, *args, check=True):
    cmd = [ADB_PATH, "-s", serial] + list(args)
    return subprocess.run(cmd, check=check)

def subir_un_video_y_mover(serial, carpeta_asignada):
    os.makedirs(USADOS_VIDEOS_PATH, exist_ok=True)

    carpeta_path = os.path.join(BASE_VIDEOS_PATH, carpeta_asignada)
    if not os.path.exists(carpeta_path):
        print(f"⚠️ La carpeta {carpeta_asignada} no existe.")
        return None

    # Buscar videos en la carpeta asignada
    videos = [f for f in os.listdir(carpeta_path)
              if f.lower().endswith(('.mp4', '.mov', '.mkv', '.webm', '.avi', '.m4v'))]

    if not videos:
        print(f"⚠️ No se encontraron videos en {carpeta_asignada}.")
        return None

    videos.sort()
    video_a_subir = videos[0]
    ruta_video = os.path.join(carpeta_path, video_a_subir)

    # Crear carpeta en el celular si no existe
    try:
        run_adb(serial, "shell", "mkdir", "-p", DEVICE_VIDEOS_DIR)
    except Exception as e:
        print(f"⚠️ No se pudo crear carpeta en el dispositivo: {e}")

    print(f"📤 Subiendo {video_a_subir} → {serial}:{DEVICE_VIDEOS_DIR}")
    try:
        run_adb(serial, "push", ruta_video, DEVICE_VIDEOS_DIR)
        # ✅ Forzar indexado de la carpeta de videos
        forzar_indexado(serial, "DCIM/Video")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error subiendo {video_a_subir}: {e}")
        return None

    # Copiar a videosUsados/<carpeta> en lugar de mover
    destino_subcarpeta = os.path.join(USADOS_VIDEOS_PATH, carpeta_asignada)
    os.makedirs(destino_subcarpeta, exist_ok=True)

    nuevo_destino = os.path.join(destino_subcarpeta, video_a_subir)
    try:
        shutil.copy2(ruta_video, nuevo_destino)  # 📌 ahora es copia
        print(f"✅ {video_a_subir} copiado a {nuevo_destino}")
    except Exception as e:
        print(f"⚠️ No se pudo copiar a usados: {e}")

    return video_a_subir

def Gestos_VIDEOS(serial):
    carpeta_asignada = ASIGNACION_VIDEOS.get(serial)
    if not carpeta_asignada:
        print(f"❌ No hay carpeta asignada para {serial}")
        return

    # Subir video correspondiente al celular
    video_subido = subir_un_video_y_mover(serial, carpeta_asignada)
    if not video_subido:
        print("⚠️ No se pudo subir ningún video. Cancelando.")
        return
    
    run, tap, long_tap, move, write, buscarTextoEnRegion, detectarColorOTap,leerTextoEnRegion = crear_funciones_con_serial(serial)
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
            tap("1.14%", "90%")  
            time.sleep(1)
            if buscarTextoEnRegion(("2.50%","46.25%","85.15%","55.7%"),"Detect"):
                run("shell input keyevent 4")  # Back
                time.sleep(1)
                tap("16.2%", "89.5%")
            else:
                print("\n No se encontró 'overlay' en pantalla, tocando en el centro")
                
            
        
    time.sleep(1.6)
    
    #abre
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
        2:("94.72%", "16.92%"),
        1:("28.70%", "32.56%")
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
    time.sleep(0.6)
    coords = buscarTextoEnRegion(("1%", "73%", "100%", "100%"), "Post",umbral_similitud=0.9)
    if coords:
        tap(*coords)
    else:
        coords = buscarTextoEnRegion(("1%", "73%", "100%", "100%"), "Post",umbral_similitud=0.6)
        if coords:
            tap(*coords)
        else:
            coords = buscarTextoEnRegion(("1%", "73%", "100%", "100%"), "Post",umbral_similitud=0.5)
            if coords:
                tap(*coords)
    
    time.sleep(30) 
        # ✅ Borrar todos los videos del dispositivo al terminar
    limpiar_videos_dispositivo(serial)

    
def limpiar_videos_dispositivo(serial, carpeta=DEVICE_VIDEOS_DIR):
    try:
        run_adb(serial, "shell", "rm", "-rf", f"{carpeta}/*")
        print(f"🧹 Carpeta de videos limpiada en {serial}: {carpeta}")
    except Exception as e:
        print(f"⚠️ Error limpiando carpeta en {serial}: {e}")

def VideosMujeres(serial):
    from core.tiktok_funcs.TiktokCuentaScan import ultimacuenta
    dispositivos = cargar_videos()
    if serial not in dispositivos:
        print(f"❌ Serial {serial} no encontrado en JSON.")
        return

    data = dispositivos[serial]
    por_subir = data.get("cuentasPorSubir", [])

    while por_subir:
        cuenta_actual = por_subir[0]
        print(f"\n🎬 Procesando cuenta {cuenta_actual} en {serial}...")

        # 1️⃣ Cambiar a la cuenta actual
        switchAccount(serial)

        # 2️⃣ Buscar carpeta asignada
        cuenta_info = next((c for c in data["cuentas"] if c["cuenta"] == cuenta_actual), None)
        if not cuenta_info:
            print(f"⚠️ No se encontró carpeta para {cuenta_actual}")
            break

        carpeta_path = cuenta_info.get("carpeta_path")
        if not carpeta_path or not os.path.exists(carpeta_path):
            print(f"⚠️ Carpeta inválida: {carpeta_path}")
            break

        print(f"📂 Usando videos desde: {carpeta_path}")

        # 3️⃣ Subir videos a DCIM/Videos
        procesar_celular(serial, carpeta_path)

        # 4️⃣ Ejecutar los gestos de subida a TikTok
        try:
            Gestos_VIDEOS(serial)   # 👉 tu función que hace taps y sube el video
        except Exception as e:
            print(f"❌ Error subiendo video: {e}")
            break

        # 5️⃣ Borrar videos del teléfono después de subir
        try:
            subprocess.run([ADB_PATH, "-s", serial, "shell", "rm", "-rf", "/sdcard/DCIM/Videos/*"])
            print("🧹 Videos borrados del teléfono.")
        except Exception as e:
            print(f"⚠️ No se pudo limpiar carpeta: {e}")

        # 6️⃣ Actualizar estado
        siguiente = actualizar_estado_cuenta(serial, cuenta_actual)
        if not siguiente:
            break
        por_subir = data.get("cuentasPorSubir", [])
        
