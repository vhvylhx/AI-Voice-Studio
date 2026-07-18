# Resource Manager Architecture

Resource Manager la ha tang dung chung cho cac job dai va AI pipeline.

Flow:

1. Job khai bao ResourceRequirement.
2. Queue hoi ResourceDecisionService.
3. Neu ready, ResourceLeaseManager cap lease.
4. JobRunner chay worker.
5. Job ket thuc/pause/cancel/error/shutdown thi release lease.

Khong Train, Generate, analyzer, stress test, kill process, download model hoac sua GPT-SoVITS runtime trong Resource Manager.
