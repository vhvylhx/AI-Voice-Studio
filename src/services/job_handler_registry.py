from services.job_worker import (
    BaseJobWorker,
    DemoProgressJobWorker,
    GeneratePrepareJobWorker,
    ProjectBackupJobWorker,
    ProjectValidateJobWorker,
    ReferenceVerifyJobWorker,
)


class JobHandlerRegistry:

    def __init__(
        self,
    ):

        self.handlers = {}

        self.register(
            "demo_progress",
            DemoProgressJobWorker,
        )

        self.register(
            "reference_verify",
            ReferenceVerifyJobWorker,
        )

        self.register(
            "project_validate",
            ProjectValidateJobWorker,
        )

        self.register(
            "project_backup",
            ProjectBackupJobWorker,
        )

        self.register(
            "generate_prepare",
            GeneratePrepareJobWorker,
        )

    def register(
        self,
        job_type,
        handler,
    ):

        self.handlers[
            job_type
        ] = handler

    def has_handler(
        self,
        job_type,
    ):

        return job_type in self.handlers

    def create(
        self,
        job_type,
    ):

        handler = self.handlers.get(
            job_type
        )

        if handler is None:

            return None

        return handler()

    def supported_types(
        self,
    ):

        return sorted(
            self.handlers
        )

    def resource_requirement(
        self,
        job_type,
    ):

        handler = self.handlers.get(
            job_type
        )

        if handler is None:

            return BaseJobWorker.resource_requirement

        return getattr(
            handler,
            "resource_requirement",
            BaseJobWorker.resource_requirement,
        )
