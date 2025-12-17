# 🧪 PRUEBA DEL SISTEMA TIKTOK ACTUAL
## Guía para entender cómo funciona antes de copiar a Facebook

---

## 🎯 OBJETIVO

Que alguien pruebe el sistema TikTok existente para:
1. **Entender** cómo funciona la automatización
2. **Verificar** que todo funciona en su celular
3. **Familiarizarse** con el flujo antes de copiar a Facebook

**Tiempo estimado:** 30-60 minutos

---

## ✅ PRE-REQUISITOS

### Necesitas:
- [ ] 1 celular Android
- [ ] Cable USB
- [ ] Cuenta TikTok (puede ser de prueba)
- [ ] 3-5 imágenes para crear un carrusel
- [ ] PC con el proyecto instalado

### Verificar instalación:
```bash
# 1. ADB instalado
adb version
# Debe mostrar: Android Debug Bridge version X.X.X

# 2. Python instalado
python --version
# Debe mostrar: Python 3.x.x

# 3. Tesseract instalado
tesseract --version
# Debe mostrar versión
```

---

## 🔧 PASO 1: PREPARAR EL CELULAR (5 min)

### Habilitar modo desarrollador:

**Android:**
1. Ir a **Ajustes** → **Acerca del teléfono**
2. Tocar **Número de compilación** 7 veces
3. Mensaje: "Ahora eres desarrollador"

### Habilitar depuración USB:

1. Ir a **Ajustes** → **Opciones de desarrollador**
2. Activar **Depuración USB**
3. Conectar celular a PC con cable USB
4. Aparecerá mensaje en celular: "¿Permitir depuración USB?"
5. Marcar "Permitir siempre desde esta computadora"
6. Tocar **Permitir**

### Verificar conexión:

```bash
adb devices
```

**Salida esperada:**
```
List of devices attached
RF8X20S0C7D    device
```

Si dice "unauthorized" → Revisa que permitiste en el celular
Si no aparece nada → Revisa cable USB / drivers

---

## 📱 PASO 2: INSTALAR TIKTOK Y CONFIGURAR (5 min)

### En el celular:

1. **Instalar TikTok** desde Play Store (si no lo tienes)
2. **Iniciar sesión** con cuenta de prueba
3. **Subir 5-10 imágenes** a la galería del celular
   - Pueden ser cualquier cosa (memes, fotos, screenshots)
   - Solo para probar el sistema

### Verificar que TikTok está instalado:

```bash
adb shell pm list packages | findstr tiktok
```

**Salida esperada:**
```
package:com.zhiliaoapp.musically
```

---

## 🗂️ PASO 3: PREPARAR CARPETAS DE IMÁGENES (10 min)

### Estructura que el sistema espera:

```
C:\Users\TU_USUARIO\Documents\Carrusel\ImagenesCrudas\Carrusel\
├── 1\
│   ├── imagen1.jpg
│   ├── imagen2.jpg
│   └── imagen3.jpg
├── 2\
│   ├── imagen1.jpg
│   └── imagen2.jpg
└── 3\
    └── imagen1.jpg
```

### Crear carpetas de prueba:

**Windows:**
```bash
# Navegar a Documents
cd %USERPROFILE%\Documents

# Crear estructura
mkdir Carrusel\ImagenesCrudas\Carrusel\1
mkdir Carrusel\ImagenesCrudas\Carrusel\2
mkdir Carrusel\ImagenesCrudas\Carrusel\3

# Copiar imágenes a cada carpeta (manualmente)
```

**Contenido mínimo:**
- Carpeta 1: Al menos 3 imágenes
- Carpeta 2: Al menos 3 imágenes
- Carpeta 3: Al menos 3 imágenes

### Verificar:

```bash
dir %USERPROFILE%\Documents\Carrusel\ImagenesCrudas\Carrusel\1
# Debe mostrar las imágenes
```

---

## 🚀 PASO 4: EJECUTAR EL SISTEMA (Primera prueba - 15 min)

### Opción A: Desde la UI (Recomendado)

```bash
cd C:\Users\Cris\Desktop\Automatizacion\ControlDePantallas
python main.py
```

**En la interfaz:**

1. **Verificar que aparece tu celular** en la lista
   - Debe mostrar el serial (ej: RF8X20S0C7D)

2. **Seleccionar el checkbox** de tu celular

3. **Click en "📱 Inicializar SCRCPY"** (opcional)
   - Te permite ver la pantalla del celular en la PC
   - Útil para observar qué está haciendo

4. **Click en "🔎 Subir Carruseles"**

**Qué va a pasar:**

```
📍 Fase 1: ESCANEO (30-60 segundos)
   ├─ Abre TikTok en el celular
   ├─ Va a Settings → Switch account
   ├─ Usa OCR para leer nombres de cuentas
   └─ Guarda en data/dispositivos.json

📍 Fase 2: DIÁLOGO
   ├─ Aparece ventana con cuentas detectadas
   ├─ Puedes seleccionar cuáles usar
   └─ Click "Aceptar"

📍 Fase 3: PUBLICACIÓN (45-90 seg por cuenta)
   ├─ Para cada cuenta seleccionada:
   │   ├─ Carga imágenes desde carpeta asignada
   │   ├─ Sube imágenes al celular vía ADB
   │   ├─ Abre TikTok
   │   ├─ Ejecuta gestos automatizados:
   │   │   ├─ Tap en botón "+"
   │   │   ├─ Selecciona "Camera"
   │   │   ├─ Selecciona las 11 imágenes en orden
   │   │   ├─ Tap "Next"
   │   │   ├─ Agrega música
   │   │   ├─ Escribe descripción
   │   │   └─ Tap "Post"
   │   ├─ Verifica con OCR que diga "posted"
   │   └─ Cambia a siguiente cuenta
   └─ Mueve carpetas usadas a "CarruselesUsados/"
```

**Observa en el celular:**
- Verás cómo se mueve solo
- Los taps son rápidos pero visibles
- Puede que veas parpadeos (cambios de pantalla)

**En la consola (output):**
```
🔍 Escaneando cuentas en TikTok del RF8X20S0C7D...
➕ Nuevas: {'cuenta1', 'cuenta2'}
✅ Total de cuentas encontradas: {'cuenta1', 'cuenta2'}
📌 Cuenta fija: cuenta1 → 1
📦 Cuenta asignada: cuenta2 → 2
💾 Guardado para RF8X20S0C7D en dispositivos.json
✅ Escaneo terminado en RF8X20S0C7D

🚀 Iniciando flujo de publicación (intento #1)
  ✓ Abrir TikTok
  ✓ Seleccionar imágenes
  ✓ Agregar música
  ✓ Publicar
✅ Publicación exitosa
```

---

## 🔍 PASO 5: VERIFICAR QUÉ PASÓ (10 min)

### 1. Verificar en TikTok:

Abre TikTok manualmente en el celular:
- [ ] ¿Se publicó el carrusel?
- [ ] ¿Tiene las imágenes correctas?
- [ ] ¿Tiene música?
- [ ] ¿Está visible en el perfil?

### 2. Verificar archivos generados:

```bash
# Ver qué guardó el sistema
type data\dispositivos.json
```

**Debe contener algo como:**
```json
{
  "RF8X20S0C7D": {
    "cuentas": [
      {
        "cuenta": "mi_cuenta_tiktok",
        "carpeta_path": "C:\\Users\\...\\Carrusel\\1",
        "carpeta_nombre": "1"
      }
    ],
    "cuentasDetectadas": ["mi_cuenta_tiktok"],
    "cuentasPorSubir": [],
    "cuentasSubidas": ["mi_cuenta_tiktok"]
  }
}
```

### 3. Verificar carpetas movidas:

```bash
dir %USERPROFILE%\Documents\Carrusel\ImagenesCrudas\CarruselesUsados\
```

**Debe mostrar:**
```
1\  (carpeta que se usó, ahora movida aquí)
```

---

## 🧪 PASO 6: PRUEBAS ADICIONALES (Entender el flujo)

### Prueba 1: Solo escanear cuentas

```bash
# Desde Python
python
>>> from core.tiktok_funcs.TiktokCuentaScan import TitkokCuentas
>>> TitkokCuentas("TU_SERIAL")
```

**Observa:**
- Cómo abre TikTok
- Cómo navega a Settings
- Cómo hace scroll para ver más cuentas
- Cómo usa OCR para leer nombres

**Salida en consola:**
```
🔍 Escaneando cuentas en TikTok del TU_SERIAL...
➕ Nuevas: {'cuenta1'}
➕ Nuevas: {'cuenta2'}
⛔ No hay nuevas cuentas, deteniendo scroll.
✅ Total de cuentas encontradas: {'cuenta1', 'cuenta2'}
```

### Prueba 2: Cambiar entre cuentas manualmente

```bash
python
>>> from core.tiktok_funcs.utils import switchAccount
>>> switchAccount("TU_SERIAL")
```

**Observa:**
- Abre TikTok
- Va a Settings
- Abre Switch account
- Queda listo para seleccionar

### Prueba 3: Ejecutar gestos de publicación

```bash
python
>>> from core.tiktok_funcs.CarruselTiktok import ejecutar_gestos
>>> ejecutar_gestos("TU_SERIAL")
```

**Observa:**
- Secuencia completa de taps
- Cómo selecciona las 11 imágenes en orden
- Cómo agrega música
- Cómo publica

---

## 📊 ENTENDER EL CÓDIGO (Para copiar a Facebook)

### Archivo clave: `core/tiktok_funcs/CarruselTiktok.py`

**Estructura básica:**
```python
def ejecutar_gestos(serial: str):
    # 1. Obtener funciones ADB
    run, tap, long_tap, move, write, buscarTextoEnRegion, ... = crear_funciones_con_serial(serial)

    # 2. Encender celular
    run("shell input keyevent 224")  # Botón power
    time.sleep(1)

    # 3. Desbloquear (swipe hacia arriba)
    move("50%","68%","50%","20%")
    time.sleep(1)

    # 4. Abrir TikTok
    run("shell monkey -p com.zhiliaoapp.musically -c android.intent.category.LAUNCHER 1")
    time.sleep(5)

    # 5. Tap en botón "+"
    tap("50%", "90.34%")
    time.sleep(4)

    # 6. Buscar "Camera" con OCR
    coords = buscarTextoEnRegion(region, "Camera", umbral_similitud=0.9)
    if coords:
        tap(*coords)

    # 7. Seleccionar imágenes (11 taps en orden)
    tap("61.48%", "63.68%")  # Imagen 1
    tap("28.70%", "63.68%")  # Imagen 2
    # ... etc (11 imágenes total)

    # 8. Tap "Next"
    coords = buscarTextoEnRegion(region, "Next")
    tap(*coords)

    # 9. Agregar música
    coords = buscarTextoEnRegion(region, "♪")
    tap(*coords)

    # 10. Publicar
    coords = buscarTextoEnRegion(region, "Post")
    tap(*coords)

    # 11. Verificar éxito
    if buscarTextoEnRegion(full_screen, "posted"):
        print("✅ Publicado!")
        return True
```

**LO IMPORTANTE:**
- Cada `tap()` es una coordenada en porcentaje (funciona en cualquier resolución)
- `buscarTextoEnRegion()` usa OCR para encontrar botones por texto
- La secuencia es siempre la misma
- Si falla, usa fallbacks (coordenadas fijas)

---

## 🎯 CHECKLIST DE COMPRENSIÓN

Después de las pruebas, deberías poder responder:

### Conceptos básicos:
- [ ] ¿Qué es ADB y para qué sirve?
  - **Respuesta:** Android Debug Bridge, controla el celular desde PC

- [ ] ¿Qué hace `tap("50%", "90%")`?
  - **Respuesta:** Toca en el centro horizontal (50%), casi abajo (90%)

- [ ] ¿Qué hace `buscarTextoEnRegion(region, "Post")`?
  - **Respuesta:** Usa OCR para encontrar dónde dice "Post" en la pantalla

- [ ] ¿Por qué usa porcentajes y no píxeles?
  - **Respuesta:** Funciona en cualquier resolución de pantalla

### Flujo del sistema:
- [ ] ¿Cuáles son las 3 fases del sistema?
  - **Respuesta:**
    1. Escanear cuentas (OCR)
    2. Diálogo de selección (UI)
    3. Publicación automatizada (gestos)

- [ ] ¿Dónde guarda las imágenes antes de subir al celular?
  - **Respuesta:** `./imagenes_temp/SERIAL/`

- [ ] ¿Cómo sabe qué carpeta de imágenes asignar a cada cuenta?
  - **Respuesta:** `data/asignaciones.json` (fijas) + dinámicas (orden)

- [ ] ¿Qué hace con las carpetas después de publicar?
  - **Respuesta:** Las mueve a `CarruselesUsados/`

### OCR y detección:
- [ ] ¿Qué pasa si OCR no encuentra "Post"?
  - **Respuesta:** Usa coordenada fallback (tap en zona típica)

- [ ] ¿Cómo detecta que ya no hay más cuentas al escanear?
  - **Respuesta:** Busca texto "Add account" con OCR

- [ ] ¿Cómo verifica que publicó exitosamente?
  - **Respuesta:** OCR busca texto "posted" en pantalla

### Control del sistema:
- [ ] ¿Cómo se detiene una operación en curso?
  - **Respuesta:** Botón "⏹ Detener" → pone `hilos_activos[serial] = False`

- [ ] ¿Qué hace la función `should_stop(serial)`?
  - **Respuesta:** Verifica `hilos_activos[serial]`, si es False → detiene

- [ ] ¿Por qué usa `_sleep()` en vez de `time.sleep()`?
  - **Respuesta:** `_sleep()` cooperativo, permite detención rápida

---

## 🔧 TROUBLESHOOTING COMÚN

### Problema: "No se detectaron cuentas"

**Causas:**
1. OCR no lee bien el texto (idioma, fuente)
2. TikTok no abrió correctamente
3. Pantalla no está en Switch account

**Solución:**
```bash
# 1. Verificar que Tesseract funciona
python
>>> import pytesseract
>>> from PIL import Image
>>> img = Image.open("test.png")  # Captura de pantalla
>>> print(pytesseract.image_to_string(img))

# 2. Capturar pantalla manualmente para debug
adb -s TU_SERIAL exec-out screencap -p > debug.png
# Abrir debug.png y ver qué texto hay

# 3. Ajustar umbral de similitud en código
buscarTextoEnRegion(region, "texto", umbral_similitud=0.5)  # Más tolerante
```

### Problema: "Taps no funcionan en mi celular"

**Causa:** Resolución diferente

**Solución:**
```bash
# 1. Ver resolución de tu celular
adb shell wm size
# Ej: Physical size: 1080x2400

# 2. Probar tap manual
adb shell input tap 540 1200  # Centro de pantalla
# ¿Funcionó? → Las coordenadas son correctas

# 3. Si los % no funcionan, calcular píxeles manualmente:
# Si tu pantalla es 1080x2400 y el código dice tap("50%", "50%"):
# X = 1080 * 0.5 = 540
# Y = 2400 * 0.5 = 1200
# Entonces: tap en (540, 1200)
```

### Problema: "No sube imágenes al celular"

**Causa:** Permisos de ADB

**Solución:**
```bash
# 1. Verificar que ADB puede escribir
adb -s TU_SERIAL shell ls /sdcard/
# Debe mostrar carpetas (Download, DCIM, etc.)

# 2. Probar subir archivo manualmente
echo "test" > test.txt
adb -s TU_SERIAL push test.txt /sdcard/Download/
# Verificar
adb -s TU_SERIAL shell ls /sdcard/Download/test.txt

# 3. Si falla, habilitar "Transferencia de archivos" en el celular
# (Al conectar USB, seleccionar "Transferir archivos" en vez de "Solo carga")
```

---

## 📝 REPORTE DE PRUEBAS

Al terminar, completa este checklist y compártelo con el equipo:

```
REPORTE DE PRUEBAS - SISTEMA TIKTOK
====================================

Fecha: _______________
Probado por: _______________
Celular: _______________
Serial: _______________

✅ PRE-REQUISITOS
[ ] ADB instalado y funcionando
[ ] Celular detectado (adb devices)
[ ] TikTok instalado
[ ] Carpetas de imágenes creadas

✅ PRUEBA 1: ESCANEO DE CUENTAS
[ ] Sistema detectó cuentas correctamente
[ ] Cantidad de cuentas detectadas: _____
[ ] Guardó en dispositivos.json
Observaciones: _______________________

✅ PRUEBA 2: PUBLICACIÓN DE CARRUSEL
[ ] Seleccionó imágenes correctamente
[ ] Agregó música
[ ] Publicó exitosamente
[ ] Verificó "posted" con OCR
Tiempo total: _____ segundos
Observaciones: _______________________

✅ PRUEBA 3: VERIFICACIÓN MANUAL
[ ] Carrusel visible en TikTok
[ ] Imágenes correctas
[ ] Música presente
[ ] Carpeta movida a CarruselesUsados/

✅ COMPRENSIÓN
[ ] Entiendo cómo funciona ADB
[ ] Entiendo el flujo de 3 fases
[ ] Entiendo qué hace cada función
[ ] Puedo explicar cómo se copia a Facebook

PROBLEMAS ENCONTRADOS:
________________________
________________________

SUGERENCIAS:
________________________
________________________

LISTO PARA ADAPTAR A FACEBOOK: [ ] SÍ  [ ] NO
```

---

## 🚀 SIGUIENTE PASO

Una vez completado este documento y las pruebas:

**✅ Estás listo para:**
1. Copiar el código a `facebook_funcs/`
2. Cambiar coordenadas TikTok → Facebook
3. Probar con Facebook

**📖 Consulta:**
- `TAREAS_PARALELAS_FACEBOOK.md` - División de trabajo en equipo
- `INICIO_RAPIDO.md` - Pasos de desarrollo

---

**¡IMPORTANTE!** No pases a Facebook hasta que:
- ✅ Entiendas cómo funciona este sistema
- ✅ Lo hayas probado al menos 1 vez exitosamente
- ✅ Puedas explicar qué hace cada función

**Razón:** Si no entiendes TikTok, será difícil adaptar a Facebook.
