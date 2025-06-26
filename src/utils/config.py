import os
from typing import Optional
from pydantic import BaseSettings, Field
from dotenv import load_dotenv

load_dotenv()

class Config(BaseSettings):
    # LiveKit Configuration
    livekit_url: str = Field(default="wss://forceapp-jaadrt7a.livekit.cloud", env="LIVEKIT_URL")
    livekit_api_key: str = Field(env="LIVEKIT_API_KEY")
    livekit_api_secret: str = Field(env="LIVEKIT_API_SECRET")
    
    # SIP Configuration
    outbound_trunk_id: str = Field(default="ST_GZ4Bo8JH4ly7", env="OUTBOUND_TRUNK_ID")
    inbound_trunk_id: str = Field(default="ST_62xofSEmFyRe", env="INBOUND_TRUNK_ID")
    sip_uri: str = Field(default="6jf4gz4gbna.sip.livekit.cloud", env="SIP_URI")
    
    # Agent Configuration
    agent_name: str = Field(default="laura-sdr", env="AGENT_NAME")
    
    # API Keys
    groq_api_key: str = Field(env="GROQ_API_KEY")
    elevenlabs_api_key: str = Field(env="ELEVENLABS_API_KEY")
    openai_api_key: str = Field(env="OPENAI_API_KEY")
    
    # VAD Configuration (IDENTICAL to Pipecat)
    vad_confidence: float = Field(default=0.8, env="VAD_CONFIDENCE")
    vad_start_secs: float = Field(default=0.2, env="VAD_START_SECS")
    vad_stop_secs: float = Field(default=0.8, env="VAD_STOP_SECS")
    vad_min_volume: float = Field(default=0.6, env="VAD_MIN_VOLUME")
    
    # TTS Configuration (IDENTICAL to Pipecat)
    elevenlabs_voice_id: str = Field(default="qHkrJuifPpn95wK3rm2A", env="ELEVENLABS_VOICE_ID")
    elevenlabs_model: str = Field(default="eleven_flash_v2_5", env="ELEVENLABS_MODEL")
    elevenlabs_stability: float = Field(default=0.2, env="ELEVENLABS_STABILITY")
    elevenlabs_similarity_boost: float = Field(default=0.30, env="ELEVENLABS_SIMILARITY_BOOST")
    elevenlabs_style: float = Field(default=1.0, env="ELEVENLABS_STYLE")
    elevenlabs_use_speaker_boost: bool = Field(default=False, env="ELEVENLABS_USE_SPEAKER_BOOST")
    elevenlabs_optimize_streaming_latency: int = Field(default=4, env="ELEVENLABS_OPTIMIZE_STREAMING_LATENCY")
    
    # OpenAI TTS Fallback
    openai_tts_voice: str = Field(default="nova", env="OPENAI_TTS_VOICE")
    openai_tts_model: str = Field(default="tts-1", env="OPENAI_TTS_MODEL")
    openai_tts_language: str = Field(default="es", env="OPENAI_TTS_LANGUAGE")
    
    # Groq Configuration
    groq_stt_model: str = Field(default="whisper-large-v3-turbo", env="GROQ_STT_MODEL")
    groq_llm_model: str = Field(default="llama-3.3-70b-versatile", env="GROQ_LLM_MODEL")
    
    # Laura SDR System Prompt (IDENTICAL to Pipecat)
    system_prompt: str = Field(
        default="""For Meta's Llama 70B models, a more direct and concise prompt that distills the core instructions and persona tends to work best. Llama models are good at following clear, brief directives.

---
### **Prompt para Laura (Llama 70B)**

**Rol**: Laura, consultora IA de TDX. Directa, audaz, educada, mentalidad vendedora.

**Estilo**: Voz rápida, respuestas de una frase. Profesional, concisa.

**Objetivo**: Identificar dolor tech, proponer solución TDX (IA, automatización, MVP 15 días), agendar reunión de 25 min.

**Guía**:
* **Inicio**: Saluda, preséntate ("Laura, TDX").
* **Propósito**: Menciona retos clave de líderes (ej. "atención lenta, sobrecarga, innovar rápido"). Pregunta si resuena.
* **Identificación**: Haz preguntas muy cortas sobre el dolor relevante.
* **Solución**: Conecta el dolor a una oferta TDX.
* **Cierre**: Agenda 25 min para ver resultados de casos similares.

**Reglas**:
* **¡No uses mis palabras exactas!** Improvisa con tu estilo.
* Espera al usuario. Responde solo cuando hablen.
* Escucha 70%, habla 30%.
* Lenguaje profesional. Números en palabras.
* ¡Tu meta es agendar la reunión!

---""",
        env="SYSTEM_PROMPT"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = False

config = Config()