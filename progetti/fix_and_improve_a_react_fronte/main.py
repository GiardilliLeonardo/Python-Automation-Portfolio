# Task: Fix and Improve a React Frontend Connected to Python FastAPI APIs

import logging
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker, Session, declarative_base
import uvicorn

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# --- Database Configuration (SQLite for ready-to-use portability) ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./database.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- SQLAlchemy Models ---
class DBItem(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, index=True, nullable=True)
    completed = Column(Boolean, default=False)

# Create tables
Base.metadata.create_all(bind=engine)

# --- Pydantic Schemas (Validation & Serialization) ---
class ItemBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="Title of the item")
    description: Optional[str] = Field(None,
