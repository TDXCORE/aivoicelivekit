#!/usr/bin/env python3
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from src.services.outbound_service import OutboundCallService
from src.utils.logger import setup_logger
from loguru import logger

setup_logger()

app = FastAPI(title="LiveKit Voice Agent API", version="1.0.0")

outbound_service = OutboundCallService()

class OutboundCallRequest(BaseModel):
    phone_number: str
    agent_name: Optional[str] = "laura-sdr"

class CallResponse(BaseModel):
    success: bool
    room_name: Optional[str] = None
    message: str

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "livekit-voice-agent"}

@app.post("/make-call", response_model=CallResponse)
async def make_outbound_call(request: OutboundCallRequest):
    try:
        logger.info(f"Initiating outbound call to {request.phone_number}")
        
        room_name = await outbound_service.initiate_call(
            to_number=request.phone_number,
            agent_name=request.agent_name
        )
        
        if room_name:
            return CallResponse(
                success=True,
                room_name=room_name,
                message=f"Call initiated successfully to {request.phone_number}"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to initiate call"
            )
    
    except Exception as e:
        logger.error(f"Error initiating call: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/end-call/{room_name}")
async def end_call(room_name: str):
    try:
        success = await outbound_service.end_call(room_name)
        if success:
            return {"success": True, "message": f"Call {room_name} ended successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to end call")
    
    except Exception as e:
        logger.error(f"Error ending call: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {
        "message": "LiveKit Voice Agent API - Laura SDR",
        "endpoints": {
            "health": "/health",
            "make_call": "/make-call",
            "end_call": "/end-call/{room_name}"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)