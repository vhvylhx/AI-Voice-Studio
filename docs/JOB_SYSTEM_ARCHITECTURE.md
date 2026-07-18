# Job System Architecture

Job System la ha tang chung cho tac vu dai cua AI Voice Studio.

UI/Service -> JobQueueService -> JobRepository -> JobRunner -> BaseJobWorker -> Progress/Log/Event -> UI/API.

Sprint AVS-014.14 chua Train/Generate/analyzer that.
# AVS-014.15 Resource-aware Job System

Resource Manager duoc chen vao truoc Worker:

JobQueueService -> ResourceDecisionService -> ResourceLeaseManager -> JobRunner -> BaseJobWorker.

Neu tai nguyen chua du, job chuyen sang `waiting_resource`. Neu ready, queue cap lease truoc khi runner bat dau. Runner release lease khi job ket thuc, pause, cancel, fail, interrupted hoac shutdown.

---
