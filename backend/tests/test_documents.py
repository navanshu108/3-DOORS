"""Deterministic unit tests for local document extraction and chunking."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.core.config import Settings
from app.core.exceptions import DocumentIngestionError
from app.services.documents import DocumentService


class FakeStore:
    """Minimal storage fake; extraction tests do not call its methods."""


class FakeLLM:
    """Minimal LLM fake; extraction tests do not call its methods."""


@pytest.fixture
def service(tmp_path: Path) -> DocumentService:
    settings = Settings(
        database_path=tmp_path / "vectors",
        documents_path=tmp_path / "documents",
        cache_path=tmp_path / "cache",
        chunk_size=20,
        chunk_overlap=5,
    )
    settings.ensure_directories()
    return DocumentService(settings, FakeStore(), FakeLLM())  # type: ignore[arg-type]


def test_chunks_preserve_all_content(service: DocumentService) -> None:
    chunks = service._chunk_text("one two three four five six seven eight nine")
    assert len(chunks) > 1
    assert all(chunk for chunk in chunks)


def test_rejects_empty_text_document(service: DocumentService, tmp_path: Path) -> None:
    path = tmp_path / "empty.txt"
    path.write_text(" \n\t ", encoding="utf-8")
    with pytest.raises(DocumentIngestionError, match="No readable text"):
        service._extract_text(path, ".txt")
