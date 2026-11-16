"""Offline unit tests for Day 7 Milestone 3 (BM25, Hybrid RRF, Rerank, Neighbor Context)."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.retrievers import (
    BM25Retriever,
    HybridRRFRetriever,
    RerankHybridRetriever,
    pack_context_with_neighbors,
)
from src.run_m3_experiments import evaluate_config

CHUNKS = [
    {
        "id": "doc_p11_c01",
        "text": "Tăng trưởng GDP Việt Nam năm 2023 dự kiến đạt 4,7%.",
        "source_id": "doc",
        "source": "doc.pdf",
        "page": 11,
        "metadata": {"section": "tong_quan"},
    },
    {
        "id": "doc_p11_c02",
        "text": "Lạm phát CPI giảm từ 4,9% xuống 2% nhờ giá nhiên liệu hạ nhiệt.",
        "source_id": "doc",
        "source": "doc.pdf",
        "page": 11,
        "metadata": {"section": "tong_quan"},
    },
    {
        "id": "doc_p45_c01",
        "text": "Việt Nam có 47 cảng biển nhưng 95% hàng hóa đi qua 3 cảng lớn.",
        "source_id": "doc",
        "source": "doc.pdf",
        "page": 45,
        "metadata": {"section": "chuong_2"},
    },
]


class _FakeDense:
    def search(self, query: str, *, filters=None, top_k: int = 3):
        rows = [
            {**CHUNKS[2], "score": 0.85, "rank": 1},
            {**CHUNKS[0], "score": 0.80, "rank": 2},
            {**CHUNKS[1], "score": 0.70, "rank": 3},
        ]
        if filters and "section" in filters:
            rows = [r for r in rows if r["metadata"].get("section") == filters["section"]]
        return rows[:top_k]


class Milestone3Tests(unittest.TestCase):
    def test_bm25_and_filter(self) -> None:
        bm25 = BM25Retriever(CHUNKS)
        hits = bm25.search("tăng trưởng GDP 4,7%", top_k=2)
        self.assertEqual(hits[0]["id"], "doc_p11_c01")

        filtered = bm25.search("Việt Nam", filters={"section": "chuong_2"}, top_k=3)
        self.assertEqual([h["id"] for h in filtered], ["doc_p45_c01"])

    def test_hybrid_rrf_and_rerank(self) -> None:
        bm25 = BM25Retriever(CHUNKS)
        hybrid = HybridRRFRetriever(_FakeDense(), bm25, rrf_k=60, candidate_k=3)
        rerank = RerankHybridRetriever(hybrid, candidate_k=3)

        h_hits = hybrid.search("47 cảng biển 95% hàng hóa", top_k=3)
        self.assertEqual(h_hits[0]["id"], "doc_p45_c01")

        r_hits = rerank.search("47 cảng biển 95% hàng hóa", top_k=3)
        self.assertEqual(r_hits[0]["id"], "doc_p45_c01")

    def test_neighbor_context_and_evaluation(self) -> None:
        bm25 = BM25Retriever(CHUNKS)
        ctx, ids = pack_context_with_neighbors([{**CHUNKS[0], "score": 0.9, "rank": 1}], CHUNKS, budget=1000)
        self.assertEqual(ids, ["doc_p11_c01", "doc_p11_c02"])
        self.assertIn("Lạm phát CPI", ctx)

        questions = [
            {
                "id": "q_test",
                "split": "dev",
                "question": "Tăng trưởng GDP 2023?",
                "gold": [{"source_id": "doc", "page": 11, "evidence": "4,7%"}],
                "expected_answer": "4,7%",
            }
        ]
        summary, _ = evaluate_config("bm25", "BM25", bm25, questions, CHUNKS, top_k=3, budget=1000)
        self.assertEqual(summary["hit1_ratio"], "1/1")
        self.assertEqual(summary["context_ratio"], "1/1")


if __name__ == "__main__":
    unittest.main()
