#!/bin/bash

# Setup script for testing Twilio + LiveKit integration
# This script helps you configure and test the integration

set -e

echo "🔧 Setting up Twilio + LiveKit integration test environment..."

# Check if .env.test exists and has been configured
if [ ! -f ".env.test" ]; then
    echo "❌ .env.test file not found!"
    echo "Please copy .env.test.example to .env.test and configure your credentials"
    exit 1
fi

# Check if required environment variables are set  
export $(grep -v '^#' .env.test | xargs)

required_vars=(
    "TWILIO_ACCOUNT_SID"
    "TWILIO_AUTH_TOKEN" 
    "TWILIO_PHONE_NUMBER"
    "LIVEKIT_API_KEY"
    "LIVEKIT_API_SECRET"
)

echo "✅ Checking required environment variables..."
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ] || [ "${!var}" = "your_${var,,}_here" ]; then
        echo "❌ $var is not set or still has placeholder value"
        echo "Please configure $var in .env.test file"
        exit 1
    fi
    echo "✓ $var is configured"
done

# Install required dependencies
echo "📦 Installing required dependencies..."
pip install twilio livekit-api fastapi uvicorn python-dotenv

# Test Twilio credentials
echo "🔍 Testing Twilio credentials..."
python3 -c "
from twilio.rest import Client
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv('.env.test')

try:
    client = Client(os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))
    account = client.api.account.fetch()
    print(f'✅ Twilio credentials valid - Account: {account.friendly_name}')
except Exception as e:
    print(f'❌ Twilio credentials invalid: {e}')
    exit(1)
"

# Test LiveKit credentials  
echo "🔍 Testing LiveKit credentials..."
python3 -c "
from livekit import api
from dotenv import load_dotenv
import os
import asyncio

# Load environment variables
load_dotenv('.env.test')

async def test_livekit():
    try:
        lk_api = api.LiveKitAPI(
            url=os.getenv('LIVEKIT_URL'),
            api_key=os.getenv('LIVEKIT_API_KEY'),
            api_secret=os.getenv('LIVEKIT_API_SECRET')
        )
        rooms = await lk_api.room.list_rooms(api.ListRoomsRequest())
        print(f'✅ LiveKit credentials valid - Found {len(rooms.rooms)} rooms')
    except Exception as e:
        print(f'❌ LiveKit credentials invalid: {e}')
        exit(1)

asyncio.run(test_livekit())
"

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Make sure your voice agent is running on Render"
echo "2. Test the integration with:"
echo "   python test_twilio_call.py --to +1234567890"
echo ""
echo "3. Or add webhook handler to your main app and test incoming calls"
echo ""
echo "📖 Usage examples:"
echo "   # Test call to specific number"
echo "   python test_twilio_call.py --to +1234567890"
echo ""
echo "   # Test with custom room name"
echo "   python test_twilio_call.py --to +1234567890 --room my-test-room"
echo ""
echo "   # Monitor for longer duration"
echo "   python test_twilio_call.py --to +1234567890 --monitor 120"
echo ""
echo "🔗 Webhook URL for Twilio configuration:"
echo "   https://aivoicelivekit.onrender.com/webhook/twilio"
echo ""