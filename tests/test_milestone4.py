"""Offline unit tests for Day 7 Milestone 4 (review template & agent_metrics compatibility)."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "starter"))

from agent_metrics import aggregate
from src.prepare_reviews import build_review_artifacts


class Milestone4Tests(unittest.TestCase):
    def test_build_review_artifacts_compatible_with_agent_metrics(self) -> None:
        cases = [
            {"id": "q16", "split": "test", "question": "CTMTQG?", "answerable": True},
            {"id": "u03", "split": "test", "question": "Lãi suất 2024?", "answerable": False, "absence_reason": "Không có"},
        ]
        questions = [
            {"id": "q16", "split": "test", "question": "CTMTQG?", "gold": [{"source_id": "doc", "page": 50, "evidence": "3 CTMTQG"}], "expected_answer": "3 CTMTQG"}
        ]
        traces = [
            {
                "query_id": "q16",
                "status": "answered",
                "answer": "Còn 3 CTMTQG [c1].",
                "citations": ["c1"],
                "events": [{"event": "search"}, {"event": "answer"}],
                "final_context": "[c1] 3 CTMTQG",
            },
            {
                "query_id": "u03",
                "status": "abstain",
                "answer": "Không đủ bằng chứng để trả lời.",
                "citations": [],
                "events": [{"event": "search"}, {"event": "invalid_or_missing_citations"}],
                "final_context": "",
            },
        ]

        reviews, audit_md = build_review_artifacts(cases, traces, questions)
        self.assertIn("## `q16`", audit_md)
        self.assertIn("## `u03`", audit_md)

        report = aggregate(cases, traces, reviews)
        self.assertEqual(report["tool_use"], {"n": 2, "N": 2})
        self.assertEqual(report["grounded_answer"]["mean"], 2.0)
        self.assertEqual(report["citation_validity"], {"n": 1, "N": 1})
        self.assertEqual(report["abstention"], {"n": 1, "N": 1})
        self.assertEqual(report["false_abstention"], {"n": 0, "N": 1})


if __name__ == "__main__":
    unittest.main()
