from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from langchain_core.messages import HumanMessage, SystemMessage
from pypdf import PdfReader
import io
from typing import List

from model.watsonx import get_chatwatsonx
import prompts

app = FastAPI()

# In-memory storage for demonstration purposes.
# In a production environment, consider using a more persistent solution like Redis or a database.
chat_histories = {}
session_digests = {}

def get_history(session_id: str) -> List[SystemMessage | HumanMessage]:
    """
    Retrieves the chat history for a given session or creates a new one.
    """
    if session_id not in chat_histories:
        chat_histories[session_id] = [SystemMessage(content=prompts.INITIAL_SYSTEM_PROMPT)]
    return chat_histories[session_id]

def _chunk_text(text: str, chunk_size: int = 3000, overlap: int = 200) -> List[str]:
    """
    Splits a long text into smaller, overlapping chunks.
    """
    if not text:
        return []
    chunks = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + chunk_size, n)
        chunks.append(text[start:end])
        if end == n:
            break
        # Overlap ensures context is not lost at chunk boundaries
        start += chunk_size - overlap
    return chunks

def _extract_text_from_pdf(content: bytes) -> str:
    """
    Extracts all text from a PDF file's content.
    """
    try:
        reader = PdfReader(io.BytesIO(content))
        pages_text = [page.extract_text() or "" for page in reader.pages]
        return "\n\n".join(pages_text)
    except Exception as e:
        # This provides a fallback or logging point if PDF extraction fails
        print(f"Error extracting PDF text: {e}")
        return ""

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...), session_id: str = Form(...)):
    """
    Handles file uploads. It processes PDFs to create a summarized case brief,
    ingests text files directly, and acknowledges other binary file types.
    """
    content = await file.read()
    history = get_history(session_id)
    chat = get_chatwatsonx()
    filename = file.filename or "unknown_file"

    if filename.lower().endswith(".pdf"):
        full_text = _extract_text_from_pdf(content)
        if not full_text.strip():
            return JSONResponse(status_code=400, content={"error": "PDF contains no extractable text."})

        chunks = _chunk_text(full_text)
        
        # Summarize each chunk individually
        per_chunk_summaries = []
        system_prompt = SystemMessage(content=prompts.LEGAL_ASSISTANT_SYSTEM_PROMPT)
        for i, chunk in enumerate(chunks, 1):
            human_prompt = HumanMessage(content=prompts.get_summarize_chunk_prompt(chunk, i, len(chunks)))
            try:
                response = chat.invoke([system_prompt, human_prompt])
                per_chunk_summaries.append(response.content)
            except Exception as e:
                per_chunk_summaries.append(f"[Error summarizing chunk {i}: {e}]")
        
        # Create a final, consolidated digest from the summaries
        digest_prompt = HumanMessage(content=prompts.get_digest_prompt(per_chunk_summaries))
        final_brief = chat.invoke([system_prompt, digest_prompt])
        
        session_digests[session_id] = final_brief.content
        history.append(SystemMessage(content=prompts.PDF_PROCESS_SUCCESS.format(filename=filename)))
        
        return {"message": f"PDF '{filename}' processed successfully.", "pages": len(chunks)}

    # Handle plain text files
    text = None
    for encoding in ("utf-8", "utf-16", "latin-1"):
        try:
            text = content.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    
    if text is not None:
        history.append(SystemMessage(content=prompts.TEXT_UPLOAD_SUCCESS.format(filename=filename)))
        # Store a truncated version for context
        session_digests[session_id] = text[:8000]
        return {"message": f"Text file '{filename}' uploaded and added to context."}
    
    # Acknowledge other file types without processing
    history.append(SystemMessage(content=prompts.BINARY_FILE_UPLOAD.format(filename=filename, content_type=file.content_type)))
    return {"message": f"Binary file '{filename}' received. Type: {file.content_type}."}

@app.post("/chat/")
async def chat(user_input: str = Form(...), session_id: str = Form(...)):
    """
    Handles the chat interaction. It uses the session's document digest, if available,
    to provide context-aware responses.
    """
    chat = get_chatwatsonx()
    history = get_history(session_id)
    digest = session_digests.get(session_id)
    
    messages = list(history)  # Create a mutable copy

    if digest:
        context_msg = SystemMessage(content=prompts.get_chat_context_prompt(digest))
        messages.append(context_msg)
    
    messages.append(HumanMessage(content=user_input))
    
    response = chat.invoke(messages)
    
    # Append the user input and model response to the permanent history
    history.append(HumanMessage(content=user_input))
    history.append(response)
    
    return {"response": response.content, "used_digest": bool(digest)}

@app.get("/")
def root():
    """
    Root endpoint to confirm the API is running.
    """
    return {"message": "FastAPI chat is running. Use /upload/ to upload docs and /chat/ to chat."}
