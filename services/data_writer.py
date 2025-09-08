from abc import ABC, abstractmethod
import os
from datetime import datetime
from models.job import Job


class DataWriter(ABC):
    """
    Abstract base class for data writers. Defines the interface for writing job data.
    """

    def __init__(self, search_term: str, output_dir: str = "data"):
        search_term_safe = search_term.replace(" ", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Create a base filename without an extension
        self.base_filename = os.path.join(output_dir, f"{search_term_safe}_{timestamp}")

    @abstractmethod
    def append_job(self, job: Job):
        """
        Appends a single job record to the output file.
        This must be implemented by all subclasses.
        """
        pass
