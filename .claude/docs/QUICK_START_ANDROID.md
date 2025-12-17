# ⚡ QUICK START - Probar Sistema en Android
## Setup rápido en 15 minutos

---

## 📋 LO QUE NECESITAS

- [ ] 1 celular Android (cualquiera)
- [ ] Cable USB
- [ ] PC con Windows
- [ ] 10-15 minutos

---

## 🚀 PASO 1: HABILITAR MODO DESARROLLADOR (2 min)

### En tu celular Android:

1. Ve a **Ajustes** → **Acerca del teléfono**
2. Toca **7 veces** en "Número de compilación"
3. Aparece: "Ahora eres desarrollador" ✓

4. Vuelve a **Ajustes** → **Sistema** → **Opciones de desarrollador**
5. Activa **Depuración USB**

6. Conecta celular a PC con cable USB
7. En el celular aparece: "¿Permitir depuración USB?"
8. Toca **Permitir**

---

## 💻 PASO 2: VERIFICAR ADB (2 min)

### En tu PC (abrir CMD o PowerShell):

```bash
cd C:\Users\Cris\Desktop\Automatizacion\ControlDePantallas

# Verificar que el celular se ve
adb devices
```

**Debe mostrar algo como:**
```
List of devices attached
RF8X20S0C7D    device
```

**Si no aparece nada:**
- Verifica que permitiste depuración en el celular
- Cambia de cable USB
- Reinstala drivers: https://adb.clockworkmod.com/

---

## 📱 PASO 3: PREPARAR TIKTOK (3 min)

### En tu celular:

1. **Instala TikTok** (si no lo tienes)
2. **Inicia sesión** (cualquier cuenta, puede ser de prueba)
3. **Listo** - no necesitas hacer nada más

---

## 🖼️ PASO 4: PREPARAR IMÁGENES (5 min)

### En tu PC:

```bash
# Crear carpetas
cd %USERPROFILE%\Documents
mkdir Carrusel\ImagenesCrudas\Carrusel\1
mkdir Carrusel\ImagenesCrudas\Carrusel\2
```

### Copia imágenes:

1. Abre **Documents\Carrusel\ImagenesCrudas\Carrusel\1\**
2. Copia **3-5 imágenes** (cualquiera: memes, fotos, screenshots)
3. Abre **Documents\Carrusel\ImagenesCrudas\Carrusel\2\**
4. Copia **3-5 imágenes** más

**Resultado:**
```
Documents\
└── Carrusel\
    └── ImagenesCrudas\
        └── Carrusel\
            ├── 1\
            │   ├── imagen1.jpg
            │   ├── imagen2.jpg
            │   └── imagen3.jpg
            └── 2\
                ├── imagen1.jpg
                └── imagen2.jpg
```

---

## ▶️ PASO 5: EJECUTAR EL SISTEMA (2 min)

### En tu PC:

```bash
cd C:\Users\Cris\Desktop\Automatizacion\ControlDePantallas

# Ejecutar
python main.py
```

### En la interfaz que se abre:

1. **Verifica** que tu celular aparece en la lista
   - Debe mostrar el serial (ej: RF8X20S0C7D)

2. **Marca** el checkbox de tu celular ✓

3. **Click** en botón **"🔎 Subir Carruseles"**

---

## 👀 QUÉ VAS A VER (1-2 min)

### En tu celular (observa):

```
⏳ FASE 1: ESCANEO (30-60 segundos)
├─ Se abre TikTok solo
├─ Va a Settings → Switch account
├─ Hace scroll automático
└─ Detecta tus cuentas

💬 FASE 2: DIÁLOGO (tú decides)
├─ Aparece ventana en PC
├─ Muestra cuentas detectadas
├─ Selecciona cuáles usar
└─ Click "Aceptar"

🚀 FASE 3: PUBLICACIÓN (45-90 seg)
├─ Abre TikTok
├─ Toca botón "+"
├─ Selecciona imágenes (lo ves en pantalla)
├─ Agrega música
├─ Escribe descripción
├─ Toca "Post"
└─ Verifica que dice "posted"
```

**Todo es automático** - solo observa cómo el celular se mueve solo.

---

## ✅ RESULTADO ESPERADO

### Si funcionó correctamente:

1. **En el celular:**
   - [ ] Se publicó un carrusel en TikTok
   - [ ] Tiene las imágenes que pusiste
   - [ ] Está visible en tu perfil

2. **En la PC (consola):**
   ```
   🔍 Escaneando cuentas en TikTok del RF8X20S0C7D...
   ✅ Total de cuentas encontradas: {'mi_cuenta'}
   💾 Guardado para RF8X20S0C7D en dispositivos.json
   ✅ Escaneo terminado

   🚀 Iniciando flujo de publicación
   ✅ Publicación exitosa
   ```

3. **Archivo generado:**
   ```bash
   # Ver lo que guardó
   type data\dispositivos.json
   ```

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### Problema: "No devices found"

```bash
# En CMD/PowerShell
adb kill-server
adb start-server
adb devices
```

Si sigue sin aparecer:
- Desconecta y reconecta cable USB
- En celular: Desactiva y reactiva "Depuración USB"
- Prueba otro cable USB

---

### Problema: "No se detectaron cuentas"

**Causa:** OCR no lee bien

**Solución rápida:**
1. Asegúrate que TikTok está en **inglés** (Settings → Language)
2. Prueba de nuevo

---

### Problema: "No encuentra imágenes"

**Verifica ruta:**
```bash
dir %USERPROFILE%\Documents\Carrusel\ImagenesCrudas\Carrusel\1
```

Debe mostrar las imágenes. Si no:
- Verifica que copiaste las imágenes en la carpeta correcta
- Verifica que son JPG o PNG

---

### Problema: "Python no encontrado"

```bash
# Instalar Python (si no lo tienes)
# Descargar de: https://www.python.org/downloads/
# Marcar "Add Python to PATH" durante instalación
```

---

## 📊 CHECKLIST RÁPIDO

Después de probarlo, confirma:

- [ ] ✅ ADB detecta mi celular
- [ ] ✅ Sistema detectó cuentas TikTok
- [ ] ✅ Publicó carrusel exitosamente
- [ ] ✅ Carrusel visible en TikTok
- [ ] ✅ Entiendo cómo funciona (taps automáticos + OCR)

**Si marcaste los 5:** Listo para copiar a Facebook ✓

---

## 🎯 SIGUIENTE PASO

Una vez que funciona, puedes:

**Opción A: Experimentar más**
```bash
# Probar con más dispositivos
# Agregar más carpetas de imágenes
# Cambiar entre cuentas
```

**Opción B: Copiar a Facebook**
```bash
# Leer: TAREAS_PARALELAS_FACEBOOK.md
# Seguir los pasos para adaptar a Facebook
```

---

## ⏱️ RESUMEN TIEMPOS

```
Paso 1: Habilitar modo desarrollador    2 min
Paso 2: Verificar ADB                   2 min
Paso 3: Preparar TikTok                 3 min
Paso 4: Preparar imágenes               5 min
Paso 5: Ejecutar sistema                2 min
         ↓
Ver ejecución completa                  2 min
         ↓
TOTAL                                  16 min ⚡
```

---

## 💡 TIPS

1. **Primera vez:** Observa el celular durante la ejecución para entender qué hace
2. **SCRCPY (opcional):** Click en "📱 Inicializar SCRCPY" para ver pantalla del celular en PC
3. **Logs:** Mira la consola para ver cada paso que ejecuta
4. **Detener:** Si algo sale mal, click "⏹ Detener" en la UI

---

## 🆘 AYUDA RÁPIDA

**Si algo no funciona:**

1. Verifica que el celular está conectado:
   ```bash
   adb devices
   ```

2. Verifica que TikTok está instalado:
   ```bash
   adb shell pm list packages | findstr tiktok
   ```

3. Reinicia todo:
   ```bash
   adb kill-server
   adb start-server
   python main.py
   ```

4. Si sigue fallando: Revisa `PRUEBA_SISTEMA_TIKTOK.md` (más detallado)

---

**¿LISTO?**

Conecta tu Android, abre CMD y empieza con **PASO 1** ⬆️
