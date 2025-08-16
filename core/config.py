import os
import json
import subprocess
import time
import io
import re
from datetime import datetime
from .paths import ADB_PATH, SCRCPY_PATH
from .adb_utils import crear_funciones_con_serial, parse_coord, get_screen_size, pytesseract, crear_service_drive, modificar_fechas_en_orden, procesar_celular, guardar_dispositivos
from PIL import UnidentifiedImageError, Image
from .tiktok_funcs.utils import ejecteg


# ------------------- VARIABLES GLOBALES -------------------
# Diccionario para saber si un hilo está activo o detenido
hilos_activos = {}

# ------------------- FUNCIONES DE CONFIGURACIÓN -------------------


def cargar_dispositivos():
    """Lee el archivo dispositivos.json y devuelve el contenido como diccionario."""
    if os.path.exists("dispositivos.json"):
        with open("dispositivos.json", "r") as f:
            return json.load(f)
    return {}

def ultimacuenta(serial):
    try:
        switchAccount(serial)

        try:
            cuentas_detectadas, _ = detectar_usuarios_en_pantalla(serial)
        except (subprocess.SubprocessError, UnidentifiedImageError, OSError) as e:
            print(f"⚠️ Error al detectar usuarios: {e}")
            time.sleep(1)
            ejecteg(serial)
            ejecteg(serial)
            return ultimacuenta(serial)

        print("\n Cuentas Primera")
        if not cuentas_detectadas:
            print("⚠️ No se detectaron cuentas visibles. Reintentando...")
            time.sleep(1)
            ejecteg(serial)
            ejecteg(serial)
            return ultimacuenta(serial)

        cuentaactual = list(cuentas_detectadas)[0]
        print(cuentaactual)
        return cuentaactual

    except Exception as e:
        print(f"💥 Error inesperado: {e}")
        time.sleep(1)
        ejecteg(serial)
        ejecteg(serial)
        return ultimacuenta(serial)
    
def detectar_usuarios_en_pantalla(serial):
    Width,Heigth= get_screen_size(serial)
    resultado = subprocess.run([ADB_PATH, "-s", serial, "exec-out", "screencap", "-p"], capture_output=True)
    imagen_bytes = resultado.stdout
    if not imagen_bytes:
        return [], False

    x1 = parse_coord("19.72%", Width)
    y1 = parse_coord("6.63%", Heigth)
    x2 = parse_coord("87.87%", Width)
    y2 = parse_coord("90.71%", Heigth)


    img = Image.open(io.BytesIO(imagen_bytes))
    img = img.crop((x1, y1, x2, y2))

    data = pytesseract.image_to_data(img, lang="eng", output_type=pytesseract.Output.DICT)

    cuentas_con_pos = []  # Lista de (palabra, y)
    recolectando = False

    for i, palabra in enumerate(data["text"]):
        palabra = palabra.strip()
        if not palabra:
            continue

        lower = palabra.lower()
        y = data["top"][i]

        if lower in ["switch", "account"] and not recolectando:
            recolectando = True
            continue
        if lower in ["add", "+", "add account"]:
            break
        if recolectando and lower not in ["account", "switch"]:
            cuentas_con_pos.append((palabra, y))

    # Ordenar por coordenada Y
    cuentas_ordenadas = [nombre for nombre, _ in sorted(cuentas_con_pos, key=lambda x: x[1])]

    texto_completo = [t.lower() for t in data["text"] if t.strip()]
    hay_add_account = any("add" in t for t in texto_completo) and any("account" in t for t in texto_completo)

    return cuentas_ordenadas, hay_add_account

def descargar_carpeta_completa( folder_id,serial ):
    carpeta_destino = f"./imagenes_temp/{serial}"
    service = crear_service_drive()


    if os.path.exists(carpeta_destino):
        import shutil
        shutil.rmtree(carpeta_destino)

    os.makedirs(carpeta_destino, exist_ok=True)
    try:
        query = f"'{folder_id}' in parents and mimeType != 'application/vnd.google-apps.folder'"
        result = service.files().list(q=query, fields="files(id, name)").execute()
        files = result.get('files', [])
        print(f"📦 {len(files)} archivos encontrados")
        if not files:
            print("⚠️ No se encontraron archivos en la carpeta")
            return False

        archivos_exitosos = 0
        archivos_fallidos = 0

        for i, file in enumerate(files, 1):
            try:
                print(f"📥 Descargando {i}/{len(files)}: {file['name']}")

                request = service.files().get_media(fileId=file['id'])
                file_content = request.execute()

                ruta_archivo = os.path.join(carpeta_destino, file['name'])
                with open(ruta_archivo, 'wb') as f:
                    f.write(file_content)

                archivos_exitosos += 1
                print(f"✅ Descargado: {file['name']}")

            except Exception as e:
                print(f"❌ Error descargando {file['name']}: {e}")
                archivos_fallidos += 1

        print(f"\n📈 Descarga completada: {archivos_exitosos} exitosos, {archivos_fallidos} fallidos")
        if archivos_exitosos > 0:
            return carpeta_destino  # ✅ Devuelve la ruta si fue exitoso
        else:
            return False


    except Exception as e:
        print(f"❌ Error general descargando carpeta: {e}")
        return False

def descarga(serial,cuentaactual):
    global SERVICE_DRIVE

    data = cargar_dispositivos()
    if serial not in data:
        print(f"❌ Serial {serial} no encontrado en el JSON.")
        return None

    cuentas = data[serial].get("cuentas", [])

    for cuenta in cuentas:
        if cuenta["cuenta"] == cuentaactual:
            carpeta_id = cuenta["carpeta_id"]
            print(f"📂 Carpeta ID encontrada: {carpeta_id}")

            carpeta_descargada = descargar_carpeta_completa(carpeta_id, serial)

            if carpeta_descargada:
                modificar_fechas_en_orden(carpeta_descargada)
                procesar_celular(serial, carpeta_descargada)
            else:
                print(f"❌ No se pudo descargar la carpeta para el dispositivo {serial}")

                print(f"❌ Cuenta {cuentaactual} no encontrada para el serial {serial}.")
                return None

def actualizar_estado_cuenta(serial, cuenta_actual):
    dispositivos = cargar_dispositivos()
    if serial not in dispositivos:
        print(f"❌ Serial {serial} no encontrado.")
        return None

    data = dispositivos[serial]

    por_subir = data.get("cuentasPorSubir", [])
    subidas = data.get("cuentasSubidas", [])

    if cuenta_actual in por_subir:
        por_subir.remove(cuenta_actual)
        subidas.append(cuenta_actual)
        print(f"📦 Movido '{cuenta_actual}' de cuentasPorSubir → cuentasSubidas")
    else:
        print(f"⚠️ '{cuenta_actual}' no estaba en cuentasPorSubir")

    dispositivos[serial]["cuentasPorSubir"] = por_subir
    dispositivos[serial]["cuentasSubidas"] = subidas
    guardar_dispositivos(dispositivos)

    if por_subir:
        return por_subir[0]  # próxima cuenta a subir
    else:
        print("✅ No hay más cuentas por subir.")
        return None

def switchAccount(serial):
    run, tap, long_tap, move, write, buscarTextoEnRegion, detectarColorOTap = crear_funciones_con_serial(serial)
    # Salir a Home por si acaso
    run("shell input keyevent 224")  # Encender pantalla
    time.sleep(0.5)
    move("50%","68%","50%","20%")
    time.sleep(0.5)
    run("shell input keyevent 4")
    run("shell input keyevent 4")
    run("shell input keyevent 4")
    run("shell input keyevent 4")

    print(f"\n🚀 Abriendo TikTok en {serial}...")
    run("shell monkey -p com.zhiliaoapp.musically -c android.intent.category.LAUNCHER 1")
    time.sleep(5)
    # Ir al perfil
    long_tap("90.09%", "92.31%")  # (973, 2160)
    time.sleep(1)

    # Menú superior
    tap("95.29%", "5.50%")

    time.sleep(1)

    # Ir a Settings
    coords = buscarTextoEnRegion(("2.13%", "57.64%", "99.35%", "93.75%"), "Settings")
    if coords:
        tap(*coords)
    else:
        time.sleep(0.6)
        tap("50.46%", "89.87%")  
    time.sleep(1.8)
    # Scroll para mostrar "Switch account"
    move("50.46%", "85.68%", "50.46%", "8.42%")  # (545, 2006 → 545, 197)
    time.sleep(0.6)
    move("50.46%", "85.68%", "50.46%", "8.42%")
    time.sleep(0.8)

    # Tap en "Switch account"
    coords = buscarTextoEnRegion(("2.13%", "57.64%", "99.35%", "93.75%"), "switch")
    if coords:
        tap(*coords)
    else:
        tap("50.46%", "76.92%")       # (545, 1800)
    time.sleep(0.7)

def cambiar_a_siguiente_cuenta(serial):
    Width,Height=get_screen_size(serial)
    run, tap, long_tap, move, write, buscarTextoEnRegion = crear_funciones_con_serial(serial)
    print(f"🔁 Cambiando cuenta en dispositivo {serial}...")

    # 1. Detectar la cuenta actual visible
    cuentas_detectadas, _ = detectar_usuarios_en_pantalla(serial)
    print("\n Cuentas Primera")
    print(list(cuentas_detectadas)[0]  )

    if not cuentas_detectadas:
        print("⚠️ No se detectaron cuentas visibles.")
        return  
    cuenta_actual = list(cuentas_detectadas)[0]  # Primera cuenta visible
    print(f"📌 Cuenta actual detectada: {cuenta_actual}")
    siguiente = actualizar_estado_cuenta(serial, cuenta_actual)
    if not siguiente:
        print("✅ Ya no quedan cuentas por subir.")
        return "Fin"
    print(f"🎯 Buscando próxima cuenta a subir: {siguiente}")
    x1=parse_coord("19.72%",Width)
    y1=parse_coord("14.78%",Height)
    x2=parse_coord("87.87%",Width)
    y2=parse_coord("93.16%",Height)

    region = (x1, y1, x2,y2)
    coords = buscarTextoEnRegion(region, siguiente,umbral_similitud=0.8)

    if coords:
        x, y = coords
        tap(x,y)
        print(f"🧭 Cambiado a cuenta: {siguiente}")
        time.sleep(4)
    else:
        print(f"❌ No se encontró '{siguiente}' en pantalla.")
    return siguiente 

def cambiarcuenta(serial):
    try:
        switchAccount(serial)
        # Punto donde ya estamos listos para cambiar cuenta
        cuenta = cambiar_a_siguiente_cuenta(serial)
        
        if cuenta == "FIN":
            print(f"🏁 [{serial}] Proceso finalizado: no hay más cuentas.")
            return 

        if not cuenta:
            print(f"⚠️ [{serial}] Error al cambiar de cuenta, reintentando...")
            return cambiarcuenta(serial)
        
        time.sleep(5)
    except Exception as e:
        print(f"[{serial}] Error: {e}. Reintentando...")
        return cambiarcuenta(serial)  # Reintenta si ocurre alguna excepción

def MoverCarpetasUsadas(serial):
    FINAL_FOLDER_ID = "1ADOHMAXp5Dmd_pkqHfOmR3ffECM08QYF"
    service = crear_service_drive()
    data = cargar_dispositivos().get(serial, {})

    cuentas = data.get("cuentas", [])
    subidas = set(data.get("cuentasSubidas", []))
    movidas = 0

    for cuenta in cuentas:
        cuenta_nombre = cuenta.get("cuenta")
        carpeta_id = cuenta.get("carpeta_id")
        if cuenta_nombre in subidas and carpeta_id:
            try:
                # Obtener metadata: parent actual y nombre
                metadata = service.files().get(
                    fileId=carpeta_id,
                    fields='parents,name'
                ).execute()

                parent_actual = metadata.get('parents', [])[0]
                nombre_actual = metadata.get('name', cuenta_nombre)

                # Mover carpeta
                service.files().update(
                    fileId=carpeta_id,
                    addParents=FINAL_FOLDER_ID,
                    removeParents=parent_actual,
                    fields="id, parents"
                ).execute()

                # Generar nuevo nombre sin duplicar "usado"
                base_nombre = re.sub(r' usado \d{2}-\d{2}_\d{2}h$', '', nombre_actual)
                fecha_hora = datetime.now().strftime("%d-%m_%Hh")
                nuevo_nombre = f"{base_nombre} usado {fecha_hora}"

                # Renombrar carpeta
                service.files().update(
                    fileId=carpeta_id,
                    body={"name": nuevo_nombre}
                ).execute()

                print(f"📦 Carpeta de {cuenta_nombre} movida y renombrada a '{nuevo_nombre}'.")
                movidas += 1

            except Exception as e:
                print(f"❌ Error al mover o renombrar la carpeta de {cuenta_nombre}: {e}")

    print(f"✅ {serial}: {movidas} carpeta(s) movida(s) y renombrada(s).")
