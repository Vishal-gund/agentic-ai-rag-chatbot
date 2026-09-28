# RAG-based AI Chatbot: Agentic AI eBook Query System

## Overview

This project implements a **Retrieval-Augmented Generation (RAG)** chatbot that answers questions **exclusively** about the "Agentic AI" eBook using modern AI technologies.

The chatbot retrieves relevant passages from the PDF, grounds its answers in the document, and explicitly refuses to answer questions outside the document's scope—preventing hallucination and ensuring factual accuracy.

## Objective

Build a production-ready RAG system that:
- ✅ Loads and processes the Agentic AI eBook PDF
- ✅ Splits documents into semantic chunks
- ✅ Generates embeddings using OpenAI's `text-embedding-3-small`
- ✅ Stores vectors in Pinecone (1536-dimensional, cosine similarity)
- ✅ Retrieves top-k relevant chunks for user queries
- ✅ Uses LangGraph to orchestrate a retrieval + generation workflow
- ✅ Generates grounded answers using GPT-4 Turbo
- ✅ Returns confidence/relevance scores for transparency
- ✅ Exposes API via FastAPI with `/chat` and `/health` endpoints
- ✅ Provides an interactive UI via Streamlit
- ✅ Refuses out-of-context questions (tested with FIFA 2022 benchmark)
- ✅ Includes comprehensive testing and documentation

## Architecture