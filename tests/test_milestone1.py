"""Offline unit tests for Day 7 Milestone 1 (Day 6 connector & benchmark preparation)."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.day6_connector import Day6QdrantRetriever, collection_name_for, validate_filters
from src.prepare_benchmark import build_benchmark, validate_benchmark_counts


class _FakeEmbedder:
    model_name = "intfloat/multilingual-e5-base"
    dimensions = 4
    device = "cpu"

    def embed_query(self, question: str) -> list[float]:
        return [0.25, 0.25, 0.25, 0.25]


class _FakeQdrantClient:
    def __init__(self) -> None:
        self.last_query_filter = None

    def get_collections(self):
        return SimpleNamespace(collections=[SimpleNamespace(name="day6_b")])

    def count(self, collection_name: str, exact: bool = True):
        return SimpleNamespace(count=1)

    def query_points(self, collection_name: str, query, query_filter=None, limit: int = 3, with_payload: bool = True):
        self.last_query_filter = query_filter
        pt = SimpleNamespace(
            id="uuid-1",
            score=0.91,
            payload={
                "strategy": "B",
                "chunk_id": "wb_B_p11_c01",
                "document_id": "wb-taking-stock-2023-08",
                "source": "starter/data/data.pdf",
                "page": 11,
                "section": "tong_quan",
                "text": "Tăng trưởng GDP dự kiến đạt 4,7% trong năm 2023.",
            },
        )
        return SimpleNamespace(points=[pt])

    def scroll(self, collection_name: str, limit: int = 256, offset=None, with_payload: bool = True, with_vectors: bool = False):
        rec = SimpleNamespace(
            id="uuid-1",
            payload={
                "strategy": "B",
                "chunk_id": "wb_B_p11_c01",
                "document_id": "wb-taking-stock-2023-08",
                "source": "starter/data/data.pdf",
                "page": 11,
                "section": "tong_quan",
                "text": "Tăng trưởng GDP dự kiến đạt 4,7% trong năm 2023.",
            },
        )
        return [rec], None


class Milestone1Tests(unittest.TestCase):
    def test_collection_name_and_filter_validation(self) -> None:
        self.assertEqual(collection_name_for("B", "day6"), "day6_b")
        self.assertEqual(validate_filters({"section": "tong_quan", "year": None}), {"section": "tong_quan"})
        with self.assertRaises(ValueError):
            validate_filters({"unknown_field": "abc"})

    def test_retriever_normalizes_day7_schema_and_applies_filter(self) -> None:
        fake_client = _FakeQdrantClient()
        retriever = Day6QdrantRetriever(strategy="B", embedder=_FakeEmbedder(), client=fake_client)
        hits = retriever.search("GDP 2023", filters={"section": "tong_quan"}, top_k=3)
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["id"], "wb_B_p11_c01")
        self.assertEqual(hits[0]["source_id"], "wb-taking-stock-2023-08")
        self.assertEqual(hits[0]["page"], 11)
        self.assertEqual(hits[0]["metadata"]["section"], "tong_quan")
        self.assertIsNotNone(fake_client.last_query_filter)

        exported = retriever.export_all_chunks()
        self.assertEqual(len(exported), 1)
        self.assertEqual(exported[0]["id"], "wb_B_p11_c01")

    def test_build_benchmark_from_day6_meets_minimum_counts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ans, cases = build_benchmark(out_dir=Path(tmp))
            self.assertEqual(len(ans), 20)
            self.assertEqual(len(cases), 24)
            validate_benchmark_counts(cases)
            unans = [c for c in cases if not c["answerable"]]
            self.assertEqual(len(unans), 4)
            self.assertTrue(all(u.get("absence_reason") for u in unans))


if __name__ == "__main__":
    unittest.main()
