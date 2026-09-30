"""Tests for health and diagnostics endpoint."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    """Fixture returning FastAPI TestClient instance."""
    return TestClient(app)


def test_health_check_endpoint(client: TestClient) -> None:
    """Test that GET /health responds with 200 and valid schema."""
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert "app_name" in data
    assert "version" in data
    assert "ollama_connected" in data
    assert "ollama_model" in data
    assert "vector_store_initialized" in data
    assert "database_path" in data


def test_list_documents_endpoint(client: TestClient) -> None:
    """Test that GET /api/v1/documents returns an empty list or existing list."""
    response = client.get("/api/v1/documents")
    assert response.status_code == 200
    data = response.json()
    assert "documents" in data
    assert "total_count" in data
    assert isinstance(data["documents"], list)
