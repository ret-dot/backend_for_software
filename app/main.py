from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import whisper
import spacy
from transformers import pipeline
from .database import Base, engine, SessionLocal
import datetime
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session

class CalendarEvent(Base):
    __tablename__ = "calendar_events"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String)
    content = Column(String)
    date = Column(String)

class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String)
    note = Column(String)
    tags = Column(String)

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

nlp = spacy.load("en_core_web_sm")
summarizer = pipeline("summarization")
whisper_model = whisper.load_model("base")

class NoteInput(BaseModel):
    user_id: str
    note: str

class NoteUpdate(BaseModel):
    id: int
    note: str

class ScriptInput(BaseModel):
    topic: str
    style: str = "YouTube"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/auto-tag")
def auto_tag_note(input: NoteInput, db: Session = Depends(get_db)):
    doc = nlp(input.note)
    tags = list(set(ent.label_ for ent in doc.ents))
    note_entry = Note(user_id=input.user_id, note=input.note, tags=",".join(tags))
    db.add(note_entry)
    db.commit()
    db.refresh(note_entry)
    return {"tags": tags, "note_id": note_entry.id}

@app.get("/notes/{user_id}")
def get_notes(user_id: str, db: Session = Depends(get_db)):
    notes = db.query(Note).filter(Note.user_id == user_id).all()
    return [n.__dict__ for n in notes]

@app.get("/notes/search/{user_id}")
def search_notes(user_id: str, tag: str, db: Session = Depends(get_db)):
    notes = db.query(Note).filter(Note.user_id == user_id, Note.tags.contains(tag)).all()
    return [n.__dict__ for n in notes]

@app.delete("/notes/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == note_id).first()
    if note:
        db.delete(note)
        db.commit()
        return {"status": "deleted"}
    raise HTTPException(status_code=404, detail="Note not found")

@app.put("/notes/update")
def update_note(update: NoteUpdate, db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == update.id).first()
    if note:
        note.note = update.note
        doc = nlp(update.note)
        note.tags = ",".join(set(ent.label_ for ent in doc.ents))
        db.commit()
        return {"status": "updated"}
    raise HTTPException(status_code=404, detail="Note not found")

@app.post("/generate-script")
def generate_script(input: ScriptInput):
    prompt = f"Create a {input.style} script for the topic: {input.topic}"
    return {"script": f"[Mock script for {input.topic} in {input.style} style]"}



@app.post("/summarize-audio")
def summarize_audio(file: UploadFile = File(...)):
    with open(f"temp_{file.filename}", "wb") as f:
        f.write(file.file.read())
    result = whisper_model.transcribe(f"temp_{file.filename}")
    summary = summarizer(result['text'], max_length=100)[0]['summary_text']
    return {"summary": summary}