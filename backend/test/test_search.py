# tests/test_search.py
import pytest
from unittest.mock import AsyncMock
import asyncio

pytestmark = pytest.mark.asyncio


async def test_search_meals_success(client, mock_ai_service):
    """Verifies search endpoint parses intent and ranks results correctly."""
    payload = {
        "user_prompt": "I want a high protein meal near me",
        "user_lat": 33.7182,
        "user_lon": 73.0605
    }
    
    response = await client.post("/api/v1/search", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    # Assert return structure
    assert "results" in data
    assert "parsed_intent" in data
    assert data["parsed_intent"]["query"] == "high protein chicken"
    assert len(data["results"]) > 0


async def test_search_meals_ai_timeout_fallback(client, monkeypatch):
    """Verifies that if OpenAI times out (>2.5s), search gracefully falls back to distance/tag scoring."""
    
    async def slow_rank(*args, **kwargs):
        # Simulate AI call hanging beyond the batch timeout threshold
        await asyncio.sleep(3.0)
        return None

    # Patch calculate_compatibility to simulate timeout
    monkeypatch.setattr(
        "services.ai_service.AIService.calculate_compatibility", 
        slow_rank
    )

    payload = {
        "user_prompt": "Keto lunch under 500 cals",
        "user_lat": 33.7182,
        "user_lon": 73.0605
    }

    response = await client.post("/api/v1/search", json=payload)

    # API should still succeed using fallback rule-based ranking
    assert response.status_code == 200
    data = response.json()
    assert "results" in data