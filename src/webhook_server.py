#!/usr/bin/env python3
"""
Webhook server for handling Twilio calls and connecting them to LiveKit
This runs alongside the main voice agent to handle incoming calls
"""

from fastapi import FastAPI, Request, Response
from fastapi.responses import Response as FastAPIResponse
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

app = FastAPI(title="Twilio-LiveKit Webhook Handler")

@app.post("/webhook/twilio")
async def twilio_webhook(request: Request):
    """Handle incoming Twilio calls"""
    try:
        form_data = await request.form()
        
        # Extract Twilio call information
        call_sid = form_data.get('CallSid')
        from_number = form_data.get('From')
        to_number = form_data.get('To')
        call_status = form_data.get('CallStatus')
        
        # Extract room name from query parameters
        room_name = request.query_params.get('room', f'twilio-call-{call_sid}')
        
        logger.info(f"Incoming Twilio call: {call_sid} from {from_number} to {to_number}")
        logger.info(f"Call status: {call_status}, Room: {room_name}")
        
        # Create TwiML response that says hello and hangs up for now
        # This is a simple test - later you can connect to LiveKit
        twiml = '''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">Hello! This is Laura SDR voice assistant. The integration is working! I will hang up now for testing purposes.</Say>
    <Hangup />
</Response>'''
        
        return FastAPIResponse(
            content=twiml,
            media_type="application/xml"
        )
        
    except Exception as e:
        logger.error(f"Error handling incoming call: {e}")
        
        # Return error TwiML
        error_twiml = '''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">Sorry, there was an error with the voice assistant. Please try again later.</Say>
    <Hangup />
</Response>'''
        
        return FastAPIResponse(
            content=error_twiml,
            media_type="application/xml"
        )

@app.post("/webhook/twilio/status")
async def twilio_status_webhook(request: Request):
    """Handle Twilio call status updates"""
    try:
        form_data = await request.form()
        
        call_sid = form_data.get('CallSid')
        call_status = form_data.get('CallStatus')
        
        logger.info(f"Call status update: {call_sid} -> {call_status}")
        
        return FastAPIResponse(content="OK", media_type="text/plain")
        
    except Exception as e:
        logger.error(f"Error handling status update: {e}")
        return FastAPIResponse(content="ERROR", media_type="text/plain")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "twilio-webhook-handler"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Twilio-LiveKit Webhook Handler", "status": "running"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)