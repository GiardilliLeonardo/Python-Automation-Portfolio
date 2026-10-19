# Task: Fix and Improve a React Frontend Connected to Python FastAPI APIs

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime, timezone

class ItemBase(BaseModel):
    name: str = Field(..., example="Sample Item")
    description:
