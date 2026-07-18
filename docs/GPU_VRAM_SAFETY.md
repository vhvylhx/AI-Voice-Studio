# GPU / VRAM Safety

Nguyen tac:

- Khong chay GPU job neu khong co ResourceLease hop le.
- Khong tu cai driver.
- Khong tu chuyen cau hinh train khi OOM neu nguoi dung chua xac nhan.
- Khong hard-code GPU theo ten may.
- NVIDIA detection dung `nvidia-smi` va co timeout.
