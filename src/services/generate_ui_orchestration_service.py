class GenerateUiOrchestrationService:

    SESSION_PIPELINE = "SESSION_PIPELINE"

    LEGACY_COMPATIBILITY = "LEGACY_COMPATIBILITY"

    BLOCKED = "BLOCKED"

    def __init__(
        self,
        generate_session_service,
        job_queue_service,
        runtime_validation_service=None,
        legacy_compatibility_enabled=False,
    ):

        self.generate_session_service = generate_session_service

        self.job_queue_service = job_queue_service

        self.runtime_validation_service = runtime_validation_service

        self.legacy_compatibility_enabled = legacy_compatibility_enabled

        self.active_workflow = None

    def start(
        self,
        payload,
    ):

        if self.active_workflow is not None:

            snapshot = self.get_workflow_snapshot(
                self.active_workflow
            )

            if not snapshot.get(
                "terminal",
                False,
            ):

                return {
                    "ok": False,
                    "pipeline": self.SESSION_PIPELINE,
                    "status": snapshot["status"],
                    "blocker": "generate_workflow_in_progress",
                    "workflow": self.active_workflow,
                }

            self.active_workflow = None

        result = self.generate_session_service.create_session(
            payload
        )

        validation = result.get(
            "validation",
            {},
        )

        session = result.get(
            "session",
            {},
        )

        if not validation.get(
            "ok",
            False,
        ) or session.get(
            "status",
        ) == "blocked":

            return self.blocked_result(
                result,
                "generate_session_validation_blocked",
            )

        runtime_report = self.runtime_report(
            payload
        )

        runtime_blocker = self.runtime_blocker(
            runtime_report
        )

        if runtime_blocker:

            return self.blocked_result(
                result,
                runtime_blocker,
                runtime_report=runtime_report,
            )

        session_id = session.get(
            "session_id",
            "",
        )

        plan = self.generate_session_service.get_plan(
            session_id
        ) or {}

        jobs = []

        for unit in plan.get(
            "units",
            [],
        ):

            jobs.append(
                self.job_queue_service.enqueue_new(
                    "generate_unit",
                    project_id=payload.get(
                        "project_id",
                        "",
                    ),
                    voice_id=payload.get(
                        "voice_id",
                        "",
                    ),
                    payload={
                        "session_id": session_id,
                        "unit_id": unit.get(
                            "unit_id",
                            "",
                        ),
                    },
                )
            )

        if not jobs:

            return self.blocked_result(
                result,
                "generate_session_units_missing",
            )

        workflow = {
            "session_id": session_id,
            "job_ids": [
                job.job_id
                for job in jobs
            ],
            "pipeline": self.SESSION_PIPELINE,
            "runtime": runtime_report,
        }

        self.active_workflow = workflow

        return {
            "ok": True,
            "pipeline": self.SESSION_PIPELINE,
            "status": "QUEUED",
            "session": session,
            "job_ids": workflow["job_ids"],
            "runtime": runtime_report,
            "workflow": workflow,
            "result": result,
        }

    def get_workflow_snapshot(
        self,
        workflow,
    ):

        job_ids = workflow.get(
            "job_ids",
            [],
        )

        jobs = [
            self.job_queue_service.get(
                job_id
            )
            for job_id in job_ids
        ]

        jobs = [
            job
            for job in jobs
            if job is not None
        ]

        states = [
            job.state
            for job in jobs
        ]

        status = self.workflow_status(
            states,
            len(job_ids),
            len(jobs),
        )

        return {
            "session_id": workflow.get(
                "session_id",
                "",
            ),
            "job_ids": job_ids,
            "artifact_ids": self.artifact_ids(
                jobs
            ),
            "pipeline": workflow.get(
                "pipeline",
                self.SESSION_PIPELINE,
            ),
            "runtime": workflow.get(
                "runtime",
                {},
            ),
            "status": status,
            "terminal": status in {
                "COMPLETED",
                "FAILED",
                "BLOCKED",
            },
            "jobs": jobs,
        }

    def workflow_status(
        self,
        states,
        expected_count,
        resolved_count,
    ):

        if resolved_count != expected_count:

            return "FAILED"

        if "blocked" in states:

            return "BLOCKED"

        if "failed" in states:

            return "FAILED"

        if states and all(
            state == "completed"
            for state in states
        ):

            return "COMPLETED"

        if "running" in states:

            return "RUNNING"

        return "QUEUED"

    def artifact_ids(
        self,
        jobs,
    ):

        artifact_ids = []

        for job in jobs:

            result = job.result or {}

            artifact_id = result.get(
                "artifact_id",
                "",
            )

            if artifact_id:

                artifact_ids.append(
                    artifact_id
                )

        return artifact_ids

    def runtime_report(
        self,
        payload,
    ):

        if self.runtime_validation_service is None:

            return {
                "status": "UNAVAILABLE",
                "code": "generate_runtime_validation_missing",
                "message_vi": "Chưa có dịch vụ kiểm tra runtime Generate.",
            }

        return self.runtime_validation_service.readiness(
            {
                "voice_id": payload.get(
                    "voice_id",
                    "",
                ),
                "variant_id": payload.get(
                    "variant_id",
                    "",
                ),
            }
        )

    def runtime_blocker(
        self,
        report,
    ):

        status = report.get(
            "status",
            "UNAVAILABLE",
        )

        if status == "READY":

            return ""

        return report.get(
            "code",
            "generate_runtime_blocked",
        )

    def blocked_result(
        self,
        result,
        blocker,
        runtime_report=None,
    ):

        return {
            "ok": False,
            "pipeline": self.BLOCKED,
            "status": "BLOCKED",
            "blocker": blocker,
            "runtime": runtime_report or {},
            "result": result,
        }

    def can_use_legacy_compatibility(
        self,
        session_result,
    ):

        return (
            self.legacy_compatibility_enabled
            and session_result.get(
                "pipeline",
            ) == self.BLOCKED
            and session_result.get(
                "runtime",
                {},
            ).get(
                "status",
            ) == "UNAVAILABLE"
        )