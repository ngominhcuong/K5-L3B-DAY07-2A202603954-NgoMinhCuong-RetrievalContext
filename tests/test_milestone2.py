"""Offline unit tests for Day 7 Milestone 2 (LLMController & Agent runner)."""
from __future__ import annotations

import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.llm_controller import (
    LLMController,
    ProviderConfig,
    parse_controller_json,
    resolve_provider_config,
)
from src.run_agent_eval import run_cases

CHUNK = {
    "id": "wb_B_p11_c02",
    "text": "Kinh tế Việt Nam dự kiến tăng trưởng 4,7% trong năm 2023.",
    "source_id": "wb-taking-stock-2023-08",
    "source": "starter/data/data.pdf",
    "page": 11,
    "score": 0.88,
    "rank": 1,
    "metadata": {"section": "tong_quan"},
}


class _FakeRetriever:
    def __init__(self, results):
        self._results = results

    def search(self, query: str, *, filters=None, top_k: int = 3):
        return self._results[:top_k]


class Milestone2Tests(unittest.TestCase):
    def test_parse_controller_json_plain_and_fenced(self) -> None:
        a1 = parse_controller_json('{"action": "search", "query": "GDP 2023"}')
        self.assertEqual(a1, {"action": "search", "query": "GDP 2023"})

        a2 = parse_controller_json(
            '```json\n{"action": "answer", "answer": "4,7% [c1]", "citations": ["c1"]}\n```'
        )
        self.assertEqual(a2["action"], "answer")
        self.assertEqual(a2["citations"], ["c1"])

        with self.assertRaises(ValueError):
            parse_controller_json('{"action": "search", "query": "  "}')

    def test_resolve_provider_requires_real_credentials(self) -> None:
        clean_env = {
            k: ""
            for k in (
                "LLM_PROVIDER",
                "ANTHROPIC_API_KEY",
                "GEMINI_API_KEY",
                "OPENAI_API_KEY",
                "OPENROUTER_API_KEY",
                "OLLAMA_BASE_URL",
            )
        }
        with patch.dict(os.environ, clean_env, clear=False), patch("src.llm_controller.load_dotenv"):
            with self.assertRaises(RuntimeError):
                resolve_provider_config()

    def test_llm_controller_search_then_answer_and_abstain(self) -> None:
        turns = iter(
            [
                {"action": "search", "query": "tăng trưởng GDP 2023"},
                {"action": "answer", "answer": "Tăng trưởng đạt 4,7% [wb_B_p11_c02].", "citations": ["wb_B_p11_c02"]},
                {"action": "search", "query": "dự báo GDP 2027"},
                {"action": "answer", "answer": "Không đủ bằng chứng để trả lời.", "citations": []},
            ]
        )

        def handler(request: httpx.Request) -> httpx.Response:
            payload = {
                "choices": [{"message": {"content": json.dumps(next(turns), ensure_ascii=False)}}],
                "usage": {"prompt_tokens": 100, "completion_tokens": 20, "total_tokens": 120},
            }
            return httpx.Response(200, json=payload)

        client = httpx.Client(transport=httpx.MockTransport(handler))
        cfg = ProviderConfig(provider="openai", model="gpt-4o-mini", api_key="test", base_url="https://mock.local/v1")
        ctrl = LLMController(config=cfg, http_client=client)
        try:
            cases = [
                {"id": "q01", "split": "dev", "question": "GDP 2023?", "answerable": True},
                {"id": "u01", "split": "dev", "question": "GDP 2027?", "answerable": False},
            ]
            traces = run_cases(cases, ctrl, _FakeRetriever([CHUNK]), max_searches=3, top_k=3, budget=2400)
            self.assertEqual(traces[0]["status"], "answered")
            self.assertEqual(traces[0]["citations"], ["wb_B_p11_c02"])
            self.assertEqual(traces[0]["total_tokens"], 240)
            self.assertEqual(traces[1]["status"], "abstain")
            self.assertEqual(traces[1]["citations"], [])
        finally:
            ctrl.close()

    def test_run_cases_records_connection_error_explicitly(self) -> None:
        class BrokenController:
            def decide(self, question, history):
                raise ConnectionError("API unreachable")

        traces = run_cases(
            [{"id": "q01", "split": "dev", "question": "GDP?", "answerable": True}],
            BrokenController(),
            _FakeRetriever([CHUNK]),
        )
        self.assertEqual(traces[0]["status"], "error")
        self.assertIn("ConnectionError", traces[0]["error"])


if __name__ == "__main__":
    unittest.main()
