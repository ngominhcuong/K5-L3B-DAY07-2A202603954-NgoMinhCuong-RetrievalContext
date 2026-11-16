"""Retrieval methods and context-selection strategies for Day 7 Milestone 3."""
from __future__ import annotations

import json
import math
import re
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any

from src.day6_connector import validate_filters

REPO_DIR = Path(__file__).resolve().parents[1]


def tokenize_vi(text: str) -> list[str]:
    """Unicode-normalized word/number tokenizer for Vietnamese and numeric tokens."""
    normalized = unicodedata.normalize("NFC", text).casefold()
    return re.findall(r"\w+(?:[.,]\w+)*", normalized)


def match_filters(chunk: dict[str, Any], filters: dict[str, Any] | None) -> bool:
    """Check whether a chunk matches all requested metadata filters."""
    cleaned = validate_filters(filters)
    if not cleaned:
        return True
    meta = chunk.get("metadata", {})
    for key, expected in cleaned.items():
        if key in ("source", "page"):
            actual = chunk.get(key)
        elif key == "document_id":
            actual = chunk.get("source_id")
        else:
            actual = meta.get(key)
        if actual != expected:
            return False
    return True


class BM25Retriever:
    """In-memory BM25Okapi lexical retriever with metadata filter support."""

    def __init__(
        self,
        chunks: list[dict[str, Any]],
        *,
        k1: float = 1.5,
        b: float = 0.75,
    ) -> None:
        if not chunks:
            raise ValueError("chunks cannot be empty")
        self.chunks = chunks
        self.k1 = k1
        self.b = b
        self.doc_tokens = [tokenize_vi(c["text"]) for c in chunks]
        self.doc_tf = [Counter(toks) for toks in self.doc_tokens]
        self.doc_len = [len(toks) for toks in self.doc_tokens]
        self.avg_dl = sum(self.doc_len) / len(self.doc_len)

        df: Counter[str] = Counter()
        for tf in self.doc_tf:
            df.update(tf.keys())
        n_docs = len(chunks)
        self.idf = {
            term: math.log(1.0 + (n_docs - freq + 0.5) / (freq + 0.5))
            for term, freq in df.items()
        }

    @classmethod
    def from_json(cls, chunks_path: Path, **kwargs: Any) -> "BM25Retriever":
        chunks = json.loads(chunks_path.read_text(encoding="utf-8"))
        return cls(chunks, **kwargs)

    def _score_doc(self, query_terms: list[str], idx: int) -> float:
        tf_map = self.doc_tf[idx]
        dl = self.doc_len[idx]
        if dl == 0:
            return 0.0
        score = 0.0
        for term in query_terms:
            tf = tf_map.get(term, 0)
            if tf <= 0 or term not in self.idf:
                continue
            denom = tf + self.k1 * (1.0 - self.b + self.b * (dl / self.avg_dl))
            score += self.idf[term] * (tf * (self.k1 + 1.0)) / denom
        return score

    def search(
        self,
        query: str,
        *,
        filters: dict[str, Any] | None = None,
        top_k: int = 3,
    ) -> list[dict[str, Any]]:
        if not query.strip():
            raise ValueError("Search query cannot be empty.")
        if top_k < 1:
            raise ValueError(f"top_k must be >= 1, got {top_k}")
        q_terms = tokenize_vi(query)
        scored: list[tuple[float, int]] = []
        for idx, chunk in enumerate(self.chunks):
            if not match_filters(chunk, filters):
                continue
            s = self._score_doc(q_terms, idx)
            if s > 0:
                scored.append((s, idx))
        scored.sort(key=lambda item: (-item[0], self.chunks[item[1]]["id"]))
        results: list[dict[str, Any]] = []
        for rank, (score, idx) in enumerate(scored[:top_k], start=1):
            results.append({**self.chunks[idx], "score": float(score), "rank": rank})
        return results


class HybridRRFRetriever:
    """Hybrid Dense + BM25 retriever fused via Reciprocal Rank Fusion (RRF)."""

    def __init__(
        self,
        dense_retriever: Any,
        lexical_retriever: Any,
        *,
        rrf_k: int = 60,
        candidate_k: int = 10,
    ) -> None:
        self.dense = dense_retriever
        self.lexical = lexical_retriever
        self.rrf_k = rrf_k
        self.candidate_k = candidate_k

    def search(
        self,
        query: str,
        *,
        filters: dict[str, Any] | None = None,
        top_k: int = 3,
    ) -> list[dict[str, Any]]:
        fetch_k = max(top_k, self.candidate_k)
        dense_hits = self.dense.search(query, filters=filters, top_k=fetch_k)
        lexical_hits = self.lexical.search(query, filters=filters, top_k=fetch_k)

        fused_scores: dict[str, float] = {}
        chunk_map: dict[str, dict[str, Any]] = {}
        dense_scores: dict[str, float] = {}
        lexical_scores: dict[str, float] = {}

        for rank, c in enumerate(dense_hits, start=1):
            cid = c["id"]
            chunk_map[cid] = c
            dense_scores[cid] = float(c.get("score", 0.0))
            fused_scores[cid] = fused_scores.get(cid, 0.0) + 1.0 / (self.rrf_k + rank)

        for rank, c in enumerate(lexical_hits, start=1):
            cid = c["id"]
            chunk_map.setdefault(cid, c)
            lexical_scores[cid] = float(c.get("score", 0.0))
            fused_scores[cid] = fused_scores.get(cid, 0.0) + 1.0 / (self.rrf_k + rank)

        ranked = sorted(fused_scores.items(), key=lambda kv: (-kv[1], kv[0]))[:top_k]
        results: list[dict[str, Any]] = []
        for rank, (cid, rrf_score) in enumerate(ranked, start=1):
            base = dict(chunk_map[cid])
            base["score"] = float(rrf_score)
            base["rank"] = rank
            base["dense_score"] = dense_scores.get(cid, 0.0)
            base["lexical_score"] = lexical_scores.get(cid, 0.0)
            results.append(base)
        return results


class RerankHybridRetriever:
    """Two-stage Hybrid RRF + normalized multi-signal Reranker."""

    def __init__(
        self,
        hybrid_retriever: HybridRRFRetriever,
        *,
        candidate_k: int = 10,
        w_dense: float = 0.50,
        w_lexical: float = 0.30,
        w_overlap: float = 0.20,
    ) -> None:
        self.hybrid = hybrid_retriever
        self.candidate_k = candidate_k
        self.w_dense = w_dense
        self.w_lexical = w_lexical
        self.w_overlap = w_overlap

    @staticmethod
    def _min_max_norm(values: list[float]) -> list[float]:
        if not values:
            return []
        lo, hi = min(values), max(values)
        if hi <= lo:
            return [1.0 if hi > 0 else 0.0 for _ in values]
        return [(v - lo) / (hi - lo) for v in values]

    def search(
        self,
        query: str,
        *,
        filters: dict[str, Any] | None = None,
        top_k: int = 3,
    ) -> list[dict[str, Any]]:
        candidates = self.hybrid.search(query, filters=filters, top_k=max(top_k, self.candidate_k))
        if not candidates:
            return []

        q_terms = set(tokenize_vi(query))
        raw_dense = [float(c.get("dense_score", 0.0)) for c in candidates]
        raw_lex = [float(c.get("lexical_score", 0.0)) for c in candidates]
        norm_dense = self._min_max_norm(raw_dense)
        norm_lex = self._min_max_norm(raw_lex)

        reranked: list[tuple[float, dict[str, Any]]] = []
        for c, nd, nl in zip(candidates, norm_dense, norm_lex):
            doc_terms = set(tokenize_vi(c["text"]))
            overlap = len(q_terms & doc_terms) / len(q_terms) if q_terms else 0.0
            final_score = self.w_dense * nd + self.w_lexical * nl + self.w_overlap * overlap
            reranked.append((final_score, c))

        reranked.sort(key=lambda item: (-item[0], item[1]["id"]))
        results: list[dict[str, Any]] = []
        for rank, (score, c) in enumerate(reranked[:top_k], start=1):
            row = dict(c)
            row["score"] = float(score)
            row["rank"] = rank
            results.append(row)
        return results


def pack_context_standard(results: list[dict[str, Any]], budget: int = 2400) -> tuple[str, list[str]]:
    """Deduplicate and pack ranked chunks up to character budget."""
    blocks: list[str] = []
    ids: list[str] = []
    seen: set[str] = set()
    for c in results:
        if c["id"] in seen:
            continue
        seen.add(c["id"])
        block = f"[{c['id']} | {c['source']} | page {c['page']}]\n{c['text']}"
        candidate = "\n\n".join(blocks + [block])
        if len(candidate) <= budget:
            blocks.append(block)
            ids.append(c["id"])
    return "\n\n".join(blocks), ids


def pack_context_with_neighbors(
    results: list[dict[str, Any]],
    all_chunks: list[dict[str, Any]],
    budget: int = 3000,
) -> tuple[str, list[str]]:
    """Pack ranked chunks and append same-page next/prev neighbor chunks if budget allows."""
    by_page: dict[tuple[str, int], list[dict[str, Any]]] = {}
    for ch in all_chunks:
        by_page.setdefault((ch["source_id"], int(ch["page"])), []).append(ch)
    for key in by_page:
        by_page[key].sort(key=lambda c: c["id"])

    expanded: list[dict[str, Any]] = []
    for c in results:
        expanded.append(c)
        same_page = by_page.get((c["source_id"], int(c["page"])), [])
        for idx, item in enumerate(same_page):
            if item["id"] == c["id"]:
                if idx + 1 < len(same_page):
                    expanded.append(same_page[idx + 1])
                if idx - 1 >= 0:
                    expanded.append(same_page[idx - 1])
                break
    return pack_context_standard(expanded, budget=budget)
