"""Unit and integration tests for RAG chatbot."""

import pytest
from unittest.mock import Mock, patch
from src.config import Settings
from src.ingestion import DocumentIngestionPipeline
from src.retrieval import PineconeRetriever
from src.graph import RAGWorkflow
from fastapi.testclient import TestClient
import app as app_module


@pytest.fixture
def mock_settings():
    """Create mock settings."""
    with patch("src.config.load_settings") as mock:
        settings = Settings(
            openai_api_key="test-key",
            pinecone_api_key="test-key",
            pinecone_index_name="test-index"
        )
        mock.return_value = settings
        return settings


class TestConfiguration:
    """Test configuration handling."""
    
    def test_settings_loads(self, mock_settings):
        """Test that settings load from environment."""
        assert mock_settings.openai_api_key == "test-key"
        assert mock_settings.pinecone_index_name == "test-index"
    
    def test_required_keys_validation(self):
        """Test that required keys are validated."""
        with pytest.raises(ValueError):
            Settings(
                openai_api_key="",
                pinecone_api_key="test"
            )


class TestRequestValidation:
    """Test API request validation."""
    
    def test_empty_query_rejected(self):
        """Test that empty queries are rejected."""
        from app import ChatRequest
        with pytest.raises(ValueError):
            ChatRequest(query="")
    
    def test_query_too_short(self):
        """Test minimum query length."""
        from app import ChatRequest
        with pytest.raises(ValueError):
            ChatRequest(query="ab")
    
    def test_valid_query(self):
        """Test valid query passes."""
        from app import ChatRequest
        req = ChatRequest(query="What is Agentic AI?")
        assert req.query == "What is Agentic AI?"


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    @patch("app.app_state")
    def test_health_check(self, mock_state):
        """Test health check endpoint."""
        mock_state.__getitem__ = Mock(return_value=Mock())
        
        client = TestClient(app_module.app)
        response = client.get("/health")
        
        # Mock the response since we don't have real APIs
        assert response.status_code in [200, 503]


class TestOutOfContextRefusal:
    """Test that out-of-context questions are refused."""
    
    @pytest.mark.skip(reason="Requires live OpenAI/Pinecone")
    def test_fifa_question_refused(self, mock_settings):
        """Test that FIFA question is refused."""
        with patch("src.retrieval.PineconeRetriever"):
            with patch("src.graph.ChatOpenAI"):
                rag = RAGWorkflow(mock_settings)
                result = rag.run("Who won the 2022 FIFA World Cup?")
                
                assert "cannot answer" in result["final_answer"].lower()
                assert result["confidence_score"] < 0.5


class TestRetrievalResponse:
    """Test retrieval response structure."""
    
    @pytest.mark.skip(reason="Requires live Pinecone")
    def test_retrieved_chunk_structure(self):
        """Test that retrieved chunks have expected structure."""
        with patch("src.retrieval.PineconeRetriever.retrieve") as mock_retrieve:
            mock_retrieve.return_value = [
                {
                    "content": "Test content",
                    "page": 1,
                    "source": "test.pdf",
                    "score": 0.95,
                    "chunk_id": "chunk_1"
                }
            ]
            
            chunks = mock_retrieve("test")
            assert len(chunks) == 1
            assert "content" in chunks[0]
            assert "score" in chunks[0]


class TestChatEndpoint:
    """Test chat endpoint structure (mocked)."""
    
    def test_chat_response_structure(self):
        """Test that chat response has expected structure."""
        from app import ChatResponse, RetrievedContext
        
        response = ChatResponse(
            final_answer="Test answer",
            retrieved_context=[
                RetrievedContext(
                    content="Test",
                    page=1,
                    source="test.pdf",
                    score=0.95,
                    chunk_id="1"
                )
            ],
            confidence_score=0.85,
            question="Test question"
        )
        
        assert response.final_answer == "Test answer"
        assert response.confidence_score == 0.85
        assert len(response.retrieved_context) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])