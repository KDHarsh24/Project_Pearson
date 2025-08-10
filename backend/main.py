from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from model.watsonx import get_chatwatsonx
from langchain_core.messages import HumanMessage, SystemMessage
from pypdf import PdfReader

import os
from typing import List

app = FastAPI()

# Store chat history in memory (per session, for demo)
chat_histories = {}
session_digests = {}

def get_history(session_id):
    if session_id not in chat_histories:
        chat_histories[session_id] = [SystemMessage(content="You are a helpful assistant.")]
    return chat_histories[session_id]

def _chunk_text(text: str, chunk_size: int = 3000, overlap: int = 200) -> List[str]:
    chunks = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + chunk_size, n)
        chunks.append(text[start:end])
        if end == n:
            break
        start = max(0, end - overlap)
    return chunks

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...), session_id: str = Form(...)):
    content = await file.read()
    history = get_history(session_id)
    chat = get_chatwatsonx()

    # Handle PDFs specially: extract text and ask the model to read/understand
    if (file.filename or "").lower().endswith(".pdf"):
        if PdfReader is None:
            return JSONResponse(status_code=500, content={"error": "No PDF library available. Install 'pypdf' or 'PyPDF2'."})
        try:
            # PdfReader accepts bytes via a BytesIO-like object
            import io
            reader = PdfReader(io.BytesIO(content))
            pages_text = []
            for i, page in enumerate(reader.pages):
                try:
                    pages_text.append(page.extract_text() or "")
                except Exception:
                    pages_text.append("")
            full_text = "\n\n".join(pages_text)
        except Exception as e:
            return JSONResponse(status_code=400, content={"error": f"Failed to read PDF: {str(e)}"})

        if not full_text.strip():
            return JSONResponse(status_code=400, content={"error": "PDF contains no extractable text."})

        chunks = _chunk_text(full_text)
        # Ask the model to read and understand each chunk, then produce a final digest
        per_chunk_summaries = []
        system = SystemMessage(content="You are a legal assistant. Read the provided case law text carefully and summarize key facts, issues, holdings, and reasoning. Preserve names, dates, and citations.")
        for idx, ch in enumerate(chunks, start=1):
            msgs = [system, HumanMessage(content=f"Chunk {idx}/{len(chunks)}:\n\n{ch}\n\nSummarize crisply." )]
            try:
                resp = chat.invoke(msgs)
                per_chunk_summaries.append(resp.content)
            except Exception as e:
                per_chunk_summaries.append(f"[Error summarizing chunk {idx}: {e}]")

        # Create a consolidated digest
        digest_prompt = (
            "Combine the following chunk summaries into one coherent case brief.\n"
            "Include: citation, court, date, parties, procedural posture, facts, issues, rules, analysis, holding, and disposition.\n"
            "Use bullet points, keep it under 500-700 words, and avoid duplication.\n\n"
            + "\n\n".join(per_chunk_summaries)
        )
        final = chat.invoke([system, HumanMessage(content=digest_prompt)])
        session_digests[session_id] = final.content
        history.append(SystemMessage(content=f"PDF '{file.filename}' processed. A case brief has been prepared and will be used to answer questions."))
        return {"message": f"PDF '{file.filename}' uploaded and processed.", "pages": len(chunks)}

    # Try to decode as text for general text files
    text = None
    for encoding in ("utf-8", "utf-16", "latin-1"):
        try:
            text = content.decode(encoding)
            break
        except Exception:
            continue
    if text is not None:
        history.append(SystemMessage(content=f"Document uploaded ({file.filename}). Content ingested."))
        # Optionally store as digest for Q&A context
        session_digests[session_id] = text[:8000]
        return {"message": f"Text file '{file.filename}' uploaded and added to context."}
    else:
        # Non-text binary (images, etc.) acknowledged
        history.append(SystemMessage(content=f"Binary file uploaded: {file.filename} (type: {file.content_type}). Currently not OCR-parsed."))
        return {"message": f"Binary file '{file.filename}' uploaded. Type: {file.content_type}."}

@app.post("/chat/")
async def chat(user_input: str = Form(...), session_id: str = Form(...)):
    chat = get_chatwatsonx()
    history = get_history(session_id)
    digest = session_digests.get(session_id)
    if digest:
        context_msg = SystemMessage(content=f"Use the following case brief as authoritative context for answering questions. If a question is unrelated, say so briefly.\n\n{digest}")
        messages = [*history, context_msg, HumanMessage(content=user_input)]
    else:
        messages = [*history, HumanMessage(content=user_input)]
    response = chat.invoke(messages)
    history.append(HumanMessage(content=user_input))
    history.append(response)
    return {"response": response.content, "used_digest": bool(digest)}

@app.get("/")
def root():
    return {"message": "FastAPI chat is running. Use /upload/ to upload docs and /chat/ to chat."}
