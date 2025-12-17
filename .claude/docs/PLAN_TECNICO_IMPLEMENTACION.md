# 🔧 PLAN TÉCNICO DE IMPLEMENTACIÓN
## Sistema Facebook - Enfoque Experimental

---

## 🎯 FILOSOFÍA DEL PROYECTO

**Diferencia clave con TikTok:**
- **TikTok:** Optimizado para evasión → producción sostenible
- **Facebook:** Optimizado para experimentación → recolección de datos

**Objetivo:** Replicar la arquitectura de TikTok SIN anti-detección avanzada, para medir la respuesta de Facebook.

---

## 📦 QUÉ REUTILIZAMOS (70% del código)

### ✅ Infraestructura Base (100% reutilizable)

```python
# Archivos que NO necesitan cambios:
core/
├── config.py                    # ✅ Configuración global
├── paths.py                     # ✅ Rutas del sistema
├── scrcpy_manager.py            # ✅ Control de pantallas
└── adb_utils.py                 # ✅ Funciones ADB base
    ├── get_screen_size()
    ├── parse_coord()
    ├── crear_funciones_con_serial()
    ├── procesar_celular()
    └── modificar_fechas_en_orden()
```

**Justificación:** Estas funciones son agnósticas a la plataforma.

---

### ✅ Sistema de Control (100% reutilizable)

```python
# Control de threads y detención
from core.config import hilos_activos

def should_stop(serial: str) -> bool:
    return not hilos_activos.get(serial, True)

def _sleep(serial: str, segundos: float):
    # Sleep cooperativo que respeta detención
    fin = time.time() + max(0.0, segundos)
    while time.time() < fin:
        if should_stop(serial):
            return
        time.sleep(0.1)
```

**Justificación:** El sistema de detención es universal.

---

### ✅ UI Base (90% reutilizable)

```python
# ui/main_window.py - Reutilizar estructura:

# Workers genéricos (ya existen)
class GenericWorker(QObject):          # ✅ Reutilizar
class ScanWorker(QObject):             # 🔄 Adaptar para FB
class ChangeWorker(QObject):           # 🔄 Adaptar para FB

# Sistema de indicadores visuales
self.status_buttons[serial]            # ✅ Reutilizar
self._set_estado_visual()              # ✅ Reutilizar
self._start_pulse() / _stop_pulse()    # ✅ Reutilizar

# Gestión de checkboxes
self.checkboxes[serial]                # ✅ Reutilizar
self.is_selected()                     # ✅ Reutilizar
```

**Cambios necesarios:**
```python
# Agregar botones nuevos para Facebook
btn_fb_videos = QPushButton("📘 Publicar Videos FB")
btn_fb_videos.clicked.connect(self.flujo_facebook_videos)

# Nuevo color para estado "facebook_posting"
self.color_accion["facebook_posting"] = "#1877f2"  # Azul FB
```

---

### ✅ Funciones Auxiliares (100% reutilizable)

```python
# De utils.py - Reutilizar directamente:

silenciar_dispositivo(serial)          # ✅ Universal
ejecteg(serial)                        # ✅ Universal (botón back)
cerrary_salir(serial)                  # ✅ Universal (cerrar apps)
get_screen_size(serial)                # ✅ Universal
should_stop(serial)                    # ✅ Universal

# De adb_utils.py:
crear_funciones_con_serial(serial)     # ✅ Universal
# Retorna: run, tap, long_tap, move, write,
#          buscarTextoEnRegion, detectarColorOTap, leerTextoEnRegion
```

---

## 🆕 QUÉ CREAMOS NUEVO (30% del código)

### 1. Estructura de Carpetas Nueva

```
core/
└── facebook_funcs/                    # 🆕 Nuevo módulo
    ├── __init__.py
    ├── FacebookVideoPost.py           # Core de publicación
    ├── FacebookCuentaScan.py          # Detección de cuentas
    ├── cambiarCuentasFB.py            # Cambio entre cuentas (si aplica)
    ├── utils_fb.py                    # Utilidades específicas FB
    └── experimental_logger.py         # 🔬 Sistema de logging experimental

data/
└── dispositivos_facebook.json         # 🆕 Datos separados de TikTok
```

---

### 2. Sistema de Datos (JSON) - Estructura Nueva

```json
{
  "SERIAL_DISPOSITIVO": {
    "experimento_id": "FB_EXP_001",
    "fecha_inicio": "2025-01-15",
    "grupo_experimental": "A",  // A=bajo, B=medio, C=agresivo

    "cuenta_facebook": {
      "username": "test_cuenta_01",
      "estado": "activa",  // activa, warning, banned, shadowban
      "fecha_creacion": "2025-01-10",
      "dias_warm_up": 0,

      "carpeta_videos": "C:/Videos/Facebook/Cuenta01",
      "videos_pendientes": ["video1.mp4", "video2.mp4"],
      "videos_publicados": ["video3.mp4"],

      "configuracion": {
        "frecuencia_diaria": 3,  // posts por día
        "horarios": ["10:00", "15:00", "20:00"],
        "descripcion_template": "Video #{numero}"
      }
    },

    "datos_experimentales": {
      "posts_exitosos": 5,
      "posts_fallidos": 0,
      "warnings_recibidos": [],
      "fecha_primer_warning": null,
      "fecha_ban": null,
      "tipo_ban": null,  // temporal, permanente, shadowban
      "alcance_promedio": 0,
      "ultimo_post": "2025-01-15 14:30:00"
    }
  }
}
```

---

### 3. FacebookVideoPost.py - Core del Experimento

```python
# core/facebook_funcs/FacebookVideoPost.py

import time
from datetime import datetime
from core.adb_utils import crear_funciones_con_serial, get_screen_size
from .utils_fb import should_stop_fb, cargar_dispositivos_fb
from .experimental_logger import ExperimentalLogger

def publicar_video_facebook(serial: str):
    """
    Publica 1 video en Facebook - Versión EXPERIMENTAL
    NO intenta evadir detección - objetivo es medir respuesta
    """
    logger = ExperimentalLogger(serial)
    run, tap, long_tap, move, write, buscarTextoEnRegion, detectarColorOTap, leerTextoEnRegion = crear_funciones_con_serial(serial)

    logger.log_inicio("publicar_video")

    try:
        # 1. ABRIR FACEBOOK
        logger.log_step("abrir_app")
        abrir_facebook(serial)
        if should_stop_fb(serial):
            return logger.log_detenido("después de abrir app")

        # 2. VERIFICAR WARNINGS/BANS
        logger.log_step("check_warnings")
        if detectar_warnings_facebook(serial):
            return logger.log_ban_detectado()

        # 3. IR A CREAR PUBLICACIÓN
        logger.log_step("navegar_crear_post")
        if not ir_a_crear_post(serial):
            return logger.log_error("No se pudo navegar a crear post")

        # 4. SELECCIONAR VIDEO
        logger.log_step("seleccionar_video")
        video_path = obtener_siguiente_video(serial)
        if not seleccionar_video_galeria(serial, video_path):
            return logger.log_error("No se pudo seleccionar video")

        # 5. ESPERAR PROCESAMIENTO
        logger.log_step("esperar_procesamiento")
        if not esperar_procesamiento_video(serial):
            return logger.log_error("Video no procesó correctamente")

        # 6. AGREGAR DESCRIPCIÓN (opcional)
        logger.log_step("agregar_descripcion")
        descripcion = generar_descripcion_simple(serial)
        escribir_descripcion(serial, descripcion)

        # 7. PUBLICAR
        logger.log_step("tap_publicar")
        tap_boton_publicar(serial)

        # 8. VERIFICAR ÉXITO
        logger.log_step("verificar_publicacion")
        if verificar_publicacion_exitosa(serial):
            logger.log_exito(video_path, descripcion)
            actualizar_datos_experimentales(serial, "exito", video_path)
            return True
        else:
            logger.log_error("No se confirmó publicación")
            actualizar_datos_experimentales(serial, "fallo", video_path)
            return False

    except Exception as e:
        logger.log_excepcion(e)
        return False
    finally:
        logger.log_fin()


# ========== FUNCIONES AUXILIARES ==========

def abrir_facebook(serial: str):
    """Abre la app de Facebook"""
    run, _, _, move, _, _, _, _ = crear_funciones_con_serial(serial)

    # Encender y desbloquear
    run("shell input keyevent 224")
    time.sleep(0.5)
    move("50%", "68%", "50%", "20%")
    time.sleep(0.5)

    # Lanzar Facebook
    run("shell monkey -p com.facebook.katana -c android.intent.category.LAUNCHER 1")
    time.sleep(5)  # Esperar a que abra


def detectar_warnings_facebook(serial: str) -> bool:
    """
    Detecta si Facebook muestra algún warning/ban
    CRÍTICO: Estos mensajes son DATOS VALIOSOS
    """
    _, _, _, _, _, buscarTextoEnRegion, _, _ = crear_funciones_con_serial(serial)
    logger = ExperimentalLogger(serial)

    TEXTOS_WARNING = [
        "suspicious activity",
        "automated behavior",
        "verify your identity",
        "unusual activity",
        "security check",
        "temporarily blocked",
        "against our community standards",
        "spam"
    ]

    region_completa = ("0%", "0%", "100%", "100%")

    for texto in TEXTOS_WARNING:
        if buscarTextoEnRegion(region_completa, texto, umbral_similitud=0.6):
            # ⭐ ESTO ES ORO - Capturar screenshot
            logger.log_warning_detectado(texto)
            capturar_screenshot_warning(serial, texto)
            actualizar_estado_cuenta(serial, "warning", texto)
            return True

    return False


def ir_a_crear_post(serial: str) -> bool:
    """
    Navega a la pantalla de crear publicación
    """
    _, tap, _, _, _, buscarTextoEnRegion, _, _ = crear_funciones_con_serial(serial)

    # Buscar "What's on your mind?" o equivalente
    textos_buscar = [
        "What's on your mind",
        "¿Qué estás pensando",
        "Write something",
        "Escribe algo"
    ]

    region_superior = ("5%", "5%", "95%", "30%")

    for texto in textos_buscar:
        coords = buscarTextoEnRegion(region_superior, texto, umbral_similitud=0.6)
        if coords:
            tap(*coords)
            time.sleep(2)
            return True

    # Fallback: tap en zona típica
    tap("50%", "15%")
    time.sleep(2)
    return True


def seleccionar_video_galeria(serial: str, video_filename: str) -> bool:
    """
    Selecciona video desde la galería
    """
    _, tap, _, _, _, buscarTextoEnRegion, _, _ = crear_funciones_con_serial(serial)

    # 1. Buscar botón "Photo/Video"
    textos_boton = ["Photo", "Video", "Foto", "Vídeo"]
    region_opciones = ("0%", "20%", "100%", "50%")

    for texto in textos_boton:
        coords = buscarTextoEnRegion(region_opciones, texto, umbral_similitud=0.7)
        if coords:
            tap(*coords)
            time.sleep(2)
            break
    else:
        # Fallback
        tap("20%", "35%")
        time.sleep(2)

    # 2. Tap en galería
    tap("20%", "50%")  # Zona típica de galería
    time.sleep(2)

    # 3. Seleccionar primer video (simplificado)
    # TODO: Buscar el video específico por nombre
    tap("25%", "40%")  # Primera posición típica
    time.sleep(1)

    # 4. Confirmar selección
    coords = buscarTextoEnRegion(("60%", "80%", "100%", "100%"), "Next")
    if coords:
        tap(*coords)
    else:
        tap("80%", "90%")  # Fallback zona botón Next

    time.sleep(3)
    return True


def esperar_procesamiento_video(serial: str, timeout: int = 60) -> bool:
    """
    Espera a que Facebook procese el video
    """
    _, _, _, _, _, buscarTextoEnRegion, _, _ = crear_funciones_con_serial(serial)

    tiempo_inicio = time.time()
    region_central = ("20%", "30%", "80%", "70%")

    while (time.time() - tiempo_inicio) < timeout:
        if should_stop_fb(serial):
            return False

        # Buscar indicador de procesamiento
        if buscarTextoEnRegion(region_central, "Processing", umbral_similitud=0.6):
            time.sleep(2)
            continue

        # Si ya no dice "Processing", asumimos que terminó
        time.sleep(2)
        return True

    return False  # Timeout


def escribir_descripcion(serial: str, texto: str):
    """
    Escribe descripción del post
    """
    _, tap, _, _, write, _, _, _ = crear_funciones_con_serial(serial)

    # Tap en campo de texto
    tap("50%", "25%")
    time.sleep(1)

    # Escribir
    write(texto)
    time.sleep(0.5)


def tap_boton_publicar(serial: str):
    """
    Toca el botón de publicar
    """
    _, tap, _, _, _, buscarTextoEnRegion, _, _ = crear_funciones_con_serial(serial)

    textos_publicar = ["Post", "Publicar", "Share", "Compartir"]
    region_boton = ("60%", "80%", "100%", "100%")

    for texto in textos_publicar:
        coords = buscarTextoEnRegion(region_boton, texto, umbral_similitud=0.7)
        if coords:
            tap(*coords)
            time.sleep(3)
            return

    # Fallback
    tap("80%", "92%")
    time.sleep(3)


def verificar_publicacion_exitosa(serial: str, timeout: int = 30) -> bool:
    """
    Verifica si la publicación fue exitosa
    """
    _, _, _, _, _, buscarTextoEnRegion, _, _ = crear_funciones_con_serial(serial)

    tiempo_inicio = time.time()
    region_completa = ("0%", "0%", "100%", "100%")

    textos_exito = [
        "Posted",
        "Publicado",
        "Your post is now live",
        "View post"
    ]

    while (time.time() - tiempo_inicio) < timeout:
        if should_stop_fb(serial):
            return False

        for texto in textos_exito:
            if buscarTextoEnRegion(region_completa, texto, umbral_similitud=0.6):
                return True

        time.sleep(1)

    return False


# ========== FUNCIONES DE DATOS ==========

def obtener_siguiente_video(serial: str) -> str:
    """Obtiene el siguiente video a publicar"""
    datos = cargar_dispositivos_fb()
    cuenta = datos[serial]["cuenta_facebook"]

    if cuenta["videos_pendientes"]:
        return cuenta["videos_pendientes"][0]
    else:
        raise Exception("No hay videos pendientes")


def generar_descripcion_simple(serial: str) -> str:
    """Genera descripción simple para el post"""
    datos = cargar_dispositivos_fb()
    cuenta = datos[serial]["cuenta_facebook"]

    num_posts = len(cuenta["videos_publicados"]) + 1
    template = cuenta["configuracion"].get("descripcion_template", "Video #{numero}")

    return template.replace("{numero}", str(num_posts))


def actualizar_datos_experimentales(serial: str, resultado: str, video: str):
    """
    Actualiza los datos experimentales después de cada intento
    ⭐ CRÍTICO: Estos datos son el objetivo del experimento
    """
    import json
    from core.paths import DISPOSITIVOS_FACEBOOK_FILE

    with open(DISPOSITIVOS_FACEBOOK_FILE, 'r') as f:
        datos = json.load(f)

    cuenta = datos[serial]["cuenta_facebook"]
    exp = datos[serial]["datos_experimentales"]

    if resultado == "exito":
        exp["posts_exitosos"] += 1
        cuenta["videos_pendientes"].remove(video)
        cuenta["videos_publicados"].append(video)
    elif resultado == "fallo":
        exp["posts_fallidos"] += 1

    exp["ultimo_post"] = datetime.now().isoformat()

    with open(DISPOSITIVOS_FACEBOOK_FILE, 'w') as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)


def actualizar_estado_cuenta(serial: str, nuevo_estado: str, mensaje: str = None):
    """
    Actualiza el estado de la cuenta (activa, warning, banned)
    """
    import json
    from core.paths import DISPOSITIVOS_FACEBOOK_FILE

    with open(DISPOSITIVOS_FACEBOOK_FILE, 'r') as f:
        datos = json.load(f)

    cuenta = datos[serial]["cuenta_facebook"]
    exp = datos[serial]["datos_experimentales"]

    cuenta["estado"] = nuevo_estado

    if nuevo_estado == "warning":
        if not exp["fecha_primer_warning"]:
            exp["fecha_primer_warning"] = datetime.now().isoformat()
        exp["warnings_recibidos"].append({
            "fecha": datetime.now().isoformat(),
            "mensaje": mensaje
        })
    elif nuevo_estado == "banned":
        exp["fecha_ban"] = datetime.now().isoformat()
        exp["tipo_ban"] = determinar_tipo_ban(mensaje)

    with open(DISPOSITIVOS_FACEBOOK_FILE, 'w') as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)


def determinar_tipo_ban(mensaje: str) -> str:
    """Intenta determinar el tipo de ban basado en el mensaje"""
    if not mensaje:
        return "desconocido"

    mensaje_lower = mensaje.lower()

    if "temporarily" in mensaje_lower or "temporal" in mensaje_lower:
        return "temporal"
    elif "permanently" in mensaje_lower or "permanente" in mensaje_lower:
        return "permanente"
    elif "shadowban" in mensaje_lower:
        return "shadowban"
    else:
        return "desconocido"


def capturar_screenshot_warning(serial: str, tipo_warning: str):
    """
    Captura screenshot cuando se detecta un warning
    ⭐ EVIDENCIA VISUAL del experimento
    """
    import subprocess
    import os
    from core.paths import ADB_PATH
    from datetime import datetime

    # Crear carpeta de screenshots si no existe
    screenshots_dir = f"data/screenshots_fb/{serial}"
    os.makedirs(screenshots_dir, exist_ok=True)

    # Nombre del archivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{screenshots_dir}/warning_{tipo_warning.replace(' ', '_')}_{timestamp}.png"

    # Capturar
    resultado = subprocess.run(
        [ADB_PATH, "-s", serial, "exec-out", "screencap", "-p"],
        capture_output=True
    )

    with open(filename, 'wb') as f:
        f.write(resultado.stdout)

    print(f"📸 Screenshot capturado: {filename}")
```

---

### 4. experimental_logger.py - Sistema de Logging

```python
# core/facebook_funcs/experimental_logger.py

import json
import os
from datetime import datetime
from pathlib import Path

class ExperimentalLogger:
    """
    Sistema de logging específico para el experimento
    Registra cada acción con timestamps precisos
    """

    def __init__(self, serial: str):
        self.serial = serial
        self.log_dir = Path(f"data/logs_experimento/{serial}")
        self.log_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"session_{timestamp}.json"

        self.session_data = {
            "serial": serial,
            "inicio": datetime.now().isoformat(),
            "pasos": [],
            "resultado": None,
            "duracion_total": None
        }

        self.tiempo_inicio = datetime.now()

    def log_inicio(self, accion: str):
        print(f"🚀 [{self.serial}] Iniciando: {accion}")
        self.session_data["accion"] = accion

    def log_step(self, paso: str):
        timestamp = datetime.now()
        duracion = (timestamp - self.tiempo_inicio).total_seconds()

        self.session_data["pasos"].append({
            "paso": paso,
            "timestamp": timestamp.isoformat(),
            "segundos_desde_inicio": duracion
        })

        print(f"  ✓ [{self.serial}] {paso} ({duracion:.1f}s)")

    def log_exito(self, video: str, descripcion: str):
        self.session_data["resultado"] = "EXITO"
        self.session_data["video_publicado"] = video
        self.session_data["descripcion"] = descripcion
        print(f"✅ [{self.serial}] Publicación exitosa: {video}")

    def log_error(self, mensaje: str):
        self.session_data["resultado"] = "ERROR"
        self.session_data["error"] = mensaje
        print(f"❌ [{self.serial}] Error: {mensaje}")

    def log_warning_detectado(self, tipo_warning: str):
        self.session_data["resultado"] = "WARNING_DETECTADO"
        self.session_data["tipo_warning"] = tipo_warning
        print(f"⚠️ [{self.serial}] WARNING DETECTADO: {tipo_warning}")

    def log_ban_detectado(self):
        self.session_data["resultado"] = "BAN_DETECTADO"
        print(f"🚫 [{self.serial}] BAN DETECTADO")
        return False

    def log_detenido(self, contexto: str):
        self.session_data["resultado"] = "DETENIDO"
        self.session_data["contexto_detencion"] = contexto
        print(f"⏹ [{self.serial}] Detenido: {contexto}")
        return False

    def log_excepcion(self, e: Exception):
        self.session_data["resultado"] = "EXCEPCION"
        self.session_data["excepcion"] = str(e)
        print(f"💥 [{self.serial}] Excepción: {e}")

    def log_fin(self):
        duracion = (datetime.now() - self.tiempo_inicio).total_seconds()
        self.session_data["fin"] = datetime.now().isoformat()
        self.session_data["duracion_total"] = duracion

        # Guardar log
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.session_data, f, indent=2, ensure_ascii=False)

        print(f"📝 [{self.serial}] Log guardado: {self.log_file}")
        print(f"⏱️ [{self.serial}] Duración total: {duracion:.1f}s")
```

---

### 5. utils_fb.py - Utilidades Facebook

```python
# core/facebook_funcs/utils_fb.py

import json
import os
from core.config import hilos_activos
from core.paths import DISPOSITIVOS_FACEBOOK_FILE

def should_stop_fb(serial: str) -> bool:
    """Control de detención para Facebook"""
    return not hilos_activos.get(serial, True)

def cargar_dispositivos_fb():
    """Carga datos de dispositivos Facebook"""
    if os.path.exists(DISPOSITIVOS_FACEBOOK_FILE):
        with open(DISPOSITIVOS_FACEBOOK_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def guardar_dispositivos_fb(datos):
    """Guarda datos de dispositivos Facebook"""
    with open(DISPOSITIVOS_FACEBOOK_FILE, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)
```

---

### 6. core/paths.py - Agregar ruta nueva

```python
# Agregar al archivo existente:
DISPOSITIVOS_FACEBOOK_FILE = os.path.join(DATA_DIR, "dispositivos_facebook.json")
```

---

## 🔄 ADAPTACIONES EN UI

### ui/main_window.py - Cambios mínimos

```python
# ========== AGREGAR AL TOOLBAR (alrededor línea 370) ==========

# Botón nuevo para Facebook
btn_fb_videos = QPushButton("📘 Subir Videos FB")
btn_fb_videos.setObjectName("accent")
btn_fb_videos.clicked.connect(self.flujo_facebook_videos)

# Agregar al layout
row1.addWidget(btn_fb_videos)


# ========== AGREGAR MÉTODOS NUEVOS (al final de la clase) ==========

def flujo_facebook_videos(self):
    """
    Flujo para publicar videos en Facebook
    Similar a flujo_cuentas_video pero más simple (sin detección de cuentas)
    """
    seleccionados = [s for s in self.seriales if self.is_selected(s)]
    if not seleccionados:
        QMessageBox.warning(
            self,
            "Dispositivos no seleccionados",
            "⚠ No hay dispositivos seleccionados.\nPor favor, selecciona al menos uno."
        )
        return

    # Lanzar worker para cada dispositivo
    for serial in seleccionados:
        self._start_facebook_worker(serial)

    self.limpiar_checkboxes_checkbox_global()


def _start_facebook_worker(self, serial: str):
    """Lanza worker para publicación en Facebook"""
    from core.facebook_funcs.FacebookVideoPost import publicar_video_facebook

    self.estado_dispositivos[serial] = "facebook_posting"
    self._set_estado_visual(serial, "facebook_posting")
    hilos_activos[serial] = True

    th = QThread(self)
    worker = GenericWorker(serial, publicar_video_facebook)
    worker.moveToThread(th)

    th.started.connect(worker.run)
    worker.finished.connect(lambda s=serial: self._on_facebook_finished(s))
    worker.failed.connect(lambda s=serial, err="": self._on_facebook_failed(s, err))

    worker.finished.connect(th.quit)
    worker.failed.connect(th.quit)
    th.finished.connect(th.deleteLater)

    self._generic_threads[serial] = th
    self._generic_workers[serial] = worker
    th.start()


def _on_facebook_finished(self, serial: str):
    """Callback cuando termina publicación en Facebook"""
    print(f"✅ Publicación FB terminada en {serial}")
    self.estado_dispositivos[serial] = None
    self._set_estado_visual(serial, None)
    self._generic_workers.pop(serial, None)
    self._generic_threads.pop(serial, None)
    self.mostrar_mensaje_finalizado("Facebook", f"Publicación en {serial}")


def _on_facebook_failed(self, serial: str, err: str):
    """Callback cuando falla publicación en Facebook"""
    print(f"💥 Error FB en {serial}: {err}")
    self.estado_dispositivos[serial] = None
    self._set_estado_visual(serial, None)
    self._generic_workers.pop(serial, None)
    self._generic_threads.pop(serial, None)

    # Si fue un ban, mostrar mensaje especial
    if "warning" in err.lower() or "ban" in err.lower():
        QMessageBox.warning(
            self,
            "⚠️ Cuenta Detectada",
            f"Facebook detectó automatización en {serial}.\n\n"
            f"Esto es parte del experimento - los datos han sido registrados.\n\n"
            f"Error: {err}"
        )


# ========== AGREGAR COLOR NUEVO (en __init__, alrededor línea 330) ==========

self.color_accion["facebook_posting"] = "#1877f2"  # Azul oficial de Facebook
```

---

## 📊 DIFERENCIAS CLAVE CON TIKTOK

| Aspecto | TikTok (Actual) | Facebook (Nuevo) | Justificación |
|---------|-----------------|------------------|---------------|
| **Anti-detección** | ✅ Implementada | ❌ NO implementada | FB es experimento, no producción |
| **Warm-up** | Opcional | ❌ NO (experimental) | Queremos medir detección rápida |
| **Múltiples cuentas** | ✅ Sí (cambio automático) | ❌ 1 cuenta por device | Simplificar experimento |
| **Randomización** | ✅ Sí | ❌ NO necesaria | Patrones predecibles = más datos |
| **Logging** | Básico | ⭐ EXHAUSTIVO | Capturar todo para análisis |
| **Screenshots** | No | ⭐ SÍ (en warnings) | Evidencia visual |
| **Frecuencia** | Alta (sin límite) | ⚡ Controlada (1-5/día) | Variable experimental |
| **Objetivo** | Producción sostenible | 🔬 Recolección de datos | Distinto propósito |

---

## ⚡ SIMPLIFICACIONES INTENCIONALES

### ❌ NO implementaremos (a diferencia de TikTok):

1. **Sistema de asignación dinámica de carpetas**
   - TikTok: Asigna carpetas automáticamente a cuentas detectadas
   - Facebook: 1 cuenta fija por dispositivo (pre-configurada)

2. **Cambio automático entre cuentas**
   - TikTok: `cambiarCuentas.py` - switcher complejo
   - Facebook: NO necesario - 1 cuenta por experimento

3. **Detección multi-scroll de cuentas**
   - TikTok: Scrollea para encontrar todas las cuentas
   - Facebook: NO aplica - cuenta única

4. **Sistema de "cuentas por subir" vs "subidas"**
   - TikTok: Tracking complejo de estado
   - Facebook: Lista simple de videos pendientes

5. **Gestos de "entrenar" o warm-up**
   - TikTok: `entrenar.py` - simula comportamiento humano
   - Facebook: NO - queremos ser detectados

**Por qué simplificamos:** Objetivo es MEDIR detección, no evadirla.

---

## 🎯 RESUMEN DE IMPLEMENTACIÓN

### Timeline Real:

**Día 1-2:**
- Copiar estructura de `tiktok_funcs/` → `facebook_funcs/`
- Crear `FacebookVideoPost.py` (400 líneas aprox)
- Crear `experimental_logger.py` (150 líneas aprox)
- Crear `utils_fb.py` (50 líneas aprox)

**Día 3-4:**
- Mapear coordenadas de Facebook (abrir app en emulador/device)
- Probar flujo manualmente paso por paso
- Ajustar regiones de OCR

**Día 5:**
- Integrar en UI (`main_window.py` - 3 métodos nuevos)
- Crear JSON inicial de configuración
- Prueba end-to-end con 1 dispositivo

**Total: ~800 líneas de código nuevo** (vs ~3000 líneas reutilizadas)

**Ratio: 73% reutilizado, 27% nuevo** ✅

---

## 🔧 HERRAMIENTAS DE DESARROLLO

### Para mapear coordenadas:
```bash
# Capturar pantalla y anotar coordenadas
adb -s SERIAL exec-out screencap -p > fb_screen.png

# Ver resolución
adb -s SERIAL shell wm size
```

### Para debugging OCR:
```python
# Probar detección de texto
from PIL import Image
import pytesseract

img = Image.open("fb_screen.png")
texto = pytesseract.image_to_string(img)
print(texto)
```

### Para ver logs en tiempo real:
```bash
# Terminal separada
tail -f data/logs_experimento/SERIAL/session_TIMESTAMP.json
```

---

## ✅ CHECKLIST DE IMPLEMENTACIÓN

### Fase 1: Setup (Día 1)
- [ ] Crear carpeta `core/facebook_funcs/`
- [ ] Crear `__init__.py`
- [ ] Copiar `utils.py` → `utils_fb.py` y simplificar
- [ ] Crear `experimental_logger.py`
- [ ] Agregar `DISPOSITIVOS_FACEBOOK_FILE` a `paths.py`

### Fase 2: Core (Día 2-3)
- [ ] Implementar `abrir_facebook()`
- [ ] Implementar `detectar_warnings_facebook()`
- [ ] Implementar `ir_a_crear_post()`
- [ ] Implementar `seleccionar_video_galeria()`
- [ ] Implementar `esperar_procesamiento_video()`
- [ ] Implementar `tap_boton_publicar()`
- [ ] Implementar `verificar_publicacion_exitosa()`

### Fase 3: Datos (Día 3-4)
- [ ] Implementar `obtener_siguiente_video()`
- [ ] Implementar `actualizar_datos_experimentales()`
- [ ] Implementar `actualizar_estado_cuenta()`
- [ ] Implementar `capturar_screenshot_warning()`
- [ ] Crear JSON inicial de prueba

### Fase 4: Integración (Día 4-5)
- [ ] Agregar botón en UI
- [ ] Implementar `flujo_facebook_videos()`
- [ ] Implementar `_start_facebook_worker()`
- [ ] Implementar callbacks de éxito/error
- [ ] Agregar color a `color_accion`

### Fase 5: Testing (Día 5-7)
- [ ] Prueba manual paso por paso
- [ ] Ajustar coordenadas por resolución
- [ ] Validar OCR con diferentes textos
- [ ] Prueba end-to-end completa
- [ ] Verificar logs se generan correctamente
- [ ] Verificar screenshots se capturan

---

**Código total estimado:** ~800 líneas nuevas + 3000 reutilizadas = **3800 líneas**

**Tiempo estimado:** 5-7 días de desarrollo activo

**Complejidad:** MEDIA (mucho más simple que el sistema TikTok porque no necesita evasión)
