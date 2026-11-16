# Bảng đối chiếu chấm tay Agent (Audit Sheet)

Đọc câu trả lời, citation và `final_context` bên dưới để xác nhận/sửa `reviews_template.json` thành `reviews.json` trước khi chạy `starter/agent_metrics.py`.
- `context_grade`: `0` = không có evidence; `1` = thiếu điều kiện/nguồn; `2` = đủ evidence & nguồn.
- `answer_grade` (câu có đáp án): `0` = sai/thiếu evidence/từ chối nhầm; `1` = đúng một phần; `2` = đúng & đủ.

## `q16` (test · có đáp án)
- **Câu hỏi:** Từ năm 2011 đến 2021, Chính phủ đã thu gọn quy mô chi tiêu và số lượng các Chương trình mục tiêu quốc gia (CTMTQG) như thế nào?
- **Đáp án chuẩn:** Quy mô chi tiêu giảm từ 9,1% xuống 2,8% tổng chi tiêu; số lượng giảm từ 16 CTMTQG và 45 chương trình mục tiêu nhỏ xuống còn 3 CTMTQG và một vài chương trình cấp phát.
- **Gold:** `[{"source_id": "wb-taking-stock-2023-08", "page": 50, "evidence": "Trong giai đoạn từ 2011-2021, Chính phủ đã giảm quy mô các chương trình bổ sung ngân sách có mục tiêu (chiếm 9,1% đến 2,8% tổng chi tiêu) và số lượng các chương trình (từ 16 CTMTQG và 45 chương trình mục tiêu quy mô nhỏ hơn xuống còn 3 CTMTQG và một vài chương trình cấp phát)."}]`
- **Agent status:** `answered` | **Search calls:** 1
- **Agent answer:** Từ năm 2011 đến 2021, Chính phủ đã thu gọn quy mô chi tiêu và số lượng các Chương trình mục tiêu quốc gia (CTMTQG) như sau [wb-taking-stock-2023-08_B_p50_c01]:

1. **Quy mô chi tiêu**: Giảm từ 9,1% xuống còn 2,8% tổng chi tiêu
2. **Số lượng chương trình**: Giảm từ 16 CTMTQG và 45 chương trình mục tiêu quy mô nhỏ hơn xuống còn 3 CTMTQG và một vài chương trình cấp phát
- **Agent citations:** `['wb-taking-stock-2023-08_B_p50_c01']`

<details><summary>Final context gửi cho model</summary>

```text
[wb-taking-stock-2023-08_B_p50_c01 | starter/data/data.pdf | page 50]
• Thiếu cơ chế hiệu quả để thúc đẩy tài chính và đầu tư liên kết: Phương thức "chương trình đầu tư công" đã được nêu trong Luật đầu tư công (Luật ĐTC, 2019),97 nhưng chưa được cụ thể hóa và áp dụng hiệu quả trong thực tiễn. Phương thức này có thể kết nối các bên cả theo chiều dọc và chiều ngang. Đối với nguồn lực trong nước, cơ chế kết nối chính thức theo chiều dọc được thực hiện duy nhất hiện nay là thông qua các Chương trình mục tiêu quốc gia (CTMTQG). Trong giai đoạn từ 2011-2021, Chính phủ đã giảm quy mô các chương trình bổ sung ngân sách có mục tiêu (chiếm 9,1% đến 2,8% tổng chi tiêu) và số lượng các chương trình (từ 16 CTMTQG và 45 chương trình mục tiêu quy mô nhỏ hơn xuống còn 3 CTMTQG và một vài chương trình cấp phát).

[wb-taking-stock-2023-08_B_p36_c02 | starter/data/data.pdf | page 36]
Những bước đi đó bao gồm xác định chỉ tiêu giải ngân đầu tư và đảm bảo hiệu lực thực thi, trách nhiệm giải trình ở các cấp chính quyền khác nhau để hoàn thành chỉ tiêu; tập trung cao độ để giải ngân các chương trình đầu tư quan trọng của quốc gia như đường cao tốc, truyền tải điện và các chương trình mục tiêu quốc gia; cho phép có sự linh hoạt trong các quy định về phân bổ ngân sách được xác định trong Chương trình Phục hồi và Phát triển Kinh tế 2022-2023 (1,8% GDP); và cho phép được linh hoạt phần nào để thực hiện một số hoạt động đấu thầu sớm trước khi phân bổ ngân sách.

[wb-taking-stock-2023-08_B_p15_c01 | starter/data/data.pdf | page 15]
10 Chiến lược phát triển kinh tế xã hội giai đoạn 2021-2030 và quy hoạch phát triển quốc gia tổng thể giai đoạn 2021-2030 và tầm nhìn đến năm 2050.
```
</details>

## `q17` (test · có đáp án)
- **Câu hỏi:** Trường hợp xung đột nguồn nước giữa Quảng Nam (thượng nguồn) và Đà Nẵng (hạ lưu) cho thấy chi phí xử lý tại hai địa phương chênh lệch như thế nào?
- **Đáp án chuẩn:** Chi phí xử lý ở Quảng Nam (thượng nguồn) ước tính là 50 triệu USD, trong khi chi phí quản lý rủi ro ngập lụt/hạn hán ở Đà Nẵng (hạ lưu) lên đến trên 350 triệu USD.
- **Gold:** `[{"source_id": "wb-taking-stock-2023-08", "page": 52, "evidence": "Mặc dù chi phí ước tính để xử lý vấn đề này ở Quảng Nam (trên thượng nguồn) là 50 triệu USD, nhưng ở dưới hạ lưu tại Đà Nẵng, chi phí ước tính để quản lý rủi ro ngập lụt / hạn hán có thể lên đến trên 350 triệu USD."}]`
- **Agent status:** `answered` | **Search calls:** 1
- **Agent answer:** Trường hợp xung đột nguồn nước giữa Quảng Nam (thượng nguồn) và Đà Nẵng (hạ lưu) cho thấy chi phí xử lý chênh lệch rất lớn. Chi phí ước tính để xử lý vấn đề ở Quảng Nam (thượng nguồn) là 50 triệu USD, nhưng ở hạ lưu tại Đà Nẵng, chi phí ước tính để quản lý rủi ro ngập lụt/hạn hán có thể lên đến trên 350 triệu USD [wb-taking-stock-2023-08_B_p52_c01]. Điều này cho thấy chi phí tại Đà Nẵng cao hơn gấp 7 lần so với Quảng Nam.
- **Agent citations:** `['wb-taking-stock-2023-08_B_p52_c01']`

<details><summary>Final context gửi cho model</summary>

```text
[wb-taking-stock-2023-08_B_p52_c01 | starter/data/data.pdf | page 52]
đơn kiến nghị lên tỉnh Quảng Nam và Thủ tướng Chính phủ về các vấn đề liên quan đến thay đổi dòng chảy làm trầm trọng thêm tình trạng ngập lụt khi có mưa lớn ở thượng nguồn và gây hạn hán ở vùng hạ lưu trong mùa khô.105 Mặc dù chi phí ước tính để xử lý vấn đề này ở Quảng Nam (trên thượng nguồn) là 50 triệu USD, nhưng ở dưới hạ lưu tại Đà Nẵng, chi phí ước tính để quản lý rủi ro ngập lụt / hạn hán có thể lên đến trên 350 triệu USD.106 Tuy nhiên, như đã nêu trên, các hệ thống QLĐTC và quan hệ ngân sách giữa các cấp chính quyền hiện nay không thể cho phép và ưu tiên triển khai các dự án đầu tư và giải quyết những việc có tính chất liên vùng, liên tỉnh như vậy.

[wb-taking-stock-2023-08_B_p46_c02 | starter/data/data.pdf | page 46]
Chẳng hạn, theo ước tính của Ngân hàng Thế giới, thành phố Đà Nẵng có thể chịu tổn thất về tài sản ở mức khoảng 900 tỷ VND - tương đương khoảng 4,5% chi tiêu hàng năm và 0,8% GRDP - do các sự kiện thời tiết cực đoan gây ra trong giai đoạn 2021–2030. Nhiều địa phương đông dân trên cả nước còn phải đối mặt với nguy cơ cao về nước biển dâng, xâm nhập mặn, sụt lún đất, và sạt lở bờ sông, bờ biển, như tại vùng đồng bằng sông Cửu Long . với hơn 17 triệu dân.87

[wb-taking-stock-2023-08_B_p49_c06 | starter/data/data.pdf | page 49]
hạ tầng, nhưng hiện mới chỉ có hướng dẫn về hạch toán và quản lý tài sản hạ tầng đường bộ, nước sạch và thủy lợi. Các hướng dẫn này cũng chưa được áp dụng nhất quán, do vậy làm giảm tính chính xác của các báo cáo liên quan tới giá trị tài sản. Hệ thống ngân sách song trùng, trong đó Bộ Tài chính quản lý ngân sách chi thường xuyên còn Bộ KH&ĐT quản lý ngân sách chi đầu tư, cũng tạo ra những thách thức trong việc đảm bảo vốn cho công tác vận hành và bảo trì.
```
</details>

## `q18` (test · có đáp án)
- **Câu hỏi:** Mỗi năm tại Việt Nam, tình trạng lũ, lụt bờ sông và bờ biển khiến bình quân bao nhiêu USD giá trị hoạt động kinh tế và bao nhiêu việc làm ở các lĩnh vực nào phải chịu rủi ro?
- **Đáp án chuẩn:** Bình quân khoảng 852 triệu USD giá trị hoạt động kinh tế và 316.000 việc làm trong các lĩnh vực nông nghiệp, nuôi trồng thủy sản, du lịch và công nghiệp.
- **Gold:** `[{"source_id": "wb-taking-stock-2023-08", "page": 46, "evidence": "Hàng năm, bình quân khoảng 852 triệu US$ giá trị hoạt động kinh tế và 316.000 việc làm trong các lĩnh vực nông nghiệp, nuôi trồng thủy sản, du lịch và công nghiệp phải chịu rủi ro từ tình trạng lũ, lụt bờ sông và bờ biển"}]`
- **Agent status:** `answered` | **Search calls:** 1
- **Agent answer:** Theo tài liệu, hàng năm tại Việt Nam, bình quân khoảng 852 triệu USD giá trị hoạt động kinh tế và 316.000 việc làm phải chịu rủi ro từ tình trạng lũ, lụt bờ sông và bờ biển [wb-taking-stock-2023-08_B_p46_c01]. Các lĩnh vực bị ảnh hưởng bao gồm: nông nghiệp, nuôi trồng thủy sản, du lịch và công nghiệp [wb-taking-stock-2023-08_B_p46_c01].
- **Agent citations:** `['wb-taking-stock-2023-08_B_p46_c01']`

<details><summary>Final context gửi cho model</summary>

```text
[wb-taking-stock-2023-08_B_p46_c01 | starter/data/data.pdf | page 46]
Biến đổi khí hậu càng làm trầm trọng thêm những thách thức trên Việt Nam là một trong 10 quốc gia bị biến đổi khí hậu (BĐKH) và thiên tai gây ảnh hưởng nhiều nhất trên toàn cầu. 86 Hàng năm, bình quân khoảng 852 triệu US$ giá trị hoạt động kinh tế và 316.000 việc làm trong các lĩnh vực nông nghiệp, nuôi trồng thủy sản, du lịch và công nghiệp phải chịu rủi ro từ tình trạng lũ, lụt bờ sông và bờ biển . Đây là vấn đề rất cấp thiết tại nhiều địa bàn động lực tăng trưởng của cả nước và các vùng liên quan - như thành phố Hồ Chí Minh, Đà Nẵng và Cần Thơ - đều là các địa phương tuyến đầu nhưng cũng phải hứng chịu các hậu quả liên quan tới thời tiết cực đoan và BĐKH.

[wb-taking-stock-2023-08_B_p46_c03 | starter/data/data.pdf | page 46]
Đầu tư công và tài sản công của Việt Nam đang phải đối diện với rủi ro khí hậu và các sự kiện thời tiết cực đoan ngày càng gia tăng. Trong năm 2022, phí tổn do thiệt hại trực tiếp đối với công trình hạ tầng năng lượng và giao thông do bão và ngập lụt gây ra ước lên đến 475 triệu US$. Các doanh nghiệp ước tính họ phải chi đến 280 triệu US$ do hạ tầng chưa đảm bảo tin cậy và có khả năng chống chịu. Cho dù với những rủi ro như trên, đầu tư bình quân cho hạ tầng giúp phòng chống, thích ứng với thiên tai mới chỉ đạt khoảng 0,05 GDP.

[wb-taking-stock-2023-08_B_p46_c02 | starter/data/data.pdf | page 46]
Chẳng hạn, theo ước tính của Ngân hàng Thế giới, thành phố Đà Nẵng có thể chịu tổn thất về tài sản ở mức khoảng 900 tỷ VND - tương đương khoảng 4,5% chi tiêu hàng năm và 0,8% GRDP - do các sự kiện thời tiết cực đoan gây ra trong giai đoạn 2021–2030. Nhiều địa phương đông dân trên cả nước còn phải đối mặt với nguy cơ cao về nước biển dâng, xâm nhập mặn, sụt lún đất, và sạt lở bờ sông, bờ biển, như tại vùng đồng bằng sông Cửu Long . với hơn 17 triệu dân.87
```
</details>

## `q19` (test · có đáp án)
- **Câu hỏi:** Trong nhu cầu tài chính ứng phó biến đổi khí hậu và chuyển đổi xanh, đầu tư công có thể chiếm tỷ trọng bao nhiêu phần trăm GDP mỗi năm và riêng lộ trình nâng cao khả năng chống chịu chiếm tỷ lệ bao nhiêu?
- **Đáp án chuẩn:** Đầu tư công chiếm hơn một phần ba nhu cầu tài chính (tương đương khoảng 2,4% GDP mỗi năm), và riêng lộ trình nâng cao khả năng chống chịu chiếm khoảng hai phần ba số tiền đó.
- **Gold:** `[{"source_id": "wb-taking-stock-2023-08", "page": 47, "evidence": "Đầu tư công - với vai trò quan trọng trong việc làm hình mẫu và chất xúc tác thu hút đầu tư tư nhân - có thể chiếm hơn một phần ba nhu cầu tài chính, tương đương khoảng 2,4% GDP. Riêng lộ trình nâng cao khả năng chống chịu đã chiếm khoảng hai phần ba số tiền trên"}]`
- **Agent status:** `answered` | **Search calls:** 1
- **Agent answer:** Theo tài liệu, trong nhu cầu tài chính ứng phó biến đổi khí hậu và chuyển đổi xanh, đầu tư công có thể chiếm hơn một phần ba nhu cầu tài chính, tương đương khoảng 2,4% GDP mỗi năm [wb-taking-stock-2023-08_B_p47_c01]. Riêng lộ trình nâng cao khả năng chống chịu đã chiếm khoảng hai phần ba số tiền trên, tức là chiếm tỷ lệ khoảng 1,6% GDP (hai phần ba của 2,4%) [wb-taking-stock-2023-08_B_p47_c01].
- **Agent citations:** `['wb-taking-stock-2023-08_B_p47_c01']`

<details><summary>Final context gửi cho model</summary>

```text
[wb-taking-stock-2023-08_B_p47_c01 | starter/data/data.pdf | page 47]
đương 6,8% GDP mỗi năm.89 Đầu tư công - với vai trò quan trọng trong việc làm hình mẫu và chất xúc tác thu hút đầu tư tư nhân - có thể chiếm hơn một phần ba nhu cầu tài chính, tương đương khoảng 2,4% GDP. Riêng lộ trình nâng cao khả năng chống chịu đã chiếm khoảng hai phần ba số tiền trên vì cần huy động một lượng tài chính lớn để phòng vệ cho tài sản và công trình hạ tầng của quốc gia cũng như những người dân có nguy cơ dễ tổn thương. Tuy nhiên, thích ứng với BĐKH chưa được xem xét đầy đủ trong chiến lược tài khóa tổng thể cũng như trong việc xác định dự án ưu tiên cho đầu tư công ở Việt Nam.90

[wb-taking-stock-2023-08_B_p42_c05 | starter/data/data.pdf | page 42]
76 Đánh giá tác động của đầu tư công đến tăng trưởng (chuyên đề nghiên cứu chính sách số 8604/2018 của Ngân hàng Thế giới). 77 Thế mạnh của đầu tư công: Chuyển nguồn lực thành tài sản để thúc đẩy tăng trưởng (Ngân hàng Thế giới, 2014).

[wb-taking-stock-2023-08_B_p46_c04 | starter/data/data.pdf | page 46]
Chi phí cải thiện khả năng chống chịu vùng duyên hải được dự báo sẽ lên đến 4 tỷ US$ vào năm 2035, trong đó riêng chi phí xây dựng và nâng cấp đê biển phải mất đến 2 tỷ US$.88 Tổng nhu cầu tài chính phát sinh thêm của Việt Nam để xử lý những thách thức liên quan đến BĐKH và chuyển đổi xanh có thể lên đến khoảng 701 tỷ US$ trong giai đoạn 2022-2040, tương 86 Các nguồn khác nhau: bao gồm climateknowlegeportal.worldbank.org; climatelinks.org; and climaterisk.undp.org. 87 Việt Nam: Báo cáo Quốc gia về Khí hậu và Phát triển (CCDR) (Ngân hàng Thế giới, 2022). 88 Bờ biển có khả năng chống chịu: Phát triển vùng duyên hải của Việt Nam giữa cơ hội và rủi ro thiên tai (Ngân hàng Thế giới, 2020).
```
</details>

## `q20` (test · có đáp án)
- **Câu hỏi:** Trong đánh giá tổng quan về hiệu suất hạ tầng, chất lượng hạ tầng của Việt Nam đứng thứ mấy trên bao nhiêu quốc gia toàn thế giới và xếp sau những nước nào trong khu vực?
- **Đáp án chuẩn:** Đứng thứ 77 trên 141 quốc gia toàn thế giới, sau Trung Quốc, Ấn Độ, In-đô-nê-xia, Ma-lai-xia và Thái Lan.
- **Gold:** `[{"source_id": "wb-taking-stock-2023-08", "page": 16, "evidence": "Chất lượng hạ tầng của Việt Nam đứng thứ 77 trên 141 quốc gia trên toàn thế giới, 13 đứng sau các quốc gia so sánh trong khu vực như Trung Quốc, Ấn Độ, In- đô-nê-xia, Ma-lai-xia, và Thái Lan"}]`
- **Agent status:** `answered` | **Search calls:** 1
- **Agent answer:** Trong đánh giá tổng quan về hiệu suất hạ tầng, chất lượng hạ tầng của Việt Nam đứng thứ 77 trên 141 quốc gia toàn thế giới [wb-taking-stock-2023-08_B_p16_c02]. Trong khu vực, Việt Nam xếp sau các quốc gia như Trung Quốc, Ấn Độ, In-đô-nê-xia, Ma-lai-xia, và Thái Lan [wb-taking-stock-2023-08_B_p16_c02].
- **Agent citations:** `['wb-taking-stock-2023-08_B_p16_c02']`

<details><summary>Final context gửi cho model</summary>

```text
[wb-taking-stock-2023-08_B_p16_c02 | starter/data/data.pdf | page 16]
Chất lượng hạ tầng của Việt Nam đứng thứ 77 trên 141 quốc gia trên toàn thế giới, 13 đứng sau các quốc gia so sánh trong khu vực như Trung Quốc, Ấn Độ, In- đô-nê-xia, Ma-lai-xia, và Thái Lan - là các quốc gia Việt Nam đang cạnh tranh để thu hút vốn đầu tư trực tiếp nước ngoài (FDI). Ngân sách đầu tư thực hiện luôn thấp hơn dự toán, chỉ giải ngân được trung bình 77% dự toán phân bổ trong giai đoạn từ 2017 đến 2022. Chênh lệch lớn giữa số dự toán và số thực giải ngân (23%), kèm theo đó là tình trạng chi đầu tư bị chuyển nguồn ở mức cao, đã và đang cao hơn hẳn so với nhiều quốc gia so sánh, và cách xa so với thông lệ quốc tế tốt là dưới 5%.

[wb-taking-stock-2023-08_B_p15_c06 | starter/data/data.pdf | page 15]
Việt Nam, trong quá trình phát triển hướng tới mức thu nhập trung bình cao vào năm 2030 và thu nhập cao vào năm 2045, mong muốn trở thành quốc gia công nghiệp và hiện đại, đem lại chất lượng sống tốt hơn cho người dân. Để đạt được mục tiêu phát triển đầy tham vọng nêu trên, dự kiến Chính phủ Việt Nam cần đầu tư bình quân 7,3% GDP mỗi năm cho hạ tầng trong giai đoạn 2021-2030. 10 Mặc dù nhu cầu ngày càng lớn, nhưng đầu tư công của Việt Nam đã và đang theo xu hướng giảm dần, từ 8% GDP trong năm 2011 xuống còn 6% trong năm 2022. Tuy cần CHUYÊN ĐỀ ĐẶC BIỆT: ĐỂ ĐẦU TƯ CÔNG THÚC ĐẨY TĂNG TRƯỞNG

[wb-taking-stock-2023-08_B_p16_c07 | starter/data/data.pdf | page 16]
Trong khi đó, kinh nghiệm quốc tế cho thấy đầu tư là động lực quan trọng nhất đối với các quốc gia tăng trưởng cao khi họ đang ở trình độ phát triển như Việt Nam hiện nay. 12 Dữ liệu về hệ số hiệu quả sử dụng vốn đầu tư (ICOR) lấy của Tổng cục Thống kê Việt Nam (TCTK). 13 Diễn đàn Kinh tế thế giới - Chỉ số Năng lực cạnh tranh toàn cầu (2019). 14 Khung đánh giá chi tiêu công và trách nhiệm giải trình tài chính (PEFA). 15 Đầu tư tại các khu vực ở Việt Nam: Cơ hội và Thách thức (Chuyên đề chính sách của Ngân hàng Thế giới, 2023). Trong cùng đánh giá đó, chúng tôi ghi nhận chậm tiến độ có xu hướng chênh lệch nhiều hơn từ một đến ba năm đối với các dự án nhỏ.
```
</details>

## `u03` (test · thiếu bằng chứng)
- **Câu hỏi:** Báo cáo có nêu mức lãi suất điều hành cụ thể (tính bằng %/năm) mà Ngân hàng Nhà nước Việt Nam dự kiến áp dụng vào cuối năm 2024 không?
- **Lý do thiếu bằng chứng:** Báo cáo đề cập các đợt cắt giảm lãi suất điều hành trong nửa đầu năm 2023 nhưng không đưa ra con số dự báo mức lãi suất điều hành cụ thể cho cuối năm 2024.
- **Agent status:** `abstain` | **Search calls:** 2
- **Agent answer:** Không đủ bằng chứng để trả lời.
- **Agent citations:** `[]`

<details><summary>Final context gửi cho model</summary>

```text
[wb-taking-stock-2023-08_B_p13_c06 | starter/data/data.pdf | page 13]
2024f 5,5 3,0 0,5 -0,3 35,2 2023f 4,7 3,5 0,2 -0,7 36,0 2025f 6,0 3,0 1,0 -0,2 34,4 Nguồn: TCTK; Bộ Tài chính; NHNN; IMF; và tính toán của cán bộ Ngân hàng Thế giới. Ghi chú: e = số ước thực hiện; f = số dự báo, *: không bao gồm các khoản chi tiêu ngân sách chưa được phân bổ và áp dụng chuẩn GFS. Bảng 0.1. Một số chỉ số kinh tế, Việt Nam 2020-2025 Chỉ số Tăng trưởng GDP (%) Chỉ số giá tiêu dùng (bình quân, %) Cân đối tài khoản vãng lai (% GDP) Cân đối tài khóa (*) (% GDP) Nợ công (% GDP) 2020 2,9 3,2 4,3 -2,9 41,3 2022e 8,0 3,1 -0,3 -0,3 35,7 2021 2,6 1,8 -2,1 -3,4 39,3

[wb-taking-stock-2023-08_B_p26_c02 | starter/data/data.pdf | page 26]
Việt Nam ghi nhận khoản mục sai sót ròng ở mức lớn (7,5 tỷ US$ trong quý đầu năm 2023), 39 có lẽ phản ánh dòng vốn tiếp tục chảy ra nước ngoài nhưng không được ghi nhận, do kỳ vọng đồng tiền tiếp tục bị mất giá và còn chênh lệch lãi suất. Mặc dù khoản mục sai sót ròng có tăng lên, nhưng thặng dư trên cả tài khoản vãng lai và tài khoản tài chính đã hỗ trợ làm tăng thặng dư cán cân thanh toán tổng thể, tạo điều kiện cho Ngân hàng Nhà nước Việt Nam (NHNN) nâng dự trữ ngoại hối (từ 87,1% tỷ US$ vào cuối quý 4 năm 2023 lên 88,7 tỷ US$ vào cuối quý 1 năm 2023, tương đương 3,3 tháng nhập khẩu.

[wb-taking-stock-2023-08_B_p30_c02 | starter/data/data.pdf | page 30]
Chỉ số giá của một số mặt hàng nhập khẩu Tháng 06/2019 = 100 (không điều chỉnh theo mùa vụ) T6-18 T6-19 T6-20 T6-21 T6-22 T6-23 Nguồn: Haver Analytics, Ngân hàng Nhà nước Việt Nam T6-19 T8-19 T10-19 T2-20 T2-21 T2-22 T2-23 T12-19 T12-20 T12-21 T12-22 T4-20 T4-21 T4-22 T4-23 T8-20 T8-21 T8-22 T6-21 T6-22 T6-23 T6-20 T10-20 T10-21 T10-22 Hình 1.20. Lãi suất Tỷ lệ % 8 6 4 2 0 Việt Nam: Lợi suất trái phiếu chính phủ 10 năm (%) Tỷ giá chào bán liên ngân hàng VND kỳ hạn 2 tuần [VIBOR] (%) Chiết khấu của NHNN Khu vực ngân hàng tiếp tục phải đối mặt với thách thức trong nửa đầu năm 2023.
```
</details>

## `u04` (test · thiếu bằng chứng)
- **Câu hỏi:** Tổng mức đầu tư bằng tiền (tỷ VND hoặc tỷ USD) riêng cho tuyến đường sắt cao tốc Bắc – Nam được báo cáo ước tính là bao nhiêu?
- **Lý do thiếu bằng chứng:** Báo cáo có đề cập đến hạ tầng giao thông (cảng biển, sân bay, đường cao tốc) nhưng không nêu dự toán tổng mức đầu tư cho tuyến đường sắt cao tốc Bắc – Nam.
- **Agent status:** `abstain` | **Search calls:** 3
- **Agent answer:** Không đủ bằng chứng để trả lời.
- **Agent citations:** `[]`

<details><summary>Final context gửi cho model</summary>

```text
[wb-taking-stock-2023-08_B_p41_c03 | starter/data/data.pdf | page 41]
Hộp 2.1. Những hạn chế về hạ tầng giao thông Trong 20 năm qua, chi tiêu cho giao thông - bằng khoảng 23% chi đầu tư từ NSNN và 3,5% GDP - tập trung chủ yếu cho hạ tầng giao thông nông thôn (75%), do các địa phương quản lý. Trong điều kiện ngân sách hạn chế, đầu tư tập trung theo hướng đó gây ảnh hưởng đến triển khai các công trình đầu tư có tầm quan trọng chiến lược quốc gia. Chính vì lẽ đó, mật độ đường cao tốc ở Việt Nam thuộc dạng thấp nhất trong khu vực Đông Á và Thái Bình Dương (ĐÁ-TBD), và chi phí vận tải đường bộ đứng cao nhất so với các nước khác trong khu vực. Nhiều đoạn dọc trục đường cao tốc Bắc - Nam đến nay chưa được xây dựng. Hạ tầng đườngoc sắt cũng bị lãng quên.

[wb-taking-stock-2023-08_B_p36_c01 | starter/data/data.pdf | page 36]
64 https://www.elibrary.imf.org/display/book/9781557751928/ch005.xml. Công thức (3) được dùng để ước tính tác động tài khóa: FI=(ΔG-nG-1) - [ΔT-(ΔY/Y-1) T-1].

65 So với dự toán được Quốc hội phê duyệt, tính đến 31/12/2022.

nhanh, khi giải ngân vốn đầu tư công tăng tới 43,3% so cùng kỳ năm trước trong nửa đầu năm 2023. Mặc dù vậy, tiến độ triển khai đầu tư công lâu nay vẫn chậm, ví dụ chỉ đạt 67,3% trong năm 2022. 65 Các bước đi nhằm đẩy nhanh và cải thiện hiệu suất triển khai sẽ giúp giải quyết những hạn chế phát sinh về hạ tầng để phục vụ tăng trưởng, bao gồm nhu cầu đầu tư cấp thiết cho mạng lưới truyền tải điện cũng như nâng cao khả năng chống chịu với biến đổi khí hậu.

[wb-taking-stock-2023-08_B_p43_c01 | starter/data/data.pdf | page 43]
tư được phân bổ. Trong giai đoạn từ 2017 đến 2022, chi đầu tư chỉ thực hiện trung bình được 77% dự toán (tham khảo Hình 2.4). Chênh lệch giữa dự toán và thực hiện (23%) với hệ quả phải chuyển nguồn chi đầu tư (ở mức từ 18 đến 31% tổng chi đầu tư) nhiều hơn hẳn so với các quốc gia so sánh, và cao hơn rất nhiều so với thông lệ quốc tế tốt là 5%. 78 Yếu kém về hiệu suất quản lý đầu tư công (QLĐTC) cũng được thể hiện qua tình trạng chậm tiến độ hoàn thành dự án và đội vốn. Theo một đánh giá gần đây 79 của Ngân hàng Thế giới tại một số dự án giao thông quy mô lớn, chậm tiến độ bình quân lên đến năm năm, còn đội vốn bình quân lên đến gấp đôi dự toán kinh phí ban đầu ở giai đoạn thiết kế và phân bổ ngân sách.
```
</details>

