# CONTEXTO ACTUAL - Sistema de Automatización TikTok/Facebook

**Fecha:** 15 de Diciembre, 2025
**Estado:** Instalando LDPlayer - PROBLEMA CON HYPER-V ACTIVO

---

## PROBLEMA ACTUAL: HYPER-V SIGUE ACTIVO

### Síntoma:
- Por más que le des a "Recuperar", el aviso de Hyper-V sigue apareciendo
- Causa fallos en LDPlayer
- El sistema no arranca correctamente

### SOLUCIÓN DEFINITIVA:

#### Método 1: Deshabilitar desde CMD (MÁS EFECTIVO)

```bash
# Abrir PowerShell/CMD como ADMINISTRADOR
# Ejecutar estos comandos:

bcdedit /set hypervisorlaunchtype off
dism /Online /Disable-Feature:Microsoft-Hyper-V-All

# Reiniciar PC
shutdown /r /t 0
```

#### Método 2: Si el Método 1 no funciona

```bash
# PowerShell como ADMINISTRADOR

# Deshabilitar Windows Sandbox
Disable-WindowsOptionalFeature -Online -FeatureName Containers-DisposableClientVM -NoRestart

# Deshabilitar Virtual Machine Platform
Disable-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform -NoRestart

# Deshabilitar Hyper-V
Disable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V-All -NoRestart

# Reiniciar
shutdown /r /t 0
```

#### Método 3: NUCLEAR (si nada funciona)

```bash
# PowerShell como ADMINISTRADOR

# Listar todas las características de virtualización
Get-WindowsOptionalFeature -Online | Where-Object {$_.State -eq "Enabled" -and $_.FeatureName -like "*Hyper*"}

# Deshabilitar TODAS
Get-WindowsOptionalFeature -Online | Where-Object {$_.State -eq "Enabled" -and $_.FeatureName -like "*Hyper*"} | Disable-WindowsOptionalFeature -Online -NoRestart
Get-WindowsOptionalFeature -Online | Where-Object {$_.State -eq "Enabled" -and $_.FeatureName -like "*Virtual*"} | Disable-WindowsOptionalFeature -Online -NoRestart

# Reiniciar
shutdown /r /t 0
```

#### Verificar que se desactivó:

```bash
# Después del reinicio, ejecutar:
bcdedit

# Buscar esta línea:
# hypervisorlaunchtype    Off
# Si dice "Off" = ✅ BIEN
# Si dice "Auto" = ❌ MAL, repetir proceso
```

---

## SETUP RÁPIDO DESPUÉS DE SOLUCIONAR HYPER-V

### 1. Abrir LDPlayer
```
- Debe abrir sin errores ahora
- Esperar 30-60 segundos a que cargue
```

### 2. Configurar ADB en LDPlayer
```
Settings → Other Settings
- ✅ Enable Root
- ✅ ADB Debugging ON
```

### 3. Conectar desde PC
```bash
cd C:\Users\Cris\Desktop\Automatizacion\ControlDePantallas

# Conectar
adb connect 127.0.0.1:5555

# Verificar
adb devices
# Debe mostrar: 127.0.0.1:5555    device
```

### 4. Instalar TikTok
```
Dentro de LDPlayer:
- Play Store → TikTok → Instalar
- Iniciar sesión con cuenta de prueba
```

### 5. Preparar imágenes
```bash
mkdir %USERPROFILE%\Documents\Carrusel\ImagenesCrudas\Carrusel\1
mkdir %USERPROFILE%\Documents\Carrusel\ImagenesCrudas\Carrusel\2
# Copiar 3-5 imágenes a cada carpeta
```

### 6. Ejecutar sistema
```bash
python main.py
# Seleccionar dispositivo 127.0.0.1:5555
# Click "🔎 Subir Carruseles"
```

---

## RECORDATORIOS IMPORTANTES

### Emulador vs Celular Real:
- **Emulador:** Para testing/desarrollo, más fácil, PERO detectado por Facebook/TikTok
- **Celular físico:** Para producción/experimento real, más realista

### Si ADB no conecta:
```bash
adb kill-server
adb start-server
adb connect 127.0.0.1:5555
```

### Puertos LDPlayer:
- Instancia 1: `127.0.0.1:5555`
- Instancia 2: `127.0.0.1:5557`
- Instancia 3: `127.0.0.1:5559`

---

## ESTADO ACTUAL

**BLOQUEADO POR:** Hyper-V activo
**ACCIÓN REQUERIDA:** Ejecutar uno de los 3 métodos arriba como ADMINISTRADOR
**TIEMPO:** 5 minutos + reinicio
**DESPUÉS:** Seguir "SETUP RÁPIDO" de arriba
