# 🚀 Instrucciones de Deploy Manual para Render

Dado que GitHub está bloqueando el push por protección de secretos, necesitas hacer el deploy manualmente en Render.

## **Opción 1: Deploy Directo en Render (Recomendado)**

### 1. **Ir al Dashboard de Render**
- Ve a: https://dashboard.render.com
- Busca tu servicio "aivoicelivekit" o similar

### 2. **Configurar Variables de Entorno**
En la sección "Environment" de tu servicio, agrega estas variables (usa tus credenciales reales):

```
LIVEKIT_URL=wss://your-livekit-instance.livekit.cloud
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
GROQ_API_KEY=your_groq_api_key
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number
```

### 3. **Subir Archivos Manualmente**
Copia y pega el contenido de estos archivos en Render:

#### **src/main.py**
```python
import asyncio
import logging
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli
from livekit import agents
from agent.voice_agent import entrypoint
from utils.config import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    logger.info("Starting LiveKit Voice Agent for Laura SDR...")
    logger.info(f"LiveKit URL: {config.livekit_url}")
    logger.info(f"Agent Name: {config.agent_name}")
    logger.info(f"VAD Config - Start: {config.vad_start_secs}s, Stop: {config.vad_stop_secs}s")

if __name__ == "__main__":
    # Use string value instead of enum for compatibility
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            worker_type="room",  # Fixed: use string instead of WorkerType.ROOM
            ws_url=config.livekit_url,
            api_key=config.livekit_api_key,
            api_secret=config.livekit_api_secret
        )
    )
```

#### **render.yaml**
```yaml
services:
  - type: web  # Changed from 'worker' to 'web' for SIP handling
    name: livekit-voice-agent
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "python src/main.py start"
    plan: starter
    envVars:
      - key: PYTHON_VERSION
        value: "3.12"
```

#### **requirements.txt**
```
livekit-agents==1.1.4
livekit-plugins-openai
livekit-plugins-silero
groq
elevenlabs
twilio
python-dotenv
pydantic
pydantic-settings
loguru
numpy
aiohttp
```

### 4. **Trigger Manual Deploy**
- En Render, ve a la sección "Deploys"
- Haz clic en "Deploy latest commit" o "Manual Deploy"

## **Opción 2: Usar GitHub sin Credenciales**

Si prefieres usar GitHub, puedes:

1. **Permitir el secreto temporalmente**:
   - Usa los enlaces que GitHub te dio para permitir los secretos
   - Haz el push
   - Luego revierte el commit con credenciales

2. **O crear una nueva rama**:
   ```bash
   git checkout -b deploy-without-secrets
   git push origin deploy-without-secrets
   ```

## **Verificación Post-Deploy**

Después del deploy, verifica en los logs de Render:

✅ **Logs Esperados**:
```
INFO:__main__:Starting LiveKit Voice Agent for Laura SDR...
INFO:livekit.agents:starting worker
INFO:livekit.agents:registered worker
```

❌ **NO deberías ver**:
```
AttributeError: 'str' object has no attribute 'value'
```

## **Probar la Llamada**

Una vez deployado, ejecuta:
```bash
python simple_test_call.py --to +573153041548
```

**Flujo esperado**:
1. "Connecting you to Laura SDR voice assistant. Please wait a moment."
2. Laura: "¡Hola! Soy Laura de TDX. Ayudo a líderes empresariales con retos tecnológicos..."

¡El deploy manual debería resolver el problema de las credenciales!
