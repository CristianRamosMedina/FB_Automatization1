# ⚡ TAREAS PARALELAS - Proyecto Facebook
## División de trabajo para 2-4 personas trabajando simultáneamente

---

## 🎯 OBJETIVO

Completar el proyecto Facebook en **5 días** trabajando en paralelo.

**Equipo ideal:** 2-3 personas
**Timeline:** 5 días (en vez de 10 días secuenciales)

---

## 👥 ROLES Y ASIGNACIÓN

### 🔵 PERSONA A: "Tester del sistema TikTok"
**Prerrequisito:** Ninguno
**Duración:** Día 1 completo (puede empezar YA)
**Objetivo:** Entender cómo funciona el sistema actual probándolo

### 🟢 PERSONA B: "Mapeador de Facebook"
**Prerrequisito:** Ninguno
**Duración:** Día 1-2
**Objetivo:** Mapear todas las coordenadas de Facebook

### 🟡 PERSONA C: "Desarrollador core"
**Prerrequisito:** Esperar a que A termine Día 1
**Duración:** Día 2-3
**Objetivo:** Copiar y adaptar el código

### 🟠 PERSONA D (opcional): "Preparador de datos"
**Prerrequisito:** Ninguno
**Duración:** Día 1-5 (asíncrono)
**Objetivo:** Crear cuentas FB, conseguir videos, preparar experimento

---

## 📅 TIMELINE PARALELO

```
DÍA 1:
├─ 🔵 PERSONA A: Probar sistema TikTok [6-8h]
├─ 🟢 PERSONA B: Mapear Facebook (Parte 1) [6-8h]
└─ 🟠 PERSONA D: Crear cuentas FB [2-3h]

DÍA 2:
├─ 🟢 PERSONA B: Mapear Facebook (Parte 2) [4-6h]
├─ 🟡 PERSONA C: Copiar código + adaptar [6-8h]
└─ 🟠 PERSONA D: Conseguir videos [2-3h]

DÍA 3:
├─ 🟡 PERSONA C: Integrar en UI [4-6h]
├─ 🔵 PERSONA A + 🟢 PERSONA B: Testing conjunto [4-6h]
└─ 🟠 PERSONA D: Preparar dispositivos [2-3h]

DÍA 4:
├─ TODO EL EQUIPO: Testing final [4h]
└─ TODO EL EQUIPO: Ajustes y bugfixes [4h]

DÍA 5:
└─ TODO EL EQUIPO: Iniciar experimento [2h setup]
```

**Total tiempo equipo:** 5 días
**Total horas-persona:** ~60h (vs 15h secuenciales → Eficiencia x4)

---

## 🔵 TAREA 1: PROBAR SISTEMA TIKTOK (Persona A)

### 📋 Checklist de tareas:

**DÍA 1 - Mañana (4 horas):**
- [ ] Leer `PRUEBA_SISTEMA_TIKTOK.md` completo (30 min)
- [ ] Configurar celular Android con ADB (30 min)
- [ ] Verificar que TikTok está instalado (10 min)
- [ ] Crear carpetas de imágenes de prueba (20 min)
- [ ] Ejecutar sistema completo desde UI (60 min)
- [ ] Documentar resultados (30 min)

**DÍA 1 - Tarde (3-4 horas):**
- [ ] Pruebas individuales de funciones:
  - [ ] `TitkokCuentas()` - Solo escaneo (30 min)
  - [ ] `switchAccount()` - Solo cambiar cuenta (20 min)
  - [ ] `ejecutar_gestos()` - Solo publicar (40 min)
- [ ] Leer código `CarruselTiktok.py` línea por línea (60 min)
- [ ] Identificar qué coordenadas son específicas de TikTok (30 min)
- [ ] Crear documento de aprendizajes (30 min)

### 📄 Entregable:

**Archivo:** `APRENDIZAJES_TIKTOK.md`

**Contenido:**
```markdown
# APRENDIZAJES DEL SISTEMA TIKTOK

## ✅ Qué funciona
- Sistema detecta cuentas: SÍ / NO
- Sistema publica carruseles: SÍ / NO
- OCR funciona bien: SÍ / NO
- Tiempos: Escaneo ___ seg, Publicación ___ seg

## 🔍 Coordenadas identificadas (para cambiar en Facebook)
1. Botón "+": tap("50%", "90.34%")
   → En Facebook será "What's on your mind?"

2. Botón "Camera": buscarTextoEnRegion(...)
   → En Facebook será "Photo/Video"

3. Selección de imágenes: 11 taps en grid
   → En Facebook será seleccionar 1 video

4. Botón "Next": buscarTextoEnRegion(..., "Next")
   → En Facebook igual (probablemente)

5. Botón "Post": buscarTextoEnRegion(..., "Post")
   → En Facebook igual

6. Verificación: buscarTextoEnRegion(..., "posted")
   → En Facebook será "Posted" (inglés)

## 🐛 Problemas encontrados
- Problema 1: ...
- Problema 2: ...

## 💡 Recomendaciones para Facebook
- Recomendación 1: ...
- Recomendación 2: ...
```

### 🤝 Handoff a Persona C:

Al final del Día 1:
1. Compartir `APRENDIZAJES_TIKTOK.md`
2. Hacer demo en vivo (15 min) mostrando:
   - Cómo se ve la ejecución
   - Qué hace cada función
   - Dónde están los archivos clave

---

## 🟢 TAREA 2: MAPEAR FACEBOOK (Persona B)

### 📋 Checklist de tareas:

**DÍA 1 - Completo (6-8 horas):**

#### Parte 1: Setup (1 hora)
- [ ] Instalar Facebook en celular Android
- [ ] Configurar ADB (si no está)
- [ ] Crear cuenta Facebook de prueba
- [ ] Subir 5 videos de prueba a galería del celular

#### Parte 2: Mapeo manual (3-4 horas)
- [ ] Capturar pantallas de cada paso:
  ```bash
  # Pantalla 1: Home de Facebook
  adb -s SERIAL exec-out screencap -p > fb_1_home.png

  # Pantalla 2: Crear post
  # (Hacer tap manual en "What's on your mind?")
  adb -s SERIAL exec-out screencap -p > fb_2_crear_post.png

  # Pantalla 3: Galería de videos
  # (Hacer tap manual en "Photo/Video")
  adb -s SERIAL exec-out screencap -p > fb_3_galeria.png

  # Pantalla 4: Vista previa + Post
  # (Seleccionar video manual)
  adb -s SERIAL exec-out screencap -p > fb_4_post.png
  ```

- [ ] Medir coordenadas con Paint/GIMP:
  - [ ] Región "What's on your mind?"
  - [ ] Botón "Photo/Video"
  - [ ] Primera posición de video en galería
  - [ ] Botón "Next" o "Done"
  - [ ] Campo de texto (descripción)
  - [ ] Botón "Post"
  - [ ] Región donde aparece "Posted"

- [ ] Obtener resolución del celular:
  ```bash
  adb -s SERIAL shell wm size
  ```

- [ ] Convertir coordenadas píxeles → porcentajes

#### Parte 3: Pruebas manuales con ADB (2-3 horas)
- [ ] Probar cada tap manualmente:
  ```bash
  # Ejemplo: Tap en "What's on your mind?"
  # Si mediste (540, 350) en pantalla 1080x2400:
  # X% = 540/1080 = 50%
  # Y% = 350/2400 = 14.58%

  adb -s SERIAL shell input tap 540 350
  # ¿Funcionó? → Anotar coordenada
  ```

- [ ] Secuencia completa manual:
  ```bash
  # 1. Abrir Facebook
  adb shell monkey -p com.facebook.katana -c android.intent.category.LAUNCHER 1

  # 2. Tap "What's on your mind?"
  adb shell input tap X Y

  # 3. Tap "Photo/Video"
  adb shell input tap X Y

  # 4. Tap primer video
  adb shell input tap X Y

  # 5. Tap "Next"
  adb shell input tap X Y

  # 6. Escribir descripción
  adb shell input text "Test"

  # 7. Tap "Post"
  adb shell input tap X Y
  ```

- [ ] Verificar que se publica correctamente

**DÍA 2 - Mañana (2-3 horas):**

#### Parte 4: Documentación de coordenadas
- [ ] Crear `core/facebook_funcs/COORDENADAS_FB.txt`

### 📄 Entregable:

**Archivo:** `core/facebook_funcs/COORDENADAS_FB.txt`

**Contenido:**
```
COORDENADAS FACEBOOK - [TU NOMBRE]
===================================

RESOLUCIÓN DEL DISPOSITIVO: 1080x2400
SERIAL: RF8X20S0C7D
MARCA/MODELO: Samsung Galaxy A50
VERSIÓN ANDROID: 11
VERSIÓN FACEBOOK: 450.0.0.39.107

====================================
PANTALLA 1: HOME DE FACEBOOK
====================================

Región "What's on your mind?":
  Píxeles: (50, 150, 1030, 350)
  Porcentaje: (4.63%, 6.25%, 95.37%, 14.58%)

Texto OCR detectado en región:
  - "What's on your mind?"
  - "What's on your mind, [Nombre]?"

Coordenada de tap (centro del cuadro):
  Píxeles: (540, 250)
  Porcentaje: (50%, 10.42%)

✅ PROBADO: Sí, funciona

====================================
PANTALLA 2: CREAR PUBLICACIÓN
====================================

Botón "Photo/Video":
  Píxeles: (200, 800)
  Porcentaje: (18.52%, 33.33%)

Texto OCR:
  - "Photo/Video"
  - "Photo"
  - "Video"

✅ PROBADO: Sí, funciona

Campo de texto (descripción):
  Píxeles: (100, 600)
  Porcentaje: (9.26%, 25%)

✅ PROBADO: Tap funciona, abre teclado

====================================
PANTALLA 3: GALERÍA DE VIDEOS
====================================

Primera posición de video:
  Píxeles: (270, 960)
  Porcentaje: (25%, 40%)

✅ PROBADO: Selecciona primer video

Botón "Next" / "Done":
  Píxeles: (860, 2150)
  Porcentaje: (79.63%, 89.58%)

Texto OCR:
  - "Next"
  - "Done"

✅ PROBADO: Avanza a siguiente pantalla

====================================
PANTALLA 4: PUBLICAR
====================================

Botón "Post":
  Píxeles: (860, 2200)
  Porcentaje: (79.63%, 91.67%)

Texto OCR:
  - "Post"
  - "Publicar" (si idioma español)

✅ PROBADO: Publica correctamente

Región de verificación "Posted":
  Píxeles: (0, 1800, 1080, 2200)
  Porcentaje: (0%, 75%, 100%, 91.67%)

Texto OCR después de publicar:
  - "Posted"
  - "Your post is now live"

✅ PROBADO: OCR detecta "Posted" correctamente

====================================
TIEMPOS OBSERVADOS
====================================

1. Abrir Facebook: ~5 segundos
2. Pantalla Home → Crear post: ~2 segundos
3. Seleccionar video: ~3 segundos
4. Procesamiento de video: ~15-30 segundos ⚠️ IMPORTANTE
5. Publicar: ~5 segundos
6. Confirmación "Posted": ~3 segundos

TOTAL ESTIMADO: 35-50 segundos por video

====================================
PROBLEMAS / OBSERVACIONES
====================================

1. Procesamiento de video tarda 15-30 seg
   → Necesita espera dinámica con timeout

2. A veces aparece "Add location" o "Tag people"
   → Ignorar, no es necesario

3. Si el video ya está en Facebook, muestra warning
   → Detectar texto "already posted"

4. Botón "Post" a veces cambia de posición
   → Usar OCR en vez de coordenada fija

====================================
RECOMENDACIONES PARA CÓDIGO
====================================

1. Usar OCR para TODO (no confiar en coordenadas fijas)
2. Esperar procesamiento con timeout de 60 segundos
3. Verificar múltiples textos: "Posted", "Your post is live"
4. Agregar capturas de pantalla en cada paso (debug)

====================================
SECUENCIA COMPLETA PROBADA
====================================

adb shell monkey -p com.facebook.katana -c android.intent.category.LAUNCHER 1
sleep 5
adb shell input tap 540 250
sleep 2
adb shell input tap 200 800
sleep 3
adb shell input tap 270 960
sleep 2
adb shell input tap 860 2150
sleep 30  # Esperar procesamiento
adb shell input text "Test post"
sleep 1
adb shell input tap 860 2200
sleep 5

✅ RESULTADO: Video publicado correctamente
```

### 🤝 Handoff a Persona C:

Al final del Día 1:
1. Compartir `COORDENADAS_FB.txt`
2. Compartir capturas de pantalla (fb_1_home.png, etc.)
3. Hacer demo de secuencia manual (10 min)

---

## 🟡 TAREA 3: DESARROLLAR CÓDIGO (Persona C)

### 📋 Checklist de tareas:

**Prerrequisito:** Esperar a que Persona A termine Día 1

**DÍA 2 - Completo (6-8 horas):**

#### Parte 1: Setup (30 min)
- [ ] Leer `APRENDIZAJES_TIKTOK.md` (de Persona A)
- [ ] Leer `COORDENADAS_FB.txt` (de Persona B)
- [ ] Crear estructura de carpetas:
  ```bash
  mkdir core\facebook_funcs
  cd core\facebook_funcs
  type nul > __init__.py
  type nul > FacebookVideoPost.py
  type nul > utils_fb.py
  ```

#### Parte 2: Copiar y adaptar código (4-5 horas)

**Archivo 1: `utils_fb.py`** (30 min)
```python
# Copiar de core/tiktok_funcs/utils.py
# Cambiar:
# - Referencias "tiktok" → "facebook"
# - DISPOSITIVOS_FILE → DISPOSITIVOS_FACEBOOK_FILE
```

- [ ] Copiar `utils.py`
- [ ] Buscar y reemplazar:
  - `cargar_dispositivos()` → `cargar_dispositivos_fb()`
  - `DISPOSITIVOS_FILE` → `DISPOSITIVOS_FACEBOOK_FILE`
- [ ] Eliminar funciones específicas de TikTok:
  - `switchAccount()` (no necesario para FB)
  - `AbrirJsonCarruseles()` (no hay carruseles)
- [ ] Mantener:
  - `should_stop_fb()`
  - `silenciar_dispositivo()`
  - `ejecteg()`
  - `cerrary_salir()`

**Archivo 2: `FacebookVideoPost.py`** (3-4 horas)
```python
# Copiar de core/tiktok_funcs/VideosMujeres/TiktokVideoScan.py
# O de core/tiktok_funcs/CarruselTiktok.py
# Adaptar a Facebook
```

- [ ] Copiar estructura base de `TiktokVideoScan.py`
- [ ] Crear función `publicar_video_facebook(serial)`:
  ```python
  def publicar_video_facebook(serial: str):
      # 1. Abrir Facebook
      run, tap, _, move, write, buscarTextoEnRegion, _, _ = crear_funciones_con_serial(serial)
      run("shell monkey -p com.facebook.katana -c android.intent.category.LAUNCHER 1")
      time.sleep(5)

      # 2. Tap "What's on your mind?"
      tap("50%", "10.42%")  # ← Coordenada de Persona B
      time.sleep(2)

      # 3. Tap "Photo/Video"
      coords = buscarTextoEnRegion(("5%","20%","50%","50%"), "Photo")
      if coords:
          tap(*coords)
      else:
          tap("18.52%", "33.33%")  # Fallback
      time.sleep(3)

      # 4. Seleccionar video
      tap("25%", "40%")  # Primera posición
      time.sleep(2)

      # 5. Tap "Next"
      coords = buscarTextoEnRegion(("60%","80%","100%","100%"), "Next")
      if coords:
          tap(*coords)
      else:
          tap("79.63%", "89.58%")
      time.sleep(30)  # ⚠️ ESPERAR PROCESAMIENTO

      # 6. Escribir descripción (opcional)
      tap("9.26%", "25%")  # Campo de texto
      time.sleep(1)
      write("Video de prueba")

      # 7. Tap "Post"
      coords = buscarTextoEnRegion(("60%","85%","100%","100%"), "Post")
      if coords:
          tap(*coords)
      else:
          tap("79.63%", "91.67%")
      time.sleep(5)

      # 8. Verificar
      if buscarTextoEnRegion(("0%","75%","100%","100%"), "Posted"):
          print("✅ Video publicado en Facebook")
          return True
      else:
          print("❌ No se confirmó publicación")
          return False
  ```

- [ ] Reemplazar TODAS las coordenadas con las de `COORDENADAS_FB.txt`
- [ ] Agregar timeout para procesamiento de video (30-60 seg)
- [ ] Agregar detección de warnings:
  ```python
  def detectar_warnings_facebook(serial):
      textos_warning = [
          "suspicious activity",
          "automated behavior",
          "verify your identity"
      ]
      for texto in textos_warning:
          if buscarTextoEnRegion(full_screen, texto):
              print(f"⚠️ WARNING DETECTADO: {texto}")
              return True
      return False
  ```

#### Parte 3: Logging experimental (1 hora)

- [ ] Crear `experimental_logger.py`
- [ ] Copiar código del `PLAN_TECNICO_IMPLEMENTACION.md`
- [ ] Integrar en `FacebookVideoPost.py`:
  ```python
  logger = ExperimentalLogger(serial)
  logger.log_inicio("publicar_video")
  logger.log_step("abrir_facebook")
  # ...
  logger.log_exito(video, descripcion)
  logger.log_fin()
  ```

**DÍA 3 - Mañana (3-4 horas):**

#### Parte 4: Integración en UI

- [ ] Abrir `ui/main_window.py`
- [ ] Agregar importación (línea ~40):
  ```python
  from core.facebook_funcs.FacebookVideoPost import publicar_video_facebook
  ```
- [ ] Agregar color (en `__init__`, línea ~330):
  ```python
  self.color_accion["facebook_posting"] = "#1877f2"
  ```
- [ ] Agregar botón (toolbar, línea ~390):
  ```python
  btn_fb = QPushButton("📘 Facebook")
  btn_fb.setObjectName("accent")
  btn_fb.clicked.connect(self.flujo_facebook)
  row1.addWidget(btn_fb)
  ```
- [ ] Agregar métodos (al final de MainWindow):
  ```python
  def flujo_facebook(self):
      seleccionados = [s for s in self.seriales if self.is_selected(s)]
      if not seleccionados:
          QMessageBox.warning(self, "Error", "Selecciona dispositivos")
          return
      for serial in seleccionados:
          self._start_facebook_worker(serial)

  def _start_facebook_worker(self, serial):
      self.estado_dispositivos[serial] = "facebook_posting"
      self._set_estado_visual(serial, "facebook_posting")
      hilos_activos[serial] = True

      th = QThread(self)
      worker = GenericWorker(serial, publicar_video_facebook)
      worker.moveToThread(th)

      th.started.connect(worker.run)
      worker.finished.connect(lambda s=serial: self._on_fb_finished(s))
      worker.failed.connect(lambda s=serial, e="": self._on_fb_failed(s, e))

      worker.finished.connect(th.quit)
      worker.failed.connect(th.quit)
      th.finished.connect(th.deleteLater)

      self._generic_threads[serial] = th
      self._generic_workers[serial] = worker
      th.start()

  def _on_fb_finished(self, serial):
      print(f"✅ Facebook finalizado en {serial}")
      self.estado_dispositivos[serial] = None
      self._set_estado_visual(serial, None)

  def _on_fb_failed(self, serial, err):
      print(f"❌ Facebook falló en {serial}: {err}")
      self.estado_dispositivos[serial] = None
      self._set_estado_visual(serial, None)
  ```

- [ ] Actualizar `core/paths.py`:
  ```python
  DISPOSITIVOS_FACEBOOK_FILE = os.path.join(DATA_DIR, "dispositivos_facebook.json")
  ```

### 📄 Entregables:

- [ ] `core/facebook_funcs/utils_fb.py` (completo)
- [ ] `core/facebook_funcs/FacebookVideoPost.py` (completo)
- [ ] `core/facebook_funcs/experimental_logger.py` (completo)
- [ ] `ui/main_window.py` (actualizado)
- [ ] `core/paths.py` (actualizado)

### 🤝 Handoff a testing (Día 3 tarde):

1. Commit de código
2. Avisar a Persona A y B que está listo para probar
3. Documentar cómo ejecutar

---

## 🟠 TAREA 4: PREPARAR EXPERIMENTO (Persona D - Opcional)

### Esta tarea es ASÍNCRONA (puede hacerse en cualquier momento)

**DÍA 1-2 (3-5 horas totales):**

#### Subtarea 1: Crear cuentas Facebook (2-3 horas)
- [ ] Conseguir 8 emails desechables:
  - TempMail.org
  - Guerrillamail.com
  - 10minutemail.com
- [ ] Crear 8 cuentas Facebook:
  - Usar nombres genéricos
  - Foto de perfil genérica
  - Sin amigos (no importa)
- [ ] Documentar credenciales:
  ```
  Cuenta 1: test.fb.01@tempmail.com / Password123
  Cuenta 2: test.fb.02@tempmail.com / Password123
  ...
  ```

#### Subtarea 2: Conseguir videos (1-2 horas)
- [ ] Descargar 50 videos genéricos:
  - Pexels.com (videos stock gratis)
  - Pixabay.com
  - Coverr.co
- [ ] Organizar en carpetas:
  ```
  C:\Videos\Facebook\
  ├── Cuenta01\
  │   ├── video1.mp4
  │   ├── video2.mp4
  │   └── video3.mp4
  ├── Cuenta02\
  ...
  ```
- [ ] Verificar formato:
  - Resolución: 720p o 1080p
  - Duración: 15-60 segundos
  - Tamaño: < 100MB

#### Subtarea 3: Configurar dispositivos (1 hora)
- [ ] Instalar Facebook en 8 celulares
- [ ] Login con las 8 cuentas (1 por celular)
- [ ] Subir videos a galería de cada celular
- [ ] Verificar que ADB detecta todos:
  ```bash
  adb devices
  ```

### 📄 Entregable:

**Archivo:** `CONFIGURACION_EXPERIMENTO.md`

```markdown
# CONFIGURACIÓN DEL EXPERIMENTO

## Cuentas Facebook
1. test.fb.01@tempmail.com / Password123 → Device RF8X20S0C7D
2. test.fb.02@tempmail.com / Password123 → Device 192.168.1.10
...

## Videos preparados
- Total: 50 videos
- Ubicación: C:\Videos\Facebook\
- Formato: MP4, 720p, 15-60 seg

## Dispositivos configurados
1. RF8X20S0C7D → Cuenta 1 → Grupo A (1 post/día)
2. 192.168.1.10 → Cuenta 2 → Grupo B (3 posts/día)
...

✅ TODO LISTO PARA EXPERIMENTO
```

---

## 🧪 DÍA 3-4: TESTING CONJUNTO (Todo el equipo)

### DÍA 3 - Tarde (4 horas)

**Todos juntos:**

#### Test 1: Ejecución básica (1 hora)
- [ ] Persona C ejecuta sistema
- [ ] Persona A y B observan
- [ ] ¿Funciona end-to-end?
  - [ ] Abre Facebook ✓
  - [ ] Navega a crear post ✓
  - [ ] Selecciona video ✓
  - [ ] Publica ✓
  - [ ] Verifica "Posted" ✓

#### Test 2: Debugging de coordenadas (2 horas)
- [ ] Si falla algún tap:
  - Persona B verifica coordenadas
  - Persona C ajusta código
  - Persona A prueba de nuevo
- [ ] Repetir hasta que funcione en 3/3 intentos

#### Test 3: Testing en múltiples dispositivos (1 hora)
- [ ] Probar en 3 dispositivos distintos
- [ ] Verificar que coordenadas % funcionan en diferentes resoluciones

### DÍA 4 - Completo (8 horas)

**División de tareas:**

**🔵 Persona A: Testing de robustez (4 horas)**
- [ ] Probar 10 veces seguidas
- [ ] Documentar fallos
- [ ] Calcular tasa de éxito

**🟢 Persona B: Captura de screenshots (2 horas)**
- [ ] Agregar capturas en cada paso (debug)
- [ ] Verificar que OCR funciona bien

**🟡 Persona C: Bugfixes + logging (4 horas)**
- [ ] Corregir bugs encontrados por Persona A
- [ ] Mejorar logging
- [ ] Optimizar timeouts

**🟠 Persona D: Preparar JSON inicial (2 horas)**
- [ ] Crear `dispositivos_facebook.json` con 8 cuentas
- [ ] Verificar que videos están en lugares correctos

**Todos juntos: Testing final (2 horas)**
- [ ] Ejecutar en los 8 dispositivos
- [ ] Verificar que todos publican correctamente
- [ ] Dar luz verde para experimento

---

## 📊 DÍA 5: INICIAR EXPERIMENTO

**Todo el equipo (2 horas):**

1. **Setup inicial:**
   - [ ] Verificar 8 dispositivos conectados
   - [ ] Verificar `dispositivos_facebook.json` correcto
   - [ ] Verificar videos en galería

2. **Primera ejecución:**
   - [ ] Ejecutar 1 post en cada dispositivo
   - [ ] Verificar que todos publican
   - [ ] Revisar logs generados

3. **Configurar monitoreo:**
   - [ ] Script para ejecutar automáticamente cada N horas
   - [ ] Sistema de alertas si falla

4. **Documentar:**
   - [ ] Timestamp de inicio
   - [ ] Configuración final
   - [ ] Próximos pasos

---

## 📋 RESUMEN DE ENTREGABLES POR PERSONA

### 🔵 Persona A:
- [ ] `APRENDIZAJES_TIKTOK.md`
- [ ] Demo en vivo del sistema TikTok
- [ ] Reporte de testing de robustez (Día 4)

### 🟢 Persona B:
- [ ] `COORDENADAS_FB.txt`
- [ ] Screenshots de Facebook (fb_1_home.png, etc.)
- [ ] Demo de secuencia manual

### 🟡 Persona C:
- [ ] `core/facebook_funcs/utils_fb.py`
- [ ] `core/facebook_funcs/FacebookVideoPost.py`
- [ ] `core/facebook_funcs/experimental_logger.py`
- [ ] `ui/main_window.py` (actualizado)
- [ ] Bugfixes del Día 4

### 🟠 Persona D:
- [ ] 8 cuentas Facebook creadas
- [ ] 50 videos descargados y organizados
- [ ] `CONFIGURACION_EXPERIMENTO.md`
- [ ] `dispositivos_facebook.json` inicial

---

## ✅ CHECKLIST DE SINCRONIZACIÓN

### Fin de Día 1:
- [ ] Persona A completó pruebas TikTok
- [ ] Persona A compartió `APRENDIZAJES_TIKTOK.md`
- [ ] Persona B mapeó al menos 50% de coordenadas
- [ ] Persona D creó 8 cuentas FB

### Fin de Día 2:
- [ ] Persona B completó `COORDENADAS_FB.txt`
- [ ] Persona C tiene código base copiado y adaptado
- [ ] Persona D tiene videos listos

### Fin de Día 3:
- [ ] Todo el equipo hizo testing conjunto
- [ ] Sistema funciona end-to-end al menos 1 vez
- [ ] Bugs documentados

### Fin de Día 4:
- [ ] Bugs corregidos
- [ ] Testing en 8 dispositivos exitoso
- [ ] Logs funcionando
- [ ] Experimento listo para iniciar

### Día 5:
- [ ] Experimento iniciado
- [ ] Primer batch de datos recolectados

---

## 🚨 BLOQUEADORES Y DEPENDENCIAS

### Persona C depende de:
- ✅ Persona A terminar Día 1 (entender TikTok)
- ✅ Persona B terminar mapeo (tener coordenadas)

**Solución:** Persona C puede empezar leyendo docs mientras espera

### Persona D es independiente:
- ⚡ Puede empezar cuando quiera
- ⚡ No bloquea a nadie
- ⚡ Es preparación asíncrona

### Testing conjunto requiere:
- ✅ Código de Persona C listo
- ✅ Coordenadas de Persona B verificadas
- ✅ Entendimiento de Persona A del flujo

---

## 💡 TIPS PARA TRABAJO EN PARALELO

1. **Comunicación diaria:**
   - Stand-up de 15 min cada mañana
   - ¿Qué hiciste ayer? ¿Qué harás hoy? ¿Bloqueadores?

2. **Documentar TODO:**
   - No asumir que otros saben qué hiciste
   - Escribir en los archivos entregables

3. **Git para coordinar:**
   ```bash
   # Persona A
   git checkout -b persona-a-testing

   # Persona B
   git checkout -b persona-b-mapeo

   # Persona C
   git checkout -b persona-c-codigo

   # Al final del día: merge
   ```

4. **Slack/Discord para preguntas:**
   - Canal dedicado al proyecto
   - Compartir screenshots de progreso

5. **Pair programming para bugs:**
   - Persona A + Persona C juntos debuggeando
   - Persona B ayuda con coordenadas

---

## ⏱️ RESUMEN DE TIEMPOS

```
SECUENCIAL (1 persona):
├─ Aprender TikTok: 8h
├─ Mapear Facebook: 8h
├─ Desarrollar código: 8h
├─ Testing: 8h
└─ TOTAL: 32 horas = 4 días (8h/día)

PARALELO (3 personas):
├─ Día 1: A+B+D en paralelo
├─ Día 2: B+C+D en paralelo
├─ Día 3: A+B+C testing
├─ Día 4: A+B+C+D bugfixing
└─ TOTAL: 4 días CALENDARIO (pero 12 horas-persona)

GANANCIA: 3x más rápido 🚀
```

---

**¿LISTO PARA EMPEZAR?**

Asigna roles y que cada persona abra su documento correspondiente:
- 🔵 Persona A → `PRUEBA_SISTEMA_TIKTOK.md`
- 🟢 Persona B → Esta sección "TAREA 2" arriba
- 🟡 Persona C → Esperar Día 2, leer docs mientras
- 🟠 Persona D → Empezar a crear cuentas YA
