#!/usr/bin/env python3
"""
Start only the webhook server for Render deployment
"""

import os
import uvicorn
from webhook_server import app
from utils.logger import setup_logger

def main():
    setup_logger()
    
    # Get port from environment variable (Render sets this)
    port = int(os.getenv("PORT", 8000))
    
    print(f"Starting Twilio webhook server on port {port}...")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        log_level="info"
    )

if __name__ == "__main__":
    main()