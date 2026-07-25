from pydantic import BaseModel
from typing import Optional

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    client_id: Optional[str] = "C-1002"  # Defaulting for PoC purposes
