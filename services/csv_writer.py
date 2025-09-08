import csv
import os
from models.job import Job
from .data_writer import DataWriter


class CSVWriter(DataWriter):
    """
    A writer that appends job data to a CSV file, one job at a time.
    """

    def __init__(self, search_term: str, output_dir: str = "data"):
        super().__init__(search_term, output_dir)
        self.filename = f"{self.base_filename}.csv"
        self._header_written = False

    def append_job(self, job: Job):
        # Check if the file exists to determine if we need to write a header
        file_exists = os.path.exists(self.filename)

        try:
            with open(self.filename, "a", newline="", encoding="utf-8") as csvfile:
                fieldnames = Job.__dataclass_fields__.keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                if not file_exists and not self._header_written:
                    writer.writeheader()
                    self._header_written = True

                writer.writerow(
                    {
                        "title": job.title,
                        "company_name": job.company_name,
                        "location": job.location,
                        "url": job.url,
                        "email": job.email,
                        "job_description": job.job_description,
                    }
                )
        except IOError as e:
            print(f"Error writing to CSV file {self.filename}: {e}")
