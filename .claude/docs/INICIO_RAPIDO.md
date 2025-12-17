# 🚀 INICIO RÁPIDO - Proyecto Facebook
## Primeros pasos para empezar HOY

---

## ✅ PRE-REQUISITOS

Antes de empezar, verifica que tienes:
- [x] Sistema TikTok funcionando (ya lo tienes ✓)
- [x] Dispositivos Android con ADB (ya los tienes ✓)
- [x] Python + PyQt5 instalado (ya lo tienes ✓)
- [x] 15 cuentas Facebook desechables (crear antes de Semana 3)
- [x] 50 videos genéricos para publicar (conseguir antes de Semana 3)

---

## 📋 RESUMEN ULTRA-RÁPIDO

**¿Qué harás?**
Copiar el sistema TikTok, simplificarlo, y adaptarlo para Facebook como experimento.

**¿Cuánto código?**
~800 líneas nuevas + 3000 reutilizadas = Total 3800 líneas

**¿Cuánto tiempo?**
5-7 días de desarrollo + 2 semanas de experimento = 3 semanas total

**¿Riesgos?**
Ninguno. TikTok queda intacto, Facebook usa cuentas desechables.

---

## 🎯 DÍA 1: SETUP INICIAL (2-3 horas)

### Paso 1: Crear estructura de carpetas

```bash
cd C:\Users\Cris\Desktop\Automatizacion\ControlDePantallas

# Crear carpeta principal de Facebook
mkdir core\facebook_funcs
cd core\facebook_funcs

# Crear archivos vacíos
type nul > __init__.py
type nul > FacebookVideoPost.py
type nul > experimental_logger.py
type nul > utils_fb.py

# Volver a raíz
cd ..\..

# Crear carpetas de datos
mkdir data\logs_experimento
mkdir data\screenshots_fb
```

### Paso 2: Crear JSON inicial

Crear archivo: `data/dispositivos_facebook.json`

```json
{
  "EJEMPLO_SERIAL": {
    "experimento_id": "FB_EXP_001",
    "grupo_experimental": "A",
    "fecha_inicio": "2025-01-15",

    "cuenta_facebook": {
      "username": "test_cuenta_01",
      "estado": "activa",
      "carpeta_videos": "C:/Users/Cris/Videos/Facebook/Cuenta01",
      "videos_pendientes": ["video1.mp4", "video2.mp4", "video3.mp4"],
      "videos_publicados": []
    },

    "datos_experimentales": {
      "posts_exitosos": 0,
      "posts_fallidos": 0,
      "warnings_recibidos": [],
      "fecha_primer_warning": null,
      "fecha_ban": null,
      "tipo_ban": null,
      "ultimo_post": null
    }
  }
}
```

### Paso 3: Actualizar paths.py

Abrir: `core/paths.py`

Agregar al final:
```python
# Facebook experimental
DISPOSITIVOS_FACEBOOK_FILE = os.path.join(DATA_DIR, "dispositivos_facebook.json")
```

### Paso 4: Crear utils_fb.py

Copiar el contenido básico:

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

print("✅ utils_fb.py cargado")
```

### Paso 5: Verificar que funciona

Abrir Python en la raíz del proyecto:

```python
>>> from core.facebook_funcs.utils_fb import cargar_dispositivos_fb
✅ utils_fb.py cargado

>>> datos = cargar_dispositivos_fb()
>>> print(datos)
{'EJEMPLO_SERIAL': {...}}

>>> # Si llegaste aquí, ¡funciona!
```

**✅ DÍA 1 COMPLETO** - Estructura base lista

---

## 🎯 DÍA 2: LOGGER EXPERIMENTAL (2-3 horas)

### Copiar código del logger

Abrir: `core/facebook_funcs/experimental_logger.py`

Copiar TODO el código de `PLAN_TECNICO_IMPLEMENTACION.md` sección "experimental_logger.py"

(Son ~150 líneas, ya está listo para copiar/pegar)

### Probar el logger

```python
>>> from core.facebook_funcs.experimental_logger import ExperimentalLogger

>>> logger = ExperimentalLogger("TEST_SERIAL")
>>> logger.log_inicio("test")
🚀 [TEST_SERIAL] Iniciando: test

>>> logger.log_step("paso_1")
  ✓ [TEST_SERIAL] paso_1 (0.0s)

>>> logger.log_step("paso_2")
  ✓ [TEST_SERIAL] paso_2 (0.1s)

>>> logger.log_exito("video1.mp4", "Test video")
✅ [TEST_SERIAL] Publicación exitosa: video1.mp4

>>> logger.log_fin()
📝 [TEST_SERIAL] Log guardado: data\logs_experimento\TEST_SERIAL\session_20250115_143022.json
⏱️ [TEST_SERIAL] Duración total: 2.3s
```

Verificar que se creó el archivo JSON:
```bash
dir data\logs_experimento\TEST_SERIAL
```

**✅ DÍA 2 COMPLETO** - Sistema de logging funcional

---

## 🎯 DÍA 3: MAPEAR COORDENADAS DE FACEBOOK (3-4 horas)

### Preparación

1. Conectar 1 dispositivo Android
2. Instalar app de Facebook
3. Login con cuenta de prueba
4. Tener 1 video en la galería

### Capturar pantallas de referencia

```bash
# Verificar que el dispositivo está conectado
adb devices

# Anotar el serial (ejemplo: RF8X20S0C7D)
set SERIAL=RF8X20S0C7D

# Pantalla principal de Facebook
adb -s %SERIAL% shell input keyevent 224
adb -s %SERIAL% shell monkey -p com.facebook.katana -c android.intent.category.LAUNCHER 1
timeout /t 5
adb -s %SERIAL% exec-out screencap -p > fb_pantalla_1_home.png

# Pantalla de crear post (tap manual en "What's on your mind")
# (Hacer tap manualmente en el dispositivo)
timeout /t 3
adb -s %SERIAL% exec-out screencap -p > fb_pantalla_2_crear_post.png

# Pantalla de selección de video
# (Hacer tap manual en "Photo/Video")
timeout /t 3
adb -s %SERIAL% exec-out screencap -p > fb_pantalla_3_seleccionar_video.png

# Pantalla de publicación final
# (Seleccionar video manualmente y esperar)
timeout /t 5
adb -s %SERIAL% exec-out screencap -p > fb_pantalla_4_publicar.png
```

### Abrir imágenes y anotar coordenadas

Usar Paint o cualquier editor para medir coordenadas de:

**Pantalla 1 (Home):**
- Región del cuadro "What's on your mind?"
  - Anotar: `(x1, y1, x2, y2)` en píxeles

**Pantalla 2 (Crear post):**
- Botón "Photo/Video"
- Campo de texto para descripción

**Pantalla 3 (Galería):**
- Primera posición de video en galería
- Botón "Next" o "Done"

**Pantalla 4 (Publicar):**
- Botón "Post" o "Publicar"
- Región donde aparece "Posted" o "Publicado"

### Obtener resolución del dispositivo

```bash
adb -s %SERIAL% shell wm size
# Ejemplo output: Physical size: 1080x2400
```

### Convertir a porcentajes

Si resolución es 1080x2400 y mediste botón en (800, 2100):
```
X% = (800 / 1080) * 100 = 74.07%
Y% = (2100 / 2400) * 100 = 87.5%
```

### Crear archivo de referencia

Crear: `core/facebook_funcs/COORDENADAS.txt`

```
RESOLUCIÓN REFERENCIA: 1080x2400

=== PANTALLA HOME ===
"What's on your mind?" región: (50, 150, 1000, 350)
  → En %: (4.6%, 6.25%, 92.6%, 14.58%)

=== PANTALLA CREAR POST ===
Botón "Photo/Video": (200, 800)
  → En %: (18.5%, 33.3%)

Campo texto descripción: (100, 600)
  → En %: (9.26%, 25%)

=== PANTALLA GALERÍA ===
Primera posición video: (270, 960)
  → En %: (25%, 40%)

Botón "Next": (800, 2150)
  → En %: (74.07%, 89.58%)

=== PANTALLA PUBLICAR ===
Botón "Post": (860, 2200)
  → En %: (79.63%, 91.67%)

Región verificación "Posted": (0, 1800, 1080, 2200)
  → En %: (0%, 75%, 100%, 91.67%)
```

**✅ DÍA 3 COMPLETO** - Coordenadas mapeadas

---

## 🎯 DÍA 4-5: IMPLEMENTAR CORE (6-8 horas)

### Copiar template de FacebookVideoPost.py

Del archivo `PLAN_TECNICO_IMPLEMENTACION.md`, copiar TODO el código de `FacebookVideoPost.py` (son ~400 líneas).

### Ajustar coordenadas

Reemplazar los porcentajes de ejemplo con los que anotaste en DÍA 3.

Ejemplo:
```python
# ANTES (ejemplo):
tap("50%", "15%")

# DESPUÉS (tus coordenadas):
tap("4.6%", "6.25%")  # "What's on your mind?"
```

### Probar función por función

**Prueba 1: Abrir Facebook**
```python
>>> from core.facebook_funcs.FacebookVideoPost import abrir_facebook
>>> abrir_facebook("TU_SERIAL")
# Observar: ¿Se abrió Facebook?
```

**Prueba 2: Ir a crear post**
```python
>>> from core.facebook_funcs.FacebookVideoPost import ir_a_crear_post
>>> ir_a_crear_post("TU_SERIAL")
# Observar: ¿Navegó a pantalla de crear?
```

**Prueba 3: Detectar warnings**
```python
>>> from core.facebook_funcs.FacebookVideoPost import detectar_warnings_facebook
>>> resultado = detectar_warnings_facebook("TU_SERIAL")
>>> print(resultado)  # Debe ser False si no hay warnings
```

### Debugging común

**Si OCR no detecta texto:**
```python
# Probar umbral más bajo
coords = buscarTextoEnRegion(region, "Post", umbral_similitud=0.5)
```

**Si tap no funciona:**
```python
# Verificar que estás usando el serial correcto
# Agregar más tiempo de espera
time.sleep(3)  # en lugar de 1
```

**✅ DÍA 4-5 COMPLETO** - Core funcional

---

## 🎯 DÍA 6: INTEGRAR EN UI (2-3 horas)

### Actualizar main_window.py

**Paso 1:** Agregar importación (línea ~40)
```python
from core.facebook_funcs.FacebookVideoPost import publicar_video_facebook
```

**Paso 2:** Agregar color (en `__init__`, línea ~330)
```python
self.color_accion["facebook_posting"] = "#1877f2"
```

**Paso 3:** Agregar botón (en toolbar, línea ~390)
```python
btn_fb_videos = QPushButton("📘 Publicar Videos FB")
btn_fb_videos.setObjectName("accent")
btn_fb_videos.clicked.connect(self.flujo_facebook_videos)
row1.addWidget(btn_fb_videos)
```

**Paso 4:** Agregar métodos (al final de la clase MainWindow)

Copiar los 3 métodos del `PLAN_TECNICO_IMPLEMENTACION.md`:
- `flujo_facebook_videos()`
- `_start_facebook_worker()`
- `_on_facebook_finished()`
- `_on_facebook_failed()`

### Probar desde UI

1. Ejecutar: `python main.py`
2. Verificar que aparece el botón "📘 Publicar Videos FB"
3. Seleccionar 1 dispositivo
4. Click en el botón
5. Observar que se ejecuta

**✅ DÍA 6 COMPLETO** - Integración UI lista

---

## 🎯 DÍA 7: PRUEBAS END-TO-END (2-4 horas)

### Preparar cuenta de prueba

1. Crear cuenta Facebook nueva (desechable)
2. Login en dispositivo Android
3. Subir 3 videos a la galería del teléfono
4. Actualizar `dispositivos_facebook.json` con el serial real

### Prueba completa 1: Publicación exitosa

```python
python main.py

# En la UI:
1. Seleccionar dispositivo
2. Click "📘 Publicar Videos FB"
3. Observar ejecución
4. Verificar:
   - ✓ Se abrió Facebook
   - ✓ Navegó a crear post
   - ✓ Seleccionó video
   - ✓ Publicó exitosamente
   - ✓ Se guardó log en data/logs_experimento/
   - ✓ Se actualizó dispositivos_facebook.json
```

### Prueba completa 2: Múltiples publicaciones

```python
# Ejecutar 3 veces seguidas (sin esperar)
# Observar si Facebook muestra algún warning
```

### Prueba completa 3: Captura de warning

Si detectaste un warning en Prueba 2:
```python
# Verificar que:
- ✓ Se capturó screenshot en data/screenshots_fb/
- ✓ Se registró en datos_experimentales
- ✓ Sistema continuó (no crasheó)
```

### Checklist final

- [ ] Sistema publica video exitosamente
- [ ] Logs se generan correctamente
- [ ] Screenshots se capturan (si hay warnings)
- [ ] JSON se actualiza
- [ ] UI responde correctamente
- [ ] No hay errores en consola críticos
- [ ] Sistema TikTok sigue funcionando (no lo rompiste)

**✅ DÍA 7 COMPLETO** - Sistema funcional end-to-end

---

## 🎬 SEMANA 2: PILOTO EXPERIMENTAL

### Preparar 3 cuentas

1. Crear 3 cuentas Facebook nuevas
2. Configurar en 3 dispositivos diferentes
3. Actualizar `dispositivos_facebook.json` con los 3 seriales

### Configuración del experimento piloto

```json
{
  "SERIAL_1": {
    "experimento_id": "FB_PILOT_001",
    "grupo_experimental": "bajo",
    "cuenta_facebook": {
      "username": "test_fb_01",
      "carpeta_videos": "C:/Videos/FB/Cuenta01",
      "videos_pendientes": ["video1.mp4", "video2.mp4", "video3.mp4"],
      "configuracion": {
        "frecuencia_diaria": 1
      }
    }
  },
  "SERIAL_2": {
    "grupo_experimental": "medio",
    "configuracion": {
      "frecuencia_diaria": 3
    }
  },
  "SERIAL_3": {
    "grupo_experimental": "alto",
    "configuracion": {
      "frecuencia_diaria": 5
    }
  }
}
```

### Ejecutar durante 7 días

**Plan diario:**
```
Día 1:
  - Device 1: 1 post
  - Device 2: 3 posts
  - Device 3: 5 posts

Días 2-7: Repetir

Total posts al final:
  - Device 1: 7 posts
  - Device 2: 21 posts
  - Device 3: 35 posts
```

### Monitoreo diario

Cada día, revisar:
```bash
# Ver logs del día
dir data\logs_experimento\SERIAL_1

# Ver si hay screenshots (warnings)
dir data\screenshots_fb\

# Ver estado en JSON
type data\dispositivos_facebook.json
```

**✅ SEMANA 2 COMPLETA** - Primeros datos experimentales

---

## 📊 SEMANA 3-4: EXPERIMENTO COMPLETO

### Escalar a 8 cuentas

Configuración final:
- 2 dispositivos Grupo A (1 post/día)
- 3 dispositivos Grupo B (3 posts/día)
- 3 dispositivos Grupo C (5 posts/día)

### Recolección de datos

Al final de 14 días, tendrás:
- Logs de ~200 publicaciones
- Screenshots de todos los warnings
- Timestamps de bans
- Dataset completo en JSON

**✅ SEMANA 3-4 COMPLETAS** - Experimento finalizado

---

## 📝 SEMANA 5: ANÁLISIS

### Extraer datos

Crear script simple:
```python
import json
import os
from datetime import datetime

# Cargar todos los logs
logs_dir = "data/logs_experimento"
todos_logs = []

for serial in os.listdir(logs_dir):
    serial_dir = os.path.join(logs_dir, serial)
    for log_file in os.listdir(serial_dir):
        with open(os.path.join(serial_dir, log_file)) as f:
            todos_logs.append(json.load(f))

# Análisis básico
exitosos = [l for l in todos_logs if l["resultado"] == "EXITO"]
warnings = [l for l in todos_logs if l["resultado"] == "WARNING_DETECTADO"]
bans = [l for l in todos_logs if l["resultado"] == "BAN_DETECTADO"]

print(f"Total publicaciones: {len(todos_logs)}")
print(f"Exitosas: {len(exitosos)} ({len(exitosos)/len(todos_logs)*100:.1f}%)")
print(f"Warnings: {len(warnings)} ({len(warnings)/len(todos_logs)*100:.1f}%)")
print(f"Bans: {len(bans)} ({len(bans)/len(todos_logs)*100:.1f}%)")

# Tiempo promedio hasta primer ban
# ...más análisis
```

### Crear gráficas

Usar matplotlib:
```python
import matplotlib.pyplot as plt

# Gráfica de éxito vs tiempo
# Gráfica de bans por grupo experimental
# etc.
```

### Escribir reporte

Usar plantilla de `PROPUESTA_EXPERIMENTO_FACEBOOK.md` sección de resultados.

**✅ SEMANA 5 COMPLETA** - Reporte final

---

## 🆘 SOLUCIÓN DE PROBLEMAS COMUNES

### Problema: OCR no detecta texto

**Solución:**
```python
# 1. Verificar que Tesseract está instalado
import pytesseract
print(pytesseract.get_tesseract_version())

# 2. Capturar pantalla y verificar manualmente
adb -s SERIAL exec-out screencap -p > test.png
# Abrir test.png y leer el texto tú mismo

# 3. Probar OCR con umbral más bajo
coords = buscarTextoEnRegion(region, "texto", umbral_similitud=0.5)

# 4. Probar con región más grande
region = ("0%", "0%", "100%", "100%")  # pantalla completa
```

### Problema: Tap no funciona

**Solución:**
```python
# 1. Verificar resolución
adb -s SERIAL shell wm size

# 2. Probar tap manual con coordenadas fijas
adb -s SERIAL shell input tap 540 1200

# 3. Agregar más tiempo de espera
time.sleep(3)  # antes de tap

# 4. Usar long_tap en vez de tap
long_tap("50%", "50%")
```

### Problema: App no abre

**Solución:**
```bash
# 1. Verificar que Facebook está instalado
adb -s SERIAL shell pm list packages | findstr facebook

# 2. Obtener nombre correcto del paquete
adb -s SERIAL shell pm list packages -3

# 3. Si el paquete es diferente, actualizar código:
run("shell monkey -p com.facebook.katana ...")
# Cambiar por el paquete correcto
```

### Problema: JSON corrupto

**Solución:**
```python
# Validar JSON online: https://jsonlint.com/
# O usar Python:
import json

with open("data/dispositivos_facebook.json") as f:
    try:
        data = json.load(f)
        print("✅ JSON válido")
    except json.JSONDecodeError as e:
        print(f"❌ JSON corrupto: {e}")
```

---

## 📞 CONTACTO Y AYUDA

Si te atascas:
1. Revisar `PLAN_TECNICO_IMPLEMENTACION.md` (detalle técnico)
2. Revisar `COMPARACION_VISUAL_TIKTOK_VS_FACEBOOK.md` (referencia)
3. Consultar código de TikTok (muchas funciones son iguales)

---

## 🎯 CHECKLIST COMPLETO

### Desarrollo (Semana 1):
- [ ] Día 1: Setup inicial
- [ ] Día 2: Logger experimental
- [ ] Día 3: Mapear coordenadas
- [ ] Día 4-5: Implementar core
- [ ] Día 6: Integrar UI
- [ ] Día 7: Pruebas end-to-end

### Experimentación (Semana 2-4):
- [ ] Crear 8 cuentas Facebook
- [ ] Preparar 50 videos
- [ ] Configurar 8 dispositivos
- [ ] Ejecutar 14 días continuos
- [ ] Monitoreo diario

### Análisis (Semana 5):
- [ ] Extraer datos de logs
- [ ] Análisis estadístico
- [ ] Crear gráficas
- [ ] Escribir reporte

---

**¡LISTO PARA EMPEZAR!**

Comienza con DÍA 1 hoy mismo. En 1 semana tendrás el sistema funcional. 🚀
