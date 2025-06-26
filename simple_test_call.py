#!/usr/bin/env python3
"""
Simple Twilio Test Call Script
"""

import argparse
import time
from twilio.rest import Client
from dotenv import load_dotenv
import os
import logging

# Load environment variables
load_dotenv('.env.test')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def make_simple_call(to_number: str):
    """Make a simple test call using Twilio SIP integration"""
    
    # Get credentials
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    from_number = os.getenv('TWILIO_PHONE_NUMBER')
    
    # Use the correct SIP trunk configuration
    # This should match your Twilio SIP trunk configuration
    sip_trunk_uri = "aivoicetdx.pstn.twilio.com"
    
    if not all([account_sid, auth_token, from_number]):
        logger.error("Missing Twilio credentials in .env.test")
        return None
    
    # Create participant identity for the call
    participant_identity = f"caller-{int(time.time())}"
    
    # Create SIP destination URI using the correct trunk
    sip_destination = f"sip:{participant_identity}@{sip_trunk_uri}"
    
    logger.info(f"Making SIP call to {to_number}")
    logger.info(f"From: {from_number}")
    logger.info(f"SIP Destination: {sip_destination}")
    logger.info(f"Participant Identity: {participant_identity}")
    
    try:
        # Initialize Twilio client
        client = Client(account_sid, auth_token)
        
        # Create TwiML that connects the call to LiveKit via SIP
        twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">Connecting you to Laura SDR voice assistant. Please wait a moment.</Say>
    <Dial>
        <Sip>{sip_destination}</Sip>
    </Dial>
</Response>'''
        
        # Make the call using TwiML
        call = client.calls.create(
            to=to_number,
            from_=from_number,
            twiml=twiml
        )
        
        logger.info(f"✅ SIP call initiated successfully!")
        logger.info(f"Call SID: {call.sid}")
        logger.info(f"Status: {call.status}")
        logger.info(f"SIP URI: {sip_destination}")
        
        return call.sid
        
    except Exception as e:
        logger.error(f"❌ Failed to make SIP call: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Make a simple test call')
    parser.add_argument('--to', required=True, help='Phone number to call (e.g., +1234567890)')
    
    args = parser.parse_args()
    
    # Validate phone number format
    if not args.to.startswith('+'):
        logger.error("Phone number must include country code (e.g., +1234567890)")
        return 1
    
    call_sid = make_simple_call(args.to)
    
    if call_sid:
        logger.info(f"🎉 Test call completed. Call SID: {call_sid}")
        logger.info("Check your phone and the Render logs for activity!")
        return 0
    else:
        logger.error("❌ Test call failed")
        return 1

if __name__ == "__main__":
    exit(main())
