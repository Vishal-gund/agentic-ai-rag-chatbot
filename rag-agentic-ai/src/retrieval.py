"""Retrieval from Pinecone vector database."""

import logging
from typing import List, Dict, Any

from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone

from src.config import Settings


class RetrievedChunk(dict):
    """Retrieved document chunk with metadata."""
    pass


class PineconeRetriever:
    """Retrieves relevant chunks from Pinecone."""
    
    def __init__(self, settings: Settings):
        """Initialize retriever.
        
        Args:
            settings: Application settings
        """
        self.settings = settings
        self.logger = settings.logger
        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            api_key=settings.openai_api_key
        )
        self.pc = Pinecone(api_key=settings.pinecone_api_key)
        self.index = self.pc.Index(settings.pinecone_index_name)
    
    def retrieve(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """Retrieve relevant chunks for query.
        
        Args:
            query: User query
            top_k: Number of results to retrieve (default from settings)
            
        Returns:
            List of retrieved chunks with metadata and scores
        """
        if not query or not query.strip():
            self.logger.warning("Empty query received")
            return []
        
        if top_k is None:
            top_k = self.settings.retrieval_top_k
        
        try:
            self.logger.info(f"Retrieving top {top_k} chunks for query: '{query[:50]}...'")
            
            # Generate embedding for query
            query_embedding = self.embeddings.embed_query(query)
            
            # Search Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            if not results or not results.get("matches"):
                self.logger.warning("No relevant chunks found")
                return []
            
            # Format results
            retrieved_chunks = []
            for match in results["matches"]:
                chunk = {
                    "content": match["metadata"].get("content_preview", ""),
                    "page": match["metadata"].get("page", 0),
                    "source": match["metadata"].get("source", "unknown"),
                    "score": float(match["score"]),
                    "chunk_id": match["id"]
                }
                retrieved_chunks.append(chunk)
            
            self.logger.info(f"✓ Retrieved {len(retrieved_chunks)} chunks")
            return retrieved_chunks
        
        except Exception as e:
            self.logger.error(f"Retrieval error: {e}")
            raise
    
    def format_context(self, chunks: List[Dict[str, Any]]) -> str:
        """Format retrieved chunks into context string.
        
        Args:
            chunks: Retrieved chunks
            
        Returns:
            Formatted context string
        """
        if not chunks:
            return "No relevant context found."
        
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            part = (
                f"[Source: {chunk['source']}, Page {chunk['page']}, "
                f"Score: {chunk['score']:.3f}]\n"
                f"{chunk['content']}\n"
            )
            context_parts.append(part)
        
        return "\n".join(context_parts)