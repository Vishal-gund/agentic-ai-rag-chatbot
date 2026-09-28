"""LangGraph workflow for RAG."""

import logging
from typing import Dict, Any, List

from langgraph.graph import StateGraph
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from src.config import Settings
from src.retrieval import PineconeRetriever


# Define state schema
class RAGState(dict):
    """State for RAG workflow."""
    question: str
    context: str
    answer: str
    confidence_score: float
    retrieved_chunks: List[Dict[str, Any]]


class RAGWorkflow:
    """LangGraph RAG workflow."""
    
    SYSTEM_PROMPT = """You are a strict document-grounded assistant.

Answer the user's question ONLY using the provided retrieved context from the Agentic AI eBook.

Do not use outside knowledge.

If the retrieved context does not contain sufficient information to answer the question, respond exactly or substantially as:

"I cannot answer this question based on the provided document. The information is not present in the Agentic AI eBook."

Never fabricate facts. Never guess. Never supplement missing information with your own knowledge.

Provide clear, concise answers grounded in the document."""
    
    def __init__(self, settings: Settings):
        """Initialize workflow.
        
        Args:
            settings: Application settings
        """
        self.settings = settings
        self.logger = settings.logger
        self.retriever = PineconeRetriever(settings)
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            temperature=0.3  # Low temperature for factual responses
        )
        self.graph = self._build_graph()
    
    def _retrieve(self, state: RAGState) -> RAGState:
        """Retrieve relevant chunks.
        
        Args:
            state: Current state
            
        Returns:
            Updated state with retrieved context
        """
        self.logger.info(f"Retrieve node: processing '{state['question'][:50]}...'")
        
        try:
            chunks = self.retriever.retrieve(
                state["question"],
                top_k=self.settings.retrieval_top_k
            )
            
            state["retrieved_chunks"] = chunks
            state["context"] = self.retriever.format_context(chunks)
            
            # Calculate initial confidence based on retrieval
            if chunks:
                avg_score = sum(c["score"] for c in chunks) / len(chunks)
                state["confidence_score"] = avg_score
            else:
                state["confidence_score"] = 0.0
            
            self.logger.info(f"Retrieve node: found {len(chunks)} chunks, avg score: {state['confidence_score']:.3f}")
            return state
        
        except Exception as e:
            self.logger.error(f"Retrieve node error: {e}")
            state["context"] = "Error during retrieval."
            state["retrieved_chunks"] = []
            state["confidence_score"] = 0.0
            return state
    
    def _generate(self, state: RAGState) -> RAGState:
        """Generate answer from context.
        
        Args:
            state: Current state with context
            
        Returns:
            Updated state with answer
        """
        self.logger.info("Generate node: generating answer")
        
        try:
            # Build messages
            system_msg = SystemMessage(content=self.SYSTEM_PROMPT)
            
            user_content = (
                f"Question: {state['question']}\n\n"
                f"Retrieved Context:\n{state['context']}\n\n"
                f"Please answer the question based ONLY on the retrieved context above."
            )
            user_msg = HumanMessage(content=user_content)
            
            # Generate answer
            response = self.llm.invoke([system_msg, user_msg])
            state["answer"] = response.content
            
            # Adjust confidence based on refusal
            if "cannot answer" in response.content.lower():
                state["confidence_score"] = min(state["confidence_score"], self.settings.confidence_threshold - 0.1)
            
            self.logger.info("Generate node: answer generated")
            return state
        
        except Exception as e:
            self.logger.error(f"Generate node error: {e}")
            state["answer"] = f"Error generating answer: {e}"
            state["confidence_score"] = 0.0
            return state
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow.
        
        Returns:
            Compiled graph
        """
        workflow = StateGraph(RAGState)
        
        # Add nodes
        workflow.add_node("retrieve", self._retrieve)
        workflow.add_node("generate", self._generate)
        
        # Set entry point
        workflow.set_entry_point("retrieve")
        
        # Add edges: retrieve -> generate -> end
        workflow.add_edge("retrieve", "generate")
        workflow.set_finish_point("generate")
        
        # Compile
        return workflow.compile()
    
    def run(self, question: str) -> Dict[str, Any]:
        """Run the RAG workflow.
        
        Args:
            question: User question
            
        Returns:
            Dict with answer, context, confidence
        """
        self.logger.info(f"Starting RAG workflow for: '{question}'")
        
        state = RAGState(
            question=question,
            context="",
            answer="",
            confidence_score=0.0,
            retrieved_chunks=[]
        )
        
        try:
            result = self.graph.invoke(state)
            
            self.logger.info(f"RAG workflow complete. Confidence: {result['confidence_score']:.3f}")
            
            return {
                "final_answer": result["answer"],
                "retrieved_context": result["retrieved_chunks"],
                "confidence_score": round(result["confidence_score"], 3),
                "question": question
            }
        
        except Exception as e:
            self.logger.error(f"Workflow execution error: {e}")
            return {
                "final_answer": f"Error: {e}",
                "retrieved_context": [],
                "confidence_score": 0.0,
                "question": question,
                "error": str(e)
            }