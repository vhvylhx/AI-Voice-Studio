from models.job_model import now_iso


class JobStateError(ValueError):

    pass


class JobStateMachine:

    TRANSITIONS = {
        "created": {
            "queued",
            "blocked",
            "cancelled",
        },
        "queued": {
            "waiting_dependency",
            "waiting_resource",
            "running",
            "cancel_requested",
            "cancelled",
            "blocked",
        },
        "waiting_dependency": {
            "queued",
            "blocked",
            "cancel_requested",
            "cancelled",
        },
        "waiting_resource": {
            "queued",
            "running",
            "blocked",
            "cancel_requested",
            "cancelled",
        },
        "running": {
            "pause_requested",
            "cancel_requested",
            "completed",
            "failed",
            "interrupted",
        },
        "pause_requested": {
            "paused",
            "cancel_requested",
            "interrupted",
        },
        "paused": {
            "resume_requested",
            "cancel_requested",
            "interrupted",
        },
        "resume_requested": {
            "queued",
            "running",
            "cancel_requested",
        },
        "cancel_requested": {
            "cancelling",
            "cancelled",
            "interrupted",
        },
        "cancelling": {
            "cancelled",
            "interrupted",
        },
        "retry_wait": {
            "queued",
            "cancel_requested",
            "blocked",
        },
        "failed": {
            "retry_wait",
            "queued",
        },
        "interrupted": {
            "queued",
            "cancelled",
            "blocked",
        },
        "completed": set(),
        "cancelled": set(),
        "blocked": set(),
    }

    def can_transition(
        self,
        current,
        target,
    ):

        return target in self.TRANSITIONS.get(
            current,
            set(),
        )

    def validate(
        self,
        current,
        target,
    ):

        if not self.can_transition(
            current,
            target,
        ):

            raise JobStateError(
                f"invalid_job_transition:{current}->{target}"
            )

        return True

    def apply(
        self,
        job,
        target,
    ):

        self.validate(
            job.state,
            target,
        )

        job.state = target

        now = now_iso()

        job.updated_at = now

        if target == "queued" and not job.queued_at:

            job.queued_at = now

        elif target == "running" and not job.started_at:

            job.started_at = now

        elif target == "paused":

            job.paused_at = now

        elif target in {
            "resume_requested",
            "running",
        } and job.paused_at:

            job.resumed_at = now

        elif target == "completed":

            job.completed_at = now

        elif target == "failed":

            job.failed_at = now

        elif target == "cancelled":

            job.cancelled_at = now

        return job
