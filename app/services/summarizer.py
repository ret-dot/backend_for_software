### File: backend/app/services/summarizer.py

from transformers import pipeline, Pipeline
from typing import Optional

# Load the summarization model
def load_summarizer(model_name: str = "facebook/bart-large-cnn") -> Pipeline:
    try:
        return pipeline("summarization", model=model_name)
    except Exception as e:
        raise RuntimeError(f"Failed to load summarization model: {e}")

# Initialize summarizer once
summarizer_pipeline = load_summarizer()

# Split long texts into smaller chunks
def split_into_chunks(text: str, max_tokens: int = 1024):
    sentences = text.split('. ')
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) < max_tokens:
            current_chunk += sentence + '. '
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + '. '
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

# Main summarizer function
def summarize(text: str, max_length: int = 100, min_length: int = 25) -> str:
    if not text or not text.strip():
        return "No text provided for summarization."

    try:
        if len(text.split()) > 500:
            chunks = split_into_chunks(text)
            summaries = summarizer_pipeline(chunks, max_length=max_length, min_length=min_length, do_sample=False)
            return " ".join([s['summary_text'] for s in summaries])
        else:
            summary = summarizer_pipeline(text, max_length=max_length, min_length=min_length, do_sample=False)
            return summary[0]['summary_text']
    except Exception as e:
        return f"Summarization failed: {e}"
