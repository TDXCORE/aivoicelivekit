#!/usr/bin/env python3
import asyncio
import logging
from livekit.agents import WorkerOptions, cli
from src.agent.voice_agent import entrypoint
from src.utils.config import config
from src.utils.logger import setup_logger

def main():
    setup_logger()
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting LiveKit Voice Agent for Laura SDR...")
    logger.info(f"LiveKit URL: {config.livekit_url}")
    logger.info(f"Agent Name: {config.agent_name}")
    logger.info(f"VAD Config - Start: {config.vad_start_secs}s, Stop: {config.vad_stop_secs}s")
    
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            ws_url=config.livekit_url,
            api_key=config.livekit_api_key,
            api_secret=config.livekit_api_secret,
            worker_type="voice_agent"
        )
    )

if __name__ == "__main__":
    main()