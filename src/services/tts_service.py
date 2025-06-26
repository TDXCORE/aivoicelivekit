import asyncio
from typing import AsyncGenerator, Optional
from elevenlabs.client import AsyncElevenLabs
from elevenlabs import Voice, VoiceSettings
import openai
from loguru import logger
from ..utils.config import config

class UltraFastTTSService:
    def __init__(self):
        self.elevenlabs_client = AsyncElevenLabs(api_key=config.elevenlabs_api_key)
        self.openai_client = openai.AsyncOpenAI(api_key=config.openai_api_key)
        
        self.elevenlabs_voice = Voice(
            voice_id=config.elevenlabs_voice_id,
            settings=VoiceSettings(
                stability=config.elevenlabs_stability,
                similarity_boost=config.elevenlabs_similarity_boost,
                style=config.elevenlabs_style,
                use_speaker_boost=config.elevenlabs_use_speaker_boost
            )
        )
        
    async def synthesize_speech(self, text: str, use_streaming: bool = True) -> AsyncGenerator[bytes, None]:
        try:
            async for chunk in self._elevenlabs_synthesis(text, use_streaming):
                yield chunk
        except Exception as e:
            logger.warning(f"ElevenLabs TTS failed, falling back to OpenAI: {e}")
            try:
                async for chunk in self._openai_synthesis(text):
                    yield chunk
            except Exception as fallback_error:
                logger.error(f"Both TTS services failed: {fallback_error}")
                return
    
    async def _elevenlabs_synthesis(self, text: str, use_streaming: bool = True) -> AsyncGenerator[bytes, None]:
        if use_streaming:
            audio_stream = await self.elevenlabs_client.generate(
                text=text,
                voice=self.elevenlabs_voice,
                model=config.elevenlabs_model,
                stream=True,
                optimize_streaming_latency=config.elevenlabs_optimize_streaming_latency
            )
            
            async for chunk in audio_stream:
                if chunk:
                    yield chunk
        else:
            audio = await self.elevenlabs_client.generate(
                text=text,
                voice=self.elevenlabs_voice,
                model=config.elevenlabs_model
            )
            yield audio
    
    async def _openai_synthesis(self, text: str) -> AsyncGenerator[bytes, None]:
        response = await self.openai_client.audio.speech.create(
            model=config.openai_tts_model,
            voice=config.openai_tts_voice,
            input=text,
            response_format="mp3"
        )
        
        async for chunk in response.iter_bytes():
            yield chunk