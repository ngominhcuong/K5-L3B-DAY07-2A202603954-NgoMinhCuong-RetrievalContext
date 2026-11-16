"""Run Milestone 3 retrieval & context experiments on the dev split (0 LLM calls)."""
from __future__ import annotations

import argparse
import json
import re
import time
import unicodedata
from pathlib import Path
from typing import Any, Callable

from src.day6_connector import Day6QdrantRetriever
from src.retrievers import (
    BM25Retriever,
    HybridRRFRetriever,
    RerankHybridRetriever,
    pack_context_standard,
    pack_context_with_neighbors,
)

REPO_DIR = Path(__file__).resolve().parents[1]


def norm_ws(text: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", text)).strip()


def is_chunk_hit(chunk: dict[str, Any], gold: list[dict[str, Any]]) -> bool:
    c_norm = norm_ws(chunk["text"])
    return any(
        chunk["source_id"] == g["source_id"]
        and int(chunk["page"]) == int(g["page"])
        and norm_ws(g["evidence"]) in c_norm
        for g in gold
    )


def is_context_hit(context_chunks: list[dict[str, Any]], gold: list[dict[str, Any]]) -> bool:
    if any(is_chunk_hit(c, gold) for c in context_chunks):
        return True
    # Check concatenated chunks from the same (source_id, page) for cross-paragraph evidence.
    for g in gold:
        same_page_texts = [
            c["text"]
            for c in sorted(context_chunks, key=lambda x: x["id"])
            if c["source_id"] == g["source_id"] and int(c["page"]) == int(g["page"])
        ]
        if same_page_texts and norm_ws(g["evidence"]) in norm_ws(" ".join(same_page_texts)):
            return True
    return False


def evaluate_config(
    name: str,
    description: str,
    retriever: Any,
    questions: list[dict[str, Any]],
    all_chunks: list[dict[str, Any]],
    *,
    top_k: int = 3,
    budget: int = 2400,
    use_neighbors: bool = False,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    chunk_by_id = {c["id"]: c for c in all_chunks}
    traces: list[dict[str, Any]] = []
    hit1_count = 0
    hit3_count = 0
    ctx_count = 0
    total_ms = 0.0

    for q in questions:
        t0 = time.perf_counter()
        results = retriever.search(q["question"], filters=q.get("filter"), top_k=top_k)
        if use_neighbors:
            context, ctx_ids = pack_context_with_neighbors(results, all_chunks, budget=budget)
        else:
            context, ctx_ids = pack_context_standard(results, budget=budget)
        elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
        total_ms += elapsed_ms

        top1_hit = bool(results) and is_chunk_hit(results[0], q["gold"])
        top3_hit = any(is_chunk_hit(c, q["gold"]) for c in results[:3])
        ctx_chunks = [chunk_by_id[cid] for cid in ctx_ids if cid in chunk_by_id]
        ctx_hit = is_context_hit(ctx_chunks, q["gold"])

        hit1_count += int(top1_hit)
        hit3_count += int(top3_hit)
        ctx_count += int(ctx_hit)

        traces.append(
            {
                "query_id": q["id"],
                "split": q["split"],
                "question": q["question"],
                "filter": q.get("filter"),
                "hit1": top1_hit,
                "hit3": top3_hit,
                "context_hit": ctx_hit,
                "top_ids": [r["id"] for r in results],
                "top_pages": [r["page"] for r in results],
                "context_ids": ctx_ids,
                "context_chars": len(context),
                "elapsed_ms": elapsed_ms,
            }
        )

    n = len(questions)
    summary = {
        "config": name,
        "description": description,
        "split": questions[0]["split"] if questions else "dev",
        "n": n,
        "top_k": top_k,
        "budget_chars": budget,
        "hit1_n": hit1_count,
        "hit1_ratio": f"{hit1_count}/{n}",
        "hit1_pct": round(100.0 * hit1_count / n, 2) if n else 0.0,
        "hit3_n": hit3_count,
        "hit3_ratio": f"{hit3_count}/{n}",
        "hit3_pct": round(100.0 * hit3_count / n, 2) if n else 0.0,
        "context_n": ctx_count,
        "context_ratio": f"{ctx_count}/{n}",
        "context_pct": round(100.0 * ctx_count / n, 2) if n else 0.0,
        "total_elapsed_ms": round(total_ms, 2),
        "api_cost_usd": 0.0,
        "missed_hit1": [t["query_id"] for t in traces if not t["hit1"]],
        "missed_hit3": [t["query_id"] for t in traces if not t["hit3"]],
        "missed_context": [t["query_id"] for t in traces if not t["context_hit"]],
    }
    return summary, traces


def build_markdown_reports(summaries: list[dict[str, Any]], all_traces: dict[str, list[dict[str, Any]]]) -> tuple[str, str]:
    table_lines = [
        "# Bảng so sánh Retrieval & Context trên Dev (Mốc 3)",
        "",
        "| Cấu hình | Phương pháp & tham số | Hit@1 | Evidence Hit@3 | Context Evidence Rate | Thời gian (ms) | Chi phí |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for s in summaries:
        table_lines.append(
            f"| `{s['config']}` | {s['description']} | "
            f"{s['hit1_ratio']} ({s['hit1_pct']}%) | "
            f"{s['hit3_ratio']} ({s['hit3_pct']}%) | "
            f"{s['context_ratio']} ({s['context_pct']}%) | "
            f"{s['total_elapsed_ms']} | ${s['api_cost_usd']:.2f} |"
        )

    err_lines = ["# Phân tích lỗi trên Dev (Mốc 3)", ""]
    for s in summaries:
        cfg = s["config"]
        err_lines.append(f"## `{cfg}` ({s['description']})")
        err_lines.append(f"- Trượt Hit@1: {s['missed_hit1'] or 'Không có'}")
        err_lines.append(f"- Trượt Evidence Hit@3: {s['missed_hit3'] or 'Không có'}")
        err_lines.append(f"- Trượt Context Evidence: {s['missed_context'] or 'Không có'}")
        for t in all_traces[cfg]:
            if not t["hit1"] or not t["context_hit"]:
                err_lines.append(
                    f"  - `{t['query_id']}`: hit1={t['hit1']}, hit3={t['hit3']}, ctx={t['context_hit']} | "
                    f"top_ids={t['top_ids']}, top_pages={t['top_pages']}"
                )
        err_lines.append("")
    return "\n".join(table_lines) + "\n", "\n".join(err_lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Milestone 3 retrieval comparison on dev.")
    parser.add_argument("--chunks", type=Path, default=REPO_DIR / "data" / "day7_chunks.json")
    parser.add_argument("--questions", type=Path, default=REPO_DIR / "data" / "day7_questions_answerable.json")
    parser.add_argument("--split", choices=("dev", "test"), default="dev")
    parser.add_argument("--output", type=Path, default=REPO_DIR / "results" / "m3-dev-comparison")
    args = parser.parse_args()

    all_chunks = json.loads(args.chunks.read_text(encoding="utf-8"))
    all_questions = json.loads(args.questions.read_text(encoding="utf-8"))
    questions = [q for q in all_questions if q["split"] == args.split]

    dense = Day6QdrantRetriever()
    try:
        bm25 = BM25Retriever(all_chunks)
        hybrid_rrf = HybridRRFRetriever(dense, bm25, rrf_k=60, candidate_k=10)
        rerank_hybrid = RerankHybridRetriever(hybrid_rrf, candidate_k=10, w_dense=0.50, w_lexical=0.30, w_overlap=0.20)

        configs: list[tuple[str, str, Any, int, int, bool]] = [
            ("1_dense_baseline", "Dense Qdrant Day 6 (`top_k=3`, `budget=2400`)", dense, 3, 2400, False),
            ("2_bm25_lexical", "Lexical BM25 (`k1=1.5, b=0.75`, `top_k=3`, `budget=2400`)", bm25, 3, 2400, False),
            ("3_hybrid_rrf", "Hybrid Dense + BM25 via RRF (`k=60, cand=10`, `top_k=3`, `budget=2400`)", hybrid_rrf, 3, 2400, False),
            ("4_hybrid_rerank", "Cải thiện 1: Hybrid RRF + Normalized Rerank (`cand=10`, `top_k=3`, `budget=2400`)", rerank_hybrid, 3, 2400, False),
            ("5_hybrid_rerank_neighbor", "Cải thiện 2: Hybrid Rerank + Neighbor Context (`top_k=3`, `budget=3000`)", rerank_hybrid, 3, 3000, True),
        ]

        summaries: list[dict[str, Any]] = []
        all_traces: dict[str, list[dict[str, Any]]] = {}
        args.output.mkdir(parents=True, exist_ok=True)

        for name, desc, retriever, top_k, budget, use_neighbors in configs:
            summary, traces = evaluate_config(
                name,
                desc,
                retriever,
                questions,
                all_chunks,
                top_k=top_k,
                budget=budget,
                use_neighbors=use_neighbors,
            )
            summaries.append(summary)
            all_traces[name] = traces
            (args.output / f"traces_{name}.json").write_text(
                json.dumps(traces, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
    finally:
        dense.close()

    table_md, err_md = build_markdown_reports(summaries, all_traces)
    (args.output / "summary.json").write_text(
        json.dumps(summaries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (args.output / "comparison_table.md").write_text(table_md, encoding="utf-8")
    (args.output / "dev_error_analysis.md").write_text(err_md, encoding="utf-8")

    print(table_md)


if __name__ == "__main__":
    main()
