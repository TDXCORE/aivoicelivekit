#!/usr/bin/env python3
"""
Combined server that runs both the webhook handler and the voice agent
"""

import asyncio
import logging
import threading
import uvicorn
import os
from webhook_server import app as webhook_app
from main import main as voice_agent_main

def run_webhook_server():
    """Run the webhook server in a separate thread"""
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(webhook_app, host="0.0.0.0", port=port, log_level="info")

def run_voice_agent():
    """Run the voice agent"""
    voice_agent_main()

def main():
    """Run both services"""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting combined Twilio Webhook + LiveKit Voice Agent server...")
    
    # Start webhook server in a separate thread
    webhook_thread = threading.Thread(target=run_webhook_server, daemon=True)
    webhook_thread.start()
    
    logger.info("Webhook server started in background thread")
    
    # Run voice agent in main thread
    logger.info("Starting voice agent...")
    run_voice_agent()

if __name__ == "__main__":
    main()