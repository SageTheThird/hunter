from abc import ABC, abstractmethod
from models.job import Job


class JobClient(ABC):
    """
    Abstract base class for a job client.
    """

    @abstractmethod
    def get_jobs(self, what, where) -> list[Job]:
        pass
