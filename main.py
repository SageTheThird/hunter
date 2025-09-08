import asyncio
import argparse
import os
from dotenv import load_dotenv

from api.adzuna import AdzunaClient
from api.arbetnow import ArbeitnowClient
from services.job_search import JobSearch
from services.csv_writer import CSVWriter
from services.scraper import ScraperService


async def main(
    search_what: str, search_where: str, remote_only: bool, test_limit: int = 0
):
    """
    Main asynchronous function to run the job search and scraping pipeline.
    """
    # --- Configuration ---
    # Load environment variables from .env file
    load_dotenv()
    ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
    ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")

    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        print("Error: ADZUNA_APP_ID and ADZUNA_APP_KEY must be set in the .env file.")
        return

    # --- Initialization ---
    adzuna_client = AdzunaClient(app_id=ADZUNA_APP_ID, app_key=ADZUNA_APP_KEY)
    arbeitnow_client = ArbeitnowClient()

    job_search = JobSearch(clients=[adzuna_client, arbeitnow_client])
    scraper_service = ScraperService()

    # Create a dynamic search term for the filename
    search_term_prefix = "remote_" if remote_only else ""
    csv_writer = CSVWriter(search_term=f"{search_term_prefix}{search_what}")

    # --- Execution ---
    print(
        f"Searching for '{search_what}' jobs in '{search_where}' (Remote: {remote_only})..."
    )
    all_jobs = job_search.search(
        what=search_what, where=search_where, remote_only=remote_only
    )

    if not all_jobs:
        print("No jobs found from APIs. Exiting.")
        return

    # If a test limit is set, slice the list of jobs
    if test_limit > 0:
        print(f"--- Applying test limit: only processing first {test_limit} jobs. ---")
        all_jobs = all_jobs[:test_limit]

    enriched_jobs = await scraper_service.enrich_jobs_with_details(all_jobs)
    csv_writer.write_jobs(enriched_jobs)

    print("Job search and export complete.")


if __name__ == "__main__":
    # --- Command-Line Argument Parsing ---
    parser = argparse.ArgumentParser(
        description="Automated Job Search and Scraper Tool"
    )
    parser.add_argument(
        "search_what",
        type=str,
        help="The job title or keyword to search for (e.g., 'software engineer').",
    )
    parser.add_argument(
        "search_where", type=str, help="The location to search in (e.g., 'USA')."
    )
    parser.add_argument(
        "--remote",
        action="store_true",
        help="Add this flag to search for remote-only jobs.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Limit the number of jobs to scrape for testing purposes (e.g., --limit 5).",
    )

    args = parser.parse_args()

    # Run the main asynchronous function with parsed arguments
    asyncio.run(
        main(
            search_what=args.search_what,
            search_where=args.search_where,
            remote_only=args.remote,
            test_limit=args.limit,
        )
    )
