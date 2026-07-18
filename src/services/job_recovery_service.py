class JobRecoveryService:

    def __init__(
        self,
        repository,
    ):

        self.repository = repository

    def recover_startup(
        self,
    ):

        return self.repository.recover_startup()

    def summary(
        self,
    ):

        jobs = self.repository.list_jobs()

        return {
            "queued": len(
                [
                    job
                    for job in jobs
                    if job.state == "queued"
                ]
            ),
            "paused": len(
                [
                    job
                    for job in jobs
                    if job.state == "paused"
                ]
            ),
            "interrupted": len(
                [
                    job
                    for job in jobs
                    if job.state == "interrupted"
                ]
            ),
        }
