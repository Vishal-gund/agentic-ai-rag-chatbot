"""Streamlit UI for RAG chatbot."""

import logging
import sys

import streamlit as st

from src.config import load_settings
from src.graph import RAGWorkflow


# Page config
st.set_page_config(
    page_title="Agentic AI Chatbot",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if "rag_workflow" not in st.session_state:
    try:
        settings = load_settings()
        st.session_state.rag_workflow = RAGWorkflow(settings)
        st.session_state.settings = settings
    except Exception as e:
        st.error(f"Failed to initialize RAG workflow: {e}")
        sys.exit(1)


# Header
st.title("🤖 Agentic AI Chatbot")
st.markdown("""
This chatbot answers questions about the **Agentic AI eBook** using Retrieval-Augmented Generation (RAG).

**How it works:**
1. Your question is converted to embeddings
2. The system retrieves relevant passages from the eBook
3. An LLM generates an answer based ONLY on the retrieved context
4. You see the answer, retrieved passages, and confidence score
""")

st.divider()

# Sidebar with info
with st.sidebar:
    st.header("📚 About")
    st.write("""
    **Technology Stack:**
    - LangChain + LangGraph
    - OpenAI Embeddings
    - Pinecone Vector DB
    - FastAPI Backend
    - Streamlit UI
    """)
    
    st.write("""
    **Features:**
    - Document-grounded answers
    - Confidence scoring
    - Retrieved context display
    - Out-of-context question handling
    """)
    
    st.divider()
    
    st.subheader("Sample Questions")
    sample_questions = [
        "What is Agentic AI according to the eBook?",
        "How do AI agents differ from traditional automation systems?",
        "What are the core components of an Agentic Architecture?",
        "What role does memory play in Agentic AI workflows?",
        "Who won the 2022 FIFA World Cup?"
    ]
    
    for q in sample_questions:
        if st.button(q, key=f"sample_{q}"):
            st.session_state.user_query = q


# Main chat interface
col1, col2 = st.columns([3, 1])

with col1:
    user_query = st.text_input(
        "Ask a question about the Agentic AI eBook:",
        placeholder="e.g., What is Agentic AI?",
        key="user_query" if "user_query" not in st.session_state else None,
        value=st.session_state.get("user_query", "")
    )

with col2:
    submit_button = st.button("🚀 Submit", use_container_width=True)

st.divider()

# Process query
if submit_button or (st.session_state.get("user_query") and st.session_state.get("query_submitted")):
    if not user_query.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Processing your question..."):
            try:
                result = st.session_state.rag_workflow.run(user_query)
                st.session_state.last_result = result
                st.session_state.query_submitted = False
            except Exception as e:
                st.error(f"Error processing query: {e}")
                st.session_state.last_result = None

# Display results
if "last_result" in st.session_state and st.session_state.last_result:
    result = st.session_state.last_result
    
    # Answer section
    st.subheader("📝 Answer")
    answer_container = st.container(border=True)
    with answer_container:
        st.markdown(result["final_answer"])
    
    # Confidence score
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("🎯 Confidence Score")
    with col2:
        confidence = result["confidence_score"]
        if confidence > 0.7:
            color = "🟢"
        elif confidence > 0.4:
            color = "🟡"
        else:
            color = "🔴"
        st.metric("Relevance", f"{color} {confidence:.1%}")
    
    # Progress bar for confidence
    st.progress(min(max(confidence, 0), 1))
    
    # Retrieved context
    if result["retrieved_context"]:
        st.subheader("📚 Retrieved Context")
        
        for i, chunk in enumerate(result["retrieved_context"], 1):
            with st.expander(
                f"Source {i}: {chunk['source']} (Page {chunk['page']}) - Score: {chunk['score']:.3f}"
            ):
                st.markdown(chunk["content"])
    else:
        st.info("No relevant context retrieved from the document.")
    
    # Refusal indicator
    if "cannot answer" in result["final_answer"].lower():
        st.warning(
            "⚠️ **Out-of-Context Question**: This question is not covered in the Agentic AI eBook. "
            "The system correctly refused to answer from general knowledge."
        )

# Footer
st.divider()
st.markdown(
    """
    <div style='text-align: center; color: #888; font-size: 0.9em;'>
    RAG-based AI Chatbot | Powered by LangChain, OpenAI, and Pinecone
    </div>
    """,
    unsafe_allow_html=True
)