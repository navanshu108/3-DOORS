"""Router tests do not require Ollama, LanceDB, or browser-use."""

from __future__ import annotations

import pytest

from app.agent.router import AgentRouter
from app.models.schemas import RouteDestination, SourceCitation, SourceType


class FakeRag:
    async def retrieve(self, _query: str, limit: int = 5) -> list[SourceCitation]:
        _ = limit
        return [
            SourceCitation(
                title="notes",
                source_type=SourceType.LOCAL_DOC,
                reference_id="1",
                snippet="Local note",
                score=0.9,
            )
        ]

    async def evaluate_context_sufficiency(
        self, _query: str, _sources: list[SourceCitation]
    ) -> tuple[bool, float, str]:
        return True, 0.9, "Local context is sufficient."


@pytest.mark.asyncio
async def test_temporal_query_uses_hybrid_route() -> None:
    decision, sources, _ = await AgentRouter(FakeRag(), object()).route_query(
        "What is the latest plan?"
    )  # type: ignore[arg-type]
    assert decision.destination is RouteDestination.HYBRID
    assert sources


@pytest.mark.asyncio
async def test_force_web_bypasses_retrieval() -> None:
    decision, sources, _ = await AgentRouter(FakeRag(), object()).route_query(
        "anything", force_web=True
    )  # type: ignore[arg-type]
    assert decision.destination is RouteDestination.WEB_RESEARCH
    assert sources == []
