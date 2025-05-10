from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from ..api.dependencies import get_db
from ..schemas.note import NoteInput
from ..schemas.event import CalendarInput
from ..schemas.scripts import ScriptInput
from ..models.models import Note, CalendarEvent
from ..services import tagging, summarizer, scripts
import whisper

router = APIRouter()

whisper_model = whisper.load_model("base")

# --- Notes ---
@router.post("/notes/create")
def create_note(input: NoteInput, db: Session = Depends(get_db)):
    tags = tagging.auto_tag(input.note)
    note = Note(user_id=input.user_id, note=input.note, tags=",".join(tags))
    db.add(note)
    db.commit()
    db.refresh(note)
    return {"note_id": note.id, "tags": tags}

@router.get("/notes/{user_id}")
def get_notes(user_id: str, db: Session = Depends(get_db)):
    return db.query(Note).filter(Note.user_id == user_id).all()

@router.delete("/notes/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(note)
    db.commit()
    return {"status": "deleted"}

@router.put("/notes/{note_id}")
def update_note(note_id: int, input: NoteInput, db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    note.note = input.note
    note.tags = ",".join(tagging.auto_tag(input.note))
    db.commit()
    return {"status": "updated", "tags": note.tags}


# --- Calendar ---
@router.post("/calendar/schedule")
def schedule_content(input: CalendarInput, db: Session = Depends(get_db)):
    event = CalendarEvent(user_id=input.user_id, content=input.content, date=input.date)
    db.add(event)
    db.commit()
    db.refresh(event)
    return {"status": "Scheduled", "event": event.__dict__}

@router.get("/calendar/events/{user_id}")
def get_calendar_events(user_id: str, db: Session = Depends(get_db)):
    return db.query(CalendarEvent).filter(CalendarEvent.user_id == user_id).all()


# --- Scripts ---
@router.post("/generate-script")
def generate_script(input: ScriptInput):
    script = scripts.generate(input.topic, input.style)
    return {"script": script}


# --- Audio Summary ---
@router.post("/summarize-audio")
def summarize_audio(file: UploadFile = File(...)):
    with open(f"temp_{file.filename}", "wb") as f:
        f.write(file.file.read())
    result = whisper_model.transcribe(f"temp_{file.filename}")
    summary = summarizer.summarize(result['text'])
    return {"summary": summary}
