import math
import re
from dataclasses import dataclass
from typing import Any

from backend.app.security import Role, UserContext
from backend.app.store import DataStore


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


@dataclass
class RetrievalResult:
    score: float
    document: dict[str, Any]
    chunk: dict[str, Any]


class Retriever:
    """Local deterministic fallback; pgvector/Sentence Transformers can replace scoring only."""

    def __init__(self, store: DataStore):
        self.store = store

    def search(self, query: str, user: UserContext, project_id: str | None = None, limit: int = 5) -> list[RetrievalResult]:
        user.require("documents" if user.role != Role.SUPPLIER else "external_documents")
        query_tokens = _tokens(query)
        results: list[RetrievalResult] = []
        for doc in self.store.all("engineering_documents"):
            if not (doc["is_current"] and doc["revision_status"] == "Released"):
                continue
            if project_id and doc["project_id"] != project_id:
                continue
            if user.role == Role.SUPPLIER and doc["classification"] != "external":
                continue
            for chunk in self.store.filter("document_chunks", revision_id=doc["revision_id"]):
                terms = _tokens(f"{doc['title']} {chunk['text']}")
                overlap = len(query_tokens & terms)
                score = overlap / math.sqrt(max(1, len(query_tokens) * len(terms)))
                if score > 0:
                    results.append(RetrievalResult(score=round(score, 4), document=doc, chunk=chunk))
        return sorted(results, key=lambda r: r.score, reverse=True)[:limit]
