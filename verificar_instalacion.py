#!/usr/bin/env python3
"""
Script de verificación de instalación
Sistema de Automatización TikTok/Facebook
"""

import sys
import subprocess
import os

def print_header(text):
    """Imprime un header bonito"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def print_result(check_name, passed, message=""):
    """Imprime el resultado de una verificación"""
    status = "✅" if passed else "❌"
    print(f"{status} {check_name}")
    if message:
        print(f"   → {message}")

def check_python_version():
    """Verifica versión de Python"""
    version = sys.version_info
    passed = version.major == 3 and version.minor >= 8
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    print_result(
        "Python instalado",
        passed,
        f"Versión: {version_str} {'(OK)' if passed else '(Necesitas 3.8+)'}"
    )
    return passed

def check_module(module_name, import_statement=None):
    """Verifica si un módulo está instalado"""
    if import_statement is None:
        import_statement = module_name

    try:
        exec(f"import {import_statement}")
        print_result(f"Módulo {module_name}", True, "Instalado correctamente")
        return True
    except ImportError as e:
        print_result(f"Módulo {module_name}", False, f"No instalado: {e}")
        return False

def check_system_command(command, name):
    """Verifica si un comando del sistema está disponible"""
    try:
        result = subprocess.run(
            [command, "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print_result(f"{name} instalado", True, version)
            return True
        else:
            print_result(f"{name} instalado", False, "Comando no funciona")
            return False
    except FileNotFoundError:
        print_result(f"{name} instalado", False, "Comando no encontrado en PATH")
        return False
    except subprocess.TimeoutExpired:
        print_result(f"{name} instalado", False, "Timeout al ejecutar comando")
        return False
    except Exception as e:
        print_result(f"{name} instalado", False, f"Error: {e}")
        return False

def check_adb_devices():
    """Verifica dispositivos Android conectados"""
    try:
        result = subprocess.run(
            ["adb", "devices"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            devices = [line for line in lines if line.strip() and 'device' in line]

            if devices:
                print_result(
                    "Dispositivos Android conectados",
                    True,
                    f"{len(devices)} dispositivo(s) detectado(s)"
                )
                for device in devices:
                    serial = device.split()[0]
                    print(f"      • {serial}")
                return True
            else:
                print_result(
                    "Dispositivos Android conectados",
                    False,
                    "No hay dispositivos conectados"
                )
                return False
        else:
            print_result("Dispositivos Android conectados", False, "Error al ejecutar adb devices")
            return False
    except Exception as e:
        print_result("Dispositivos Android conectados", False, f"Error: {e}")
        return False

def check_project_structure():
    """Verifica estructura básica del proyecto"""
    required_dirs = ["core", "ui", "data"]
    required_files = ["main.py", "requirements.txt"]

    all_good = True

    for directory in required_dirs:
        exists = os.path.isdir(directory)
        print_result(f"Carpeta '{directory}'", exists)
        all_good = all_good and exists

    for file in required_files:
        exists = os.path.isfile(file)
        print_result(f"Archivo '{file}'", exists)
        all_good = all_good and exists

    return all_good

def main():
    print_header("VERIFICACIÓN DE INSTALACIÓN")
    print("Sistema de Automatización TikTok/Facebook")

    results = {}

    # Verificar Python
    print_header("1. PYTHON")
    results['python'] = check_python_version()

    # Verificar módulos de Python
    print_header("2. MÓDULOS DE PYTHON")
    results['pyqt5'] = check_module("PyQt5")
    results['pillow'] = check_module("Pillow", "PIL")
    results['pytesseract'] = check_module("pytesseract")
    results['google_api'] = check_module("google-api-python-client", "googleapiclient")
    results['google_auth'] = check_module("google-auth", "google.auth")

    # Verificar comandos del sistema
    print_header("3. HERRAMIENTAS DEL SISTEMA")
    results['tesseract'] = check_system_command("tesseract", "Tesseract-OCR")
    results['adb'] = check_system_command("adb", "ADB (Android Debug Bridge)")

    # Verificar dispositivos
    print_header("4. DISPOSITIVOS ANDROID")
    results['devices'] = check_adb_devices()

    # Verificar estructura del proyecto
    print_header("5. ESTRUCTURA DEL PROYECTO")
    results['structure'] = check_project_structure()

    # Resumen final
    print_header("RESUMEN")

    passed = sum(1 for v in results.values() if v)
    total = len(results)
    percentage = (passed / total) * 100

    print(f"\n  Tests pasados: {passed}/{total} ({percentage:.1f}%)")

    if percentage == 100:
        print("\n  🎉 ¡INSTALACIÓN COMPLETA!")
        print("  → Puedes ejecutar el sistema con: python main.py")
    elif percentage >= 80:
        print("\n  ⚠️  INSTALACIÓN CASI COMPLETA")
        print("  → Revisa los elementos marcados con ❌")
    else:
        print("\n  ❌ INSTALACIÓN INCOMPLETA")
        print("  → Sigue la guía INSTALACION.md para completar")

    # Recomendaciones específicas
    print_header("RECOMENDACIONES")

    if not results.get('python'):
        print("  • Instala Python 3.8 o superior desde python.org")

    if not all([results.get('pyqt5'), results.get('pillow'), results.get('pytesseract')]):
        print("  • Ejecuta: pip install -r requirements.txt")

    if not results.get('tesseract'):
        print("  • Instala Tesseract-OCR y agrégalo al PATH")
        print("    Windows: https://github.com/UB-Mannheim/tesseract/wiki")

    if not results.get('adb'):
        print("  • Instala Android Platform Tools y agrégalo al PATH")
        print("    https://developer.android.com/tools/releases/platform-tools")

    if not results.get('devices'):
        print("  • Conecta al menos 1 dispositivo Android con depuración USB habilitada")
        print("  • Ejecuta 'adb devices' para verificar")

    if not results.get('structure'):
        print("  • Verifica que estás en la carpeta correcta del proyecto")

    print("\n" + "="*60)
    print("  Para más ayuda, consulta: INSTALACION.md")
    print("="*60 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Verificación interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
