from pydantic import BaseModel
from enum import Enum

class ScriptStyle(str, Enum):
    youtube = "YouTube"
    twitter = "Twitter"
    instagram = "Instagram"

class ScriptInput(BaseModel):
    topic: str
    style: ScriptStyle = ScriptStyle.youtube
