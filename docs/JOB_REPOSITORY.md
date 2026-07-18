# Job Repository

JobRepository luu JSON trong `workspace/jobs/jobs/<job_id>/job.json`.

Nguyen tac:

- atomic write;
- schema_version;
- corrupt record duoc copy vao `workspace/jobs/corrupt`;
- record hong khong lam crash app;
- khong xoa history mac dinh;
- query theo state, project, type va priority.
