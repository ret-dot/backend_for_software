### File: backend/app/schemas/__init__.py

from .note import NoteInput
from .event import CalendarInput
from .scripts import ScriptInput

__all__ = [
    "NoteInput",
    "CalendarInput",
    "ScriptInput"
]
