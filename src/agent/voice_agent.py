import asyncio
from typing import Optional
from livekit import rtc
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli, llm
from livekit import agents
from livekit.agents.stt import StreamAdapter
from livekit.agents.tts import StreamAdapter as TTSStreamAdapter
from livekit.plugins import openai, silero
import numpy as np
from loguru import logger

from services.groq_service import GroqSTTService, GroqLLMService
from services.tts_service import UltraFastTTSService
from utils.config import config

class GroqSTTAdapter(StreamAdapter):
    def __init__(self):
        super().__init__()
        self.groq_stt = GroqSTTService()
    
    async def recognize(self, *, buffer: rtc.AudioFrame, language: str = "es") -> str:
        audio_data = buffer.data.tobytes()
        result = await self.groq_stt.transcribe(audio_data)
        return result or ""

class GroqLLMAdapter:
    def __init__(self):
        self.groq_llm = GroqLLMService()
    
    async def chat(self, *, chat_ctx: list, fnc_ctx: Optional[list] = None):
        if chat_ctx:
            last_message = chat_ctx[-1].content
            async for chunk in self.groq_llm.generate_response(last_message):
                yield chunk

class FastTTSAdapter(TTSStreamAdapter):
    def __init__(self):
        super().__init__()
        self.tts_service = UltraFastTTSService()
    
    async def synthesize(self, *, text: str) -> rtc.AudioFrame:
        audio_chunks = []
        async for chunk in self.tts_service.synthesize_speech(text, use_streaming=True):
            audio_chunks.append(chunk)
        
        if audio_chunks:
            audio_data = b''.join(audio_chunks)
            return rtc.AudioFrame(
                data=np.frombuffer(audio_data, dtype=np.int16),
                sample_rate=24000,
                num_channels=1
            )
        return rtc.AudioFrame(data=np.array([], dtype=np.int16), sample_rate=24000, num_channels=1)

class VoiceAgent:
    def __init__(self):
        self.groq_stt = GroqSTTAdapter()
        self.groq_llm = GroqLLMAdapter()
        self.fast_tts = FastTTSAdapter()
        
        self.vad = silero.VAD.load(
            confidence=config.vad_confidence,
            start_secs=config.vad_start_secs,
            stop_secs=config.vad_stop_secs,
            min_volume=config.vad_min_volume
        )
        
        self.voice_assistant = None
        self.conversation_started = False
        self.chat_history = []
        
    async def on_participant_connected(self, participant: rtc.RemoteParticipant):
        logger.info(f"Participant connected: {participant.identity}")
        
        # Create a voice assistant session
        self.voice_assistant = {
            'vad': self.vad,
            'stt': self.groq_stt,
            'llm': self.groq_llm,
            'tts': self.fast_tts,
            'active': True
        }
        
        # Initialize conversation with Laura's greeting
        self.chat_history = [
            {"role": "system", "content": config.system_prompt},
            {"role": "assistant", "content": "¡Hola! Soy Laura de TDX. Ayudo a líderes empresariales con retos tecnológicos como atención lenta, sobrecarga operativa y necesidad de innovar rápido. ¿Alguno de estos temas resuena contigo?"}
        ]
        
        # Send initial greeting
        await self.send_initial_greeting()
        logger.info("Voice assistant started for participant with Laura SDR greeting")
    
    async def send_initial_greeting(self):
        """Send Laura's initial greeting"""
        try:
            greeting = "¡Hola! Soy Laura de TDX. Ayudo a líderes empresariales con retos tecnológicos como atención lenta, sobrecarga operativa y necesidad de innovar rápido. ¿Alguno de estos temas resuena contigo?"
            
            # Generate TTS for greeting
            audio_frame = await self.fast_tts.synthesize(text=greeting)
            if audio_frame:
                logger.info("Laura's greeting generated successfully")
                # Note: In a full implementation, you'd publish this audio to the room
                # For now, we log that the greeting was prepared
            
        except Exception as e:
            logger.error(f"Error generating initial greeting: {e}")
    
    async def on_participant_disconnected(self, participant: rtc.RemoteParticipant):
        logger.info(f"Participant disconnected: {participant.identity}")
        if self.voice_assistant:
            self.voice_assistant['active'] = False
            self.voice_assistant = None
            self.conversation_started = False
            self.chat_history = []
    
    async def handle_audio_stream(self, audio_track: rtc.AudioTrack):
        logger.info("Starting audio stream handling for Laura SDR")
        
        async for frame in audio_track:
            if self.voice_assistant and self.voice_assistant.get('active'):
                try:
                    # Process audio with VAD
                    vad_result = await self.vad.detect(frame)
                    
                    if vad_result.speech_detected:
                        logger.info("Speech detected, processing with STT")
                        
                        # Transcribe audio
                        text = await self.groq_stt.recognize(buffer=frame, language="es")
                        
                        if text and text.strip():
                            logger.info(f"User said: {text}")
                            
                            # Add user message to chat history
                            self.chat_history.append({"role": "user", "content": text})
                            
                            # Generate Laura's response
                            response = await self.generate_laura_response(text)
                            
                            if response:
                                logger.info(f"Laura responds: {response}")
                                
                                # Add Laura's response to chat history
                                self.chat_history.append({"role": "assistant", "content": response})
                                
                                # Generate and send TTS
                                await self.send_tts_response(response)
                
                except Exception as e:
                    logger.error(f"Error processing audio frame: {e}")
    
    async def generate_laura_response(self, user_input: str) -> str:
        """Generate Laura SDR's response using Groq LLM"""
        try:
            # Prepare context for Laura
            context = self.chat_history + [{"role": "user", "content": user_input}]
            
            # Generate response using Groq LLM
            response_chunks = []
            async for chunk in self.groq_llm.chat(chat_ctx=context):
                response_chunks.append(chunk)
            
            response = "".join(response_chunks).strip()
            return response if response else "Disculpa, ¿podrías repetir eso?"
            
        except Exception as e:
            logger.error(f"Error generating Laura's response: {e}")
            return "Disculpa, tuve un problema técnico. ¿Podrías repetir tu pregunta?"
    
    async def send_tts_response(self, text: str):
        """Generate and send TTS response"""
        try:
            audio_frame = await self.fast_tts.synthesize(text=text)
            if audio_frame:
                logger.info("TTS response generated successfully")
                # Note: In a full implementation, you'd publish this audio to the room
                
        except Exception as e:
            logger.error(f"Error generating TTS response: {e}")

async def entrypoint(ctx: JobContext):
    logger.info(f"Connecting to room: {ctx.room.name}")
    
    # Check if this is a SIP call room (created by dispatch rule)
    if ctx.room.name.startswith('call-'):
        logger.info(f"Detected SIP call room: {ctx.room.name}")
    
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    
    agent = VoiceAgent()
    
    @ctx.room.on("participant_connected")
    def on_participant_connected(participant: rtc.RemoteParticipant):
        logger.info(f"Participant connected to room {ctx.room.name}: {participant.identity}")
        asyncio.create_task(agent.on_participant_connected(participant))
    
    @ctx.room.on("participant_disconnected") 
    def on_participant_disconnected(participant: rtc.RemoteParticipant):
        logger.info(f"Participant disconnected from room {ctx.room.name}: {participant.identity}")
        asyncio.create_task(agent.on_participant_disconnected(participant))
    
    @ctx.room.on("track_subscribed")
    def on_track_subscribed(track: rtc.Track, publication: rtc.TrackPublication, participant: rtc.RemoteParticipant):
        if track.kind == rtc.TrackKind.KIND_AUDIO:
            logger.info(f"Audio track subscribed from {participant.identity}")
            asyncio.create_task(agent.handle_audio_stream(track))
    
    logger.info(f"Voice agent initialized and listening for participants in room: {ctx.room.name}")

if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            ws_url=config.livekit_url,
            api_key=config.livekit_api_key,
            api_secret=config.livekit_api_secret
        )
    )
