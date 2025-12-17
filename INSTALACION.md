# 🚀 GUÍA DE INSTALACIÓN
## Sistema de Automatización TikTok/Facebook

---

## 📋 REQUISITOS PREVIOS

### Sistema Operativo
- Windows 10/11 (recomendado)
- Linux (probado en Ubuntu 20.04+)
- macOS (soporte parcial)

### Hardware
- 8GB RAM mínimo (16GB recomendado)
- 10GB espacio en disco
- Puertos USB disponibles para celulares

---

## ⚙️ INSTALACIÓN PASO A PASO

### 1️⃣ INSTALAR PYTHON (Si no lo tienes)

**Windows:**
```bash
# Descargar desde: https://www.python.org/downloads/
# Versión recomendada: Python 3.10.x

# Durante instalación:
# ✅ Marcar "Add Python to PATH"
# ✅ Marcar "Install pip"

# Verificar instalación:
python --version
pip --version
```

**Debe mostrar:** Python 3.10.x y pip 23.x.x

---

### 2️⃣ INSTALAR TESSERACT-OCR (Reconocimiento de texto)

**Windows:**
```bash
# 1. Descargar instalador:
# https://github.com/UB-Mannheim/tesseract/wiki

# 2. Ejecutar instalador (usar ruta por defecto):
# C:\Program Files\Tesseract-OCR

# 3. Agregar a PATH del sistema:
# Panel de Control → Sistema → Configuración avanzada del sistema
# → Variables de entorno → Path → Editar → Nuevo
# → Agregar: C:\Program Files\Tesseract-OCR

# 4. Reiniciar terminal y verificar:
tesseract --version
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install tesseract-ocr
tesseract --version
```

**Debe mostrar:** tesseract 5.x.x

---

### 3️⃣ INSTALAR ANDROID PLATFORM TOOLS (ADB)

**Windows:**
```bash
# 1. Descargar:
# https://developer.android.com/tools/releases/platform-tools

# 2. Extraer a: C:\Android\platform-tools\

# 3. Agregar a PATH:
# Variables de entorno → Path → Nuevo
# → C:\Android\platform-tools

# 4. Reiniciar terminal y verificar:
adb version
```

**Linux:**
```bash
sudo apt install android-tools-adb
adb version
```

**Debe mostrar:** Android Debug Bridge version 1.0.x

---

### 4️⃣ CLONAR/DESCARGAR EL PROYECTO

```bash
# Si ya tienes el proyecto, navega a la carpeta:
cd C:\Users\Cris\Desktop\Automatizacion\ControlDePantallas

# O descarga/clona desde tu repositorio:
# git clone [URL_DEL_REPO]
# cd ControlDePantallas
```

---

### 5️⃣ INSTALAR DEPENDENCIAS DE PYTHON

```bash
# Navegar a la carpeta del proyecto
cd C:\Users\Cris\Desktop\Automatizacion\ControlDePantallas

# Instalar todas las dependencias
pip install -r requirements.txt

# Esto instalará:
# - PyQt5 (interfaz gráfica)
# - Pillow (procesamiento de imágenes)
# - pytesseract (OCR)
# - google-api-python-client (Google Drive)
# - google-auth (autenticación Google)
```

**Tiempo estimado:** 2-5 minutos

---

### 6️⃣ VERIFICAR INSTALACIÓN

```bash
# Ejecutar script de verificación:
python -c "import PyQt5; print('✅ PyQt5 instalado')"
python -c "from PIL import Image; print('✅ Pillow instalado')"
python -c "import pytesseract; print('✅ pytesseract instalado')"
python -c "from google.oauth2 import service_account; print('✅ Google API instalado')"

# Verificar herramientas del sistema:
tesseract --version
adb version
```

**Si todo muestra ✅ → Instalación completa!**

---

### 7️⃣ CONFIGURAR DISPOSITIVOS ANDROID

**En cada celular Android:**

1. **Habilitar modo desarrollador:**
   - Ajustes → Acerca del teléfono
   - Tocar 7 veces en "Número de compilación"
   - Aparece: "Ahora eres desarrollador"

2. **Habilitar depuración USB:**
   - Ajustes → Opciones de desarrollador
   - Activar "Depuración USB"

3. **Conectar celular a PC con cable USB**

4. **Aceptar en el celular:**
   - Aparece: "¿Permitir depuración USB?"
   - Marcar: "Permitir siempre desde esta computadora"
   - Tocar: "Permitir"

5. **Verificar conexión:**
```bash
adb devices
```

**Debe mostrar:**
```
List of devices attached
RF8X20S0C7D    device
```

---

## 🎯 EJECUTAR EL SISTEMA

```bash
# Navegar al proyecto
cd C:\Users\Cris\Desktop\Automatizacion\ControlDePantallas

# Ejecutar interfaz gráfica
python main.py
```

**Debe abrirse la interfaz gráfica!** ✅

---

## 📦 INSTALACIÓN OPCIONAL: SCRCPY

SCRCPY permite ver y controlar la pantalla del celular en tu PC.

**Windows:**
```bash
# 1. Descargar desde:
# https://github.com/Genymobile/scrcpy/releases

# 2. Extraer a: C:\scrcpy\

# 3. Agregar a PATH:
# Variables de entorno → Path → Nuevo → C:\scrcpy

# 4. Verificar:
scrcpy --version
```

**Linux:**
```bash
sudo apt install scrcpy
scrcpy --version
```

---

## 🔧 SOLUCIÓN DE PROBLEMAS

### ❌ "python no se reconoce como comando"
**Solución:** Python no está en PATH
- Reinstalar Python y marcar "Add Python to PATH"
- O agregar manualmente: `C:\Users\[TU_USUARIO]\AppData\Local\Programs\Python\Python310`

### ❌ "tesseract no se reconoce como comando"
**Solución:** Tesseract no está en PATH
- Agregar a PATH: `C:\Program Files\Tesseract-OCR`
- Reiniciar terminal

### ❌ "adb no se reconoce como comando"
**Solución:** ADB no está en PATH
- Agregar a PATH donde extrajiste platform-tools
- Reiniciar terminal

### ❌ "No module named 'PyQt5'"
**Solución:** Dependencias no instaladas
```bash
pip install -r requirements.txt
```

### ❌ "No devices found" al ejecutar adb devices
**Soluciones:**
1. Verificar que depuración USB está habilitada
2. Cambiar cable USB (algunos solo cargan)
3. Probar otro puerto USB
4. Reinstalar drivers del celular
5. En el celular: Desactivar y reactivar depuración USB

### ❌ "Device unauthorized"
**Solución:**
- En el celular aparece diálogo "¿Permitir depuración USB?"
- Tocar "Permitir"
- Si no aparece: desconectar, `adb kill-server`, `adb start-server`, reconectar

### ❌ Error al abrir interfaz gráfica
**Solución:**
```bash
# Verificar que PyQt5 está instalado correctamente
pip uninstall PyQt5 PyQt5-sip PyQt5-Qt5
pip install PyQt5==5.15.10
```

---

## 📊 VERIFICACIÓN FINAL - CHECKLIST

- [ ] ✅ Python 3.10+ instalado
- [ ] ✅ `pip --version` funciona
- [ ] ✅ `tesseract --version` funciona
- [ ] ✅ `adb version` funciona
- [ ] ✅ `pip install -r requirements.txt` completado sin errores
- [ ] ✅ Imports de Python verificados (PyQt5, Pillow, etc.)
- [ ] ✅ Al menos 1 dispositivo Android conectado (`adb devices`)
- [ ] ✅ `python main.py` abre la interfaz gráfica
- [ ] ✅ Interfaz muestra dispositivos conectados

**Si todos tienen ✅ → Sistema listo para usar! 🎉**

---

## 🆘 AYUDA ADICIONAL

### Documentación del proyecto:
- `README_PROYECTO_FACEBOOK.md` - Índice general
- `QUICK_START_ANDROID.md` - Probar sistema en 15 min
- `PRUEBA_SISTEMA_TIKTOK.md` - Entender el sistema actual

### Contacto:
Si tienes problemas persistentes, documenta:
1. Sistema operativo y versión
2. Versión de Python (`python --version`)
3. Mensaje de error completo
4. Qué paso fallaba

---

**Última actualización:** 17 de Diciembre, 2025
