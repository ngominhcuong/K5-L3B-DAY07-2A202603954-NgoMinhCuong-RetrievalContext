# Bảng so sánh Retrieval & Context trên Dev (Mốc 3)

| Cấu hình | Phương pháp & tham số | Hit@1 | Evidence Hit@3 | Context Evidence Rate | Thời gian (ms) | Chi phí |
|---|---|---:|---:|---:|---:|---:|
| `1_dense_baseline` | Dense Qdrant Day 6 (`top_k=3`, `budget=2400`) | 5/5 (100.0%) | 5/5 (100.0%) | 5/5 (100.0%) | 371.78 | $0.00 |
| `2_bm25_lexical` | Lexical BM25 (`k1=1.5, b=0.75`, `top_k=3`, `budget=2400`) | 5/5 (100.0%) | 5/5 (100.0%) | 5/5 (100.0%) | 10.33 | $0.00 |
| `3_hybrid_rrf` | Hybrid Dense + BM25 via RRF (`k=60, cand=10`, `top_k=3`, `budget=2400`) | 5/5 (100.0%) | 5/5 (100.0%) | 5/5 (100.0%) | 452.42 | $0.00 |
| `4_hybrid_rerank` | Cải thiện 1: Hybrid RRF + Normalized Rerank (`cand=10`, `top_k=3`, `budget=2400`) | 5/5 (100.0%) | 5/5 (100.0%) | 5/5 (100.0%) | 374.53 | $0.00 |
| `5_hybrid_rerank_neighbor` | Cải thiện 2: Hybrid Rerank + Neighbor Context (`top_k=3`, `budget=3000`) | 5/5 (100.0%) | 5/5 (100.0%) | 5/5 (100.0%) | 355.77 | $0.00 |
