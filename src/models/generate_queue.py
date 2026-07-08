from dataclasses import dataclass, field

from models.generate_job import GenerateJob


@dataclass
class GenerateQueue:

    jobs: list[GenerateJob] = field(
        default_factory=list
    )

    def add(self, job):

        self.jobs.append(job)

    def clear(self):

        self.jobs.clear()

    def remove(self, job):

        if job in self.jobs:

            self.jobs.remove(job)

    def waiting(self):

        return [
            job
            for job in self.jobs
            if job.status == "waiting"
        ]

    def running(self):

        return [
            job
            for job in self.jobs
            if job.status == "running"
        ]

    def finished(self):

        return [
            job
            for job in self.jobs
            if job.status == "finished"
        ]

    def failed(self):

        return [
            job
            for job in self.jobs
            if job.status == "failed"
        ]

    def __len__(self):

        return len(self.jobs)