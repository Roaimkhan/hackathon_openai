# tests/conftest.py
import pytest
from unittest.mock import AsyncMock, patch
from httpx import ASGITransport, AsyncClient

from app.main import app  # Import your FastAPI app instance
from schemas.search import IntentParseResult, CompatibilityScore

@pytest.fixture
def mock_ai_service(monkeypatch):
    """Mocks OpenAI responses so tests execute instantly without API calls."""
    mock_service = AsyncMock()
    
    # Mock parse_search_intent response
    mock_service.parse_search_intent.return_value = IntentParseResult(
        query="high protein chicken",
        tags=["high-protein"],
        max_calories=800,
        max_distance_km=10.0,
        macro_targets={"protein": 30.0}
    )
    
    # Mock batch calculate_compatibility responses
    mock_service.calculate_compatibility.return_value = CompatibilityScore(
        score=0.85,
        reasoning="Fits high-protein requirement well."
    )
    
    # Override the service dependency inside your container/route
    # Adjust path according to your app structure
    monkeypatch.setattr("services.search_service.ai_service", mock_service)
    return mock_service


@pytest.fixture
async def client():
    """Async client to execute requests against FastAPI without a running network server."""
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as ac:
        yield ac