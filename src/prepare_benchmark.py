"""Prepare Day 7 benchmark files from Day 6 questions and Day 7 unanswerable cases."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

REPO_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DAY6_QUESTIONS = (
    REPO_DIR.parent
    / "K5-L3B-DAY06-NgoMinhCuong-2A202603954-DataIngestion"
    / "benchmark"
    / "questions.json"
)
DEFAULT_UNANSWERABLE = REPO_DIR / "data" / "unanswerable_questions.json"
DEFAULT_OUT_DIR = REPO_DIR / "data"


def convert_day6_question(q: dict[str, Any]) -> dict[str, Any]:
    """Convert a Day 6 question (including alt_evidences and filter) to Day 7 schema."""
    gold: list[dict[str, Any]] = [
        {
            "source_id": q["gold_source_id"],
            "page": int(q["gold_page"]),
            "evidence": q["evidence_quote"],
        }
    ]
    for alt in q.get("alt_evidences", []):
        gold.append(
            {
                "source_id": alt.get("source_id", q["gold_source_id"]),
                "page": int(alt["page"]),
                "evidence": alt["evidence_quote"],
            }
        )

    out: dict[str, Any] = {
        "id": q["id"],
        "split": q["split"],
        "question": q["question"],
        "gold": gold,
        "expected_answer": q["expected_answer"],
    }
    if q.get("type"):
        out["type"] = q["type"]
    if q.get("filter"):
        out["filter"] = q["filter"]
    return out


def to_agent_case(item: dict[str, Any], *, answerable: bool) -> dict[str, Any]:
    """Convert either an answerable question or unanswerable item to agent_cases schema."""
    case: dict[str, Any] = {
        "id": item["id"],
        "split": item["split"],
        "question": item["question"],
        "answerable": answerable,
        "expected_behavior": "search_and_answer" if answerable else "search_and_abstain",
    }
    if not answerable:
        case["absence_reason"] = item["absence_reason"]
    if item.get("filter"):
        case["filter"] = item["filter"]
    return case


def validate_benchmark_counts(agent_cases: list[dict[str, Any]]) -> None:
    """Enforce Day 7 minimum benchmark counts: dev >= 15+2, test >= 5+2."""
    dev_ans = [c for c in agent_cases if c["split"] == "dev" and c["answerable"]]
    dev_unans = [c for c in agent_cases if c["split"] == "dev" and not c["answerable"]]
    test_ans = [c for c in agent_cases if c["split"] == "test" and c["answerable"]]
    test_unans = [c for c in agent_cases if c["split"] == "test" and not c["answerable"]]

    if len(dev_ans) < 15 or len(dev_unans) < 2:
        raise ValueError(f"Dev split requires >=15 answerable & >=2 unanswerable, got {len(dev_ans)}+{len(dev_unans)}")
    if len(test_ans) < 5 or len(test_unans) < 2:
        raise ValueError(f"Test split requires >=5 answerable & >=2 unanswerable, got {len(test_ans)}+{len(test_unans)}")


def build_benchmark(
    day6_questions_path: Path = DEFAULT_DAY6_QUESTIONS,
    unanswerable_path: Path = DEFAULT_UNANSWERABLE,
    out_dir: Path = DEFAULT_OUT_DIR,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    raw_day6 = json.loads(day6_questions_path.read_text(encoding="utf-8"))
    raw_list = raw_day6["questions"] if isinstance(raw_day6, dict) else raw_day6
    unanswerables = json.loads(unanswerable_path.read_text(encoding="utf-8"))

    answerable_questions = [convert_day6_question(q) for q in raw_list]
    agent_cases = [to_agent_case(q, answerable=True) for q in answerable_questions] + [
        to_agent_case(u, answerable=False) for u in unanswerables
    ]
    validate_benchmark_counts(agent_cases)

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "day7_questions_answerable.json").write_text(
        json.dumps(answerable_questions, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (out_dir / "day7_agent_cases.json").write_text(
        json.dumps(agent_cases, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return answerable_questions, agent_cases


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Day 7 benchmark JSON files from Day 6 + unanswerable cases.")
    parser.add_argument("--day6-questions", type=Path, default=DEFAULT_DAY6_QUESTIONS)
    parser.add_argument("--unanswerable", type=Path, default=DEFAULT_UNANSWERABLE)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    args = parser.parse_args()

    ans, cases = build_benchmark(args.day6_questions, args.unanswerable, args.out_dir)
    print(f"[OK] Generated {len(ans)} answerable questions and {len(cases)} total agent cases in {args.out_dir}")


if __name__ == "__main__":
    main()
