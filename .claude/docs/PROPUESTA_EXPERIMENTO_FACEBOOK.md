# PROPUESTA DE INVESTIGACIÓN
## Estudio Comparativo: Sistemas Anti-Bot en Redes Sociales
### TikTok vs Facebook - Automatización Multi-Dispositivo

---

## 📋 RESUMEN EJECUTIVO

**Objetivo:** Expandir nuestro sistema actual de automatización (exitoso en TikTok) hacia Facebook para estudiar y comparar los sistemas de detección de automatización entre plataformas.

**Pregunta de investigación:** ¿Cómo difieren los sistemas anti-bot de Facebook vs TikTok en términos de detección, velocidad de respuesta y tolerancia?

**Método:** Replicar la arquitectura técnica que actualmente funciona en TikTok, aplicándola a Facebook para observar comportamientos del sistema de detección.

**Duración estimada:** 4-6 semanas (desarrollo + experimentación)

**Recursos necesarios:**
- Cuentas Facebook desechables (10-15)
- Dispositivos Android actuales (ya disponibles)
- Videos pre-producidos listos para publicar

---

## 🎯 JUSTIFICACIÓN DEL PROYECTO

### Contexto actual:
Nuestro sistema de automatización multi-dispositivo para TikTok está operativo y genera datos valiosos sobre:
- Comportamiento de algoritmos de contenido
- Patrones de distribución viral
- Métricas de engagement automatizado

### Oportunidad:
Facebook es la red social más grande del mundo (3 mil millones de usuarios) pero se desconoce:
- Qué tan agresivo es su sistema anti-bot comparado con TikTok
- Qué patrones específicos detecta
- Qué tan rápido responde a automatización
- Si las mismas técnicas que funcionan en TikTok son viables

### Valor científico:
Este experimento generará conocimiento original sobre:
1. Diferencias arquitectónicas entre sistemas anti-fraude
2. Efectividad relativa de distintos enfoques de detección
3. Comportamiento de plataformas ante automatización controlada
4. Datos cuantitativos para publicaciones académicas en social computing

---

## 🔬 DISEÑO EXPERIMENTAL

### Variables Independientes (Lo que controlamos):
- **Frecuencia de publicación** (1, 3, 5 videos/día)
- **Horarios de actividad** (concentrados vs distribuidos)
- **Cantidad de dispositivos** (1, 3, 5 celulares)
- **Contenido** (videos idénticos vs variados)
- **Comportamiento pre-post** (con/sin warm-up de cuenta)

### Variables Dependientes (Lo que medimos):
- **Tiempo hasta primer warning** (horas/días)
- **Tiempo hasta ban** (horas/días)
- **Tipo de restricción** (temporal, permanente, shadowban)
- **Alcance de contenido** (views, shares, engagement)
- **Mensajes de error** (tipos de detección reportados)

### Grupo de Control:
TikTok (sistema actual) - ya sabemos que funciona sin bans frecuentes

### Grupo Experimental:
Facebook (nuevo sistema) - observar comportamiento

---

## 📊 HIPÓTESIS A PROBAR

### H1: Velocidad de Detección
**Hipótesis:** Facebook detectará automatización 5-10x más rápido que TikTok
- TikTok actual: Sin bans después de semanas/meses
- Facebook esperado: Detección en 24-72 horas

### H2: Severidad de Consecuencias
**Hipótesis:** Facebook aplicará bans permanentes mientras TikTok solo aplica shadowbans temporales

### H3: Sensibilidad a Frecuencia
**Hipótesis:** Facebook tolerará máximo 2-3 posts/día, TikTok permite 10+

### H4: Efecto Cascada
**Hipótesis:** Un ban en Facebook comprometerá el dispositivo para futuras cuentas (no pasa en TikTok)

---

## 🛠️ METODOLOGÍA (Simplificado)

### ¿Cómo funciona actualmente con TikTok?
1. Sistema controla múltiples celulares Android simultáneamente
2. Detecta automáticamente cuentas en cada dispositivo
3. Sube contenido (carruseles de imágenes) de carpetas pre-asignadas
4. Simula interacciones humanas (taps, scrolls, timing)
5. Monitorea resultados y métricas

### ¿Qué adaptaremos para Facebook?
**Reutilizaremos (~70%):**
- Control de dispositivos (funciona igual)
- Sistema de archivos (cambiar imágenes → videos)
- Interfaz de usuario (agregar botones para Facebook)
- Detección de cuentas (misma tecnología)

**Crearemos (~30%):**
- Gestos específicos de Facebook (navegar app diferente)
- Sistema de verificación de publicación (UI distinta)
- Recolección de datos experimentales (logs detallados)

### Diferencia clave:
- **TikTok:** Optimizado para NO ser detectado (producción)
- **Facebook:** Diseñado para SER detectado y MEDIR la respuesta (investigación)

---

## 📅 PLAN DE EJECUCIÓN

### FASE 1: Desarrollo Base (Semana 1-2)
**Objetivo:** Adaptar código existente para Facebook

**Actividades:**
- Copiar y modificar módulos de TikTok
- Mapear coordenadas de UI de Facebook
- Implementar flujo de publicación de video
- Pruebas manuales con 1 cuenta

**Entregable:** Sistema funcional básico

---

### FASE 2: Experimento Piloto (Semana 3)
**Objetivo:** Validar que el sistema funciona y recolecta datos

**Configuración:**
- 3 dispositivos
- 1 cuenta Facebook por dispositivo
- 1 video/día por cuenta
- Monitoreo 24/7

**Métricas a observar:**
- ¿Publica exitosamente?
- ¿Cuándo llega el primer warning?
- ¿Qué mensaje muestra Facebook?

**Entregable:** Primeros datos experimentales + ajustes al sistema

---

### FASE 3: Experimento Completo (Semana 4-5)
**Objetivo:** Recolectar datos robustos con variables múltiples

**Configuración:**
| Grupo | Dispositivos | Cuentas | Frecuencia | Videos/día |
|-------|--------------|---------|------------|------------|
| A (control bajo) | 2 | 2 | Baja | 1 |
| B (medio) | 3 | 3 | Media | 3 |
| C (agresivo) | 3 | 3 | Alta | 5 |
| **Total** | **8** | **8** | - | **24** |

**Duración:** 14 días continuos

**Datos recolectados:**
- Timestamp de cada publicación
- Respuesta de Facebook (éxito/warning/ban)
- Alcance de contenido (views, reacciones)
- Tiempo exacto hasta restricción
- Tipo de restricción aplicada
- Mensajes de error capturados

---

### FASE 4: Análisis y Reporte (Semana 6)
**Objetivo:** Procesar datos y generar conclusiones

**Actividades:**
- Análisis estadístico de datos
- Gráficas comparativas TikTok vs Facebook
- Identificación de patrones de detección
- Redacción de reporte científico

**Entregables:**
1. Reporte ejecutivo (este documento + resultados)
2. Dataset completo (para futuras investigaciones)
3. Documentación técnica
4. Posible paper académico

---

## 📈 RESULTADOS ESPERADOS

### Datos Cuantitativos:
- **Tiempo promedio hasta ban** (con desviación estándar)
- **Tasa de éxito de publicación** (% posts que pasan)
- **Alcance promedio** (views por post antes de ban)
- **Correlación frecuencia-detección** (gráfica)

### Insights Cualitativos:
- Tipos de mensajes de advertencia
- Diferencias de comportamiento por horario
- Patrones específicos que disparan detección
- Comparación directa con TikTok

### Publicaciones Académicas:
Potencial paper para conferencias de:
- Social Computing (ACM)
- Web Science
- Computational Social Science

---

## 💰 PRESUPUESTO Y RECURSOS

### Recursos Técnicos (Ya disponibles ✅):
- Dispositivos Android: **Ya tenemos**
- Sistema base de automatización: **Ya desarrollado**
- Infraestructura de código: **Reutilizable al 70%**

### Recursos Nuevos Necesarios:

| Item | Cantidad | Costo | Justificación |
|------|----------|-------|---------------|
| **Cuentas Facebook** | 15 | $0 | Crear con emails desechables |
| **Videos de prueba** | 50 | $0 | Contenido genérico/stock |
| **SIM cards datos** | 5 (opcional) | $50 | Variar IPs si es necesario |
| **Tiempo desarrollo** | 60 horas | - | Programador (ya asignado) |
| **Tiempo análisis** | 20 horas | - | Investigador principal |

**Costo total estimado:** < $100 USD

---

## ⚠️ RIESGOS Y MITIGACIÓN

### Riesgos Técnicos:
| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| **Ban inmediato de cuentas** | Alta | Bajo | Tenemos cuentas desechables (esperado) |
| **Cambio de UI Facebook** | Media | Medio | Sistema con fallbacks múltiples |
| **Bloqueo de dispositivos** | Media | Medio | Usar dispositivos dedicados solo a experimento |
| **Resultados no concluyentes** | Baja | Medio | Diseño experimental robusto con grupo control |

### Riesgos Éticos:
❌ **No aplica** - Este es un experimento controlado con:
- Cuentas propias (no terceros)
- Sin spam a usuarios reales
- Contenido neutro (videos genéricos)
- Sin intención maliciosa
- Objetivo: Investigación académica

### Limitaciones Conocidas:
1. **Muestra pequeña** (15 cuentas) - pero suficiente para observar patrones
2. **Contenido controlado** - no prueba con contenido viral real
3. **No generalizable** - Facebook puede cambiar sistemas en el tiempo

---

## 📊 COMPARACIÓN CON SITUACIÓN ACTUAL

### Sistema TikTok (Actual):
✅ **Funciona:** Semanas/meses sin bans
✅ **Estable:** Arquitectura probada
✅ **Productivo:** Genera contenido y datos consistentemente
✅ **Escalable:** Múltiples dispositivos simultáneos

### Sistema Facebook (Propuesto):
❓ **Desconocido:** No hay datos sobre viabilidad
🔬 **Experimental:** Objetivo es investigar, no producir
📊 **Generará conocimiento:** Datos comparativos valiosos
⚡ **Rápido:** Reutiliza 70% del código existente

### ¿Por qué vale la pena?
1. **Bajo costo** (< $100, código reutilizable)
2. **Alto valor científico** (datos originales)
3. **Riesgo controlado** (cuentas desechables)
4. **Timeline corto** (6 semanas)
5. **Aprendizaje transferible** (aplicable a otras plataformas)

---

## 🎓 CONTRIBUCIÓN CIENTÍFICA

### Preguntas que responderemos:
1. ¿Qué tan diferentes son los sistemas anti-bot de plataformas mainstream?
2. ¿Existe una "tolerancia" cuantificable a automatización?
3. ¿Qué variables son más críticas para evitar detección?
4. ¿Son generalizables las técnicas de evasión entre plataformas?

### Aplicaciones futuras:
- Framework para evaluar sistemas anti-fraude
- Metodología replicable para Instagram, Twitter/X, LinkedIn
- Benchmark de robustez de plataformas sociales
- Guías para investigadores de social computing

---

## ✅ CRITERIOS DE ÉXITO

### Éxito Mínimo (debe cumplirse):
- [ ] Sistema publica al menos 10 videos exitosamente
- [ ] Recolectamos datos de al menos 5 bans/warnings
- [ ] Identificamos diferencias cuantificables con TikTok
- [ ] Documentación completa para replicación

### Éxito Esperado:
- [ ] Dataset completo de 8 cuentas x 14 días
- [ ] Correlaciones estadísticas significativas
- [ ] Reporte ejecutivo con recomendaciones
- [ ] Código publicable (open source)

### Éxito Excepcional:
- [ ] Paper aceptado en conferencia académica
- [ ] Framework generalizable a otras plataformas
- [ ] Identificación de vulnerabilidades específicas
- [ ] Contribución a comunidad de investigación

---

## 📝 PRÓXIMOS PASOS

### Si se aprueba el proyecto:

**Semana 1:**
1. Confirmar disponibilidad de dispositivos
2. Crear cuentas Facebook (batch de 15)
3. Preparar videos de prueba (50 videos stock)
4. Iniciar desarrollo del módulo Facebook

**Entregable Semana 1:** Demo funcional con 1 dispositivo

**Semana 2:**
5. Completar desarrollo
6. Pruebas con 3 dispositivos
7. Ajustar sistema de logging/métricas

**Entregable Semana 2:** Sistema listo para experimento

**Semana 3-5:**
8. Ejecutar experimento completo
9. Monitoreo diario de resultados
10. Ajustes en tiempo real si es necesario

**Entregable Semana 5:** Dataset experimental completo

**Semana 6:**
11. Análisis de datos
12. Redacción de reporte
13. Presentación de resultados

**Entregable Final:** Reporte ejecutivo + paper draft

---

## 🎯 CONCLUSIÓN

Este proyecto representa una **extensión natural** de nuestro trabajo actual en TikTok, con:
- **Bajo riesgo** (cuentas desechables, código reutilizable)
- **Alto valor científico** (datos comparativos originales)
- **Costo mínimo** (< $100)
- **Timeline realista** (6 semanas)

No buscamos crear un sistema productivo en Facebook (sabemos que probablemente será baneado), sino **entender científicamente las diferencias entre sistemas anti-bot** de plataformas líderes.

Los datos generados serán valiosos para:
1. Investigación académica en social computing
2. Comprensión de arquitecturas de detección
3. Benchmark de plataformas sociales
4. Futuras investigaciones en el área

---

## 📞 CONTACTO

**Responsable del proyecto:** [Tu nombre]
**Email:** [Tu email]
**Fecha de propuesta:** 13 de Diciembre, 2025

---

**ANEXOS:**
- Anexo A: Arquitectura técnica detallada (disponible bajo solicitud)
- Anexo B: Código fuente sistema TikTok (referencia)
- Anexo C: Protocolo de recolección de datos
- Anexo D: Consentimiento informado (si aplica)
