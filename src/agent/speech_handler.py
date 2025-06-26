import asyncio
from typing import AsyncGenerator, Optional
from loguru import logger
from ..services.groq_service import GroqSTTService, GroqLLMService
from ..services.tts_service import UltraFastTTSService

class SpeechHandler:
    def __init__(self):
        self.stt_service = GroqSTTService()
        self.llm_service = GroqLLMService()
        self.tts_service = UltraFastTTSService()
        self.is_processing = False
        
    async def process_speech_pipeline(self, audio_data: bytes) -> AsyncGenerator[bytes, None]:
        if self.is_processing:
            logger.debug("Speech pipeline already processing, skipping")
            return
            
        self.is_processing = True
        try:
            transcribed_text = await self.stt_service.transcribe(audio_data)
            if not transcribed_text:
                logger.debug("No transcription result")
                return
                
            logger.info(f"Transcribed: {transcribed_text}")
            
            response_text = ""
            async for chunk in self.llm_service.generate_response(transcribed_text):
                response_text += chunk
            
            if response_text:
                logger.info(f"LLM Response: {response_text}")
                async for audio_chunk in self.tts_service.synthesize_speech(response_text):
                    yield audio_chunk
                    
        except Exception as e:
            logger.error(f"Speech pipeline error: {e}")
        finally:
            self.is_processing = False
    
    async def handle_interruption(self):
        if self.is_processing:
            logger.info("Handling speech interruption")
            self.is_processing = False
    
    def reset_conversation(self):
        self.llm_service.clear_history()
        logger.info("Conversation history cleared")