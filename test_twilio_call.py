#!/usr/bin/env python3
"""
Twilio to LiveKit Voice Bot Test Script

This script creates a test call using Twilio that connects to your LiveKit voice agent
running on Render. It demonstrates the complete integration flow:
Twilio Phone Call -> LiveKit Room -> Voice Agent on Render

Prerequisites:
1. Twilio Account SID and Auth Token
2. LiveKit API Key and Secret  
3. Voice agent deployed and running on Render
4. Twilio phone number configured

Usage:
    python test_twilio_call.py --to +1234567890
"""

import argparse
import asyncio
import os
from twilio.rest import Client
from livekit import api
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.test')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TwilioLiveKitTester:
    def __init__(self):
        # Twilio credentials
        self.twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.twilio_phone_number = os.getenv('TWILIO_PHONE_NUMBER')
        
        # LiveKit credentials
        self.livekit_url = os.getenv('LIVEKIT_URL', 'wss://forceapp-jaadrt7a.livekit.cloud')
        self.livekit_api_key = os.getenv('LIVEKIT_API_KEY')
        self.livekit_api_secret = os.getenv('LIVEKIT_API_SECRET')
        
        # Render webhook URL (where your voice agent is deployed)
        self.render_webhook_url = os.getenv('RENDER_WEBHOOK_URL', 'https://aivoicelivekit.onrender.com')
        
        self._validate_credentials()
        
        # Initialize clients
        self.twilio_client = Client(self.twilio_account_sid, self.twilio_auth_token)
        self.livekit_api = api.LiveKitAPI(
            url=self.livekit_url,
            api_key=self.livekit_api_key,
            api_secret=self.livekit_api_secret
        )

    def _validate_credentials(self):
        """Validate that all required credentials are present"""
        required_vars = [
            ('TWILIO_ACCOUNT_SID', self.twilio_account_sid),
            ('TWILIO_AUTH_TOKEN', self.twilio_auth_token),
            ('TWILIO_PHONE_NUMBER', self.twilio_phone_number),
            ('LIVEKIT_API_KEY', self.livekit_api_key),
            ('LIVEKIT_API_SECRET', self.livekit_api_secret)
        ]
        
        missing = [name for name, value in required_vars if not value]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

    async def create_livekit_room(self, room_name: str) -> str:
        """Create a LiveKit room for the call"""
        try:
            room = await self.livekit_api.room.create_room(
                api.CreateRoomRequest(name=room_name)
            )
            logger.info(f"Created LiveKit room: {room.name}")
            return room.name
        except Exception as e:
            logger.error(f"Failed to create LiveKit room: {e}")
            raise

    def generate_twiml_webhook_url(self, room_name: str) -> str:
        """Generate the TwiML webhook URL that connects to LiveKit"""
        # This URL should point to your Render deployment with room parameter
        return f"{self.render_webhook_url}/webhook/twilio?room={room_name}"

    def make_test_call(self, to_number: str, room_name: str = None) -> str:
        """Make a test call using Twilio"""
        if not room_name:
            import time
            room_name = f"test-call-{int(time.time())}"
        
        webhook_url = self.generate_twiml_webhook_url(room_name)
        
        try:
            call = self.twilio_client.calls.create(
                to=to_number,
                from_=self.twilio_phone_number,
                url=webhook_url,
                method='POST'
            )
            
            logger.info(f"Call initiated successfully!")
            logger.info(f"Call SID: {call.sid}")
            logger.info(f"From: {self.twilio_phone_number}")
            logger.info(f"To: {to_number}")  
            logger.info(f"Webhook URL: {webhook_url}")
            logger.info(f"LiveKit Room: {room_name}")
            
            return call.sid
            
        except Exception as e:
            logger.error(f"Failed to make call: {e}")
            raise

    async def monitor_room(self, room_name: str, duration: int = 60):
        """Monitor the LiveKit room for activity"""
        logger.info(f"Monitoring room '{room_name}' for {duration} seconds...")
        
        import time
        start_time = time.time()
        while time.time() - start_time < duration:
            try:
                rooms = await self.livekit_api.room.list_rooms(
                    api.ListRoomsRequest()
                )
                
                target_room = next((r for r in rooms.rooms if r.name == room_name), None)
                if target_room:
                    logger.info(f"Room status: {target_room.num_participants} participants, "
                              f"created: {target_room.creation_time}")
                    
                    if target_room.num_participants > 0:
                        participants = await self.livekit_api.room.list_participants(
                            api.ListParticipantsRequest(room=room_name)
                        )
                        for p in participants.participants:
                            logger.info(f"Participant: {p.identity} ({p.state})")
                
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"Error monitoring room: {e}")
                await asyncio.sleep(5)

    async def test_integration(self, to_number: str, monitor_duration: int = 60):
        """Run the complete integration test"""
        import time
        room_name = f"test-call-{int(time.time())}"
        
        logger.info("=== Twilio -> LiveKit -> Render Integration Test ===")
        logger.info(f"Target number: {to_number}")
        logger.info(f"Room name: {room_name}")
        
        try:
            # Step 1: Create LiveKit room
            await self.create_livekit_room(room_name)
            
            # Step 2: Make Twilio call
            call_sid = self.make_test_call(to_number, room_name)
            
            # Step 3: Monitor room activity
            await self.monitor_room(room_name, monitor_duration)
            
            logger.info("=== Test completed ===")
            return call_sid
            
        except Exception as e:
            logger.error(f"Integration test failed: {e}")
            raise


def main():
    parser = argparse.ArgumentParser(description='Test Twilio to LiveKit voice bot integration')
    parser.add_argument('--to', required=True, help='Phone number to call (e.g., +1234567890)')
    parser.add_argument('--monitor', type=int, default=60, help='Monitor duration in seconds (default: 60)')
    parser.add_argument('--room', help='Specific room name (optional)')
    
    args = parser.parse_args()
    
    # Validate phone number format
    if not args.to.startswith('+'):
        logger.error("Phone number must include country code (e.g., +1234567890)")
        return 1
    
    try:
        tester = TwilioLiveKitTester()
        
        if args.room:
            # Simple call test with existing room
            call_sid = tester.make_test_call(args.to, args.room)
            logger.info(f"Call placed with SID: {call_sid}")
        else:
            # Full integration test
            asyncio.run(tester.test_integration(args.to, args.monitor))
        
        return 0
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("Please set the required environment variables:")
        logger.error("- TWILIO_ACCOUNT_SID")
        logger.error("- TWILIO_AUTH_TOKEN") 
        logger.error("- TWILIO_PHONE_NUMBER")
        logger.error("- LIVEKIT_API_KEY")
        logger.error("- LIVEKIT_API_SECRET")
        return 1
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())