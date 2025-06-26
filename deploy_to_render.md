# Deploy de Cambios a Render

## 🚀 Pasos para Subir los Cambios

### 1. **Verificar Cambios Locales**
Los siguientes archivos han sido modificados y necesitan ser subidos a Render:

- ✅ `src/main.py` - Corregido worker_type compatibility
- ✅ `render.yaml` - Cambiado a web service
- ✅ `requirements.txt` - Versiones fijas de LiveKit
- ✅ `src/agent/voice_agent.py` - Implementación completa de Laura SDR
- ✅ `simple_test_call.py` - Enfoque SIP correcto
- ✅ `.env.test` - Variables de entorno completas

### 2. **Comandos Git para Deploy**

```bash
# Agregar todos los cambios
git add .

# Commit con mensaje descriptivo
git commit -m "Fix: Twilio-LiveKit SIP integration - Laura SDR agent working

- Fixed LiveKit agents compatibility (worker_type string)
- Changed render.yaml to web service for SIP handling
- Implemented complete Laura SDR conversation logic
- Updated simple_test_call.py to use SIP dialing
- Pinned LiveKit agents version to 1.1.4
- Added complete environment variables"

# Push a la rama principal (esto triggerea el deploy en Render)
git push origin main
```

### 3. **Verificar Deploy en Render**

1. Ve a tu dashboard de Render: https://dashboard.render.com
2. Busca tu servicio "livekit-voice-agent"
3. Verifica que el deploy se inicie automáticamente
4. Monitorea los logs para ver:
   - ✅ Instalación de dependencias
   - ✅ Inicio del agente sin errores de compatibilidad
   - ✅ Registro exitoso del worker

### 4. **Logs Esperados Después del Deploy**

```
INFO:__main__:Starting LiveKit Voice Agent for Laura SDR...
INFO:livekit.agents:starting worker
INFO:livekit.agents:registered worker
```

**NO deberías ver**:
```
AttributeError: 'str' object has no attribute 'value'
```

### 5. **Probar Después del Deploy**

```bash
# Hacer una llamada de prueba
python simple_test_call.py --to +573153041548
```

**Flujo esperado**:
1. Escuchas: "Connecting you to Laura SDR voice assistant. Please wait a moment."
2. Después de unos segundos, Laura debería decir: "¡Hola! Soy Laura de TDX. Ayudo a líderes empresariales con retos tecnológicos..."

### 6. **Troubleshooting**

Si Laura no habla después del mensaje inicial:

1. **Verificar logs de Render**:
   ```
   INFO:__main__:Detected SIP call room: call-caller-XXXXXX
   INFO:__main__:Participant connected to room: caller-XXXXXX
   INFO:__main__:Laura's greeting generated successfully
   ```

2. **Verificar variables de entorno en Render**:
   - GROQ_API_KEY debe estar configurada
   - ELEVENLABS_API_KEY debe estar configurada
   - LIVEKIT_API_KEY y LIVEKIT_API_SECRET deben estar configuradas

3. **Si hay errores de TTS**:
   - Verificar que ELEVENLABS_API_KEY sea válida
   - Verificar que el voice_id sea correcto

## 🎯 Resultado Esperado

Después del deploy exitoso:
- ✅ Agente se inicia sin errores de compatibilidad
- ✅ Llamadas SIP se conectan correctamente
- ✅ Laura saluda automáticamente al conectarse
- ✅ Laura responde a preguntas usando Groq LLM
- ✅ TTS funciona con ElevenLabs

## 📞 Flujo de Llamada Completo

1. **Usuario llama** → Twilio recibe
2. **Twilio** → Conecta via SIP a LiveKit
3. **LiveKit** → Crea sala `call-{participant.identity}`
4. **Agente** → Se une a la sala automáticamente
5. **Laura** → Saluda: "¡Hola! Soy Laura de TDX..."
6. **Usuario habla** → STT transcribe
7. **Groq LLM** → Genera respuesta de Laura
8. **ElevenLabs** → Convierte a voz
9. **Usuario escucha** → Respuesta de Laura

¡Ahora ejecuta los comandos git para hacer el deploy!
