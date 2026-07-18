# Job Data Safety

Job khong so huu Project/Voice/Reference.

Job chi tham chieu stable IDs va ghi state/log rieng trong `workspace/jobs`.

Cancel/Retry khong duoc corrupt Project, Reference Vault hoac output hop le.

Interrupted job khong duoc danh dau completed.
# AVS-014.15 Resource Data Safety

- Resource snapshot khong doc/noi bo process list va khong expose secret/token.
- Resource lease chi nam trong `workspace/jobs/resources`, khong sua Project/Voice/Dataset/workspace source.
- Resource Manager khong kill process, khong stress GPU/CPU/RAM, khong tai model va khong sua runtime GPT-SoVITS.

---
