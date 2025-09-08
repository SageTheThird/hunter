from models.job_client import JobClient
from models.job import Job
import requests


class ArbeitnowClient(JobClient):
    BASE_URL = "https://www.arbeitnow.com/api"

    def get_jobs(self, what, where, page=1, remote_only: bool = False) -> list[Job]:
        params = {
            "search": what,
            "location": where,
            "page": page,
        }

        if remote_only:
            params["remote"] = "true"

        try:
            response = requests.get(f"{self.BASE_URL}/job-board-api", params=params)
            response.raise_for_status()
            jobs_data = response.json().get("data", [])
            return [
                Job(
                    title=job.get("title"),
                    company_name=job.get("company_name"),
                    location=job.get("location"),
                    url=job.get("url"),
                )
                for job in jobs_data
            ]
        except requests.exceptions.RequestException as e:
            print(f"An error occurred with Arbeitnow: {e}")
            return []
