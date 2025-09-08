import csv
from datetime import datetime
from typing import List
from models.job import Job  # Assuming your Job model is in a 'models' directory


class CSVWriter:
    """
    A class to handle writing job data to a CSV file.
    """

    def __init__(self, search_term: str):
        """
        Initializes the writer with a search term to be used in the filename.
        """
        self.search_term = search_term.replace(" ", "_")
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.filename = f"data/{self.search_term}_{self.timestamp}.csv"

    def write_jobs(self, jobs: List[Job]):
        if not jobs:
            print("No jobs to write.")
            return

        print(f"Saving {len(jobs)} jobs to {self.filename}...")
        fieldnames = Job.__dataclass_fields__.keys()

        try:
            with open(self.filename, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for job in jobs:
                    writer.writerow(
                        {
                            "title": job.title,
                            "company_name": job.company_name,
                            "location": job.location,
                            "url": job.url,
                            "email": job.email,
                            "job_description": job.job_description,  # Make sure this is included
                        }
                    )
            print(f"Successfully saved jobs to {self.filename}")
        except IOError as e:
            print(f"Error writing to file {self.filename}: {e}")
