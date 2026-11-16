# Báo cáo Day 7 — Agentic RAG

- **Họ và tên:** Ngô Minh Cương
- **MSSV:** `2A202603954`
- **Lớp:** `L3B`

## Dữ liệu và benchmark

- **Nguồn, quyền sử dụng, số trang và số chunk:**
  - Tài liệu World Bank Group — _Báo cáo Điểm lại Tháng 8/2023: Để đầu tư công thúc đẩy tăng trưởng_ (`wb-taking-stock-2023-08`, tiếng Việt, giấy phép `CC BY 3.0 IGO`).
  - Tổng 58 trang PDF vật lý, **41 trang nội dung hợp lệ**, tách theo đoạn `by_paragraph(max_size=750)` (Strategy B từ Day 6) thành **237 chunks** (lưu tại [data/day7_chunks.json](../../data/day7_chunks.json)).
- **Vector store, embedding model, phiên bản và số chiều:**
  - Vector store: **Qdrant** local persistent (`K5-L3B-DAY06-NgoMinhCuong-2A202603954-DataIngestion/starter/qdrant_storage`, collection `day6_b`, metric `COSINE`, kết nối qua [src/day6_connector.py](../../src/day6_connector.py)).
  - Embedding model: `intfloat/multilingual-e5-base` (**768 chiều**, chuẩn hóa L2, prefix `"passage: "` khi index và `"query: "` khi truy vấn).
- **Agent model, cách chạy và phân chia dev/test:**
  - Agent model: `anthropic/claude-haiku-4-5-20251001` (qua [src/llm_controller.py](../../src/llm_controller.py), `temperature=0.0`) ghép với `run_agent` trong [starter/agentic.py](../../starter/agentic.py) và runner [src/run_agent_eval.py](../../src/run_agent_eval.py). *(Trước đó có thử nghiệm một phần `dev` với `gemini/gemini-3.5-flash` nhưng chạm giới hạn 20 RPD nên đã chạy toàn bộ `dev` và `test` đồng nhất trên `claude-haiku-4-5-20251001`).*
  - Benchmark **24 câu** ([data/day7_agent_cases.json](../../data/day7_agent_cases.json), phần retrieval tại [data/day7_questions_answerable.json](../../data/day7_questions_answerable.json), câu thiếu bằng chứng tại [data/unanswerable_questions.json](../../data/unanswerable_questions.json)):
    - **Dev (17 câu):** 15 câu có đáp án (`q01`–`q15`) + 2 câu thiếu bằng chứng (`u01`, `u02`).
    - **Test (7 câu):** 5 câu có đáp án (`q16`–`q20`) + 2 câu thiếu bằng chứng (`u03`, `u04`).
- **Cách xác định câu có/thiếu evidence và tiêu chí chấm:**
  - Câu có đáp án được đối chiếu trích dẫn nguyên văn (`gold`) trên PDF; câu thiếu bằng chứng (`u01`–`u04`) sát chủ đề kinh tế VN nhưng không có số liệu trong tài liệu, có `absence_reason` và không đưa vào mẫu số retrieval metrics.
  - Chấm thủ công theo [BENCHMARK.md](../../BENCHMARK.md): Context `0/1/2`, Grounded answer `0/1/2`, Citation hợp lệ (có trong context **và** thực sự hỗ trợ câu trả lời), Abstention đúng / từ chối nhầm.

## Retrieval và thử nghiệm

| Cấu hình | Phương pháp, top-k, filter, rerank, context budget | Giả thuyết / thay đổi | Split | Hit@1 | Evidence Hit@3 | Context Evidence Rate | Thời gian / chi phí |
|---|---|---|---|---|---|---|---|
| `1_dense_baseline` | Dense Qdrant Day 6 (`top_k=3`, filter theo câu, `budget=2400`) | Baseline | dev | 12/15 (80.0%) | 14/15 (93.33%) | 15/15 (100.0%) | 1343.95 ms / \$0.00 |
| `2_bm25_lexical` | Lexical BM25Okapi (`k1=1.5, b=0.75`, `top_k=3`, `budget=2400`) | Bắt từ khóa/số liệu chính xác | dev | 11/15 (73.33%) | 14/15 (93.33%) | 14/15 (93.33%) | 38.82 ms / \$0.00 |
| `3_hybrid_rrf` | Hybrid Dense + BM25 via RRF (`k=60, cand=10`, `top_k=3`, `budget=2400`) | Kết hợp ngữ nghĩa + từ khóa bằng RRF | dev | **13/15 (86.67%)** | **14/15 (93.33%)** | **15/15 (100.0%)** | 880.33 ms / \$0.00 |
| `4_hybrid_rerank` | Cải thiện 1: Hybrid RRF + Normalized Rerank (`0.5*D + 0.3*L + 0.2*O`, `budget=2400`) | Ưu tiên chunk khớp nhiều từ khóa query | dev | 11/15 (73.33%) | 14/15 (93.33%) | 14/15 (93.33%) | 776.46 ms / \$0.00 |
| `5_hybrid_rerank_neighbor` | Cải thiện 2: Hybrid Rerank + Neighbor Context (`budget=3000`) | Kéo đoạn lân cận để gom evidence vắt đoạn (`q04`) | dev | 11/15 (73.33%) | 14/15 (93.33%) | 14/15 (93.33%) | 872.62 ms / \$0.00 |
| `3_hybrid_rrf` *(Đã chốt)* | Hybrid Dense + BM25 via RRF (`k=60, cand=10`, `top_k=3`, `budget=2400`) | Đánh giá test sau khi chốt | test | 5/5 (100.0%) | 5/5 (100.0%) | 5/5 (100.0%) | 452.42 ms / \$0.00 |
| `1_dense_baseline` | Dense Qdrant Day 6 (`top_k=3`, `budget=2400`) | Baseline đối chứng trên test | test | 5/5 (100.0%) | 5/5 (100.0%) | 5/5 (100.0%) | 371.78 ms / \$0.00 |

### Phân tích lỗi trên `dev` & Lý do chọn cấu hình
- **Lỗi 1 (`q06` trên Dense baseline):** Dense đặt chunk giải thích `p32_c02` lên Rank 1 và đẩy `p32_c01` (chứa con số `16,9%` và lý do giãn hoãn thuế) xuống Rank 2 (`Hit@1=False`). Khi chuyển sang `3_hybrid_rrf`, BM25 khớp chính xác các từ khóa `"16,9%"`, `"thuế thu nhập doanh nghiệp"`, giúp đưa `p32_c01` lên Rank 1 (`Hit@1` tăng từ `12/15` lên `13/15`).
- **Lỗi 2 (`q04` & `q11` trên Cải thiện 1 & 2):**
  - Ở `4_hybrid_rerank`, việc cộng trọng số lexical/overlap (`0.30 + 0.20`) làm tụt hạng các câu diễn đạt lại (`q03`, `q08`) khiến `Hit@1` giảm còn `11/15`.
  - Ở `5_hybrid_rerank_neighbor`, mở rộng neighbor giúp `q04` vào context (`ctx=True`), nhưng ở `q11` các neighbor của Rank 1–2 (`p.17`) lại chiếm hết `budget=3000` khiến chunk gốc ở Rank 3 (`p.53`) bị đẩy khỏi context (`ctx=False`).
- **Lý do chốt `3_hybrid_rrf`:** Đạt `Hit@1` cao nhất (`13/15 = 86.67%`), `Hit@3 = 14/15 (93.33%)`, `Context Evidence Rate = 15/15 (100.0%)`, thời gian thực thi nhanh (`880.33 ms`) và không tốn thêm chi phí.

## Agent và đánh giá

- **Tool, số lượt gọi, điều kiện dừng, cách chọn context và xử lý lỗi:**
  - Tool retrieval duy nhất qua giao diện `Retriever.search(query, filters, top_k=3)`, `max_searches=3`, `budget=2400` ký tự, deduplication theo `chunk_id`.
  - Dừng khi model trả `action="answer"` (có `[chunk_id]` hợp lệ) hoặc đạt giới hạn `max_searches=3` (chuyển sang `abstain`). Lỗi kết nối/quota API được ghi riêng với `status="error"`, không thay bằng mock.

| Cấu hình / split | Tool use | Số lượt gọi | Grounded answer 0/1/2 và trung bình | Citation hợp lệ | Câu có citation | Abstention đúng | Từ chối nhầm |
|---|---|---|---|---|---|---|---|
| `1_dense_baseline` / test | 7/7 (100%) | 1 lượt (5 câu), 2 lượt (1 câu), 3 lượt (1 câu) | 0 / 0 / 5 (TB `2.00 / 2`) | 5/5 (100%) | 5/5 (100%) | 2/2 (100%) | 0/5 (0%) |
| `3_hybrid_rrf` / test | 7/7 (100%) | 1 lượt (5 câu), 2 lượt (1 câu), 3 lượt (1 câu) | 0 / 0 / 5 (TB `2.00 / 2`) | 5/5 (100%) | 5/5 (100%) | 2/2 (100%) | 0/5 (0%) |

### Ví dụ minh họa (ít nhất 1 câu có bằng chứng, 1 câu thiếu bằng chứng, 1 lỗi)
| Query ID | Loại câu | Tool call và kết quả | Câu trả lời và citation | Nhãn, lý do |
|---|---|---|---|---|
| `q16` (test, `hybrid_rrf`) | Có bằng chứng | `search("thu gọn quy mô chi tiêu số lượng CTMTQG 2011 2021")` → trả về `wb-taking-stock-2023-08_B_p50_c01` ở Rank 1 | Quy mô chi tiêu giảm từ 9,1% xuống 2,8%; số lượng từ 16 CTMTQG và 45 chương trình nhỏ xuống còn 3 CTMTQG và một vài chương trình cấp phát `[wb-taking-stock-2023-08_B_p50_c01]` | `answer_grade=2`, `context_grade=2`, `citation_support=[true]` — chunk p.50 hỗ trợ đầy đủ mọi số liệu. |
| `u03` (test, `hybrid_rrf`) | Thiếu bằng chứng | `search` 2 lượt về lãi suất điều hành NHNN cuối năm 2024 → các chunk p.13, p.26, p.30 không có số dự báo cuối 2024 | `"Không đủ bằng chứng để trả lời."` (`citations: []`) | `abstention_correct=true` — không suy đoán ngoài tài liệu. |
| `q11` (dev, `5_hybrid_rerank_neighbor`) | Lỗi context | Retrieval Rank 1–2 nằm ở phần Tổng quan (`p.17`), Rank 3 ở `p.53` | Mở rộng neighbor quanh `p.17` làm tràn `budget=3000`, đẩy `p53_c02` ra khỏi context cuối | `Context Evidence=False` — minh họa đánh đổi khi mở rộng neighbor không giới hạn số lượng theo rank. |

- **Đường dẫn trace, nhãn, lệnh chạy, thời gian và chi phí:**
  - Code retrieval & benchmark: [src/retrievers.py](../../src/retrievers.py), [src/run_m3_experiments.py](../../src/run_m3_experiments.py), [src/prepare_reviews.py](../../src/prepare_reviews.py), [starter/agent_metrics.py](../../starter/agent_metrics.py).
  - Kết quả Dev: [m2-dense-dev/traces.json](../../results/m2-dense-dev/traces.json), [m3-dev-comparison/comparison_table.md](../../results/m3-dev-comparison/comparison_table.md), [m3-dev-comparison/dev_error_analysis.md](../../results/m3-dev-comparison/dev_error_analysis.md).
  - Kết quả Test Retrieval: [m4-test-retrieval/comparison_table.md](../../results/m4-test-retrieval/comparison_table.md), [m4-test-retrieval/summary.json](../../results/m4-test-retrieval/summary.json).
  - Kết quả Test Baseline (`25,306 tokens`, `27,334.92 ms`, ước tính `~$0.03–$0.04` theo biểu phí Haiku 4.5 `$1/MTok input, $5/MTok output`): [traces.json](../../results/m4-test-baseline/traces.json) · [audit_sheet.md](../../results/m4-test-baseline/audit_sheet.md) · [reviews.json](../../results/m4-test-baseline/reviews.json) · [summary.json](../../results/m4-test-baseline/summary.json).
  - Kết quả Test Hybrid RRF (`25,933 tokens`, `25,899.26 ms`, ước tính `~$0.03–$0.04` theo biểu phí Haiku 4.5 `$1/MTok input, $5/MTok output`): [traces.json](../../results/m4-test-hybrid/traces.json) · [audit_sheet.md](../../results/m4-test-hybrid/audit_sheet.md) · [reviews.json](../../results/m4-test-hybrid/reviews.json) · [summary.json](../../results/m4-test-hybrid/summary.json).
  - Lệnh chạy tái lập (đầy đủ từ cài đặt môi trường Day 6/Day 7 → Mốc 1 → Mốc 4):
    - **0a. Tạo môi trường & cài thư viện Day 7** (gồm `qdrant-client`, `sentence-transformers`, `torch`, `python-dotenv`, `httpx` trong [requirements.txt](../../requirements.txt)): `python -m venv .venv` → kích hoạt `.venv` → `pip install -r requirements.txt`.
    - **0b. Chuẩn bị Qdrant Vector Store từ Day 6** (vì `qdrant_storage/` bị gitignore): đặt repo Day 6 (`K5-L3B-DAY06-NgoMinhCuong-2A202603954-DataIngestion`) cạnh thư mục Day 7, cài thêm gói của Day 6 (`pip install -r ../K5-L3B-DAY06-NgoMinhCuong-2A202603954-DataIngestion/starter/requirements.txt`), rồi chạy `python -m src.run` tại `../K5-L3B-DAY06-NgoMinhCuong-2A202603954-DataIngestion/starter` để tái tạo `qdrant_storage/` (41 trang, 237 chunks ở Strategy B). *(Không cần Docker/PostgreSQL vì Day 6 dùng Qdrant local persistent).*
    - **0c. Cấu hình `.env`:** sao chép [.env.example](../../.env.example) thành `.env`, giữ nguyên `DAY6_QDRANT_PATH` (hoặc trỏ tới đường dẫn `qdrant_storage` vừa tạo) và điền API key (`ANTHROPIC_API_KEY` với `LLM_PROVIDER=anthropic`, `LLM_MODEL=claude-haiku-4-5-20251001`, hoặc Gemini/OpenAI/OpenRouter/Ollama).
    - **1. Kiểm thử offline:** `python -m unittest discover -s tests -v`
    - **2. Mốc 1 (Benchmark & Export Day 6):** `python -m src.prepare_benchmark` → `python -m src.day6_connector --check --export data/day7_chunks.json`
    - **3. Mốc 2 (Agent trên dev):** `python -m src.run_agent_eval --split dev --output results/m2-dense-dev`
    - **4. Mốc 3 (So sánh 5 cấu hình retrieval trên dev):** `python -m src.run_m3_experiments --split dev --output results/m3-dev-comparison`
    - **5. Mốc 4 (Retrieval & Agent trên test):** `python -m src.run_m3_experiments --split test --output results/m4-test-retrieval` → `python -m src.run_agent_eval --split test --retriever dense --output results/m4-test-baseline` → `python -m src.run_agent_eval --split test --retriever hybrid_rrf --output results/m4-test-hybrid`
    - **6. Mốc 4 (Chấm tay & tổng hợp):** `python -m src.prepare_reviews --traces results/m4-test-baseline/traces.json --split test` & `python -m src.prepare_reviews --traces results/m4-test-hybrid/traces.json --split test` → `python starter/agent_metrics.py --cases data/day7_agent_cases.json --traces results/m4-test-baseline/traces.json --reviews results/m4-test-baseline/reviews.json --split test --output results/m4-test-baseline/summary.json` & `python starter/agent_metrics.py --cases data/day7_agent_cases.json --traces results/m4-test-hybrid/traces.json --reviews results/m4-test-hybrid/reviews.json --split test --output results/m4-test-hybrid/summary.json`
- **Kết quả trước/sau, ví dụ lỗi, đánh đổi và giới hạn:**
  - Trên `dev`, chuyển từ `1_dense_baseline` sang `3_hybrid_rrf` nâng `Hit@1` từ `12/15 (80.0%)` lên `13/15 (86.67%)` và giảm thời gian retrieval từ `1343.95 ms` xuống `880.33 ms`. Trên `test` (`n=7`), cả hai cấu hình đều đạt `5/5` retrieval và `2.00/2` grounded answer, `2/2` abstention đúng, `0` lỗi hệ thống (`~25k` tokens, `~26s` mỗi lượt chạy 7 câu).
  - **Giới hạn:** Tập `test` chỉ có 5 câu có đáp án + 2 câu thiếu bằng chứng nên chưa tạo phân hóa lớn giữa Dense và Hybrid như trên `dev`; ngoài ra báo cáo World Bank có một số bằng chứng vắt qua 2 đoạn (`q04`) đòi hỏi đánh giá theo hợp nhất context cùng trang thay vì khớp chuỗi trong 1 chunk đơn lẻ.
