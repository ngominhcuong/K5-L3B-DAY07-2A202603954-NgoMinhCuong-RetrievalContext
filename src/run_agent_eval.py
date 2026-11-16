"""Run the real Agentic RAG pipeline (LLMController + Day6QdrantRetriever) and save full traces."""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

REPO_DIR = Path(__file__).resolve().parents[1]
STARTER_DIR = REPO_DIR / "starter"
if str(STARTER_DIR) not in sys.path:
    sys.path.insert(0, str(STARTER_DIR))

from agentic import run_agent  # noqa: E402
from src.day6_connector import Day6QdrantRetriever  # noqa: E402
from src.llm_controller import LLMController, resolve_provider_config  # noqa: E402
from src.retrievers import BM25Retriever, HybridRRFRetriever  # noqa: E402


def build_retriever(mode: str, chunks_path: Path) -> tuple[Any, Any]:
    """Create the requested real retriever ('dense' or 'hybrid_rrf') and return (retriever, closer)."""
    dense = Day6QdrantRetriever()
    if mode == "dense":
        return dense, dense
    if mode == "hybrid_rrf":
        chunks = json.loads(chunks_path.read_text(encoding="utf-8"))
        bm25 = BM25Retriever(chunks)
        return HybridRRFRetriever(dense, bm25, rrf_k=60, candidate_k=10), dense
    dense.close()
    raise ValueError(f"Unsupported retriever mode: {mode!r}")


def run_cases(
    cases: list[dict[str, Any]],
    controller: Any,
    retriever: Any,
    *,
    max_searches: int = 3,
    top_k: int = 3,
    budget: int = 2400,
) -> list[dict[str, Any]]:
    """Run agent on each case, recording traces and explicit errors without mock fallback."""
    traces: list[dict[str, Any]] = []
    for case in cases:
        qid = case["id"]
        if hasattr(controller, "reset_logs"):
            controller.reset_logs()
        t0 = time.perf_counter()
        try:
            res = run_agent(
                case["question"],
                controller,
                retriever,
                filters=case.get("filter"),
                max_searches=max_searches,
                top_k=top_k,
                budget=budget,
            )
            elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
            llm_logs = list(getattr(controller, "call_logs", []))
            total_tokens = sum(log.get("usage", {}).get("total_tokens", 0) for log in llm_logs)
            search_events = [e for e in res.get("events", []) if e.get("event") == "search"]
            final_context = search_events[-1].get("context", "") if search_events else ""
            final_context_ids = search_events[-1].get("context_ids", []) if search_events else []

            traces.append(
                {
                    "query_id": qid,
                    "split": case["split"],
                    "question": case["question"],
                    "answerable": case["answerable"],
                    "filter": case.get("filter"),
                    "status": res["status"],
                    "answer": res["answer"],
                    "citations": res["citations"],
                    "search_calls": len(search_events),
                    "final_context_ids": final_context_ids,
                    "final_context": final_context,
                    "events": res["events"],
                    "llm_calls": llm_logs,
                    "total_tokens": total_tokens,
                    "elapsed_ms": elapsed_ms,
                }
            )
        except Exception as exc:
            elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
            traces.append(
                {
                    "query_id": qid,
                    "split": case["split"],
                    "question": case["question"],
                    "answerable": case["answerable"],
                    "filter": case.get("filter"),
                    "status": "error",
                    "answer": "",
                    "citations": [],
                    "search_calls": 0,
                    "final_context_ids": [],
                    "final_context": "",
                    "events": [],
                    "error": f"{type(exc).__name__}: {exc}",
                    "elapsed_ms": elapsed_ms,
                }
            )
    return traces


def summarize_traces(traces: list[dict[str, Any]], meta: dict[str, Any]) -> dict[str, Any]:
    return {
        **meta,
        "total_cases": len(traces),
        "answered": sum(1 for t in traces if t["status"] == "answered"),
        "abstain": sum(1 for t in traces if t["status"] == "abstain"),
        "error": sum(1 for t in traces if t["status"] == "error"),
        "total_tokens": sum(t.get("total_tokens", 0) for t in traces),
        "total_elapsed_ms": round(sum(t.get("elapsed_ms", 0.0) for t in traces), 2),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Day 7 Agentic RAG (real LLM + real Day 6 Qdrant).")
    parser.add_argument("--cases", type=Path, default=REPO_DIR / "data" / "day7_agent_cases.json")
    parser.add_argument("--split", choices=("dev", "test"), default="dev")
    parser.add_argument("--case-ids", type=str, default=None, help="Comma-separated case IDs, e.g. q01,u01")
    parser.add_argument("--limit", type=int, default=None, help="Optional max number of cases to run")
    parser.add_argument("--provider", type=str, default=None, help="gemini | openrouter | openai | ollama")
    parser.add_argument("--model", type=str, default=None, help="Override LLM_MODEL from .env")
    parser.add_argument("--retriever", choices=("dense", "hybrid_rrf"), default="dense")
    parser.add_argument("--chunks", type=Path, default=REPO_DIR / "data" / "day7_chunks.json")
    parser.add_argument("--max-searches", type=int, default=3)
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--budget", type=int, default=2400)
    parser.add_argument("--resume", action="store_true", help="Skip cases already succeeded in output/traces.json")
    parser.add_argument("--output", type=Path, default=REPO_DIR / "results" / "m2-dense-dev")
    args = parser.parse_args()

    all_cases = json.loads(args.cases.read_text(encoding="utf-8"))
    selected = [c for c in all_cases if c["split"] == args.split]
    if args.case_ids:
        wanted = {x.strip() for x in args.case_ids.split(",") if x.strip()}
        selected = [c for c in selected if c["id"] in wanted]
    if args.limit is not None:
        selected = selected[: args.limit]
    if not selected:
        raise ValueError("Không có câu hỏi nào khớp điều kiện lọc.")

    existing_ok: dict[str, dict[str, Any]] = {}
    traces_path = args.output / "traces.json"
    if args.resume and traces_path.exists():
        for row in json.loads(traces_path.read_text(encoding="utf-8")):
            if row.get("status") in ("answered", "abstain"):
                existing_ok[row["query_id"]] = row

    to_run = [c for c in selected if c["id"] not in existing_ok]
    config = resolve_provider_config(provider=args.provider, model=args.model)
    if to_run:
        controller = LLMController(config=config)
        retriever, dense_closer = build_retriever(args.retriever, args.chunks)
        try:
            new_traces = run_cases(
                to_run,
                controller,
                retriever,
                max_searches=args.max_searches,
                top_k=args.top_k,
                budget=args.budget,
            )
            strategy_name = dense_closer.strategy
        finally:
            controller.close()
            dense_closer.close()
    else:
        new_traces = []
        strategy_name = "B"

    by_id = {**existing_ok, **{t["query_id"]: t for t in new_traces}}
    traces = [by_id[c["id"]] for c in selected if c["id"] in by_id]

    args.output.mkdir(parents=True, exist_ok=True)
    meta = summarize_traces(
        traces,
        {
            "split": args.split,
            "provider": config.provider,
            "model": config.model,
            "retriever": args.retriever,
            "strategy": strategy_name,
            "max_searches": args.max_searches,
            "top_k": args.top_k,
            "budget_chars": args.budget,
        },
    )
    (args.output / "traces.json").write_text(
        json.dumps(traces, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (args.output / "run_meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(
        f"[OK] Ran {meta['total_cases']} {args.split} cases with {config.provider}/{config.model}: "
        f"answered={meta['answered']}, abstain={meta['abstain']}, error={meta['error']}, "
        f"tokens={meta['total_tokens']}, time={meta['total_elapsed_ms']}ms"
    )
    for t in traces:
        err = f" | ERROR: {t['error']}" if t.get("error") else ""
        print(
            f"  - {t['query_id']} ({'ans' if t['answerable'] else 'unans'}): "
            f"status={t['status']}, searches={t['search_calls']}, citations={t['citations']}{err}"
        )


if __name__ == "__main__":
    main()
