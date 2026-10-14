# Task: Build an AI Agent with RAG for Business Workflow Automation.

import json
import os
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional
import numpy as np
from openai import OpenAI
from pydantic import BaseModel, Field


# --- Configuration & Data Models ---

@dataclass
class Document:
    doc_id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None


class WorkflowTicket(BaseModel):
    ticket_id: str
    customer_id: str
    query: str
    transaction_amount: float
    currency: str = "USD"


class AgentActionResponse(BaseModel):
    status: str
    action_taken: str
    details: Dict[str, Any]


# --- In-Memory Vector Store for RAG ---

class SimpleVectorStore:
    def __init__(self, client: OpenAI, model: str = "text-embedding-3-small"):
        self.client = client
        self.model = model
        self.documents: List[Document] = []

    def _get_embedding(self, text: str) -> List[float]:
        response = self.client.embeddings.create(
            input=text,
            model=self.model
        )
        return response.data[0].embedding

    def add_documents(self, docs: List[Document]) -> None:
        for doc in docs:
            if not doc.embedding:
                doc.embedding = self._get_embedding(doc.content)
            self.documents.append(doc)

    def search(self, query: str, top_k: int = 2) -> List[Document]:
        if not self.documents:
            return []

        query_embedding = np.array(self._get_embedding(query))
        scored_docs = []

        for doc in self.documents:
            if doc.embedding is None:
                continue
            doc_emb = np.array(doc.embedding)
            norm_q = np.linalg.norm(query_embedding)
            norm_d = np.linalg.norm(doc_emb)
            
            if norm_q == 0 or norm_d == 0:
                similarity = 0.0
            else:
                similarity = float(np.dot(query_embedding, doc_emb) / (norm_q * norm_d))
            scored_docs.append((similarity, doc))

        scored_docs.sort(key=lambda x: x[0], reverse=True)
        return [doc for _, doc in scored_docs[:top_k]]


# --- External API Integrations (Business Tools) ---

class ExternalServicesAPI:
    """Mock integration with external ERP/Billing APIs."""

    @staticmethod
    def execute_refund(customer_id: str, amount: float, reason: str) -> Dict[str, Any]:
        return {
            "status": "SUCCESS",
            "transaction_id": f"tx_ref_{customer_id[:4]}_{int(amount)}",
            "amount_refunded": amount,
            "reason": reason
        }

    @staticmethod
    def escalate_ticket(ticket_id: str, department: str, priority: str) -> Dict[str, Any]:
        return {
            "status": "ESCALATED",
            "ticket_id": ticket_id,
            "assigned_queue": department,
            "priority": priority
        }


# --- RAG-Driven Business Automation Agent ---

class BusinessWorkflowAgent:
    def __init__(self, openai_client: OpenAI, vector_store: SimpleVectorStore, model: str = "gpt-4o"):
        self.client = openai_client
        self.vector_store = vector_store
        self.model = model
        self.tools_schema = self._init_tools_schema()
        self.available_tools: Dict[str, Callable] = {
            "execute_refund": ExternalServicesAPI.execute_refund,
            "escalate_ticket": ExternalServicesAPI.escalate_ticket,
        }

    def _init_tools_schema(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "execute_refund",
                    "description": "Processes an automated monetary refund to the customer according to policy.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "customer_id": {"type": "string", "description": "Customer identifier"},
                            "amount": {"type": "number", "description": "Refund amount"},
                            "reason": {"type": "string", "description": "Policy ground for refund"}
                        },
                        "required": ["customer_id", "amount", "reason"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "escalate_ticket",
                    "description": "Escalates complex requests or out-of-policy disputes to a human department.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "ticket_id": {"type": "string", "description": "The support ticket ID"},
                            "department": {"type": "string", "description": "Target team (e.g., 'Finance', 'Legal', 'L2_Support')"},
                            "priority": {"type": "string", "enum": ["low", "medium", "high", "critical"]}
                        },
                        "required": ["ticket_id", "department", "priority"]
                    }
                }
            }
        ]

    def process_ticket(self, ticket: WorkflowTicket) -> AgentActionResponse:
        # Step 1: RAG Retrieval - Fetch authoritative enterprise policy
        retrieved_docs = self.vector_store.search(ticket.query, top_k=2)
        context = "\n---\n".join([d.content for d in retrieved_docs]) if retrieved_docs else "No specific policy retrieved."

        # Step 2: System prompt construction
        system_prompt = (
            "You are an autonomous enterprise operations agent. "
            "Use the provided Policy Context to decide actions on incoming business requests.\n"
            "Strictly adhere to thresholds, SLA conditions, and operational constraints.\n\n"
            f"Policy Context:\n{context}"
        )

        user_prompt = (
            f"Process the following ticket:\n"
            f"Ticket ID: {ticket.ticket_id}\n"
            f"Customer ID: {ticket.customer_id}\n"
            f"Query: {ticket.query}\n"
            f"Transaction Amount: {ticket.transaction_amount} {ticket.currency}"
        )

        # Step 3: LLM Inference with Function Calling
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self.tools_schema,
            tool_choice="auto"
        )

        response_message = response.choices[0].message

        # Step 4: Handle tool calls or default response
        if response_message.tool_calls:
            tool_call = response_message.tool_calls[0]
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            if function_name in self.available_tools:
                tool_to_call = self.available_tools[function_name]
                execution_result = tool_to_call(**function_args)
                return AgentActionResponse(
                    status="COMPLETED",
                    action_taken=function_name,
                    details=execution_result
                )

        return AgentActionResponse(
            status="MANUAL_REVIEW_REQUIRED",
            action_taken="none",
            details={"message": response_message.content or "No action could be determined automatically."}
        )
