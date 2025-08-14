"""
Session-Based Document and Chat History Manager
==============================================

Manages documents, vector storage, and chat history per session ID.
Users can return to their sessions without re-uploading documents.
"""

import os
import json
import hashlib
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
from vectorstores.chroma_store import ChromaVectorStore

class SessionManager:
    """Manages sessions, documents, and chat history"""
    
    def __init__(self):
        # Create session directories
        self.sessions_dir = Path("sessions")
        self.documents_dir = Path("session_documents")
        self.sessions_dir.mkdir(exist_ok=True)
        self.documents_dir.mkdir(exist_ok=True)
        
        # In-memory session cache
        self.active_sessions = {}
        
        # Load existing sessions
        self._load_existing_sessions()
    
    def _load_existing_sessions(self):
        """Load existing sessions from disk"""
        for session_file in self.sessions_dir.glob("*.json"):
            session_id = session_file.stem
            try:
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
                    self.active_sessions[session_id] = session_data
                print(f"Loaded session: {session_id}")
            except Exception as e:
                print(f"Error loading session {session_id}: {e}")
    
    def create_session(self, session_id: str, user_info: Optional[Dict] = None) -> Dict[str, Any]:
        """Create a new session or return existing one"""
        if session_id in self.active_sessions:
            return self.active_sessions[session_id]
        
        session_data = {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "last_accessed": datetime.now().isoformat(),
            "user_info": user_info or {},
            "documents": {},  # Document ID -> document metadata
            "chat_history": [],  # List of all conversations
            "vector_collections": [],  # List of vector collection names for this session
            "total_analyses": 0,
            "status": "active"
        }
        
        self.active_sessions[session_id] = session_data
        self._save_session(session_id)
        
        return session_data
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data"""
        if session_id in self.active_sessions:
            # Update last accessed
            self.active_sessions[session_id]["last_accessed"] = datetime.now().isoformat()
            self._save_session(session_id)
            return self.active_sessions[session_id]
        return None
    
    def add_document_to_session(self, session_id: str, file_content: bytes, 
                               filename: str, case_title: str, case_type: str) -> Dict[str, Any]:
        """Add document to session with vector storage"""
        session = self.get_session(session_id)
        if not session:
            session = self.create_session(session_id)
        
        # Generate document ID
        doc_hash = hashlib.md5(file_content).hexdigest()[:12]
        doc_id = f"doc_{session_id}_{doc_hash}"
        
        # Save document file
        doc_file_path = self.documents_dir / f"{doc_id}_{filename}"
        with open(doc_file_path, 'wb') as f:
            f.write(file_content)
        
        # Document metadata
        doc_metadata = {
            "doc_id": doc_id,
            "filename": filename,
            "case_title": case_title,
            "case_type": case_type,
            "file_path": str(doc_file_path),
            "file_size": len(file_content),
            "uploaded_at": datetime.now().isoformat(),
            "content_hash": doc_hash
        }
        
        # Add to session
        session["documents"][doc_id] = doc_metadata
        
        # Create session-specific vector collection
        collection_name = f"session_{session_id}_docs"
        if collection_name not in session["vector_collections"]:
            session["vector_collections"].append(collection_name)
        
        # Store in vector database
        try:
            # Try to create vector store, fallback to basic storage if WatsonX not available
            try:
                vector_store = ChromaVectorStore(collection_name=collection_name)
            except Exception as ve:
                print(f"WatsonX vector store not available: {ve}")
                # Fallback: store chunks in session metadata for basic functionality
                content_text = file_content.decode('utf-8', errors='ignore')
                chunks = self._chunk_text(content_text)
                doc_metadata["vector_status"] = "stored_local"
                doc_metadata["chunks_count"] = len(chunks)
                doc_metadata["chunks"] = chunks[:5]  # Store first 5 chunks for basic search
                raise Exception("Using local fallback storage")
            
            # Convert content to text and chunk it
            content_text = file_content.decode('utf-8', errors='ignore')
            chunks = self._chunk_text(content_text)
            
            # Add to vector store with metadata
            chunk_texts = []
            chunk_metadatas = []
            
            for i, chunk in enumerate(chunks):
                chunk_texts.append(chunk)
                chunk_metadatas.append({
                    "doc_id": doc_id,
                    "filename": filename,
                    "case_title": case_title,
                    "case_type": case_type,
                    "chunk_index": i,
                    "session_id": session_id,
                    "upload_date": doc_metadata["uploaded_at"]
                })
            
            # Use add_texts method instead of add_document
            vector_store.add_texts(
                texts=chunk_texts,
                metadatas=chunk_metadatas
            )
            
            doc_metadata["vector_status"] = "stored"
            doc_metadata["chunks_count"] = len(chunks)
            
        except Exception as e:
            print(f"Vector storage error for {doc_id}: {e}")
            # If we already set local fallback status, keep it
            if doc_metadata.get("vector_status") != "stored_local":
                doc_metadata["vector_status"] = "failed"
                doc_metadata["vector_error"] = str(e)
                # Try basic chunking as fallback
                try:
                    content_text = file_content.decode('utf-8', errors='ignore')
                    chunks = self._chunk_text(content_text)
                    doc_metadata["chunks_count"] = len(chunks)
                    doc_metadata["chunks"] = chunks[:5]  # Store first 5 chunks
                    doc_metadata["vector_status"] = "stored_local"
                except Exception as chunk_error:
                    print(f"Even basic chunking failed: {chunk_error}")
                    doc_metadata["chunks_count"] = 0
        
        # Update session
        session["documents"][doc_id] = doc_metadata
        self._save_session(session_id)
        
        return doc_metadata
    
    def get_session_documents(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all documents for a session"""
        session = self.get_session(session_id)
        if not session:
            return []
        
        return list(session["documents"].values())
    
    def get_document_content(self, session_id: str, doc_id: str) -> Optional[str]:
        """Get document content by ID"""
        session = self.get_session(session_id)
        if not session or doc_id not in session["documents"]:
            return None
        
        doc_metadata = session["documents"][doc_id]
        file_path = Path(doc_metadata["file_path"])
        
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
            except Exception as e:
                print(f"Error reading document {doc_id}: {e}")
                return None
        return None
    
    def search_session_documents(self, session_id: str, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search documents within a session using vector similarity"""
        session = self.get_session(session_id)
        if not session or not session["vector_collections"]:
            return []
        
        results = []
        for collection_name in session["vector_collections"]:
            try:
                vector_store = ChromaVectorStore(collection_name=collection_name)
                search_results = vector_store.similarity_search(query, k=k)
                results.extend(search_results)
            except Exception as e:
                print(f"Search failed in collection {collection_name}: {e}")
        
        return results
    
    def add_chat_message(self, session_id: str, message_type: str, content: str, 
                        model_used: str = None, metadata: Dict = None) -> None:
        """Add message to chat history"""
        session = self.get_session(session_id)
        if not session:
            session = self.create_session(session_id)
        
        chat_entry = {
            "timestamp": datetime.now().isoformat(),
            "message_type": message_type,  # "user_prompt", "ai_response", "system"
            "content": content,
            "model_used": model_used,
            "metadata": metadata or {}
        }
        
        session["chat_history"].append(chat_entry)
        session["total_analyses"] += 1 if message_type == "ai_response" else 0
        
        self._save_session(session_id)
    
    def get_chat_history(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get chat history for session"""
        session = self.get_session(session_id)
        if not session:
            return []
        
        history = session["chat_history"]
        return history[-limit:] if limit else history
    
    def get_session_context(self, session_id: str) -> str:
        """Get relevant context from session for AI models"""
        session = self.get_session(session_id)
        if not session:
            return ""
        
        context_parts = []
        
        # Add document context
        documents = self.get_session_documents(session_id)
        if documents:
            context_parts.append("SESSION DOCUMENTS:")
            for doc in documents[-3:]:  # Last 3 documents
                context_parts.append(f"- {doc['filename']} ({doc['case_title']})")
        
        # Add recent chat context
        recent_chats = self.get_chat_history(session_id, limit=10)
        if recent_chats:
            context_parts.append("\nRECENT CONVERSATION:")
            for chat in recent_chats[-5:]:  # Last 5 exchanges
                if chat["message_type"] == "user_prompt":
                    context_parts.append(f"USER: {chat['content'][:100]}...")
        
        return "\n".join(context_parts)
    
    def _chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
        """Simple text chunking"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
        
        return chunks
    
    def _save_session(self, session_id: str) -> None:
        """Save session to disk"""
        if session_id in self.active_sessions:
            session_file = self.sessions_dir / f"{session_id}.json"
            try:
                with open(session_file, 'w') as f:
                    json.dump(self.active_sessions[session_id], f, indent=2)
            except Exception as e:
                print(f"Error saving session {session_id}: {e}")
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all sessions with summary info"""
        sessions_summary = []
        for session_id, session_data in self.active_sessions.items():
            summary = {
                "session_id": session_id,
                "created_at": session_data["created_at"],
                "last_accessed": session_data["last_accessed"],
                "documents_count": len(session_data["documents"]),
                "total_analyses": session_data["total_analyses"],
                "status": session_data["status"]
            }
            sessions_summary.append(summary)
        
        return sorted(sessions_summary, key=lambda x: x["last_accessed"], reverse=True)
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session and its associated data"""
        try:
            # Remove from memory
            if session_id in self.active_sessions:
                session_data = self.active_sessions[session_id]
                
                # Delete document files
                for doc_metadata in session_data["documents"].values():
                    file_path = Path(doc_metadata["file_path"])
                    if file_path.exists():
                        file_path.unlink()
                
                # Delete vector collections
                for collection_name in session_data["vector_collections"]:
                    try:
                        vector_store = ChromaVectorStore(collection_name=collection_name)
                        # Note: ChromaDB doesn't have a direct delete collection method
                        # You might need to implement this based on your vector store
                    except Exception as e:
                        print(f"Error deleting vector collection {collection_name}: {e}")
                
                del self.active_sessions[session_id]
            
            # Delete session file
            session_file = self.sessions_dir / f"{session_id}.json"
            if session_file.exists():
                session_file.unlink()
            
            return True
        except Exception as e:
            print(f"Error deleting session {session_id}: {e}")
            return False

# Global session manager instance
session_manager = SessionManager()
