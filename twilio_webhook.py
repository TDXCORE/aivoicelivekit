#!/usr/bin/env python3
"""
Twilio Webhook Handler for LiveKit Integration

This module handles incoming Twilio webhook calls and connects them to LiveKit rooms.
It should be integrated into your main FastAPI application on Render.

Usage:
    Add these routes to your main FastAPI app or run as standalone service.
"""

from fastapi import FastAPI, Request, Response
from fastapi.responses import Response as FastAPIResponse
import logging
from livekit import api
import os
from typing import Optional
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

class TwilioWebhookHandler:
    def __init__(self):
        self.livekit_url = os.getenv('LIVEKIT_URL', 'wss://forceapp-jaadrt7a.livekit.cloud')
        self.livekit_api_key = os.getenv('LIVEKIT_API_KEY')
        self.livekit_api_secret = os.getenv('LIVEKIT_API_SECRET')
        
        if not all([self.livekit_api_key, self.livekit_api_secret]):
            raise ValueError("LIVEKIT_API_KEY and LIVEKIT_API_SECRET must be set")
        
        self.livekit_api = api.LiveKitAPI(
            url=self.livekit_url,
            api_key=self.livekit_api_key,
            api_secret=self.livekit_api_secret
        )

    async def handle_incoming_call(self, request: Request) -> FastAPIResponse:
        """Handle incoming Twilio call and connect to LiveKit"""
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
        
        try:
            # Ensure LiveKit room exists
            await self._ensure_room_exists(room_name)
            
            # Generate access token for the call
            token = await self._generate_access_token(room_name, call_sid)
            
            # Create TwiML response to connect to LiveKit
            twiml = self._create_connect_twiml(room_name, token)
            
            return FastAPIResponse(
                content=twiml,
                media_type="application/xml"
            )
            
        except Exception as e:
            logger.error(f"Error handling incoming call: {e}")
            return FastAPIResponse(
                content=self._create_error_twiml(),
                media_type="application/xml"
            )

    async def _ensure_room_exists(self, room_name: str):
        """Ensure the LiveKit room exists"""
        try:
            await self.livekit_api.room.create_room(
                api.CreateRoomRequest(name=room_name)
            )
            logger.info(f"Created or verified room: {room_name}")
        except Exception as e:
            # Room might already exist, which is fine
            logger.debug(f"Room creation result: {e}")

    async def _generate_access_token(self, room_name: str, participant_identity: str) -> str:
        """Generate LiveKit access token for the participant"""
        from livekit import AccessToken, VideoGrants
        
        token = AccessToken(self.livekit_api_key, self.livekit_api_secret)
        token.with_identity(participant_identity)
        token.with_name(f"Twilio Call {participant_identity}")
        token.with_grants(VideoGrants(
            room_join=True,
            room=room_name,
            can_publish=True,
            can_subscribe=True
        ))
        
        return token.to_jwt()

    def _create_connect_twiml(self, room_name: str, token: str) -> str:
        """Create TwiML to connect call to LiveKit via WebRTC"""
        # Create TwiML that connects to LiveKit
        twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">Connecting you to Laura SDR voice assistant. Please wait a moment.</Say>
    <Connect>
        <Stream url="wss://{self._get_websocket_url(room_name, token)}" />
    </Connect>
</Response>'''
        return twiml

    def _get_websocket_url(self, room_name: str, token: str) -> str:
        """Get WebSocket URL for LiveKit connection"""
        # Extract hostname from LiveKit URL
        livekit_host = self.livekit_url.replace('wss://', '').replace('ws://', '')
        return f"{livekit_host}/ws?room={room_name}&token={token}"

    def _create_error_twiml(self) -> str:
        """Create error TwiML response"""
        return '''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">Sorry, there was an error connecting to the voice assistant. Please try again later.</Say>
    <Hangup />
</Response>'''

    async def handle_call_status(self, request: Request) -> FastAPIResponse:
        """Handle Twilio call status updates"""
        form_data = await request.form()
        
        call_sid = form_data.get('CallSid')
        call_status = form_data.get('CallStatus')
        
        logger.info(f"Call status update: {call_sid} -> {call_status}")
        
        # You can add logic here to handle different call statuses
        # For example, cleanup when call ends
        if call_status in ['completed', 'failed', 'canceled']:
            logger.info(f"Call {call_sid} ended with status: {call_status}")
            # Optionally clean up LiveKit room
        
        return FastAPIResponse(content="OK", media_type="text/plain")


# FastAPI app instance for standalone usage
app = FastAPI(title="Twilio-LiveKit Webhook Handler")
webhook_handler = TwilioWebhookHandler()

@app.post("/webhook/twilio")
async def twilio_webhook(request: Request):
    """Handle incoming Twilio calls"""
    return await webhook_handler.handle_incoming_call(request)

@app.post("/webhook/twilio/status")
async def twilio_status_webhook(request: Request):
    """Handle Twilio call status updates"""
    return await webhook_handler.handle_call_status(request)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "twilio-livekit-webhook"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)