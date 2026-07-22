# AVS-016 Round01 — Deep Review

## Kết luận

- Phân tích: 20 reference WAV + 40 preview WAV.
- Critical blocker: **pair_002** (transcript/reference mismatch).
- Text normalization cần sửa: **pair_005, pair_010, pair_012, pair_017**.
- Nhóm mạnh nhất: **pair_018 Benchmark, pair_020 AI, pair_009, pair_016 Benchmark**.
- Chưa được dùng kết quả này để Training tự động; cần tai người chốt các pair biên.

## Xếp hạng Pair

01. pair_018 — Benchmark Preview — 7.75/10 — KEEP — Benchmark đứng đầu: content/timbre/prosody cân bằng, chênh AI đủ rõ.
02. pair_020 — AI Preview — 7.37/10 — KEEP — AI rất mạnh về timbre/content; prosody thấp hơn nhóm đầu. Giữ nhưng nghe kỹ độ nhấn nhá.
03. pair_009 — Benchmark Preview — 7.13/10 — KEEP — Hai biến thể đều mạnh và gần hòa: AI nhỉnh similarity; Benchmark nhỉnh prosody/naturalness.
04. pair_016 — Benchmark Preview — 6.81/10 — KEEP — Benchmark rất mạnh về content/duration và tốt hơn AI rõ. Giữ ưu tiên cao.
05. pair_015 — AI Preview — 6.23/10 — MAYBE — Cả hai khá; AI nhỉnh similarity, Benchmark nhỉnh prosody/noise. AI là lựa chọn tổng thể.
06. pair_003 — AI Preview — 6.07/10 — MAYBE — AI có speaker/timbre và naturalness tốt; content/prosody chỉ mức trung bình. Ưu tiên nghe kỹ tên riêng.
07. pair_019 — Benchmark Preview — 5.88/10 — MAYBE — Benchmark tốt hơn AI rõ về content và tổng thể; noise proxy vẫn cần nghe kiểm chứng.
08. pair_001 — Benchmark Preview — 5.77/10 — MAYBE — Hai biến thể gần như hòa. Benchmark nhỉnh nhẹ tổng thể; AI nhỉnh hơn speaker similarity. Cần nghe tai người để chốt.
09. pair_005 — Benchmark Preview — 5.62/10 — MAYBE — Benchmark tốt hơn rõ, nhưng transcript bắt đầu bằng chuỗi dấu ngoặc kép lỗi. Normalize rồi regenerate.
10. pair_006 — Benchmark Preview — 5.51/10 — MAYBE — Benchmark có content/pronunciation proxy tốt hơn; AI có prosody khá. Ưu tiên Benchmark.
11. pair_004 — Benchmark Preview — 5.46/10 — MAYBE — Benchmark cân bằng hơn AI, nhưng noise proxy thấp. Giữ ở nhóm review.
12. pair_010 — AI Preview — 5.34/10 — MAYBE — AI tốt hơn rõ, nhưng transcript có dấu ngoặc kép mở không đóng. Normalize rồi regenerate.
13. pair_007 — Benchmark Preview — 4.88/10 — REJECT — Benchmark nhỉnh hơn, nhưng prosody thấp. Nên thay candidate nếu tai người cũng thấy phẳng/khác nhịp.
14. pair_014 — AI Preview — 4.57/10 — REJECT — AI nhỉnh hơn Benchmark nhưng speaker similarity thấp. Nhóm ưu tiên thay.
15. pair_017 — Benchmark Preview — 4.46/10 — MAYBE — Hai biến thể gần hòa nhưng transcript có dấu ngoặc kép + khoảng trắng đầu câu. Normalize rồi regenerate.
16. pair_011 — AI Preview — 4.15/10 — REJECT — Hai biến thể dưới trung bình; câu kết thúc bằng dấu ba chấm/đoạn thoại dở dang làm đánh giá prosody kém ổn định.
17. pair_013 — AI Preview — 4.13/10 — REJECT — AI nhỉnh hơn; content proxy khá nhưng timbre/naturalness thấp. Ưu tiên thay candidate nếu nghe không đạt.
18. pair_012 — Benchmark Preview — 3.77/10 — MAYBE — Benchmark tốt hơn, nhưng transcript có dấu ngoặc kép mở không đóng và tổng điểm thấp. Regenerate sau normalize rồi mới quyết định.
19. pair_008 — AI Preview — 3.59/10 — REJECT — AI tốt hơn Benchmark, nhưng cả hai nằm nhóm thấp. Ưu tiên thay bằng candidate Top50 khác.
20. pair_002 — AI Preview — 0.00/10 — REJECT — REJECT bắt buộc: transcript 233 ký tự nhưng reference chỉ ~5,8 giây; hai preview ~12 giây. Đây là mismatch alignment/metadata.

## Giới hạn

Xếp hạng sử dụng ensemble tín hiệu: GMM target-speaker, MFCC/log-mel DTW, timbre, F0, energy,
duration, pause, HNR/jitter/shimmer, SNR proxy và spectrogram. Đây không phải lượt nghe thính giác trực tiếp
và không thay thế human listening trước Training.
