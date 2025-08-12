# backend/prompts.py

"""
This module centralizes all prompts used for interacting with the language model.
By centralizing prompts, we can easily manage, version, and refine the model's instructions
without altering the core application logic.
"""

# System prompt for the initial state of the chat history
INITIAL_SYSTEM_PROMPT = "You are a helpful assistant."

# System prompt for the legal assistant persona used for PDF processing
LEGAL_ASSISTANT_SYSTEM_PROMPT = (
    "You are a specialized legal assistant. Your task is to analyze case law documents with high precision. "
    "Focus on extracting key legal concepts, facts, and judicial reasoning. "
    "Ensure that all names, dates, case citations, and procedural details are preserved accurately."
)

# Prompt to summarize a single chunk of text from a PDF
def get_summarize_chunk_prompt(chunk_text: str, chunk_num: int, total_chunks: int) -> str:
    """Generates a prompt to summarize a specific chunk of a document."""
    return (
        f"Analyze the following text chunk ({chunk_num}/{total_chunks}). "
        "Extract and summarize the key facts, legal issues, arguments, and holdings presented in this section. "
        "Be concise and focus on the most critical information.\n\n"
        f"--- TEXT CHUNK ---\n{chunk_text}\n--- END TEXT CHUNK ---"
    )

# Prompt to create a final, consolidated case brief from chunk summaries
def get_digest_prompt(summaries: list[str]) -> str:
    """Generates a prompt to synthesize a final case brief from individual chunk summaries."""
    summaries_text = "\n\n---\n\n".join(summaries)
    return (
        "You are tasked with creating a final, coherent case brief from the provided summaries of document chunks.\n"
        "Synthesize these summaries into a single, well-structured brief. The brief must include the following sections:\n"
        "- **Citation:** Full case citation.\n"
        "- **Court:** The court that issued the opinion.\n"
        "- **Date:** The date the opinion was filed.\n"
        "- **Parties:** The primary parties involved.\n"
        "- **Procedural Posture:** How the case reached this court.\n"
        "- **Facts:** A concise summary of the essential background and facts.\n"
        "- **Issue(s):** The legal question(s) the court is deciding.\n"
        "- **Rule(s) of Law:** The key legal rules or principles applied by the court.\n"
        "- **Analysis/Reasoning:** The court's explanation for its decision.\n"
        "- **Holding:** The court's direct answer to the issue(s).\n"
        "- **Disposition:** The final order of the court (e.g., affirmed, reversed, remanded).\n\n"
        "Use clear headings and bullet points for readability. The final brief should be comprehensive yet concise, ideally between 500 and 700 words. Avoid redundancy.\n\n"
        f"--- CHUNK SUMMARIES ---\n{summaries_text}\n--- END CHUNK SUMMARIES ---"
    )

# Prompt to provide context for the chat when a document has been uploaded
def get_chat_context_prompt(digest: str) -> str:
    """Generates a system prompt to provide the case brief as context for the chat."""
    return (
        "You are a legal research assistant. Use the following case brief as the primary, authoritative source to answer the user's questions. "
        "Your answers must be based solely on the information contained within this brief.\n"
        "If a question is outside the scope of the brief or cannot be answered with the provided information, "
        "state that clearly. Do not invent, assume, or use external knowledge.\n\n"
        f"--- CASE BRIEF ---\n{digest}\n--- END CASE BRIEF ---"
    )

# System message content for a successful text file upload
TEXT_UPLOAD_SUCCESS = "Document uploaded ({filename}). Content ingested and ready for Q&A."

# System message content for a successful PDF file processing
PDF_PROCESS_SUCCESS = "PDF '{filename}' processed. A case brief has been prepared and will be used to answer questions."

# System message content for a binary file upload
BINARY_FILE_UPLOAD = "Binary file uploaded: {filename} (type: {content_type}). This file type is not processed for content."
