from models.job import Job
from models.job_client import JobClient
import requests


class AdzunaClient(JobClient):
    BASE_URL = "https://api.adzuna.com/v1/api"

    def __init__(self, app_id, app_key, country="us"):
        self.app_id = app_id
        self.app_key = app_key
        self.country = country

    def get_jobs(
        self, what, where, page=1, results_per_page=10, remote_only: bool = False
    ) -> list[Job]:

        if remote_only:
            # Append "remote" to the search query
            search_what = f"{what} remote"
        else:
            search_what = what

        params = {
            "app_id": self.app_id,
            "app_key": self.app_key,
            "what": search_what,
            "where": where,
            "results_per_page": results_per_page,
        }

        try:
            response = requests.get(
                f"{self.BASE_URL}/jobs/{self.country}/search/{page}", params=params
            )
            response.raise_for_status()
            jobs_data = response.json().get("results", [])
            return [
                Job(
                    title=job.get("title"),
                    company_name=job.get("company", {}).get("display_name"),
                    location=job.get("location", {}).get("display_name"),
                    url=job.get("redirect_url"),
                )
                for job in jobs_data
            ]
        except requests.exceptions.RequestException as e:
            print(f"An error occurred with Adzuna: {e}")
            return []
