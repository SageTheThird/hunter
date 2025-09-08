from models.job import Job
from models.job_client import JobClient
import requests
from typing import List


class AdzunaClient(JobClient):
    BASE_URL = "https://api.adzuna.com/v1/api"

    def __init__(self, app_id, app_key, country="us"):
        self.app_id = app_id
        self.app_key = app_key
        self.country = country
        self.MAX_RESULTS_PER_PAGE = 50
        self.COUNTRY_MAP = {
            "australia": "au",
            "austria": "at",
            "brazil": "br",
            "canada": "ca",
            "france": "fr",
            "germany": "de",
            "india": "in",
            "italy": "it",
            "mexico": "mx",
            "netherlands": "nl",
            "new zealand": "nz",
            "poland": "pl",
            "singapore": "sg",
            "south africa": "za",
            "spain": "es",
            "switzerland": "ch",
            "united kingdom": "gb",
            "uk": "gb",
            "united states": "us",
            "usa": "us",
            "us": "us",
        }

    def _get_country_code(self, location: str) -> str | None:
        """
        Determines the country code from the location string.
        Returns None if no matching country is found.
        """
        # A simple search to find if a known country is mentioned in the location string
        for country, code in self.COUNTRY_MAP.items():
            if country in location.lower():
                return code
        return None  # Return None if no supported country is found

    def get_jobs(
        self, what: str, where: str, remote_only: bool = False, max_pages: int = 5
    ) -> List[Job]:
        all_found_jobs = []

        country_code = self._get_country_code(where)
        if not country_code:
            print(
                f"Adzuna search skipped: Location '{where}' is not a supported country."
            )
            return (
                all_found_jobs  # Return an empty list if the country is not supported
            )

        print(f"Adzuna client targeting country: '{country_code}'")

        current_page = 1
        while current_page <= max_pages:
            print(f"Fetching page {current_page} from Adzuna...")

            search_what = f"{what} remote" if remote_only else what
            params = {
                "app_id": self.app_id,
                "app_key": self.app_key,
                "what": search_what,
                "results_per_page": self.MAX_RESULTS_PER_PAGE,
            }
            if not remote_only:
                params["where"] = where

            try:
                # Use the page number in the URL path, as we fixed before
                url = f"{self.BASE_URL}/jobs/{country_code}/search/{current_page}"
                response = requests.get(url, params=params)
                response.raise_for_status()
                jobs_data = response.json().get("results", [])

                if not jobs_data:
                    print("Adzuna returned no more results. Stopping pagination.")
                    break

                for job in jobs_data:
                    all_found_jobs.append(
                        Job(
                            title=job.get("title"),
                            company_name=job.get("company", {}).get("display_name"),
                            location=job.get("location", {}).get("display_name"),
                            url=job.get("redirect_url"),
                        )
                    )

                current_page += 1

            except requests.exceptions.RequestException as e:
                print(f"An error occurred with Adzuna: {e}")
                break

        return all_found_jobs
