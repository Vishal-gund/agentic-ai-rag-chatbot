"""FastAPI application for Agentic AI RAG chatbot."""

from typing import List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


# ---------------------------------------------------------
# Request / Response Models
# ---------------------------------------------------------

class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    query: str = Field(
        ...,
        min_length=3,
        description="Question to ask about the Agentic AI eBook"
    )


class RetrievedContext(BaseModel):
    """A retrieved document chunk."""

    content: str
    page: int = 0
    source: str = ""
    score: float = 0.0
    chunk_id: str = ""


class ChatResponse(BaseModel):
    """Response returned by the RAG API."""

    final_answer: str
    retrieved_context: List[RetrievedContext]
    confidence_score: float
    question: str


# ---------------------------------------------------------
# Application State
# ---------------------------------------------------------

app_state = {
    "initialized": False,
    "rag_workflow": None,
}


# ---------------------------------------------------------
# FastAPI Application
# ---------------------------------------------------------

app = FastAPI(
    title="Agentic AI RAG API",
    description="RAG chatbot grounded on the Agentic AI eBook",
    version="1.0.0",
)


# ---------------------------------------------------------
# Health Check
# ---------------------------------------------------------

@app.get("/health")
def health_check():
    """Return application health status."""

    if app_state["initialized"]:
        return {
            "status": "healthy",
            "rag_initialized": True,
        }

    return {
        "status": "starting",
        "rag_initialized": False,
    }


# ---------------------------------------------------------
# Chat Endpoint
# ---------------------------------------------------------

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """Answer a question using the RAG workflow."""

    if not app_state["initialized"] or app_state["rag_workflow"] is None:
        raise HTTPException(
            status_code=503,
            detail="RAG system is not initialized."
        )

    try:
        result = app_state["rag_workflow"].run(request.query)

        return ChatResponse(
            final_answer=result["final_answer"],
            retrieved_context=[
                RetrievedContext(**chunk)
                for chunk in result.get("retrieved_context", [])
            ],
            confidence_score=result.get("confidence_score", 0.0),
            question=request.query,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# ---------------------------------------------------------
# Local Development
# ---------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )