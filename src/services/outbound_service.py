import asyncio
from typing import Optional
from livekit import api
from loguru import logger
from ..utils.config import config

class OutboundCallService:
    def __init__(self):
        self.livekit_api = api.LiveKitAPI(
            url=config.livekit_url,
            api_key=config.livekit_api_key,
            api_secret=config.livekit_api_secret
        )
    
    async def initiate_call(self, to_number: str, agent_name: str = None) -> Optional[str]:
        if agent_name is None:
            agent_name = config.agent_name
            
        try:
            room_name = f"call-{to_number.replace('+', '').replace(' ', '')}"
            
            room_info = await self.livekit_api.room.create_room(
                api.CreateRoomRequest(
                    name=room_name,
                    empty_timeout=300,
                    max_participants=2
                )
            )
            
            logger.info(f"Created room {room_name} for outbound call to {to_number}")
            
            sip_request = api.CreateSIPTrunkRequest(
                trunk_id=config.outbound_trunk_id,
                name=f"outbound-{room_name}",
                metadata=f"outbound_call_to_{to_number}",
                numbers=[to_number]
            )
            
            await self.livekit_api.sip.create_sip_participant(
                api.CreateSIPParticipantRequest(
                    sip_trunk_id=config.outbound_trunk_id,
                    sip_call_to=to_number,
                    room_name=room_name,
                    participant_identity=f"caller-{to_number}",
                    participant_metadata=f"outbound_call"
                )
            )
            
            logger.info(f"Initiated outbound call to {to_number} in room {room_name}")
            return room_name
            
        except Exception as e:
            logger.error(f"Failed to initiate outbound call to {to_number}: {e}")
            return None
    
    async def end_call(self, room_name: str) -> bool:
        try:
            await self.livekit_api.room.delete_room(
                api.DeleteRoomRequest(room=room_name)
            )
            logger.info(f"Ended call and deleted room {room_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to end call {room_name}: {e}")
            return False