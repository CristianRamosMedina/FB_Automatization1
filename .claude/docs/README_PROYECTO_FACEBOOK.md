# 📘 PROYECTO FACEBOOK - Documentación Completa
## Estudio Experimental: Sistemas Anti-Bot TikTok vs Facebook

---

## 🎯 RESUMEN DEL PROYECTO

Este proyecto expande el sistema actual de automatización (exitoso en TikTok) hacia Facebook con un enfoque **experimental**, no productivo. El objetivo es estudiar y comparar los sistemas de detección de automatización entre plataformas.

**Diferencia clave:** No buscamos evitar bans, buscamos **medirlos** como datos científicos.

---

## 📚 DOCUMENTACIÓN DISPONIBLE

### 1. **RESUMEN_EJECUTIVO_1_PAGINA.md** 📄
👤 **Para:** Tu jefe (no técnico)
⏱️ **Lectura:** 3-5 minutos
📝 **Contenido:**
- Qué es el proyecto en términos simples
- Por qué vale la pena
- Recursos necesarios (< $100)
- Timeline (6 semanas)
- Riesgos y mitigación
- Criterios de éxito

**👉 LEE ESTO PRIMERO si vas a presentar el proyecto**

---

### 2. **PROPUESTA_EXPERIMENTO_FACEBOOK.md** 📊
👤 **Para:** Jefe de proyecto / Investigador principal
⏱️ **Lectura:** 15-20 minutos
📝 **Contenido:**
- Justificación científica completa
- Diseño experimental (hipótesis, variables, métricas)
- Metodología detallada
- Plan de ejecución por fases
- Presupuesto y recursos
- Contribución científica
- Anexos

**👉 LEE ESTO para entender el experimento completo**

---

### 3. **PLAN_TECNICO_IMPLEMENTACION.md** 🔧
👤 **Para:** Desarrollador (tú)
⏱️ **Lectura:** 30-40 minutos
📝 **Contenido:**
- Qué código reutilizar (70%)
- Qué código crear nuevo (30%)
- Estructura de archivos
- Código completo de FacebookVideoPost.py (~400 líneas)
- Código completo de experimental_logger.py (~150 líneas)
- Adaptaciones en UI
- Checklist de implementación

**👉 LEE ESTO cuando estés listo para programar**

---

### 4. **COMPARACION_VISUAL_TIKTOK_VS_FACEBOOK.md** 📊
👤 **Para:** Cualquiera que quiera entender las diferencias
⏱️ **Lectura:** 10-15 minutos
📝 **Contenido:**
- Comparación lado a lado de ambos sistemas
- Diagramas de flujo
- Diferencias en UI
- Diferencias en estructura de datos
- Diferencias en filosofía
- Checklist visual de cambios

**👉 LEE ESTO para entender qué cambia vs qué se mantiene**

---

### 5. **INICIO_RAPIDO.md** 🚀
👤 **Para:** Desarrollador que va a empezar HOY
⏱️ **Lectura:** 20 minutos + seguir paso a paso
📝 **Contenido:**
- Checklist de pre-requisitos
- Día por día: qué hacer exactamente
- Comandos copy-paste listos
- Solución de problemas comunes
- Timeline de 7 días de desarrollo

**👉 LEE ESTO y empieza a programar inmediatamente**

---

### 6. **Este archivo (README_PROYECTO_FACEBOOK.md)** 📖
👤 **Para:** Navegación general
⏱️ **Lectura:** 5 minutos
📝 **Contenido:**
- Índice de toda la documentación
- Guía de por dónde empezar según tu rol
- FAQ rápido
- Estructura del proyecto

---

## 🗺️ POR DÓNDE EMPEZAR (según tu rol)

### Si eres el JEFE DE PROYECTO:
1. Lee: `RESUMEN_EJECUTIVO_1_PAGINA.md` (3 min)
2. Si te interesa, lee: `PROPUESTA_EXPERIMENTO_FACEBOOK.md` (20 min)
3. Toma decisión: ¿Aprobamos el proyecto?
4. Si sí: asigna al desarrollador + dale acceso a docs

### Si eres el DESARROLLADOR:
1. Lee: `RESUMEN_EJECUTIVO_1_PAGINA.md` (contexto general)
2. Lee: `COMPARACION_VISUAL_TIKTOK_VS_FACEBOOK.md` (entender cambios)
3. Lee: `INICIO_RAPIDO.md` (pasos concretos)
4. Empieza DÍA 1 del INICIO_RAPIDO.md
5. Consulta `PLAN_TECNICO_IMPLEMENTACION.md` cuando necesites código específico

### Si eres un INVESTIGADOR/ANALISTA:
1. Lee: `PROPUESTA_EXPERIMENTO_FACEBOOK.md` (diseño experimental)
2. Familiarízate con los datos que se generarán
3. Prepara scripts de análisis para Semana 5

### Si eres un STAKEHOLDER EXTERNO:
1. Lee: `RESUMEN_EJECUTIVO_1_PAGINA.md` (overview completo)
2. Si quieres más detalle: `PROPUESTA_EXPERIMENTO_FACEBOOK.md`

---

## ❓ FAQ RÁPIDO

### ¿Esto reemplaza el sistema TikTok?
**No.** Son sistemas **completamente separados** que coexisten sin interferir.

### ¿Cuánto cuesta?
**< $100 USD** (solo SIM cards opcionales, todo lo demás se reutiliza).

### ¿Cuánto tiempo toma?
**6 semanas totales:**
- Semana 1: Desarrollo
- Semana 2: Prueba piloto
- Semana 3-4: Experimento completo
- Semana 5: Análisis
- Semana 6: Reporte

### ¿Qué pasa si baneamos cuentas?
**Es el objetivo.** Las cuentas son desechables y los bans son **datos valiosos**, no fracasos.

### ¿Afecta al sistema TikTok actual?
**No.** El código de TikTok no se toca. Facebook está en carpeta separada.

### ¿Necesitamos aprobar algo con Facebook?
**No.** Es investigación con cuentas propias. No usamos API oficial.

### ¿Es legal?
**Sí.** Usamos cuentas propias, contenido propio, sin spam a terceros. Es investigación académica.

### ¿Qué obtenemos al final?
- Dataset experimental (JSON + logs)
- Screenshots de warnings/bans
- Gráficas comparativas TikTok vs Facebook
- Reporte científico
- Posible paper académico
- Conocimiento transferible a otras plataformas

---

## 📂 ESTRUCTURA DEL PROYECTO (después de implementar)

```
ControlDePantallas/
│
├── 📄 README_PROYECTO_FACEBOOK.md          ← Estás aquí
├── 📄 RESUMEN_EJECUTIVO_1_PAGINA.md
├── 📄 PROPUESTA_EXPERIMENTO_FACEBOOK.md
├── 📄 PLAN_TECNICO_IMPLEMENTACION.md
├── 📄 COMPARACION_VISUAL_TIKTOK_VS_FACEBOOK.md
├── 📄 INICIO_RAPIDO.md
│
├── core/
│   ├── config.py
│   ├── paths.py
│   ├── adb_utils.py
│   ├── scrcpy_manager.py
│   │
│   ├── tiktok_funcs/                       ← Sistema TikTok (sin cambios)
│   │   └── ...
│   │
│   └── facebook_funcs/                     ← Sistema Facebook (nuevo)
│       ├── __init__.py
│       ├── FacebookVideoPost.py
│       ├── experimental_logger.py
│       ├── utils_fb.py
│       └── COORDENADAS.txt
│
├── data/
│   ├── dispositivos.json                   ← TikTok (sin tocar)
│   ├── dispositivos_facebook.json          ← Facebook (nuevo)
│   │
│   ├── logs_experimento/                   ← Logs detallados (nuevo)
│   │   └── SERIAL/
│   │       └── session_TIMESTAMP.json
│   │
│   └── screenshots_fb/                     ← Screenshots de bans (nuevo)
│       └── SERIAL/
│           └── warning_TIPO_TIMESTAMP.png
│
└── ui/
    └── main_window.py                      ← +50 líneas
```

---

## 🎯 OBJETIVOS DEL PROYECTO

### Objetivo Principal:
Comparar cuantitativamente los sistemas anti-bot de TikTok vs Facebook mediante experimentación controlada.

### Objetivos Específicos:
1. **Medir velocidad de detección:** ¿Cuánto tarda Facebook en detectar automatización vs TikTok?
2. **Caracterizar restricciones:** ¿Qué tipos de bans aplica cada plataforma?
3. **Identificar variables críticas:** ¿Qué factores disparan detección más rápido?
4. **Generar conocimiento transferible:** ¿Son aplicables técnicas similares a otras plataformas?

### Entregables:
1. Sistema funcional de automatización Facebook (código)
2. Dataset experimental (200+ publicaciones)
3. Reporte científico con análisis cuantitativo
4. Documentación completa para replicación
5. Posible paper académico

---

## 📊 MÉTRICAS DE ÉXITO

### Éxito Mínimo:
- [ ] Sistema publica al menos 10 videos exitosamente
- [ ] Datos de al menos 5 bans/warnings capturados
- [ ] Diferencias cuantificables con TikTok identificadas
- [ ] Documentación completa

### Éxito Esperado:
- [ ] Dataset completo de 8 cuentas x 14 días
- [ ] Correlaciones estadísticas significativas
- [ ] Reporte ejecutivo con recomendaciones
- [ ] Código publicable (open source)

### Éxito Excepcional:
- [ ] Paper aceptado en conferencia académica
- [ ] Framework generalizable a Instagram, Twitter/X, LinkedIn
- [ ] Identificación de vulnerabilidades específicas
- [ ] Contribución citada en comunidad de investigación

---

## ⚠️ ADVERTENCIAS IMPORTANTES

### ❌ NO hacer:
- ❌ No usar cuentas valiosas (solo desechables)
- ❌ No publicar contenido ofensivo/spam
- ❌ No usar en producción (es experimental)
- ❌ No esperar sostenibilidad (habrá bans)
- ❌ No modificar código de TikTok (mantener separado)

### ✅ SÍ hacer:
- ✅ Usar cuentas creadas específicamente para el experimento
- ✅ Contenido neutro/genérico
- ✅ Registrar TODO (logs, screenshots)
- ✅ Monitoreo diario del experimento
- ✅ Backup de datos frecuente

---

## 🔐 CONSIDERACIONES ÉTICAS

### Cumplimos con:
- ✅ **Cuentas propias:** No usamos cuentas de terceros
- ✅ **Contenido propio:** Videos genéricos, no spam
- ✅ **Sin daño:** No afectamos a otros usuarios
- ✅ **Transparencia:** Investigación académica declarada
- ✅ **Datos anonimizados:** Si publicamos, sin info personal

### No cumplimos con (deliberadamente):
- ❌ **TOS de Facebook:** Violamos términos al usar automatización
  - **Justificación:** Investigación científica de sistemas anti-fraude
  - **Mitigación:** Cuentas desechables, alcance limitado, sin intención maliciosa

---

## 📅 TIMELINE VISUAL

```
┌────────────────────────────────────────────────────────────┐
│                    SEMANA 1: DESARROLLO                    │
├────────────────────────────────────────────────────────────┤
│ Día 1-2:  Setup + Logger                                  │
│ Día 3:    Mapear coordenadas                              │
│ Día 4-5:  Implementar core                                │
│ Día 6:    Integrar UI                                     │
│ Día 7:    Testing end-to-end                              │
├────────────────────────────────────────────────────────────┤
│                  SEMANA 2: PRUEBA PILOTO                   │
├────────────────────────────────────────────────────────────┤
│ 3 cuentas, 3 dispositivos                                 │
│ Validar que funciona + primeros datos                     │
├────────────────────────────────────────────────────────────┤
│              SEMANA 3-4: EXPERIMENTO COMPLETO              │
├────────────────────────────────────────────────────────────┤
│ 8 cuentas, 14 días continuos                              │
│ Grupos A, B, C (frecuencias distintas)                    │
│ Monitoreo diario + captura de datos                       │
├────────────────────────────────────────────────────────────┤
│                   SEMANA 5: ANÁLISIS                       │
├────────────────────────────────────────────────────────────┤
│ Procesar logs                                             │
│ Análisis estadístico                                      │
│ Crear gráficas                                            │
├────────────────────────────────────────────────────────────┤
│                   SEMANA 6: REPORTE                        │
├────────────────────────────────────────────────────────────┤
│ Redacción de reporte científico                           │
│ Presentación de resultados                                │
│ Preparar paper (opcional)                                 │
└────────────────────────────────────────────────────────────┘
```

---

## 🚀 PRIMEROS PASOS

### AHORA MISMO:
1. Lee `RESUMEN_EJECUTIVO_1_PAGINA.md`
2. Decide si aprobar el proyecto

### SI APRUEBAS:
1. Asigna desarrollador
2. Desarrollador lee `INICIO_RAPIDO.md`
3. Desarrollador empieza DÍA 1

### ANTES DE SEMANA 3:
1. Crear 8 cuentas Facebook desechables
2. Conseguir 50 videos genéricos
3. Preparar 8 dispositivos Android

---

## 📞 CONTACTO

**Responsable del proyecto:** [Tu nombre]
**Email:** [Tu email]
**Fecha de creación:** 13 de Diciembre, 2025

---

## 📝 CHANGELOG

**v1.0 (2025-12-13):**
- Documentación inicial completa
- 6 documentos creados
- Sistema listo para implementación

---

## 🎓 REFERENCIAS

### Papers relevantes:
- Social computing y automatización
- Detección de bots en redes sociales
- Sistemas anti-fraude

### Herramientas usadas:
- Python + PyQt5 (UI)
- ADB (Android Debug Bridge)
- Tesseract (OCR)
- JSON (datos)

### Inspiración:
- Sistema TikTok actual (funcional)
- Metodología científica experimental
- Research en social computing

---

**¡TODO LISTO PARA EMPEZAR! 🚀**

**Siguiente paso:** Lee `RESUMEN_EJECUTIVO_1_PAGINA.md` y decide si proceder.
