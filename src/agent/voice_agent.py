import asyncio
from typing import Optional
from livekit import rtc
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli, llm
from livekit.agents.voice_assistant import VoiceAssistant
from livekit.agents.stt import StreamAdapter
from livekit.agents.tts import StreamAdapter as TTSStreamAdapter
from livekit.plugins import openai, silero
import numpy as np
from loguru import logger

from ..services.groq_service import GroqSTTService, GroqLLMService
from ..services.tts_service import UltraFastTTSService
from ..utils.config import config

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
        
    async def on_participant_connected(self, participant: rtc.RemoteParticipant):
        logger.info(f"Participant connected: {participant.identity}")
        
        self.voice_assistant = VoiceAssistant(
            vad=self.vad,
            stt=self.groq_stt,
            llm=self.groq_llm,
            tts=self.fast_tts,
            chat_ctx=[
                llm.ChatMessage(
                    role="system",
                    content=config.system_prompt
                ),
                llm.ChatMessage(
                    role="assistant", 
                    content="¡Hola! Soy Laura de TDX. ¿Cómo estás? Te llamo porque sé que muchos líderes enfrentan retos como atención lenta al cliente, sobrecarga operativa o la necesidad de innovar rápido. ¿Alguno de estos te resuena?"
                )
            ]
        )
        
        await self.voice_assistant.start(participant.tracks[0] if participant.tracks else None)
        logger.info("Voice assistant started for participant")
    
    async def on_participant_disconnected(self, participant: rtc.RemoteParticipant):
        logger.info(f"Participant disconnected: {participant.identity}")
        if self.voice_assistant:
            await self.voice_assistant.stop()
            self.voice_assistant = None
    
    async def handle_audio_stream(self, audio_track: rtc.AudioTrack):
        logger.info("Starting audio stream handling")
        
        async for frame in audio_track:
            if self.voice_assistant:
                await self.voice_assistant.push_frame(frame)

async def entrypoint(ctx: JobContext):
    logger.info(f"Connecting to room: {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    
    agent = VoiceAgent()
    
    @ctx.room.on("participant_connected")
    def on_participant_connected(participant: rtc.RemoteParticipant):
        asyncio.create_task(agent.on_participant_connected(participant))
    
    @ctx.room.on("participant_disconnected") 
    def on_participant_disconnected(participant: rtc.RemoteParticipant):
        asyncio.create_task(agent.on_participant_disconnected(participant))
    
    @ctx.room.on("track_subscribed")
    def on_track_subscribed(track: rtc.Track, publication: rtc.TrackPublication, participant: rtc.RemoteParticipant):
        if track.kind == rtc.TrackKind.KIND_AUDIO:
            asyncio.create_task(agent.handle_audio_stream(track))
    
    logger.info("Voice agent initialized and listening for participants")

if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            ws_url=config.livekit_url,
            api_key=config.livekit_api_key,
            api_secret=config.livekit_api_secret
        )
    )