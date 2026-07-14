from dataclasses import dataclass, field

from models.generate_job import GenerateJob


@dataclass
class GenerateQueue:

    jobs: list[GenerateJob] = field(
        default_factory=list
    )

    #
    # CRUD
    #

    def add(self, job):

        self.jobs.append(job)

    def clear(self):

        self.jobs.clear()

    def remove(self, job):

        if job in self.jobs:

            self.jobs.remove(job)

    #
    # Query
    #

    def waiting(self):

        return self.find(
            "waiting"
        )

    def preparing(self):

        return self.find(
            "preparing"
        )

    def generating(self):

        return self.find(
            "generating"
        )

    def running(self):

        return self.find(
            "running"
        )

    def paused(self):

        return self.find(
            "paused"
        )

    def finished(self):

        return self.find(
            "finished"
        )

    def failed(self):

        return self.find(
            "failed"
        )

    def cancelled(self):

        return self.find(
            "cancelled"
        )

    #
    # Generic
    #

    def find(
        self,
        status,
    ):

        return [

            job

            for job in self.jobs

            if job.status == status

        ]

    #
    # Next Job
    #

    def next(self):

        for job in self.jobs:

            if job.status == "waiting":

                return job

        return None

    #
    # Progress
    #

    def total(self):

        return len(
            self.jobs
        )

    def completed(self):

        return len(
            self.finished()
        )

    def progress(self):

        if not self.jobs:

            return 0

        return int(

            self.completed()

            * 100

            / len(self.jobs)

        )

    #
    # Python
    #

    def __len__(self):

        return len(
            self.jobs
        )