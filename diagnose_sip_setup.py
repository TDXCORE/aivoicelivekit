#!/usr/bin/env python3
"""
Diagnostic script to verify SIP and LiveKit configuration
"""

import os
import asyncio
import logging
from dotenv import load_dotenv
from livekit import api
from twilio.rest import Client

# Load environment variables
load_dotenv('.env.test')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_livekit_connection():
    """Check if we can connect to LiveKit"""
    try:
        livekit_url = os.getenv('LIVEKIT_URL', 'wss://forceapp-jaadrt7a.livekit.cloud')
        livekit_api_key = os.getenv('LIVEKIT_API_KEY')
        livekit_api_secret = os.getenv('LIVEKIT_API_SECRET')
        
        if not all([livekit_api_key, livekit_api_secret]):
            logger.error("❌ Missing LiveKit credentials")
            return False
        
        livekit_api = api.LiveKitAPI(
            url=livekit_url,
            api_key=livekit_api_key,
            api_secret=livekit_api_secret
        )
        
        # Try to list rooms
        rooms = await livekit_api.room.list_rooms(api.ListRoomsRequest())
        logger.info(f"✅ LiveKit connection successful. Found {len(rooms.rooms)} rooms")
        return True
        
    except Exception as e:
        logger.error(f"❌ LiveKit connection failed: {e}")
        return False

def check_twilio_credentials():
    """Check Twilio credentials"""
    try:
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        from_number = os.getenv('TWILIO_PHONE_NUMBER')
        
        if not all([account_sid, auth_token, from_number]):
            logger.error("❌ Missing Twilio credentials")
            return False
        
        client = Client(account_sid, auth_token)
        
        # Try to get account info
        account = client.api.accounts(account_sid).fetch()
        logger.info(f"✅ Twilio connection successful. Account: {account.friendly_name}")
        
        # Check SIP trunks
        trunks = client.trunking.trunks.list()
        logger.info(f"✅ Found {len(trunks)} SIP trunks")
        
        for trunk in trunks:
            logger.info(f"  - Trunk: {trunk.sid} ({trunk.friendly_name})")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Twilio connection failed: {e}")
        return False

def check_environment_variables():
    """Check all required environment variables"""
    logger.info("🔍 Checking environment variables...")
    
    required_vars = [
        'LIVEKIT_URL',
        'LIVEKIT_API_KEY', 
        'LIVEKIT_API_SECRET',
        'TWILIO_ACCOUNT_SID',
        'TWILIO_AUTH_TOKEN',
        'TWILIO_PHONE_NUMBER',
        'GROQ_API_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            logger.info(f"✅ {var}: {'*' * min(len(value), 10)}...")
        else:
            logger.error(f"❌ {var}: Missing")
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    logger.info("✅ All required environment variables are set")
    return True

def check_sip_configuration():
    """Check SIP configuration"""
    logger.info("🔍 Checking SIP configuration...")
    
    sip_vars = {
        'SIP_URI': os.getenv('SIP_URI', '6jf4gz4gbna.sip.livekit.cloud'),
        'OUTBOUND_TRUNK_ID': os.getenv('OUTBOUND_TRUNK_ID', 'ST_GZ4Bo8JH4ly7'),
        'INBOUND_TRUNK_ID': os.getenv('INBOUND_TRUNK_ID', 'ST_62xofSEmFyRe')
    }
    
    for var, value in sip_vars.items():
        logger.info(f"✅ {var}: {value}")
    
    # Expected configuration based on your setup
    expected_config = {
        'Twilio SIP Trunk URI': 'aivoicetdx.pstn.twilio.com',
        'LiveKit SIP URI': '6jf4gz4gbna.sip.livekit.cloud',
        'Dispatch Rule Pattern': 'call-{participant.identity}'
    }
    
    logger.info("📋 Expected SIP Configuration:")
    for key, value in expected_config.items():
        logger.info(f"  - {key}: {value}")
    
    return True

async def main():
    """Main diagnostic function"""
    logger.info("🚀 Starting SIP and LiveKit diagnostic...")
    logger.info("=" * 60)
    
    # Check environment variables
    env_ok = check_environment_variables()
    logger.info("")
    
    # Check SIP configuration
    sip_ok = check_sip_configuration()
    logger.info("")
    
    # Check Twilio connection
    twilio_ok = check_twilio_credentials()
    logger.info("")
    
    # Check LiveKit connection
    livekit_ok = await check_livekit_connection()
    logger.info("")
    
    # Summary
    logger.info("=" * 60)
    logger.info("📊 DIAGNOSTIC SUMMARY:")
    logger.info(f"Environment Variables: {'✅' if env_ok else '❌'}")
    logger.info(f"SIP Configuration: {'✅' if sip_ok else '❌'}")
    logger.info(f"Twilio Connection: {'✅' if twilio_ok else '❌'}")
    logger.info(f"LiveKit Connection: {'✅' if livekit_ok else '❌'}")
    
    all_ok = env_ok and sip_ok and twilio_ok and livekit_ok
    
    if all_ok:
        logger.info("🎉 All checks passed! Your setup should be working.")
        logger.info("💡 If calls still fail, check:")
        logger.info("   1. Twilio SIP trunk dispatch rules")
        logger.info("   2. LiveKit SIP endpoint configuration")
        logger.info("   3. Network connectivity between Twilio and LiveKit")
    else:
        logger.error("❌ Some checks failed. Please fix the issues above.")
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    exit(asyncio.run(main()))
