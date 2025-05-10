from pydantic import BaseModel

class NoteInput(BaseModel):
    user_id: str
    note: str
