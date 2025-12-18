# Sistema de Automatizacion Multi-Dispositivo Android

Sistema de automatizacion para gestion de cuentas de TikTok y Facebook en multiples dispositivos Android simultaneamente.

## Caracteristicas

### TikTok (Implementado)
- Escaneo automatico de cuentas
- Publicacion de carruseles de imagenes
- Publicacion de videos
- Cambio automatico entre cuentas
- Creacion de cuentas nuevas
- Subida de biografias
- Sistema de analiticas
- Soporte multi-dispositivo

### Facebook (En Desarrollo)
- Creacion automatica de paginas
- Publicacion de videos en paginas
- **Estado actual:** Completo hasta ingresar nombre de pagina, falta implementar click en siguiente y cerrar teclado

## Requisitos del Sistema

### Software
- Python 3.8+
- Tesseract OCR
- ADB (Android Debug Bridge)
- SCRCPY (opcional, para visualizacion)

### Hardware
- 1 o mas dispositivos Android con depuracion USB habilitada
- Cable USB
- Windows 10/11 (probado)

## Instalacion

### 1. Clonar repositorio
```bash
git clone https://github.com/CristianRamosMedina/FB_Automatization1.git
cd FB_Automatization1
```

### 2. Instalar dependencias Python
```bash
pip install -r requirements.txt
```

### 3. Instalar Tesseract OCR
1. Descargar desde: https://github.com/UB-Mannheim/tesseract/wiki
2. Buscar: `tesseract-ocr-w64-setup-5.x.x.exe`
3. Instalar en: `C:\Program Files\Tesseract-OCR`

### 4. Instalar SCRCPY (Opcional)
1. Descargar desde: https://github.com/Genymobile/scrcpy/releases
2. Descargar: `scrcpy-win64-vX.X.zip`
3. Extraer a: `C:\scrcpy\`

### 5. Configurar dispositivos Android
1. Habilitar modo desarrollador (tocar 7 veces "Numero de compilacion")
2. Activar "Depuracion USB" en Opciones de desarrollador
3. Conectar dispositivo via USB
4. Autorizar depuracion en el dispositivo

## Uso

### Ejecutar aplicacion
```bash
python main.py
```

### Interfaz principal
La aplicacion muestra:
- Lista de dispositivos conectados
- Botones de accion para cada funcionalidad
- Sistema de seleccion multi-dispositivo

### Funciones TikTok
- **Escanear Cuentas:** Detecta cuentas TikTok en dispositivos
- **Subir Carruseles:** Publica carruseles de imagenes
- **Subir Videos:** Publica videos
- **Cambiar Cuentas:** Alterna entre cuentas
- **Crear Cuentas:** Automatiza creacion de cuentas nuevas
- **Analiticas:** Recopila metricas de cuentas

### Funciones Facebook (Beta)
- **Crear Pagina:** Automatiza creacion de paginas de Facebook
  - Estado: Funcional hasta ingreso de nombre
  - Pendiente: Click en siguiente y cierre de teclado
- **Postear Video:** Publica videos en paginas (en desarrollo)

## Estructura del Proyecto

```
ControlDePantallas/
├── core/
│   ├── adb_utils.py          # Utilidades ADB
│   ├── config.py             # Configuracion global
│   ├── paths.py              # Rutas del sistema
│   ├── scrcpy_manager.py     # Gestion de SCRCPY
│   ├── tiktok_funcs/         # Modulo TikTok
│   │   ├── CarruselTiktok.py
│   │   ├── TiktokCuentaScan.py
│   │   ├── VideosMujeres/
│   │   ├── CrearCuentasTiktok/
│   │   └── ...
│   └── facebook_funcs/       # Modulo Facebook
│       └── FacebookCrearPaginaYPostearVideo.py
├── ui/
│   └── main_window.py        # Interfaz grafica
├── data/                     # Datos de configuracion (gitignored)
├── main.py                   # Punto de entrada
└── requirements.txt          # Dependencias
```

## Configuracion

### Rutas (core/paths.py)
```python
ADB_PATH = r"C:\Users\...\adb.exe"
SCRCPY_PATH = r"C:\scrcpy\scrcpy.exe"
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

### Archivos de datos
- `data/dispositivos.json`: Mapeo dispositivos-cuentas TikTok
- `data/videos.json`: Configuracion de videos
- `data/asignaciones.json`: Asignacion de carpetas
- `data/credenciales.json`: Credenciales Google (gitignored)

## Desarrollo

### Sistema de hilos
El sistema usa threading para operaciones concurrentes:
- `hilos_activos`: Control de ejecucion
- `should_stop()`: Verificacion cooperativa

### OCR
Usa Tesseract para:
- Deteccion de texto en pantalla
- Verificacion de estados
- Busqueda de botones

### Automatizacion
Basado en:
- ADB para control de dispositivos
- Coordenadas porcentuales (independientes de resolucion)
- OCR para deteccion dinamica

## Roadmap Facebook

### Completado
- [x] Apertura de Facebook
- [x] Navegacion a menu
- [x] Apertura de seccion Paginas
- [x] Inicio de creacion de pagina
- [x] Ingreso de nombre de pagina

### En Progreso
- [ ] Click en boton "Siguiente"
- [ ] Cierre automatico de teclado
- [ ] Seleccion de categoria
- [ ] Finalizacion de creacion de pagina

### Pendiente
- [ ] Verificacion de pagina creada
- [ ] Publicacion de video en pagina
- [ ] Manejo de errores Facebook
- [ ] Sistema de logs experimental
- [ ] Pruebas multi-dispositivo

## Problemas Conocidos

1. **Google Sheets:** Credenciales deshabilitadas temporalmente
2. **SCRCPY:** Ruta hardcodeada, requiere instalacion manual
3. **Facebook:** Flujo incompleto, requiere finalizacion de creacion de pagina

## Contribuciones

Para contribuir:
1. Fork del repositorio
2. Crear branch para feature
3. Commit de cambios
4. Push a branch
5. Abrir Pull Request

## Licencia

Proyecto de automatizacion educativo/investigacion.

## Contacto

Para reportar issues o sugerencias, usar el sistema de Issues de GitHub.
