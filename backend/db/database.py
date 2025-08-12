import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base, DB_PATH

DB_URL = f"sqlite:///./{DB_PATH}"
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def init_db():
    Base.metadata.create_all(engine)
