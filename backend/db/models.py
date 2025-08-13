import os
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship

DB_PATH = os.getenv("SQLITE_PATH", "pearson.db")
Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255), nullable=False)
    hash = Column(String(64), index=True, unique=True)
    content_type = Column(String(100))
    source = Column(String(50), default="upload")  # upload | crawl | contract | witness
    status = Column(String(30), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    raw_path = Column(Text)
    curated_path = Column(Text)
    meta_json = Column(Text)
    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")

class Chunk(Base):
    __tablename__ = "chunks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), index=True)
    chunk_index = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    vector_id = Column(String(128), index=True)
    meta_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    document = relationship("Document", back_populates="chunks")

    __table_args__ = (
        UniqueConstraint("document_id", "chunk_index", name="uq_doc_chunk"),
    )
