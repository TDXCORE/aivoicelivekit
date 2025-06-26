import asyncio
from typing import AsyncGenerator, Optional
from groq import AsyncGroq
from loguru import logger
from ..utils.config import config

class GroqSTTService:
    def __init__(self):
        self.client = AsyncGroq(api_key=config.groq_api_key)
        self.model = config.groq_stt_model
        
    async def transcribe(self, audio_data: bytes) -> Optional[str]:
        try:
            transcription = await self.client.audio.transcriptions.create(
                file=("audio.wav", audio_data),
                model=self.model,
                language="es"
            )
            return transcription.text
        except Exception as e:
            logger.error(f"STT transcription error: {e}")
            return None

class GroqLLMService:
    def __init__(self):
        self.client = AsyncGroq(api_key=config.groq_api_key)
        self.model = config.groq_llm_model
        self.conversation_history = []
        
    async def generate_response(self, user_input: str) -> AsyncGenerator[str, None]:
        try:
            self.conversation_history.append({"role": "user", "content": user_input})
            
            messages = [
                {"role": "system", "content": config.system_prompt},
                *self.conversation_history
            ]
            
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=150,
                stream=True
            )
            
            full_response = ""
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield content
            
            self.conversation_history.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            yield "Disculpa, hubo un problema técnico. ¿Puedes repetir?"
    
    def clear_history(self):
        self.conversation_history = []