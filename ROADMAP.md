# AI Voice Studio Roadmap

> Nguyên tắc:
>
> Luôn ưu tiên tạo ra phiên bản sử dụng được trước (MVP), sau đó mới mở rộng tính năng.

---

# MVP (v0.1)

## Mục tiêu

Có thể clone một giọng và tạo Audio bằng GPT-SoVITS.

---

# Core

- [x] AppContext
- [x] EngineManager
- [x] RuntimeService
- [x] Event Bus
- [x] Config
- [ ] Settings hoàn chỉnh

---

# Project

- [x] Khởi tạo Project
- [x] Cấu trúc thư mục
- [x] Project Schema
- [x] Migration project.json
- [x] Workspace
- [ ] Project UI hoàn chỉnh

---

# Engine

- [x] GPT-SoVITS Adapter
- [x] Runtime Detect
- [x] Engine Config
- [x] Runtime Validation
- [x] Generate End-to-End
- [ ] Generate MP3
- [ ] Train GPT-SoVITS
- [ ] Preview

---

# Reader

- [x] Đọc DOCX
- [x] Đọc TXT
- [ ] Dán văn bản
- [ ] EPUB
- [ ] PDF

---

# Voice

- [x] Voice Schema
- [x] Voice ID cố định
- [x] Migration voice.json
- [x] Variant Schema
- [ ] Train Voice
- [ ] Preview Voice
- [ ] Voice Library

---

# Dataset

- [x] Dataset Validation
- [x] Dataset Manifest
- [x] Dataset Report
- [x] ZIP Protection
- [x] Workspace Scan
- [x] Segmentation
- [x] Audio Metadata
- [x] ffprobe
- [x] Audio Alignment Pipeline
- [x] Faster-Whisper model local
- [x] Audio Slice
- [x] GPT-SoVITS Metadata
- [x] Quality-First Alignment

---

# Generate

- [x] Generate WAV
- [ ] Generate MP3
- [ ] Batch Generate
- [ ] Queue
- [ ] Resume
- [ ] Retry

---

# Runtime

- [x] Python
- [x] FFmpeg
- [x] CUDA
- [x] NVIDIA GPU
- [x] GPT-SoVITS Detect
- [x] Runtime Profile Schema

---

# UI

- [x] Main Window
- [x] Project
- [x] Workspace
- [x] Voice
- [x] Training
- [ ] Runtime
- [ ] Generate
- [ ] Settings
- [ ] Queue

---

# API

- [ ] Generate API
- [ ] Runtime API
- [ ] Voice API
- [ ] Queue API

---

# Subtitle

- [ ] Whisper
- [ ] Faster-Whisper
- [ ] Subtitle Editor
- [ ] SRT
- [ ] ASS

---

# Video Dubbing

- [ ] Timeline
- [ ] Subtitle Sync
- [ ] Replace Audio
- [ ] Export Video

---

# Multi Engine

- [ ] XTTS
- [ ] Fish Speech
- [ ] CosyVoice
- [ ] Plugin System

---

# Tiến độ Sprint

## Hoàn thành

- [x] AVS-001 Phân tích kiến trúc và lập kế hoạch
- [x] AVS-002 AppContext + EngineManager
- [x] AVS-003 Project Schema
- [x] AVS-004 Workspace
- [x] AVS-005 Voice Schema
- [x] AVS-006 Runtime
- [x] AVS-007 GPT-SoVITS Generate
- [x] AVS-008 Engine Config
- [x] AVS-009 Generate End-to-End
- [x] AVS-010 Cleanup
- [x] AVS-011 Dataset
- [x] AVS-012 Dataset Segmentation
- [x] AVS-013 Audio Alignment Pipeline
- [x] AVS-013.5 Faster-Whisper Runtime Validation
- [x] AVS-013.6 Quality-First Dataset Alignment

---

## Đang thực hiện

- [ ] AVS-014 GPT-SoVITS Training

---

## Tiếp theo

- [ ] AVS-015 Voice Preview
- [ ] AVS-016 Batch Generate
- [ ] AVS-017 API
- [ ] AVS-018 Subtitle
- [ ] AVS-019 Video Dubbing
