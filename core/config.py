import os
import json

# ------------------- RUTAS IMPORTANTES -------------------
ADB_PATH = r"C:\Users\Acer\Documents\platform-tools-latest-windows\platform-tools\adb.exe"
SCRCPY_PATH = r"C:\Users\Acer\Documents\scrcpy-win64-v3.3.1\scrcpy-win64-v3.3.1\scrcpy.exe"

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

def ejecteg(serial):
    run, tap, long_tap, move, write, buscarTextoEnRegion = crear_funciones_con_serial(serial)
    run("shell input keyevent 4")
    run("shell input keyevent 4")
    run("shell input keyevent 4")
    run("shell input keyevent 4")

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
