from typing import List, Dict, Optional
from loguru import logger
from ..utils.config import config

class ConversationManager:
    def __init__(self):
        self.conversation_state = "greeting"
        self.user_info = {}
        self.identified_pain_points = []
        self.meeting_scheduled = False
        
    def get_current_system_prompt(self) -> str:
        return config.system_prompt
    
    def update_conversation_state(self, user_input: str, assistant_response: str):
        user_lower = user_input.lower()
        
        if self.conversation_state == "greeting":
            if any(word in user_lower for word in ["hola", "buenos", "si", "bien"]):
                self.conversation_state = "pain_identification"
                logger.info("Conversation state: greeting -> pain_identification")
        
        elif self.conversation_state == "pain_identification":
            if any(word in user_lower for word in ["si", "claro", "exacto", "problema", "dificil"]):
                self.conversation_state = "solution_presentation"
                logger.info("Conversation state: pain_identification -> solution_presentation")
        
        elif self.conversation_state == "solution_presentation":
            if any(word in user_lower for word in ["interesante", "si", "como", "reunion", "platica"]):
                self.conversation_state = "meeting_scheduling"
                logger.info("Conversation state: solution_presentation -> meeting_scheduling")
        
        elif self.conversation_state == "meeting_scheduling":
            if any(word in user_lower for word in ["si", "cuando", "agenda", "reunion", "perfecto"]):
                self.meeting_scheduled = True
                self.conversation_state = "closing"
                logger.info("Conversation state: meeting_scheduling -> closing (MEETING SCHEDULED!)")
    
    def extract_pain_points(self, user_input: str):
        pain_keywords = {
            "atencion_lenta": ["lento", "tardamos", "demora", "espera", "atencion"],
            "sobrecarga": ["mucho trabajo", "sobrecarga", "saturados", "no damos abasto"],
            "innovacion": ["innovar", "competencia", "quedamos atras", "tecnologia"],
            "procesos": ["manual", "repetitivo", "ineficiente", "procesos"],
            "costos": ["caro", "costos", "gastos", "presupuesto"]
        }
        
        for pain_type, keywords in pain_keywords.items():
            if any(keyword in user_input.lower() for keyword in keywords):
                if pain_type not in self.identified_pain_points:
                    self.identified_pain_points.append(pain_type)
                    logger.info(f"Identified pain point: {pain_type}")
    
    def get_conversation_summary(self) -> Dict:
        return {
            "state": self.conversation_state,
            "pain_points": self.identified_pain_points,
            "meeting_scheduled": self.meeting_scheduled,
            "user_info": self.user_info
        }
    
    def should_close_conversation(self) -> bool:
        return self.conversation_state == "closing" and self.meeting_scheduled