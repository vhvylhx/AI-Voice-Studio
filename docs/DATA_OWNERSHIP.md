# Data Ownership

## Training Dataset

Owner: Training domain.

Quan ly scan, health, repair, review, alignment, metadata, train config, checkpoint va progress.

## Reading Style Profile / Voice DNA

Owner: Style Profile domain.

Quan ly create, rename, description, integrity, extraction state, import, export, archive, backup va restore.

## Speaker Reference

Owner: Voice/Speaker Reference domain.

Quan ly audio/transcript tham chieu clone chat giong. Speaker Reference khong phai Voice DNA.

## Voice

Voice giu Voice ID, display name, model/checkpoint reference, Speaker Reference, Style Profile link, Variant va generate defaults.

Voice ID bat bien. Display name co the doi.

## Project

Owner: Project Manager domain.

Project giu Project ID, display name, lifecycle metadata, workspace root, project root, active Voice/Style/Training/Generate selection va health state.

Project ID bat bien. Display name co the doi.

Project Manager khong sua file nguon trong workspace that. Archive khong xoa du lieu.

## Application Workspace

Owner: App/Core domain.

Application Workspace giu registry, settings, cache, logs, temp, imports/exports va global libraries neu co.

## External Source

Owner: User.

External source gom MP3, TXT, DOCX, reference audio va dataset folder nguoi dung chon tu ngoai Project. App khong tu copy/toan bo hoac sua noi dung neu nguoi dung chua chon.

## Reference Vault

Owner: Application Workspace / Reference domain.

Reference Vault giu managed copy cho MP3/WAV/TXT tham chieu, pair manifest, selected segment, validation report, Speaker Reference, Training Reference va Style Profile draft source.

Asset ID la identity. Filename/display name/original path chi la metadata/provenance.

Managed copy khong bi xoa khi Project rename, Voice rename, Style Profile rename hoac Project archive.

## Job Queue

Owner: App/Core domain.

Job Queue luu job metadata, state, progress, dependency, retry, recovery va log trong `workspace/jobs`.

Job payload/result phai JSON-safe va khong serialize QObject, thread, callback, file handle hoac secret.

Job khong so huu Project/Voice/Reference data. Job chi tham chieu bang Project ID, Voice ID, Style Profile ID, Dataset ID va Reference Asset ID.
# Resource Manager

Owner: App/Core domain.

Resource Manager so huu hardware snapshot, resource policy, resource decision va resource lease trong `workspace/jobs/resources`.

Resource Manager khong so huu Project, Voice, Dataset, Reference, model hoac runtime. Lease chi la quyen tam thoi de mot Job duoc dung CPU/GPU/Disk theo policy.

Snapshot/API khong duoc expose secret, token, full process list, serial number hoac du lieu ca nhan trong `projects/` va `workspace/`.

---
