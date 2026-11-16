"""Generate human-audit sheet (audit_sheet.md) and reviews_template.json for starter/agent_metrics.py."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

REPO_DIR = Path(__file__).resolve().parents[1]


def build_review_artifacts(
    cases: list[dict[str, Any]],
    traces: list[dict[str, Any]],
    answerable_questions: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], str]:
    """Create starter-compatible review template and readable Markdown audit sheet."""
    trace_by_id = {t["query_id"]: t for t in traces}
    q_by_id = {q["id"]: q for q in answerable_questions}

    reviews: list[dict[str, Any]] = []
    lines: list[str] = [
        "# Bảng đối chiếu chấm tay Agent (Audit Sheet)",
        "",
        "Đọc câu trả lời, citation và `final_context` bên dưới để xác nhận/sửa `reviews_template.json` thành `reviews.json` trước khi chạy `starter/agent_metrics.py`.",
        "- `context_grade`: `0` = không có evidence; `1` = thiếu điều kiện/nguồn; `2` = đủ evidence & nguồn.",
        "- `answer_grade` (câu có đáp án): `0` = sai/thiếu evidence/từ chối nhầm; `1` = đúng một phần; `2` = đúng & đủ.",
        "",
    ]

    for case in cases:
        cid = case["id"]
        trace = trace_by_id.get(cid)
        if not trace:
            continue
        status = trace.get("status")
        citations = trace.get("citations", [])
        lines.append(f"## `{cid}` ({case['split']} · {'có đáp án' if case['answerable'] else 'thiếu bằng chứng'})")
        lines.append(f"- **Câu hỏi:** {case['question']}")
        if case["answerable"] and cid in q_by_id:
            lines.append(f"- **Đáp án chuẩn:** {q_by_id[cid]['expected_answer']}")
            lines.append(f"- **Gold:** `{json.dumps(q_by_id[cid]['gold'], ensure_ascii=False)}`")
        elif not case["answerable"]:
            lines.append(f"- **Lý do thiếu bằng chứng:** {case.get('absence_reason', '')}")

        lines.append(f"- **Agent status:** `{status}` | **Search calls:** {trace.get('search_calls', 0)}")
        lines.append(f"- **Agent answer:** {trace.get('answer', '')}")
        lines.append(f"- **Agent citations:** `{citations}`")
        if trace.get("error"):
            lines.append(f"- **Error:** `{trace['error']}`")
        lines.append("")
        lines.append("<details><summary>Final context gửi cho model</summary>\n")
        lines.append("```text")
        lines.append(trace.get("final_context", "") or "(empty)")
        lines.append("```")
        lines.append("</details>\n")

        if status == "error":
            continue

        row: dict[str, Any] = {
            "query_id": cid,
            "citation_support": [True for _ in citations],
            "context_grade": 2 if trace.get("final_context") else 0,
            "human_verified": False,
        }
        if case["answerable"]:
            row["answer_grade"] = 0 if status == "abstain" else 2
        else:
            row["abstention_correct"] = status == "abstain"
            row["citation_support"] = [False for _ in citations]
        reviews.append(row)

    return reviews, "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare manual audit files for Milestone 4.")
    parser.add_argument("--cases", type=Path, default=REPO_DIR / "data" / "day7_agent_cases.json")
    parser.add_argument("--questions", type=Path, default=REPO_DIR / "data" / "day7_questions_answerable.json")
    parser.add_argument("--traces", type=Path, required=True)
    parser.add_argument("--split", choices=("dev", "test"), default="test")
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()

    out_dir = args.output_dir or args.traces.parent
    cases = [c for c in json.loads(args.cases.read_text(encoding="utf-8")) if c["split"] == args.split]
    traces = json.loads(args.traces.read_text(encoding="utf-8"))
    questions = json.loads(args.questions.read_text(encoding="utf-8"))

    reviews, audit_md = build_review_artifacts(cases, traces, questions)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "reviews_template.json").write_text(
        json.dumps(reviews, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "audit_sheet.md").write_text(audit_md, encoding="utf-8")
    print(f"[OK] Wrote {len(reviews)} review entries and audit_sheet.md in {out_dir}")


if __name__ == "__main__":
    main()
