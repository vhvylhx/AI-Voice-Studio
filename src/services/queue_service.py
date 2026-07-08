from models.generate_queue import GenerateQueue


class QueueService:

    def __init__(self):

        self.queue = GenerateQueue()

    def add(self, job):

        self.queue.add(job)

    def add_many(self, jobs):

        for job in jobs:

            self.queue.add(job)

    def clear(self):

        self.queue.clear()

    def remove(self, job):

        self.queue.remove(job)

    def waiting(self):

        return self.queue.waiting()

    def running(self):

        return self.queue.running()

    def finished(self):

        return self.queue.finished()

    def failed(self):

        return self.queue.failed()

    def all(self):

        return self.queue.jobs

    def count(self):

        return len(self.queue)