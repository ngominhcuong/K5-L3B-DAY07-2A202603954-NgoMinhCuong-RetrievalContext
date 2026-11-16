# Phân tích lỗi trên Dev (Mốc 3)

## `1_dense_baseline` (Dense Qdrant Day 6 (`top_k=3`, `budget=2400`))
- Trượt Hit@1: ['q04', 'q06', 'q11']
- Trượt Evidence Hit@3: ['q04']
- Trượt Context Evidence: Không có
  - `q04`: hit1=False, hit3=False, ctx=True | top_ids=['wb-taking-stock-2023-08_B_p29_c02', 'wb-taking-stock-2023-08_B_p12_c05', 'wb-taking-stock-2023-08_B_p29_c01'], top_pages=[29, 12, 29]
  - `q06`: hit1=False, hit3=True, ctx=True | top_ids=['wb-taking-stock-2023-08_B_p32_c02', 'wb-taking-stock-2023-08_B_p32_c01', 'wb-taking-stock-2023-08_B_p23_c06'], top_pages=[32, 32, 23]
  - `q11`: hit1=False, hit3=True, ctx=True | top_ids=['wb-taking-stock-2023-08_B_p17_c06', 'wb-taking-stock-2023-08_B_p53_c02', 'wb-taking-stock-2023-08_B_p47_c07'], top_pages=[17, 53, 47]

## `2_bm25_lexical` (Lexical BM25 (`k1=1.5, b=0.75`, `top_k=3`, `budget=2400`))
- Trượt Hit@1: ['q03', 'q04', 'q08', 'q11']
- Trượt Evidence Hit@3: ['q04']
- Trượt Context Evidence: ['q04']
  - `q03`: hit1=False, hit3=True, ctx=True | top_ids=['wb-taking-stock-2023-08_B_p22_c04', 'wb-taking-stock-2023-08_B_p23_c03', 'wb-taking-stock-2023-08_B_p23_c02'], top_pages=[22, 23, 23]
  - `q04`: hit1=False, hit3=False, ctx=False | top_ids=['wb-taking-stock-2023-08_B_p29_c02', 'wb-taking-stock-2023-08_B_p12_c05', 'wb-taking-stock-2023-08_B_p22_c01'], top_pages=[29, 12, 22]
  - `q08`: hit1=False, hit3=True, ctx=True | top_ids=['wb-taking-stock-2023-08_B_p37_c02', 'wb-taking-stock-2023-08_B_p37_c01', 'wb-taking-stock-2023-08_B_p37_c03'], top_pages=[37, 37, 37]
  - `q11`: hit1=False, hit3=True, ctx=True | top_ids=['wb-taking-stock-2023-08_B_p17_c05', 'wb-taking-stock-2023-08_B_p17_c06', 'wb-taking-stock-2023-08_B_p53_c02'], top_pages=[17, 17, 53]

## `3_hybrid_rrf` (Hybrid Dense + BM25 via RRF (`k=60, cand=10`, `top_k=3`, `budget=2400`))
- Trượt Hit@1: ['q04', 'q11']
- Trượt Evidence Hit@3: ['q04']
- Trượt Context Evidence: Không có
  - `q04`: hit1=False, hit3=False, ctx=True | top_ids=['wb-taking-stock-2023-08_B_p29_c02', 'wb-taking-stock-2023-08_B_p12_c05', 'wb-taking-stock-2023-08_B_p29_c01'], top_pages=[29, 12, 29]
  - `q11`: hit1=False, hit3=True, ctx=True | top_ids=['wb-taking-stock-2023-08_B_p17_c06', 'wb-taking-stock-2023-08_B_p53_c02', 'wb-taking-stock-2023-08_B_p52_c03'], top_pages=[17, 53, 52]

## `4_hybrid_rerank` (Cải thiện 1: Hybrid RRF + Normalized Rerank (`cand=10`, `top_k=3`, `budget=2400`))
- Trượt Hit@1: ['q03', 'q04', 'q08', 'q11']
- Trượt Evidence Hit@3: ['q04']
- Trượt Context Evidence: ['q04']
  - `q03`: hit1=False, hit3=True, ctx=True | top_ids=['wb-taking-stock-2023-08_B_p22_c04', 'wb-taking-stock-2023-08_B_p23_c03', 'wb-taking-stock-2023-08_B_p23_c02'], top_pages=[22, 23, 23]
  - `q04`: hit1=False, hit3=False, ctx=False | top_ids=['wb-taking-stock-2023-08_B_p29_c02', 'wb-taking-stock-2023-08_B_p12_c05', 'wb-taking-stock-2023-08_B_p22_c01'], top_pages=[29, 12, 22]
  - `q08`: hit1=False, hit3=True, ctx=True | top_ids=['wb-taking-stock-2023-08_B_p37_c02', 'wb-taking-stock-2023-08_B_p37_c01', 'wb-taking-stock-2023-08_B_p37_c03'], top_pages=[37, 37, 37]
  - `q11`: hit1=False, hit3=True, ctx=True | top_ids=['wb-taking-stock-2023-08_B_p17_c05', 'wb-taking-stock-2023-08_B_p17_c06', 'wb-taking-stock-2023-08_B_p53_c02'], top_pages=[17, 17, 53]

## `5_hybrid_rerank_neighbor` (Cải thiện 2: Hybrid Rerank + Neighbor Context (`top_k=3`, `budget=3000`))
- Trượt Hit@1: ['q03', 'q04', 'q08', 'q11']
- Trượt Evidence Hit@3: ['q04']
- Trượt Context Evidence: ['q11']
  - `q03`: hit1=False, hit3=True, ctx=True | top_ids=['wb-taking-stock-2023-08_B_p22_c04', 'wb-taking-stock-2023-08_B_p23_c03', 'wb-taking-stock-2023-08_B_p23_c02'], top_pages=[22, 23, 23]
  - `q04`: hit1=False, hit3=False, ctx=True | top_ids=['wb-taking-stock-2023-08_B_p29_c02', 'wb-taking-stock-2023-08_B_p12_c05', 'wb-taking-stock-2023-08_B_p22_c01'], top_pages=[29, 12, 22]
  - `q08`: hit1=False, hit3=True, ctx=True | top_ids=['wb-taking-stock-2023-08_B_p37_c02', 'wb-taking-stock-2023-08_B_p37_c01', 'wb-taking-stock-2023-08_B_p37_c03'], top_pages=[37, 37, 37]
  - `q11`: hit1=False, hit3=True, ctx=False | top_ids=['wb-taking-stock-2023-08_B_p17_c05', 'wb-taking-stock-2023-08_B_p17_c06', 'wb-taking-stock-2023-08_B_p53_c02'], top_pages=[17, 17, 53]

