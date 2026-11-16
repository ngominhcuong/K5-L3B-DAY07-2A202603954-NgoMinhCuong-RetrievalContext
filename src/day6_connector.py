"""Day 6 Qdrant & Embedding connector and chunk exporter for Day 7."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from qdrant_client import QdrantClient, models

REPO_DIR = Path(__file__).resolve().parents[1]
DEFAULT_QDRANT_PATH = (
    REPO_DIR.parent
    / "K5-L3B-DAY06-NgoMinhCuong-2A202603954-DataIngestion"
    / "starter"
    / "qdrant_storage"
)
DEFAULT_EMBEDDING_MODEL = "intfloat/multilingual-e5-base"
DEFAULT_STRATEGY = "B"
DEFAULT_PREFIX = "day6"

ALLOWED_FILTER_FIELDS = frozenset(
    {"document_id", "source", "page", "section", "subsection", "year", "language", "document_type"}
)


def _load_env() -> None:
    load_dotenv(REPO_DIR / ".env")


def validate_filters(filters: dict[str, Any] | None) -> dict[str, Any]:
    """Validate and clean metadata filters against Day 6 allowed fields."""
    if not filters:
        return {}
    cleaned: dict[str, Any] = {}
    for key, val in filters.items():
        if key not in ALLOWED_FILTER_FIELDS:
            raise ValueError(f"Unsupported metadata filter field: {key!r}")
        if val is not None:
            cleaned[key] = val
    return cleaned


def collection_name_for(strategy: str, prefix: str = DEFAULT_PREFIX) -> str:
    safe = "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in strategy.lower())
    return f"{prefix}_{safe}"


class Day6Embedder:
    """Query embedder matching Day 6's SentenceTransformer configuration."""

    def __init__(
        self,
        model_name: str | None = None,
        device: str | None = None,
    ) -> None:
        _load_env()
        resolved_model = model_name or os.getenv("EMBEDDING_MODEL") or DEFAULT_EMBEDDING_MODEL
        if not resolved_model:
            raise ValueError("EMBEDDING_MODEL must be set to a real model name.")

        import torch
        from sentence_transformers import SentenceTransformer

        self.model_name = resolved_model
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = SentenceTransformer(self.model_name, device=self.device)
        dims = self.model.get_sentence_embedding_dimension()
        if dims is None or int(dims) <= 0:
            raise RuntimeError(f"Could not determine embedding dimensions for {self.model_name}.")
        self.dimensions = int(dims)
        self._is_e5 = "e5" in self.model_name.lower()

    def embed_query(self, question: str) -> list[float]:
        """Encode a query string using the same prefix and normalization as Day 6."""
        if not question.strip():
            raise ValueError("Question text cannot be empty.")
        text = f"query: {question}" if self._is_e5 else question
        vector = self.model.encode(
            text,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        return vector.tolist()


def _point_to_day7_chunk(payload: dict[str, Any], point_id: Any) -> dict[str, Any]:
    """Normalize a Qdrant point payload into Day 7's chunk schema."""
    meta = dict(payload)
    text = str(meta.pop("text", ""))
    chunk_id = str(meta.pop("chunk_id", point_id))
    source_id = str(meta.pop("document_id", ""))
    source = str(meta.pop("source", ""))
    page = int(meta.pop("page", -1))
    meta.pop("strategy", None)
    return {
        "id": chunk_id,
        "text": text,
        "source_id": source_id,
        "source": source,
        "page": page,
        "metadata": meta,
    }


class Day6QdrantRetriever:
    """Dense retriever querying Day 6's persistent local Qdrant store."""

    def __init__(
        self,
        storage_path: str | Path | None = None,
        strategy: str | None = None,
        collection_prefix: str | None = None,
        embedder: Day6Embedder | None = None,
        client: Any | None = None,
    ) -> None:
        _load_env()
        self.storage_path = Path(
            storage_path or os.getenv("DAY6_QDRANT_PATH") or DEFAULT_QDRANT_PATH
        )
        if not self.storage_path.is_absolute():
            self.storage_path = (REPO_DIR / self.storage_path).resolve()

        self.strategy = strategy or os.getenv("DAY6_STRATEGY") or DEFAULT_STRATEGY
        self.prefix = collection_prefix or os.getenv("DAY6_COLLECTION_PREFIX") or DEFAULT_PREFIX
        self.collection_name = collection_name_for(self.strategy, self.prefix)

        if client is not None:
            self.client = client
        else:
            if not self.storage_path.exists():
                raise FileNotFoundError(
                    f"Day 6 Qdrant storage not found at {self.storage_path}. "
                    "Run Day 6 ingestion first to populate qdrant_storage."
                )
            self.client = QdrantClient(path=str(self.storage_path))

        existing = {c.name for c in self.client.get_collections().collections}
        if self.collection_name not in existing:
            raise RuntimeError(
                f"Collection {self.collection_name!r} not found in {self.storage_path}. "
                f"Available collections: {sorted(existing)}"
            )

        self.embedder = embedder or Day6Embedder()

    def count(self) -> int:
        res = self.client.count(collection_name=self.collection_name, exact=True)
        return int(res.count)

    def search(
        self,
        query: str,
        *,
        filters: dict[str, Any] | None = None,
        top_k: int = 3,
    ) -> list[dict[str, Any]]:
        """Query Day 6 Qdrant collection and return Day 7-compatible chunk records."""
        if not query.strip():
            raise ValueError("Search query cannot be empty.")
        if top_k < 1:
            raise ValueError(f"top_k must be >= 1, got {top_k}")

        cleaned_filters = validate_filters(filters)
        q_filter = None
        if cleaned_filters:
            q_filter = models.Filter(
                must=[
                    models.FieldCondition(key=k, match=models.MatchValue(value=v))
                    for k, v in cleaned_filters.items()
                ]
            )

        query_vector = self.embedder.embed_query(query)
        response = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            query_filter=q_filter,
            limit=top_k,
            with_payload=True,
        )

        results: list[dict[str, Any]] = []
        for rank, point in enumerate(response.points, start=1):
            chunk = _point_to_day7_chunk(dict(point.payload or {}), point.id)
            chunk["score"] = float(point.score)
            chunk["rank"] = rank
            results.append(chunk)
        return results

    def export_all_chunks(self) -> list[dict[str, Any]]:
        """Scroll all chunks from the Day 6 Qdrant collection in deterministic order."""
        chunks: list[dict[str, Any]] = []
        next_offset = None
        while True:
            records, next_offset = self.client.scroll(
                collection_name=self.collection_name,
                limit=256,
                offset=next_offset,
                with_payload=True,
                with_vectors=False,
            )
            for rec in records:
                chunks.append(_point_to_day7_chunk(dict(rec.payload or {}), rec.id))
            if next_offset is None:
                break
        return sorted(chunks, key=lambda c: (c["page"], c["id"]))

    def close(self) -> None:
        if hasattr(self.client, "close"):
            self.client.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify Day 6 connection and export chunks for Day 7.")
    parser.add_argument("--check", action="store_true", help="Verify Qdrant connection, count, and embedder.")
    parser.add_argument("--export", type=Path, help="Export chunks from Day 6 Qdrant to a Day 7 JSON file.")
    parser.add_argument("--test-query", type=str, default=None, help="Optional query to test dense search.")
    args = parser.parse_args()

    retriever = Day6QdrantRetriever()
    try:
        total = retriever.count()
        print(
            f"[OK] Connected to Qdrant collection '{retriever.collection_name}' "
            f"at {retriever.storage_path} ({total} chunks)"
        )
        print(
            f"[OK] Loaded embedder '{retriever.embedder.model_name}' "
            f"(dim={retriever.embedder.dimensions}, device={retriever.embedder.device})"
        )
        if args.test_query:
            hits = retriever.search(args.test_query, top_k=3)
            print(f"[OK] Top-{len(hits)} hits for {args.test_query!r}:")
            for h in hits:
                print(f"  - rank={h['rank']} score={h['score']:.4f} id={h['id']} page={h['page']}")
        if args.export:
            chunks = retriever.export_all_chunks()
            args.export.parent.mkdir(parents=True, exist_ok=True)
            args.export.write_text(
                json.dumps(chunks, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            print(f"[OK] Exported {len(chunks)} chunks to {args.export}")
    finally:
        retriever.close()


if __name__ == "__main__":
    main()
