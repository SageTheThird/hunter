from models.job import Job
from models.job_client import JobClient


class JobSearch:
    def __init__(self, clients: list[JobClient]):
        self.clients = clients

    def search(self, what, where, remote_only: bool = False) -> list[Job]:
        """
        Searches for jobs across all clients.

        :param what: The job title/keyword to search for.
        :param where: The location to search in.
        :param remote_only: If True, filters for remote jobs only.
        """
        all_jobs = []
        for client in self.clients:
            all_jobs.extend(client.get_jobs(what, where, remote_only=remote_only))
        return all_jobs
