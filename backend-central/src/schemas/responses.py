# /src/schemas/responses.py
from pydantic import BaseModel
from typing import Dict, Any, List

class MessageResponse(BaseModel):
    success: bool = True
    message: str

class DictResponse(BaseModel):
    success: bool = True
    data: Dict[str, Any]

class ListDictResponse(BaseModel):
    success: bool = True
    data: List[Dict[str, Any]]

