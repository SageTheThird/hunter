import json
import dataclasses
from models.job import Job
from .data_writer import DataWriter


class JSONLWriter(DataWriter):
    """
    A writer that appends job data to a JSONL file, one job at a time.
    """

    def __init__(self, search_term: str, output_dir: str = "data"):
        super().__init__(search_term, output_dir)
        self.filename = f"{self.base_filename}.jsonl"

    def append_job(self, job: Job):
        try:
            # Convert the Job dataclass object to a dictionary
            job_dict = dataclasses.asdict(job)

            # Convert the dictionary to a JSON string
            json_string = json.dumps(job_dict)

            with open(self.filename, "a", encoding="utf-8") as f:
                f.write(json_string + "\n")
        except IOError as e:
            print(f"Error writing to JSONL file {self.filename}: {e}")
