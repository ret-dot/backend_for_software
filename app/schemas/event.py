from pydantic import BaseModel

class CalendarInput(BaseModel):
    user_id: str
    content: str
    date: str
