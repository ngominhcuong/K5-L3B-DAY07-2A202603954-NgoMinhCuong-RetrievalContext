# Phân tích lỗi trên Dev (Mốc 3)

## `1_dense_baseline` (Dense Qdrant Day 6 (`top_k=3`, `budget=2400`))
- Trượt Hit@1: Không có
- Trượt Evidence Hit@3: Không có
- Trượt Context Evidence: Không có

## `2_bm25_lexical` (Lexical BM25 (`k1=1.5, b=0.75`, `top_k=3`, `budget=2400`))
- Trượt Hit@1: Không có
- Trượt Evidence Hit@3: Không có
- Trượt Context Evidence: Không có

## `3_hybrid_rrf` (Hybrid Dense + BM25 via RRF (`k=60, cand=10`, `top_k=3`, `budget=2400`))
- Trượt Hit@1: Không có
- Trượt Evidence Hit@3: Không có
- Trượt Context Evidence: Không có

## `4_hybrid_rerank` (Cải thiện 1: Hybrid RRF + Normalized Rerank (`cand=10`, `top_k=3`, `budget=2400`))
- Trượt Hit@1: Không có
- Trượt Evidence Hit@3: Không có
- Trượt Context Evidence: Không có

## `5_hybrid_rerank_neighbor` (Cải thiện 2: Hybrid Rerank + Neighbor Context (`top_k=3`, `budget=3000`))
- Trượt Hit@1: Không có
- Trượt Evidence Hit@3: Không có
- Trượt Context Evidence: Không có

