# Resource Requirements

Moi workflow nang nen khai bao ResourceRequirement:

- cpu_threads;
- ram_mb;
- disk_free_mb;
- requires_gpu;
- gpu_count;
- vram_mb;
- allow_cpu_fallback;
- exclusive_gpu.

Khong duoc hard-code yeu cau resource trong UI. Worker/handler la noi khai bao contract.
