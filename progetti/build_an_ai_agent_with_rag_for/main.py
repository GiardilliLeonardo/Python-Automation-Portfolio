# Task: Build an AI Agent with RAG for Business Workflow Automation.

import os
import json
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd
from openai import OpenAI

# ==============================================================================
# CONFIGURATION & DATA MODELS
# ==============================================================================

@dataclass
class WorkflowConfig:
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    model_name: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"
    input_excel_path: str = "business_invoices.xlsx"
    output_excel_path: str = "processed_business_invoices.xlsx"
    similarity_top_k: int = 2

@dataclass
class SOPDocument:
    doc_id: str
    title: str
    content: str
    embedding: Optional[List[float]] = None

# ==============================================================================
# RAG ENGINE (IN-MEMORY VECTOR STORE)
# ==============================================================================

class LightweightRAGEngine:
    def __init__(self, client: OpenAI, model: str):
        self.client = client
        self.embedding_model = model
        self.documents: List[SOPDocument] = []
        self._embeddings_matrix: Optional[np.ndarray] = None

    def add_documents(self, docs: List[SOPDocument]) -> None:
        if not docs:
            return

        texts_to_embed = [f"{d.title}: {d.content}" for d in docs]
        response = self.client.embeddings.create(
            input=texts_to_embed,
            model=self.embedding_model
        )
        for i, item in enumerate(response.data):
            docs[i].embedding = item.embedding

        self.documents.extend(docs)
        embeddings = [doc.embedding for doc in self.documents if doc.embedding is not None]
        self._embeddings_matrix = np.array(embeddings, dtype=np.float32)

    def search(self, query: str, top_k: int = 2) -> List[SOPDocument]:
        if self._embeddings_matrix is None or len(self.documents) == 0:
            return []

        query_response = self.client.embeddings.create(
            input=[query],
            model=self.embedding_model
        )
        query_vector = np.array(query_response.data[0].embedding, dtype=np.float32)

        # Cosine similarity calculation
        norm_matrix = np.linalg.norm(self._embeddings_matrix, axis=1)
        norm_query = np.linalg.norm(query_vector)
        similarities = np.dot(self._embeddings_matrix, query_vector) / (norm_matrix * norm_query + 1e-10)

        top_k = min(top_k, len(self.documents))
        top_indices = np.argsort(similarities)[::-1][:top_k]
        return [self.documents[idx] for idx in top_indices]

# ==============================================================================
# BUSINESS WORKFLOW AUTOMATION AGENT
# ==============================================================================

class InvoiceResolutionAgent:
    def __init__(self, config: WorkflowConfig):
        self.config = config
        self.client = OpenAI(api_key=config.openai_api_key)
        self.rag = LightweightRAGEngine(self.client, config.embedding_model)
        self._initialize_knowledge_base()

    def _initialize_knowledge_base(self) -> None:
        sop_data = [
            SOPDocument(
                doc_id="SOP-001",
                title="Small Balance Write-offs",
                content="Discrepancies under $25.00 can be automatically written off without manager approval. Status: APPROVED."
            ),
            SOPDocument(
                doc_id="SOP-002",
                title="Damaged Goods Protocol",
                content="If damage is reported by client, request RMA documentation if invoice exceeds $500. Under $500, issue credit memo instantly. Status: CREDIT_PENDING."
            ),
            SOPDocument(
                doc_id="SOP-003",
                title="Service Delay Compensation",
                content="For late delivery issues, apply a mandatory 10% penalty credit up to a maximum of $200. Status: ESCALATED."
            ),
            SOPDocument(
                doc_id="SOP-004",
                title="Fraud and Duplicate Billing",
                content="Flag suspected duplicate charges or unverified vendor requests immediately to compliance. Status: REJECTED."
            )
        ]
        self.rag.add_documents(sop_data)

    def process_invoice_dispute(self, row: pd.Series) -> Dict[str, Any]:
        dispute_query = (
            f"Vendor: {row.get('Vendor', 'Unknown')}, "
            f"Amount: {row.get('DiscrepancyAmount', 0.0)}, "
            f"Reason: {row.get('DisputeReason', 'N/A')}"
        )
        relevant_docs = self.rag.search(dispute_query, top_k=self.config.similarity_top_k)

        context_str = "\n".join([f"- [{doc.doc_id}] {doc.title}: {doc.content}" for doc in relevant_docs])

        system_prompt = (
            "You are an enterprise operations resolution agent. Your role is to resolve billing discrepancies.\n"
            "Analyze the invoice data and follow internal SOPs strictly.\n"
            "Return valid JSON only matching this schema:\n"
            "{\n"
            '  "decision_status": "APPROVED" | "CREDIT_PENDING" | "ESCALATED" | "REJECTED",\n'
            '  "action_taken": "Detailed explanation of the action taken",\n'
            '  "policy_applied": "ID of SOP applied",\n'
            '  "financial_adjustment": float\n'
            "}"
        )

        user_prompt = (
            f"RELEVANT SOP POLICIES:\n{context_str}\n\
