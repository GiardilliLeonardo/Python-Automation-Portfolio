# Task: Next.js Developer Needed to integrate an AI Feature for an existing SaaS

import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from openai import AsyncOpenAI
from dotenv import load_dotenv
import uvicorn

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SaaS AI Feature API",
    description="Python Backend API for Next.js SaaS AI Integration",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-nextjs-saas-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.warning("OPENAI_API_KEY is missing. AI features will not work until configured.")

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

class AIRequest(BaseModel):
    prompt: str = Field(..., min_length=2, description="The input text/context from the Next.js frontend")
    max_tokens: int = Field(default=500, le=4096, description="Maximum tokens to generate")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Creativity level of the AI")

class AIResponse(BaseModel):
    success: bool
    data: str
    usage: dict | None = None
    error: str | None = None

@app.post("/api/v1/ai/process", response_model=AIResponse, tags=["AI"])
async def process_ai_request(request: AIRequest):
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OpenAI API key is missing")
    
    try:
        response = await client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": request.prompt}],
            max_tokens=request.max_tokens,
