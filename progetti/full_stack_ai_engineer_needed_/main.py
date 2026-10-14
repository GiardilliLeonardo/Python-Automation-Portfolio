# Task: Full-Stack AI Engineer Needed | Node.js, Python & RAG

import os
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import numpy as np
from openai import AsyncOpenAI

app = FastAPI(
    title="RAG Service Engine",
    version="1.0.0",
    description="Backend microservice designed for Node.js API integration.",
)

# allow_credentials=True cannot be used with wildcard origins in CORS specification
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class Document(BaseModel):
    id: str
    text: str
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class QueryRequest(BaseModel):
    query: str
    top_k: int = Field(default=3, ge=1, le=10)


class IngestRequest(BaseModel):
    documents: List[Document]


class QueryResponse(BaseModel):
    answer: str
    sources: List[Document]


class VectorStore:
    def __init__(self, embedding_model: str = "text-embedding-3-small"):
        self.embedding_model = embedding_model
        self.documents: List[Document] = []
        self.embeddings: Optional[np.ndarray] = None

    async def _get_embedding(self, text: str) -> np.ndarray:
        response = await client.embeddings.create(
            input=text, model=self.embedding_model
        )
        return np.array(response.data[0].embedding, dtype=np.float32)

    async def add_documents(self, docs: List[Document]) -> None:
        if not docs:
            return

        texts = [doc.text for doc in docs]
        response = await client.embeddings.create(
            input=texts, model=self.embedding_model
        )
        # Ensure embeddings match the input order
        sorted_data = sorted(response.data, key=lambda item: item.index)
        new_embeddings = np.array(
            [item.embedding for item in sorted_data], dtype=np.float32
        )

        if self.embeddings is None or len(self.documents) == 0:
            self.embeddings = new_embeddings
        else:
            self.embeddings = np.vstack([self.embeddings, new_embeddings])

        self.documents.extend(docs)

    async def search(self, query: str, top_k: int = 3) -> List[Document]:
        if not self.documents or self.embeddings is None:
            return []

        query_vec = await self._get_embedding(query)

        # Cosine similarity
        norm_matrix = np.linalg.norm(self.embeddings, axis=1)
        norm_query = np.linalg.norm(query_vec)

        if norm_query == 0:
            return []

        scores = np.dot(self
