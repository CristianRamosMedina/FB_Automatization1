import time
from core.tiktok_funcs.utils import ejecteg, switchAccount
from core.tiktok_funcs.TiktokCuentaScan import cargar_dispositivos,ultimacuenta,detectar_usuarios_en_pantalla, actualizar_estado_cuenta
from .CarruselTiktok import  ejecutar_gestos
import  os,re,  shutil, datetime
from ..adb_utils import modificar_fechas_en_orden, procesar_celular, get_screen_size, parse_coord,crear_funciones_con_serial


def cambiar_todas_las_cuentas(serial):
    contador = 0
    while True:
        data = cargar_dispositivos().get(serial, {})
        pendientes = data.get("cuentasPorSubir", [])
        if not pendientes:
            print(f"✅ {serial}: Ya no hay más cuentas por subir.")
            break

        cuenta_actual = ultimacuenta(serial)
        print("Cambiar Cuentas detecta : ")
        print(cuenta_actual)

        if cuenta_actual in pendientes:
            print("Ultima cuenta en pendientes 🥰")
            descarga(serial,cuenta_actual)
            ejecteg(serial)
            ejecutar_gestos(serial)
            cambiarcuenta(serial)
        else:
            print("Cambiando CUENTAS ")
            cambiarcuenta(serial)

        time.sleep(1)

    print(contador)
    print("\n Proceso terminado Eliminando Carpetas del Drive")
    MoverCarpetasUsadas(serial)

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

def descarga(serial, cuentaactual):
    data = cargar_dispositivos()
    if serial not in data:
        print(f"❌ Serial {serial} no encontrado en el JSON.")
        return None

    cuentas = data[serial].get("cuentas", [])

    for cuenta in cuentas:
        if cuenta["cuenta"] == cuentaactual:
            carpeta_path = cuenta.get("carpeta_path")
            if not carpeta_path or not os.path.exists(carpeta_path):
                print(f"❌ Carpeta local para {cuentaactual} no encontrada.")
                return None

            print(f"📂 Usando carpeta local: {carpeta_path}")

            modificar_fechas_en_orden(carpeta_path)
            procesar_celular(serial, carpeta_path)
            return True

    print(f"❌ Cuenta {cuentaactual} no encontrada para el serial {serial}.")
    return None

BASE_PATH = os.path.join(os.path.expanduser("~/Documents"), "Carrusel", "ImagenesCrudas")
USADOS_PATH = os.path.join(BASE_PATH, "CarruselesUsados")

def MoverCarpetasUsadas(serial):
    # Crear carpeta CarruselesUsados si no existe
    if not os.path.exists(USADOS_PATH):
        os.makedirs(USADOS_PATH)
        print(f"📂 Carpeta creada: {USADOS_PATH}")

    data = cargar_dispositivos().get(serial, {})
    cuentas = data.get("cuentas", [])
    subidas = set(data.get("cuentasSubidas", []))
    movidas = 0

    for cuenta in cuentas:
        cuenta_nombre = cuenta.get("cuenta")
        carpeta_path = cuenta.get("carpeta_path")

        if cuenta_nombre in subidas and carpeta_path and os.path.exists(carpeta_path):
            try:
                # Nombre base de la carpeta
                nombre_actual = os.path.basename(carpeta_path)

                # Evitar duplicar "usado"
                base_nombre = re.sub(r' usado \d{2}-\d{2}_\d{2}h$', '', nombre_actual)
                fecha_hora = datetime.now().strftime("%d-%m_%Hh")
                nuevo_nombre = f"{base_nombre} usado {fecha_hora}"

                # Ruta destino
                carpeta_destino = os.path.join(USADOS_PATH, nuevo_nombre)

                # Mover carpeta
                shutil.move(carpeta_path, carpeta_destino)

                print(f"📦 Carpeta de {cuenta_nombre} movida a '{carpeta_destino}'.")
                movidas += 1

            except Exception as e:
                print(f"❌ Error al mover carpeta de {cuenta_nombre}: {e}")

    print(f"✅ {serial}: {movidas} carpeta(s) movida(s) y renombrada(s).")

def cambiar_a_siguiente_cuenta(serial):
    Width,Height=get_screen_size(serial)
    run, tap, long_tap, move, write, buscarTextoEnRegion, detectarColorOTap = crear_funciones_con_serial(serial)
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
